import sys

from grid import *
from tkinter import *
from tkinter.filedialog import *




class MainDisplay:

	def __init__(self):

		self.window = Tk()

		self.height_canvas = 500
		self.width_canvas = 500

		self.grid_display = Grid_Project()

		self.canvas = Canvas(self.window, width = self.width_canvas, height = self.height_canvas)
		self.canvas.focus_set()
		self.canvas.bind("<Key>", self.press_keyboard)
		self.label_score = Label()
		self.display_buttons()
		self.get_name_window = None

		self.window.mainloop()

	def closing_option_window(self):
		self.get_name_window.destroy()
		self.get_name_window = None

	def display_generate_options(self):

		if self.get_name_window != None:
			print("Une fenêtre d'option est déjà ouverte !")
			self.get_name_window.focus_force()
		else:
			self.get_name_window = Toplevel(self.window)
			self.get_name_window.protocol("WM_DELETE_WINDOW", self.closing_option_window)

			Label(self.get_name_window, text="nom du fichier:").pack()
			file_name = Entry(self.get_name_window)
			file_name.pack()

			Label(self.get_name_window, text="hauteur grille:").pack()
			height_scale = Scale(self.get_name_window, from_=5, to=50, orient=HORIZONTAL)
			height_scale.set(20)
			height_scale.pack()

			Label(self.get_name_window, text="largeur grille:").pack()
			width_scale = Scale(self.get_name_window, from_=5, to=50, orient=HORIZONTAL)
			width_scale.set(20)
			width_scale.pack()

			Label(self.get_name_window, text="proportion de mur:").pack()
			wall_proportion_scale = Scale(self.get_name_window, from_=0, to=0.99, resolution=0.05, orient=HORIZONTAL)
			wall_proportion_scale.set(0.20)
			wall_proportion_scale.pack()

			# self.height = height_scale.get()
			# self.width = width_scale.get()
			# self.proba = wall_proportion_scale.get()
			# self.path = file_name.get()

			validate = Button(self.get_name_window, text = "Valider", command =lambda: self.generate(height_scale.get(),width_scale.get(),wall_proportion_scale.get(),file_name.get()))
			# validate = Button(self.get_name_window, text = "Valider")
			validate.pack()
		


	def display_buttons(self):
		buttonLoad = Button(self.window, text="Charger grille existante", command=self.import_file)
		buttonLoad.pack()
		buttonGenerate = Button(self.window, text="Générer nouvelle grille", command=self.display_generate_options)
		buttonGenerate.pack()

	def import_file(self):

		path = askopenfilename(filetypes=[("MADI","*.madi")])

		self.display_canvas(path)

	def generate(self,height,width,proba,path):

		self.get_name_window.destroy()
		self.get_name_window = None

		if len(path) == 0:
			path = "generated_grid.madi"

		elif len(path) < 5 or not str(path[len(path) - 5:len(path) - 1]) in ".madi":
			path += ".madi"

		grid_generator = GeneratorGrid(height, width, proba_walls = proba)
		grid_generator.export_grid(path)

		self.display_canvas(path)

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

		self.canvas.pack()
		self.display_score()
		self.display_robot()

	def display_robot(self):
		coef_reduce_circle = 0.2
		j = self.grid_display.position_robot_x
		i = self.grid_display.position_robot_y
		self.canvas.create_oval((j + coef_reduce_circle) * (self.width_canvas / self.grid_display.width), (i +coef_reduce_circle) * (self.height_canvas / self.grid_display.height), (j + 1 - coef_reduce_circle) * (self.width_canvas / self.grid_display.width), (i + 1 - coef_reduce_circle) * (self.height_canvas / self.grid_display.height), fill = 'green', tags = "robot")
		self.canvas.pack()		

	def move_robot(self, x, y):
		self.canvas.delete("robot")
		coef_reduce_circle = 0.2
		self.canvas.create_oval((x + coef_reduce_circle) * (self.width_canvas / self.grid_display.width), (y +coef_reduce_circle) * (self.height_canvas / self.grid_display.height), (x + 1 - coef_reduce_circle) * (self.width_canvas / self.grid_display.width), (y + 1 - coef_reduce_circle) * (self.height_canvas / self.grid_display.height), fill = 'green', tags = "robot")
		self.display_score()


	def display_score(self):
		self.label_score.destroy()
		self.label_score = Label(self.window, text = "score : " + str(self.grid_display.score))
		self.label_score.pack()

	def press_keyboard(self, event):

		keyboard_key = event.keysym
		y = self.grid_display.position_robot_y
		x = self.grid_display.position_robot_x

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

		self.grid_display.position_robot_y = y
		self.grid_display.position_robot_x = x
		self.grid_display.score += self.grid_display.grid[y][x].score

		self.move_robot(x, y)


window = MainDisplay()

