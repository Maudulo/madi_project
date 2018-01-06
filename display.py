import sys

from grid import *
from dijkstra import *
from PDM import *

from tkinter import *
from tkinter.filedialog import *
from tkinter import messagebox


class MainDisplay:

	def __init__(self):

		self.window = Tk()
		self.window.resizable(False, False)
		self.height_canvas = 500
		self.width_canvas = 500

		self.grid_display = Grid_Project()

		self.canvas = Canvas(self.window, width = self.width_canvas, height = self.height_canvas)
		self.canvas.focus_set()
		self.canvas.bind("<Key>", self.press_keyboard)
		self.label_score = Label()
		self.display_buttons()
		self.name_option_window = None
		self.name_selection_window = None
		self.name_compute_solution = None
		self.name_parameters = None

		self.p = 0.6
		self.q = 1
		self.gamma = 0.9
		self.max_reward = 10000
		self._base_reward = 1
		self._coef_reward = 4
		self.solution = None		

		self.window.mainloop()

	def closing_option_window(self):
		self.name_option_window.destroy()
		self.name_option_window = None

	def closing_compute_window(self):
		self.name_compute_solution.destroy()
		self.name_compute_solution = None

	def closing_selection_window(self):
		self.name_selection_window.destroy()
		self.name_selection_window = None

	def closing_parameters(self):
		self.name_parameters.destroy()
		self.name_parameters = None


	def display_generate_options(self):

		if self.name_option_window != None:
			print("Une fenêtre d'option est déjà ouverte !")
			self.name_option_window.focus_force()
		else:
			self.name_option_window = Toplevel(self.window)
			self.name_option_window.resizable(False, False)
			self.name_option_window.protocol("WM_DELETE_WINDOW", self.closing_option_window)

			Label(self.name_option_window, text="nom du fichier:").grid(row = 0, column = 0)
			file_name = Entry(self.name_option_window)
			file_name.grid(row = 0, column = 1)

			Label(self.name_option_window, text="hauteur grille:").grid(row = 1, column = 0)
			height_scale = Scale(self.name_option_window, from_=5, to=50, orient=HORIZONTAL)
			height_scale.set(20)
			height_scale.grid(row = 1, column = 1)

			Label(self.name_option_window, text="largeur grille:").grid(row = 2, column = 0)
			width_scale = Scale(self.name_option_window, from_=5, to=50, orient=HORIZONTAL)
			width_scale.set(20)
			width_scale.grid(row = 2, column = 1)

			Label(self.name_option_window, text="proportion de mur:").grid(row = 3, column = 0)
			wall_proportion_scale = Scale(self.name_option_window, from_=0, to=0.99, resolution=0.05, orient=HORIZONTAL)
			wall_proportion_scale.set(0.20)
			wall_proportion_scale.grid(row = 3, column = 1)

			# self.height = height_scale.get()
			# self.width = width_scale.get()
			# self.proba = wall_proportion_scale.get()
			# self.path = file_name.get()

			validate = Button(self.name_option_window, text = "Valider", command =lambda: self.generate(height_scale.get(),width_scale.get(),wall_proportion_scale.get(),file_name.get()))
			# validate = Button(self.name_option_window, text = "Valider")
			validate.grid(columnspan = 2)
		
	def reset_position(self):
		# reset robot position
		self.grid_display.position_robot_x = self.grid_display.origin_robot_x
		self.grid_display.position_robot_y = self.grid_display.origin_robot_y
		self.move_robot(self.grid_display.position_robot_x, self.grid_display.position_robot_y)

		# reset score
		self.grid_display.score = [0,0,0,0]
		self.grid_display.color_visited = [0,0,0,0]
		self.display_score()
		self.solution = None

	def get_to_start_position(self):
		# reset robot position
		self.grid_display.position_robot_x = self.grid_display.origin_robot_x
		self.grid_display.position_robot_y = self.grid_display.origin_robot_y
		self.move_robot(self.grid_display.position_robot_x, self.grid_display.position_robot_y)

		# reset score
		self.grid_display.score = [0,0,0,0]
		self.grid_display.color_visited = [0,0,0,0]
		self.display_score()

	def display_position_selection(self):
		if self.name_selection_window != None:
			print("Une fenêtre d'option est déjà ouverte !")
			self.name_selection_window.focus_force()
			return

		result = messagebox.askquestion("Changer les positions de départ/arrivée", "Êtes-vous sûr de vouloir changer les positions de départ/arrivée ?\nCe changement va entrainer la réinitialisation du score et de la solution", icon='warning')
		if result == 'yes':
			self._display_position_selection()



	def _display_position_selection(self):
		if self.name_selection_window != None:
			print("Une fenêtre d'option est déjà ouverte !")
			self.name_selection_window.focus_force()
		else:
			self.name_selection_window = Toplevel(self.window)
			self.name_selection_window.resizable(False, False)
			self.name_selection_window.protocol("WM_DELETE_WINDOW", self.closing_selection_window)

			Label(self.name_selection_window, text="Veuillez choisir la position de départ avec le clic gauche et la position d'arrivée avec le clic droit.", font = "Helvetica 10 bold").grid()
			
			self.canvas.bind("<Button-1>", self.select_start_position_callback)
			self.canvas.bind("<Button-3>", self.select_goal_position_callback)
		
			Button(self.name_selection_window, text="Valider", command=self.end_selection_start_goal_position).grid()
			self.solution = None
			self.grid_display.score = [0,0,0,0]
			self.display_score()

	def select_start_position_callback(self,event):
		if event.x < self.canvas.winfo_rootx() and event.x > self.label_score.winfo_rootx():
			return
		x = int(event.x // (self.height_canvas / self.grid_display.height))
		y = int(event.y // (self.width_canvas / self.grid_display.width))
		if (x != self.grid_display.goal_x or y != self.grid_display.goal_y) and "wall" not in self.grid_display.grid[y][x].type_location:
			self.grid_display.origin_robot_x = x
			self.grid_display.origin_robot_y = y
			self.display_start()

	def select_goal_position_callback(self,event):
		if event.x < self.canvas.winfo_rootx() and event.x >= self.label_score.winfo_rootx():
			return
		x = int(event.x // (self.height_canvas / self.grid_display.height))
		y = int(event.y // (self.width_canvas / self.grid_display.width))
		if (x != self.grid_display.origin_robot_x or y != self.grid_display.origin_robot_y) and "wall" not in self.grid_display.grid[y][x].type_location:
			self.grid_display.goal_x = x
			self.grid_display.goal_y = y
			self.display_goal()

	def end_selection_start_goal_position(self):
		self.canvas.unbind("<Button-1>")
		self.canvas.unbind("<Button-3>")
		self.move_robot(self.grid_display.origin_robot_x, self.grid_display.origin_robot_y)
		self.name_selection_window.destroy()
		self.name_selection_window = None



	def display_buttons(self):
		buttonLoad = Button(self.window, text="Charger grille existante", command=self.import_file)
		buttonLoad.grid(row = 0, column = 0, padx=10, pady=10)
		buttonGenerate = Button(self.window, text="Générer nouvelle grille", command=self.display_generate_options)
		buttonGenerate.grid(row = 1, column = 0, padx=10, pady=10)

	def import_file(self):

		path = askopenfilename(filetypes=[("MADI","*.madi")])

		self.display_canvas(path)



	def generate(self,height,width,proba,path):

		self.name_option_window.destroy()
		self.name_option_window = None

		reset = Button(self.window, text="Réinitialiser", command=self.reset_position)
		reset.grid(row = 0, column = 1, padx=0.1, pady=5)
		get_to_start_position = Button(self.window, text="Début", command=self.get_to_start_position)
		get_to_start_position.grid(row = 0, column = 2, padx=0.1, pady=5)
		select_start_goal_position = Button(self.window, text="Selection start/end", command=self.display_position_selection)
		select_start_goal_position.grid(row = 1, column = 1, columnspan=2, padx=10, pady=10)
		get_solution = Button(self.window, text="Calculer une solution", command=self.display_compute_solution)
		get_solution.grid(row = 0, column = 3, padx=10, pady=10)
		change_parameters = Button(self.window, text="Changer les paramètres", command=self.display_parameters)
		change_parameters.grid(row = 1, column = 3, padx=10, pady=10)


		if len(path) == 0:
			path = "generated_grid.madi"

		elif len(path) < 5 or not str(path[len(path) - 5:len(path) - 1]) in ".madi":
			path += ".madi"

		grid_generator = GeneratorGrid(height, width, proba_walls = proba)
		grid_generator.export_grid(path)

		self.display_canvas(path)
		self.T = PDM(self.grid_display).get_transition_matrix(self.p, self.q, self.max_reward)

	def display_compute_solution(self):
		if self.name_compute_solution != None:
			print("Une fenêtre d'option est déjà ouverte !")
			self.name_compute_solution.focus_force()
		else:
			self.name_compute_solution = Toplevel(self.window)
			self.name_compute_solution.resizable(False, False)
			self.name_compute_solution.protocol("WM_DELETE_WINDOW", self.closing_compute_window)

			Label(self.name_compute_solution, text="Veuillez choisir la méthode de résolution du meilleur chemin.", font = "Helvetica 10 bold").grid(pady=5)
			
			Button(self.name_compute_solution, text="PDM (consommation pure)", command =lambda: self.getSolution(politic_type = "consommation")).grid(pady=5)
			Button(self.name_compute_solution, text="PDM (ordre couleurs)", command =lambda: self.getSolution(politic_type = "couleur")).grid(pady=5)
			Button(self.name_compute_solution, text="PDM itération par valeur (couleur = risque)", command =lambda: self.getSolution(politic_type = "PDM_valeur")).grid(pady=5)
			Button(self.name_compute_solution, text="PDM itération par politique (couleur = risque)", command =lambda: self.getSolution(politic_type = "PDM_policy")).grid(pady=5)
			Button(self.name_compute_solution, text="PDM par PL (couleur = risque)", command =lambda: self.getSolution(politic_type = "PDM_PL")).grid(pady=5)
			Button(self.name_compute_solution, text="MOMDP (politique mixte)", command =lambda: self.getSolution(politic_type = "MOMDP_mixte")).grid(pady=5)
			Button(self.name_compute_solution, text="MOMDP (politique pure)", command =lambda: self.getSolution(politic_type = "MOMDP_pure")).grid(pady=5)

	def display_parameters(self):
		if self.name_parameters != None:
			print("Une fenêtre d'option est déjà ouverte !")
			self.name_parameters.focus_force()
		else:
			self.name_parameters = Toplevel(self.window)
			self.name_parameters.resizable(False, False)
			self.name_parameters.protocol("WM_DELETE_WINDOW", self.closing_parameters)

			Label(self.name_parameters, text="Veuillez choisir Les nouveaux paramètres", font = "Helvetica 10 bold").grid(row = 0,columnspan=2)
			gamma = Scale(self.name_parameters, from_=0, to=1, orient=HORIZONTAL, resolution=0.05, tickinterval=0.25, label='Gamma', length=200)
			gamma.grid(row=1,columnspan=2, pady=10)
			gamma.set(self.gamma)

			p = Scale(self.name_parameters, from_=0, to=1, orient=HORIZONTAL, resolution=0.05, tickinterval=0.25, label='P', length=200)
			p.grid(row=2,columnspan=2, pady=10)
			p.set(self.p)

			q = Scale(self.name_parameters, from_=0, to=1, orient=HORIZONTAL, resolution=0.05, tickinterval=0.25, label='Q', length=200)
			q.grid(row=3,columnspan=2, pady=10)
			q.set(self.q)

			basevar = IntVar()
			basevar.set(self._base_reward)
			base_reward = Scale(self.name_parameters, from_=1, to=9, orient=HORIZONTAL,variable = basevar, resolution=1, tickinterval=3, label='base de la récompense', length=150, command=lambda base: self.report_change(base, coefvar.get()))
			base_reward.grid(row=5,column = 0)
			coefvar = IntVar()
			coefvar.set(self._coef_reward)
			coef_reward = Scale(self.name_parameters, from_=0, to=10, orient=HORIZONTAL,variable = coefvar, resolution=1, tickinterval=5, label='fois 10 puissance:', length=150, command=lambda coef: self.report_change(basevar.get(),coef))
			coef_reward.grid(row=5,column = 1)
			coef_reward.set(self._coef_reward)
			self.label_reward = StringVar()
			Label(self.name_parameters, textvariable=self.label_reward).grid(row=4,columnspan=2)
			self.report_change(basevar.get(),coefvar.get())

			validate = Button(self.name_parameters, text = "Valider", command =lambda: self._update_parameters(gamma.get(), p.get(), q.get(),base_reward.get(),coef_reward.get())).grid(row=6,columnspan=2, pady=15)

	def report_change(self,base,coef):
		self.label_reward.set("récompense but = " + str(int(base)*10**int(coef)))

	def _update_parameters(self, gamma,p,q,base_reward, coef_reward):
		self.name_parameters.destroy()
		self.name_parameters = None
		self.gamma = gamma
		self.p = p
		self.q = q
		self._base_reward = base_reward
		self._coef_reward = coef_reward
		self.max_reward = base_reward * 10**coef_reward
		self.T = PDM(self.grid_display).get_transition_matrix(self.p, self.q, self.max_reward)

	def getSolution(self, politic_type = ""):
		p = self.p
		q = self.q
		gamma = self.gamma
		max_reward = self.max_reward

		if politic_type == "PDM_valeur":
			pdm = PDM(self.grid_display, max_reward = max_reward, p = p, q = q) 
			self.solution = pdm.iteration_by_value(gamma = gamma)
			 
		elif politic_type == "PDM_policy":
			pdm = PDM(self.grid_display, max_reward = max_reward, p = p, q = q)
			self.solution = pdm.iteration_by_policy(gamma = gamma)
			
		elif politic_type == "PDM_PL":
			pdm = PDM(self.grid_display, max_reward = max_reward, p = p, q = q) 
			self.solution = pdm.resolution_by_PL(gamma = gamma)

		elif politic_type == "MOMDP_mixte":
			pdm = PDM(self.grid_display, multi_obj = True, max_reward = max_reward, p = p, q = q) 
			self.solution = pdm.PLMO(pure_politic = False, gamma = gamma)

		elif politic_type == "MOMDP_pure":
			pdm = PDM(self.grid_display, multi_obj = True, max_reward = max_reward, p = p, q = q) 
			self.solution = pdm.PLMO(pure_politic = True, gamma = gamma)
			
		elif politic_type == "consommation":
			pdm = PDM(self.grid_display, consumption_only = True, max_reward = max_reward, p = p, q = q) 
			self.solution = pdm.iteration_by_value(gamma = gamma)

		elif politic_type == "couleur":
			pdm = PDM(self.grid_display, color_restrictive = True, max_reward = max_reward, p = p, q = q) 
			self.solution = pdm.iteration_by_value(gamma = gamma)

		else:
			print("Erreur fatale pas de fonction de ce nom\n", politic_type)

		messagebox.showinfo("Solution calculée", "La solution est calculée.\nVeuillez appuyer sur SPACE pour la visualiser")
		return



	def display_canvas(self, path):

		self.grid_display = Grid_Project()
		self.grid_display.load_grid(path)

		for i in range(self.grid_display.height):
			for j in range(self.grid_display.width):
				color = ""
				if "wall" in str(self.grid_display.grid[i][j].type_location):
					color = 'black'
				elif self.grid_display.grid[i][j].color == 0:
					color = 'light green'
				elif self.grid_display.grid[i][j].color == 1:
					color = 'light blue'
				elif self.grid_display.grid[i][j].color == 2:
					color = 'lightSalmon2'
				else:
					color = 'grey65'

				self.canvas.create_rectangle(j * (self.width_canvas / self.grid_display.width), i * (self.height_canvas / self.grid_display.height), (j + 1) * (self.width_canvas / self.grid_display.width), (i + 1) * (self.height_canvas / self.grid_display.height), fill = color)
				self.canvas.create_text(j * (self.width_canvas / self.grid_display.width) + 5, i * (self.height_canvas / self.grid_display.height) + 8, text = self.grid_display.grid[i][j].score)

		self.canvas.grid(columnspan = 4)
		self.display_score()
		self.display_start()
		self.display_robot()
		self.display_goal()

	def display_goal(self):
		self.canvas.delete("goal")
		j = self.grid_display.goal_x
		i = self.grid_display.goal_y
		self.canvas.create_rectangle((j+0.35) * (self.width_canvas / self.grid_display.width), i * (self.height_canvas / self.grid_display.height), (j + 1) * (self.width_canvas / self.grid_display.width), (i + 1) * (self.height_canvas / self.grid_display.height), fill = '#FF6600', tags = "goal")
		self.canvas.grid(columnspan = 4)
		self.display_robot()

	def display_start(self):
		self.canvas.delete("start")
		j = self.grid_display.origin_robot_x
		i = self.grid_display.origin_robot_y
		self.canvas.create_rectangle((j+0.35) * (self.width_canvas / self.grid_display.width), i * (self.height_canvas / self.grid_display.height), (j + 1) * (self.width_canvas / self.grid_display.width), (i + 1) * (self.height_canvas / self.grid_display.height), fill = '#16992C', tags = "start")
		self.canvas.grid(columnspan = 4)
		self.display_robot()

	def display_robot(self):
		coef_reduce_circle = 0.2
		j = self.grid_display.position_robot_x
		i = self.grid_display.position_robot_y
		self.canvas.create_oval((j + coef_reduce_circle) * (self.width_canvas / self.grid_display.width), (i +coef_reduce_circle) * (self.height_canvas / self.grid_display.height), (j + 1 - coef_reduce_circle) * (self.width_canvas / self.grid_display.width), (i + 1 - coef_reduce_circle) * (self.height_canvas / self.grid_display.height), fill = 'green', tags = "robot")
		self.canvas.grid(columnspan = 4)		

	def move_robot(self, x, y):
		self.grid_display.position_robot_x = x
		self.grid_display.position_robot_y = y
		self.canvas.delete("robot")
		coef_reduce_circle = 0.2
		self.canvas.create_oval((x + coef_reduce_circle) * (self.width_canvas / self.grid_display.width), (y +coef_reduce_circle) * (self.height_canvas / self.grid_display.height), (x + 1 - coef_reduce_circle) * (self.width_canvas / self.grid_display.width), (y + 1 - coef_reduce_circle) * (self.height_canvas / self.grid_display.height), fill = 'green', tags = "robot")
		self.display_score()


	def display_score(self):
		self.label_score.destroy()
		self.label_score = Label(self.window, text = "score : " + self.grid_display.display_score())
		self.label_score.grid(columnspan = 4, padx=10, pady=10)

	def press_keyboard(self, event):

		keyboard_key = event.keysym
		y = self.grid_display.position_robot_y
		x = self.grid_display.position_robot_x
		old_x = x
		old_y = y

		if(keyboard_key == "z"):
			if not (y == 0 or "wall" in self.grid_display.grid[y - 1][x].type_location):
				y = y - 1
		elif(keyboard_key == "q"):
			if not (x == 0 or "wall" in self.grid_display.grid[y][x - 1].type_location):
				x = x - 1
		elif(keyboard_key == "d"):
			if not (x == (self.grid_display.width - 1) or "wall" in self.grid_display.grid[y][x + 1].type_location):
				x = x + 1
		elif(keyboard_key == "s"):
			if not (y == (self.grid_display.height - 1) or "wall" in self.grid_display.grid[y + 1][x].type_location):
				y = y + 1

		elif(keyboard_key == "Up"):
			x,y = self.move_with_bias(0)
		elif(keyboard_key == "Down"):
			x,y = self.move_with_bias(1)
		elif(keyboard_key == "Left"):
			x,y = self.move_with_bias(2)
		elif(keyboard_key == "Right"):
			x,y = self.move_with_bias(3)

		elif(keyboard_key == "space"):
			if self.solution == None:
				messagebox.showinfo("Aucune Solution", "Vous avez réinitialisé ou vous n'avez pas encore calculé une solution")
				return

			action = self.choose_a_solution()
			print(action)
			if self.grid_display.position_robot_x == self.grid_display.goal_x and self.grid_display.position_robot_y == self.grid_display.goal_y:
				messagebox.showinfo("Fin", "Le robot a atteint son but")
				return
			else:
				x,y = self.move_with_bias(action)
			

		if not (old_x == x and old_y == y):
			self.grid_display.position_robot_y = y
			self.grid_display.position_robot_x = x
			self.grid_display.score[self.grid_display.grid[old_y][old_x].color] += self.grid_display.grid[old_y][old_x].score
			self.grid_display.color_visited[self.grid_display.grid[old_y][old_x].color] += 1
			# self.grid_display.score += self.grid_display.grid[y][x].score

			self.move_robot(x, y)

	def move_with_bias(self, direction):
		position = self.grid_display.position_robot_x + self.grid_display.position_robot_y * self.grid_display.width
		# print(self.solution)
		possibilities = np.cumsum(self.T[position][direction])
		rand = np.random.rand()
		i = 0
		for x in possibilities:
			if rand < x:
				return (i % self.grid_display.width), (int(i / self.grid_display.width))
			i += 1
		print("erreur ne somme pas à 1")

	def choose_a_solution(self):
		position = self.grid_display.position_robot_x + self.grid_display.position_robot_y * self.grid_display.width
		# print(self.solution)
		possibilities = np.cumsum(self.solution[position])
		rand = np.random.rand()
		i = 0
		for x in possibilities:
			if rand < x:
				return i
			i += 1
		print("erreur ne somme pas à 1")

window = MainDisplay()

