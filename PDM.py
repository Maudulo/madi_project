import random
from enum import Enum

import importlib
if importlib.util.find_spec("gurobipy") is not None :
	from gurobipy import *
	CAN_USE_PL = True
else:
	CAN_USE_PL = False

from tkinter import messagebox

import time
import os

class PDM:

	def __init__(self, board, goal):
		self.board = board
		self.goal = goal
		self.get_transition_matrix()
		self.width = len(self.board[0])
		self.height = len(self.board)
		self.number_of_states = self.width * self.height
		self.number_of_actions = 4


	def get_transition_matrix(self):
		
		# on créer le tableau des récompenses
		self.R = []
		for line in self.board:
			for pos in line:
				if pos.position_x == self.goal[0] and pos.position_y == self.goal[1]:
					self.R.append(1000)
				elif pos.type_location == "normal":
					self.R.append(-pos.color)
				else:
					self.R.append(0)

		# on créer la matrice de transition
		self.T = np.zeros((self.number_of_states, self.number_of_actions, self.number_of_states))
		for y in range(self.height):
			for x in range(self.width):
				bias = 0

				# vers le haut
				if y == 0: # si on est tout en haut
					self.T[self.width*y+x, 1, self.width*y+x] = 1
				elif self.board[y-1][x].type_location == "normal": # si la case du haut est accessible
					# case haut-gauche
					if x == 0:
						bias += 0.2
					elif self.board[y-1][x-1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y-1)+x-1] = 0.2
					else:
						bias +=0.2
					# case haut-droite
					if x == self.width-1:
						bias +=0.2
					elif self.board[y-1][x+1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y-1)+x+1] = 0.2
					else:
						bias +=0.2
					# case haut-centre
					self.T[self.width*y+x, 1, self.width*(y-1)+x] = 0.6+bias
				else: # si la case du haut est un mur
					self.T[self.width*y+x, 1, self.width*y+x] = 1
				
				bias = 0
				# vers le bas
				if y == self.height-1: # si on est tout en bas
					self.T[self.width*y+x, 1, self.width*y+x] = 1
				elif self.board[y+1][x].type_location == "normal": # si la case du bas est accessible
					# case bas-gauche
					if x == 0:
						bias += 0.2
					elif self.board[y+1][x-1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y+1)+x-1] = 0.2
					else:
						bias +=0.2
					# case bas-droite
					if x == self.width-1:
						bias +=0.2
					elif self.board[y+1][x+1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y+1)+x+1] = 0.2
					else:
						bias +=0.2
					# case bas-centre
					self.T[self.width*y+x, 1, self.width*(y+1)+x] = 0.6+bias
				else: # si la case du bas est un mur
					self.T[self.width*y+x, 1, self.width*y+x] = 1

				bias = 0
				# vers la gauche
				if x == 0: # si on est tout à gauche
					self.T[self.width*y+x, 1, self.width*y+x] = 1
				elif self.board[y][x-1].type_location == "normal": # si la case de gauche est accessible
					# case gauche-haut
					if y == 0:
						bias += 0.2
					elif self.board[y-1][x-1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y-1)+x-1] = 0.2
					else:
						bias +=0.2
					# case gauche-bas
					if y == self.height-1:
						bias +=0.2
					elif self.board[y+1][x-1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y+1)+x-1] = 0.2
					else:
						bias +=0.2
					# case gauche-centre
					self.T[self.width*y+x, 1, self.width*y+x-1] = 0.6+bias
				else: # si la case de gauche est un mur
					self.T[self.width*y+x, 1, self.width*y+x] = 1

				bias = 0
				# vers la droite
				if x == self.width-1: # si on est tout à droite
					self.T[self.width*y+x, 1, self.width*y+x] = 1
				elif self.board[y][x+1].type_location == "normal": # si la case de droite est accessible
					# case droite-haut
					if y == 0:
						bias += 0.2
					elif self.board[y-1][x+1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y-1)+x+1] = 0.2
					else:
						bias +=0.2
					# case droite-bas
					if y == self.height-1:
						bias +=0.2
					elif self.board[y+1][x+1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y+1)+x+1] = 0.2
					else:
						bias +=0.2
					# case droite-centre
					self.T[self.width*y+x, 1, self.width*y+x+1] = 0.6+bias
				else: # si la case de droite est un mur
					self.T[self.width*y+x, 1, self.width*y+x] = 1


	def get_best_policy_from_best_values(self, Vt):
		return [np.argmax([self.R[s] +  gamma * (np.dot(self.T[s,a]*Vt)) for a in range(self.number_of_actions)]) for s in range(self.number_of_states)]


	def iteration_by_value(self, gamma = 0.5, epsilon = 0.001):
		t = 0
		Vt_1 = np.zeros((self.number_of_states))
		Vt = np.zeros((self.number_of_states))

		while True:
			t += 1
			for s in range(self.number_of_states):
				Vt[s] = max([self.R[s] +  gamma * (np.dot(self.T[s,a]*Vt-1)) for a in range(self.number_of_actions)])
			# si l'écart de valeur entre deux itérations est inférieur à epsilon, alors on s'arrête
			# if max([abs(x-y) for (x,y) in zip(Vt,Vt_1)]) < epsilon:
			# 	break
			if np.allclose(Vt, Vt_1, atol = epsilon, rtol = 0):
				break
			else:
				Vt_1 = copy.copy(Vt)

		return (self.get_best_policy_from_best_values(Vt), Vt, t)

		
	
	def iteration_by_policy(self, gamma = 0.5):
		t = 0
		# on selectionne une action au hasard pour chaque état
		actions = [np.random.randint(0, self.number_of_actions+1) for _ in range(self.number_of_states)]
		actions_1 = copy.copy(actions)
		coefs = np.zeros((self.number_of_states, self.number_of_states))
		consts = np.zeros((self.number_of_states))
		results = np.zeros((self.number_of_states))

		while True:
			t += 1
			# on résoud le système
			for s in range(self.number_of_states):
				# Vt[s] = self.R[s] +  gamma * (np.dot(self.T[s,actions[s]]*Vt))
				coefs[s] = [self.T[s,actions[s]]]*gamma
				coefs[s,s] -= 1
				consts[s] = -self.R[s]
			results = np.linalg.solve(coefs,consts)
			# check if solution is correct
			if not np.allclose(np.dot(coefs,results),const):
				messagebox.showerror("Erreur", "une erreur est arrivée dans la résolution du système d'équations pour l'itération de la politique\nImpossible de trouver la solution")
				print("Erreur dans la résolution du système d'équations pour l'itération de la politique")
				return -1
			# on récupère la nouvelle meilleure politique 
			for s in range(self.number_of_states):
				actions[s] = np.argmax([self.R[s] +  gamma * (np.dot(self.T[s,a]*results)) for a in range(self.number_of_actions)])
			# si la politique est la même qu'au tour précédent on arrête
			if np.allclose(actions, actions_1):
				break
			else:
				actions_1 = copy.copy(actions)

		Vt = [self.R[s] +  gamma * (np.dot(self.T[s,actions[s]]*results)) for s in range(self.number_of_states)]
		
		return (actions, Vt,t)


	def resolution_by_PL(self,gamma = 0.5):
		if CAN_USE_PL:
			self._resolution_by_PL(gamma)
		else:
			messagebox.showinfo("Limitations", "Cette session ne dispose pas du solveur gurobi et de son interface gurobipy.py\nimpossible d'utiliser cette opération")

	def _resolution_by_PL(self, gamma = 0.5):
		# résoudre min sum(Vt)
		# sous contraintes: Vt[s] >= R(s,a) + gamma * sum_forall_s'(T[s,a,s'] * Vt[s']) for all s for all a
		# puis choisir la meilleur action pour chaque état 

		
		try:

		    # Create a new model
		    m = Model("mip")

		    # Create variables
		    
		    Vt = []
		    for state in range(self.number_of_states):
		    	Vt[state] = self.model.addVar(0, GRB.INFINITY, vtype=GRB.CONTINIOUS)
		    self.model.update()


		    # Set objective
		    m.setObjective(quicksum(Vt), GRB.MINIMIZE)

		    # Add constraint
		    for state in range(self.number_of_states):
		    	for action in range(self.number_of_actions):
		    		# m.addConstr(Vt[state], GRB.GREATER_EQUAL, self.R[s] +  gamma * (np.dot(self.T[s,a]*Vt))
		    		m.addConstr(Vt[state] - gamma * quicksum([self.T[s,a,s2]*Vt[s2]for s2 in range(self.number_of_states)]), GRB.GREATER_EQUAL, self.R[s])
		    m.update()

		    start_time = time.time()
		    m.optimize()
		    t = (time.time() - start_time)

		    for v in m.getVars():
		        print(v.varName, v.x)

		    print('Obj:', m.objVal)

		    return(self.get_best_policy_from_best_values(Vt), Vt, t)

		except GurobiError:
		    print("Erreur Gurobi pour l'optimisation linéaire")

