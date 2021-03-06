import random
from enum import Enum
from grid import *
import numpy as np
import copy
import sys

import importlib
from importlib import util
if importlib.util.find_spec("gurobipy") is not None :
	from gurobipy import *
	CAN_USE_PL = True
else:
	CAN_USE_PL = False

from tkinter import messagebox

import time
import os

class PDM:

	def __init__(self, grid, p = 0.6, q=1, max_reward = 1000, multi_obj = False, color_restrictive = False, consumption_only = False):
		self.grid = grid
		self.board = grid.grid
		self.goal = [self.grid.goal_y, self.grid.goal_x]
		self.width = len(self.board[0])
		self.height = len(self.board)
		self.number_of_states = self.width * self.height
		self.number_of_actions = 4 # (haut, bas, gauche droite)
		self.number_of_criteria = 4
		self.get_transition_matrix(p, q, max_reward, multi_obj, color_restrictive, consumption_only)
		

	def get_reward_matrix(self, q = 1, max_reward = 1000, multi_obj = False, color_restrictive = False, consumption_only = False):
		"""
			@params q : le facteur de puissance appliqué à la récompense
					max_reward : la récompense donnée pour la case but
					multi_obj : booléen concernant la création de la matrice de récompense associée à du multi-critère
					color_restrictive : booléen concernant l'application de la récompense sur les couleurs (un robot préfère emprunter tous les verts que de prendre une case bleue)
					consumption_only : booléen concernant l'application de la récompense sur les valeurs des cases.
			Cette fonction permet de créer la fonction de récompense.
		"""
		self.R = []

		q_max_reward = max_reward
		if max_reward**q > sys.maxsize-1:
			q_max_reward = sys.maxsize-1
		else:
			q_max_reward = max_reward**q

		if(multi_obj):
			for i in range(self.number_of_criteria):
				self.R.append([])
				for line in self.board:
					for pos in line:

						if pos.position_y == self.goal[0] and pos.position_x == self.goal[1]: # si c'est la case but
							self.R[i].append(max_reward)

						elif pos.type_location == "normal" and i == pos.color: # si c'est une case normale de la couleur correcte
							self.R[i].append(-(pos.score))

						else: # si c'est un mur ou une autre couleur
							self.R[i].append(0)

		elif consumption_only:
			for line in self.board:
				for pos in line:
					if pos.position_y == self.goal[0] and pos.position_x == self.goal[1]: # si c'est la case but
						self.R.append(q_max_reward)

					elif pos.type_location == "normal": # si c'est une case normale
						score = (pos.score)**q
						if score > sys.maxsize:
							messagebox.showinfo("attention", "les valeurs des paramètres sont trop élevés")
							score = (sys.maxsize-1)
						self.R.append(-score)

					else: # si c'est un mur
						self.R.append(-(100000000))

		elif color_restrictive:
			color_value = [1,1,1,1]
			for y in range (1,4):
				for x in range(y):
					color_value[y] *= self.grid.colors[x]
					color_value[y] += 1

			## version plus simple
			# color_value = []
			# color_value.append(1)
			# for _ in range(3):
			# 	color_value.append(color_value[-1]*self.number_of_states+1)

			for line in self.board:
				for pos in line:
					if pos.position_y == self.goal[0] and pos.position_x == self.goal[1]: # si c'est la case but
						self.R.append(max_reward)
					elif pos.type_location == "normal": # si c'est une case normale
						self.R.append(-color_value[pos.color])

					else: # si c'est un mur
						self.R.append(-(100000000))

		else:
			for line in self.board:
				for pos in line:
					if pos.position_y == self.goal[0] and pos.position_x == self.goal[1]: # si c'est la case but
						self.R.append(q_max_reward)

					elif pos.type_location == "normal": # si c'est une case normale
						score = (pos.color+1)**q
						if score > sys.maxsize:
							messagebox.showinfo("attention", "les valeurs des paramètres sont trop élevés")
							score = (sys.maxsize-1)
						self.R.append(-score)

					else: # si c'est un mur
						self.R.append(-(100000000))


	def get_transition_matrix(self, p, q, max_reward, multi_obj = False, color_restrictive = False, consumption_only = False):
		"""
			@params p : la probabilité d'effectuer correctement le déplacement, sans déviation
					q : le facteur de puissance appliqué à la récompense
					max_reward : la récompense donnée pour la case but
					multi_obj : booléen concernant la création de la matrice de récompense associée à du multi-critère
					color_restrictive : booléen concernant l'application de la récompense sur les couleurs (un robot préfère emprunter tous les verts que de prendre une case bleue)
					consumption_only : booléen concernant l'application de la récompense sur les valeurs des cases.
			@return T la fonction de transition
			Cette fonction permet de créer la fonction de transition T.
		"""
		
		# création de la matrice des récompenses
		self.get_reward_matrix(q, max_reward, multi_obj, color_restrictive, consumption_only)

		self.T = np.zeros((self.number_of_states, self.number_of_actions, self.number_of_states)) 
		#print(self.T.shape)
		for y in range(self.height):
			for x in range(self.width):
				#print(y, " ", x)
				##############################################
				############ vers le haut ####################
				##############################################

				bias = 0
				if y == 0 or not(self.board[y-1][x].type_location == "normal"): # si on est tout en haut
					self.T[self.width*y+x, 0, self.width*y+x] = 1

				else: # si la case du haut est accessible

					# proba case "haut-gauche"
					if x == 0 :
						bias += (1-p)/2
					elif self.board[y-1][x-1].type_location == "normal":
						self.T[self.width*y+x, 0, self.width*(y-1)+x-1] = (1-p)/2
					else:
						bias +=(1-p)/2

					# proba case "haut-droite"
					if x == self.width-1:
						bias += (1-p)/2
					elif self.board[y-1][x+1].type_location == "normal":
						self.T[self.width*y+x, 0, self.width*(y-1)+x+1] = (1-p)/2
					else:
						bias +=(1-p)/2

					# proba case "haut-centre"
					self.T[self.width*y+x, 0, self.width*(y-1)+x] = p+bias
	
				##############################################
				############ vers le bas #####################
				##############################################

				bias = 0
				if y == self.height-1 or not(self.board[y+1][x].type_location == "normal"): # si on est tout en bas ou que l'on cherche à se déplacer contre un mur
					self.T[self.width*y+x, 1, self.width*y+x] = 1

				else: # si la case du bas est accessible

					# case bas-gauche
					if x == 0:
						bias += (1-p)/2
					elif self.board[y+1][x-1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y+1)+(x-1)] = (1-p)/2
					else:
						bias +=(1-p)/2

					# case bas-droite
					if x == self.width-1:
						bias +=(1-p)/2
					elif self.board[y+1][x+1].type_location == "normal":
						self.T[self.width*y+x, 1, self.width*(y+1)+(x+1)] = (1-p)/2
					else:
						bias +=(1-p)/2

					# case bas-centre
					self.T[self.width*y+x, 1, self.width*(y+1)+x] = p+bias


				##############################################
				############ vers la gauche ##################
				##############################################

				bias = 0
				if x == 0 or not( self.board[y][x-1].type_location == "normal"): # si on est tout à gauche
					self.T[self.width*y+x, 2, self.width*y+x] = 1

				else: # si la case de gauche est accessible

					# case gauche-haut
					if y == 0:
						bias += (1-p)/2
					elif self.board[y-1][x-1].type_location == "normal":
						self.T[self.width*y+x, 2, self.width*(y-1)+(x-1)] = (1-p)/2
					else:
						bias +=(1-p)/2

					# case gauche-bas
					if y == self.height-1:
						bias +=(1-p)/2
					elif self.board[y+1][x-1].type_location == "normal":
						self.T[self.width*y+x, 2, self.width*(y+1)+(x-1)] = (1-p)/2
					else:
						bias +=(1-p)/2

					# case gauche-centre
					self.T[self.width*y+x, 2, self.width*y+(x-1)] = p+bias

				##############################################
				############ vers la droite ##################
				##############################################

				bias = 0
				if x == self.width-1 or not(self.board[y][x+1].type_location == "normal"): # si on est tout à droite
					self.T[self.width*y+x, 3, self.width*y+x] = 1

				else: # si la case de droite est accessible

					# case droite-haut
					if y == 0:
						bias += (1-p)/2
					elif self.board[y-1][x+1].type_location == "normal":
						self.T[self.width*y+x, 3, self.width*(y-1)+(x+1)] = (1-p)/2
					else:
						bias +=(1-p)/2

					# case droite-bas
					if y == self.height-1:
						bias +=(1-p)/2
					elif self.board[y+1][x+1].type_location == "normal":
						self.T[self.width*y+x, 3, self.width*(y+1)+(x+1)] = (1-p)/2
					else:
						bias +=(1-p)/2

					# case droite-centre
					self.T[self.width*y+x, 3, self.width*y+(x+1)] = p+bias

		return self.T


	def get_best_policy_from_best_values(self, Vt, gamma):
		"""
			@params Vt : la matrice contenant les valeurs 
					gamma : le facteur d'atténuation
			@return les politiques optimales pour chaque action et pour chaque état
		"""
		return [np.argmax([self.R[s] + gamma * (np.dot(self.T[s,a], Vt)) for a in range(self.number_of_actions)]) for s in range(self.number_of_states)]

	def iteration_by_value(self, gamma = 0.5, epsilon = 0.001):
		"""
			@params gamma : le facteur d'atténuation
					epsilon : distance maximale autorisée entre deux étapes
			@return le tableau des directions pour chaque case
			Applique une itération par valeur pour obtenir les directions en chaque case.
		"""

		t = 0
		Vt_1 = np.zeros((self.number_of_states))
		Vt = np.zeros((self.number_of_states))

		while True:
			t += 1
			for s in range(self.number_of_states):
				Vt[s] = max([self.R[s] +  gamma * (np.dot(self.T[s,a],Vt_1)) for a in range(self.number_of_actions)])

			# si l'écart de valeur entre deux itérations est inférieur à epsilon, alors on s'arrête
			if np.allclose(Vt, Vt_1, atol = epsilon, rtol = 0):
				break

			else:
				Vt_1 = copy.copy(Vt)

		directions = [[0 for _ in range(self.number_of_actions)] for _ in range(self.number_of_states)]
		best_policy = self.get_best_policy_from_best_values(Vt, gamma)

		for i in range(len(best_policy)):
			directions[i][best_policy[i]] = 1

		return directions

	def iteration_by_policy(self, gamma = 0.5):
		"""
			@params gamma : le facteur d'atténuation
			@return le tableau des directions pour chaque case
			Applique une itération par politique pour obtenir les directions en chaque case.
		"""

		t = 0

		# on selectionne une action au hasard pour chaque état
		actions = [np.random.randint(0, self.number_of_actions) for _ in range(self.number_of_states)]
		actions_1 = copy.copy(actions)
		coefs = np.zeros((self.number_of_states, self.number_of_states))
		consts = np.zeros((self.number_of_states))
		results = np.zeros((self.number_of_states))

		while True:
			t += 1

			# on résoud le système
			for s in range(self.number_of_states):
				coefs[s] = np.dot([self.T[s,actions[s]]], gamma)
				coefs[s,s] -= 1
				consts[s] = -self.R[s]
			results = np.linalg.solve(coefs,consts)

			# # check if solution is correct
			# if not np.allclose(np.dot(coefs,results),consts):
			# 	print("Erreur dans la résolution du système d'équations pour l'itération de la politique")
			# 	return -1

			# on récupère la nouvelle meilleure politique 
			for s in range(self.number_of_states):
				actions[s] = np.argmax([self.R[s] +  gamma * (np.dot(self.T[s,a],results)) for a in range(self.number_of_actions)])

			# si la politique est la même qu'au tour précédent on arrête
			if np.allclose(actions, actions_1):
				break
			else:
				actions_1 = copy.copy(actions)

		Vt = [self.R[s] + gamma * (np.dot(self.T[s,actions[s]],results)) for s in range(self.number_of_states)]
		
		directions = [[0 for _ in range(self.number_of_actions)] for _ in range(self.number_of_states)]
		best_policy = self.get_best_policy_from_best_values(Vt, gamma)
		for i in range(len(best_policy)):
			directions[i][best_policy[i]] = 1
		return directions


	def resolution_by_PL(self,gamma = 0.5):
		if CAN_USE_PL:
			return self._resolution_by_PL(gamma)
		else:
			messagebox.showinfo("Limitations", "Cette session ne dispose pas du solveur gurobi et de son interface gurobipy.py\nimpossible d'utiliser cette opération")

	def _resolution_by_PL(self, gamma = 0.5):
		"""
			@params gamma : le facteur d'atténuation
			@return le tableau des directions pour chaque case
			Applique un PL pour obtenir les directions optimales
		"""
		
		try:

			# Create a new model
			self.model = Model("mip")

			# Create variables
			Vt = [0 for _ in range(self.number_of_states)]
			for state in range(self.number_of_states):
				Vt[state] = self.model.addVar(0, GRB.INFINITY, vtype=GRB.CONTINUOUS)
			self.model.update()

			# Set objective
			self.model.setObjective(quicksum(Vt), GRB.MINIMIZE)

			# Add constraint
			for state in range(self.number_of_states):
				for action in range(self.number_of_actions):
					self.model.addConstr(Vt[state] - gamma * quicksum([self.T[state,action,s2]*Vt[s2] for s2 in range(self.number_of_states)]), GRB.GREATER_EQUAL, self.R[state])
			self.model.update()

			start_time = time.time()
			self.model.optimize()
			t = (time.time() - start_time)

			directions = [[0 for _ in range(self.number_of_actions)] for _ in range(self.number_of_states)]

			best_policy = self.get_best_policy_from_best_values([v.x for v in Vt], gamma)

			for i in range(len(best_policy)):
				directions[i][best_policy[i]] = 1
			return directions

		except GurobiError:
			print("Erreur Gurobi pour l'optimisation linéaire")



	def PLMO(self, gamma = 0.5, pure_politic = False):
		if CAN_USE_PL:
			return self._PLMO(gamma, pure_politic)
		else:
			messagebox.showinfo("Limitations", "Cette session ne dispose pas du solveur gurobi et de son interface gurobipy.py\nimpossible d'utiliser cette opération")

	def _PLMO(self, gamma, pure_politic):
		"""
			@params gamma : le facteur d'atténuation
					pure_politic : le booléen pour ajouetr les contraintes forçant une politique pure
			@return le tableau des directions pour chaque case
			Application d'un PL pour la résolution du multi-critère.
		"""

		try:
			# Create a new model
			self.model = Model("pl_mo")
			nb_var = 0

			# Create variables
			
			x = [[0 for _ in range(self.number_of_actions)] for _ in range(self.number_of_states)]
			for state in range(self.number_of_states):
				for action in range(self.number_of_actions):
					x[state][action] = self.model.addVar(0, GRB.INFINITY, vtype=GRB.CONTINUOUS)
					nb_var += 1

			F = self.model.addVar(0, GRB.INFINITY, vtype=GRB.CONTINUOUS)

			fi = [0 for _ in range(self.number_of_criteria)]
			for i in range(self.number_of_criteria):
				fi[i] = self.model.addVar(0, GRB.INFINITY, vtype=GRB.CONTINUOUS)
				nb_var += 1

			if pure_politic:
				d = [[0 for _ in range(self.number_of_actions)] for _ in range(self.number_of_states)]
				for state in range(self.number_of_states):
					for action in range(self.number_of_actions):
						d[state][action] = self.model.addVar(vtype=GRB.BINARY)
						nb_var += 1

			self.model.update()

			# Set objective
			self.model.setObjective(F, GRB.MAXIMIZE)

			nb_constr = 0

			# Add constraint
			for i in range(self.number_of_criteria):
				self.model.addConstr(F, GRB.LESS_EQUAL, fi[i])
				self.model.addConstr(fi[i], GRB.EQUAL, quicksum([self.R[i][state] * x[state][action] for state in range(self.number_of_states) for action in range(self.number_of_actions)]))
				nb_constr += 2

			for state in range(self.number_of_states):
				self.model.addConstr(quicksum([x[state][action] for action in range(self.number_of_actions)]) - gamma * quicksum([(self.T[s2,action,state] * x[s2][action]) for s2 in range(self.number_of_states) for action in range(self.number_of_actions)]), GRB.EQUAL, 1 / self.number_of_criteria)

			
			if pure_politic:
				for state in range(self.number_of_states):
					self.model.addConstr(quicksum([d[state][action] for action in range(self.number_of_actions)]), GRB.LESS_EQUAL, 1)
					nb_constr += 1
					for action in range(self.number_of_actions):
						self.model.addConstr((1 - gamma) * x[state][action], GRB.LESS_EQUAL, d[state][action])
						nb_constr += 1

			# print("nombre de variables : ", nb_var)
			# print("nombre de contraintes : ", nb_constr)

			self.model.update()

			start_time = time.time()
			self.model.optimize()
			t = (time.time() - start_time)

			list_var_gurobi = []
			directions = [[var.x/sum([a.x for a in tab]) for var in tab]for tab in x]

			return directions

		except GurobiError:
			print("Erreur Gurobi pour l'optimisation linéaire")



def _display_grid(grid):
	for y in grid:
		for x in y:
			print(x.position_x, x.position_y, x.type_location, "  ")
		print()
	return""

def first_test(gam = 0.9,p = 0.6, size = [(10,10),(10,15),(15,20),(20,20)], trials = 15):
	results = np.zeros((len(size),3))
	for i,(a,b) in enumerate(size):
		print("on calcule pour taille: ", (a,b))
		for trial in range(trials):
			print("essai : ", trial)
			g = GeneratorGrid(a,b,proba_walls=0.2)

			# g1 = PDM(g, p=p)
			# t = time.time()
			# g1.iteration_by_value(gamma=gam)
			# a1 = (time.time() - t)
			# results[i,0] += a1

			# g2 = PDM(g, p=p)
			# t = time.time()
			# g2.iteration_by_policy(gamma = gam)
			# a2 = (time.time() - t)
			# results[i,1] += a2

			# g3 = PDM(g, p=p)
			# t = time.time()
			# g3.resolution_by_PL(gamma = gam)
			# a3 = (time.time() - t)
			# results[i,2] += a3

			# g4 = PDM(g, p=p, multi_obj = True)
			# t = time.time()
			# g4.PLMO(gamma = gam, pure_politic = False)
			# a4 = (time.time() - t)
			# results[i,0] += a4

			g5 = PDM(g, p=p, multi_obj = True)
			t = time.time()
			g5.PLMO(gamma = gam, pure_politic = True)
			a5 = (time.time() - t)
			results[i,1] += a5

	# do the mean
	results /= trials

	return results

######### TEST SUR LE CHARGEMENT DU FICHIER ##############

# g1 = GeneratorGrid(4, 4, proba_walls = 0.2)
# g1.export_grid("testIMPORTANT")
# g2 = Grid_Project()
# g2.load_grid("testIMPORTANT")
# print(_display_grid(g1.grid), g1.goal_y, g1.goal_x)
# print(_display_grid(g2.grid), g2.goal_y, g2.goal_x)
# g.export_grid("testIMPORTANT")
# print("goal = ", g.goal_x, g.goal_y, g.goal_position)
# g.export_grid("test.madi")
# grid2 = Grid_Project()
# grid2.load_grid("test.madi")

######### TEST SUR LES CRITERES PAR VALEUR, PAR POLITIQUE ET PL ##############

# pdm = PDM(g2, p = 0.6, color_restrictive = True) 
# print(pdm.resolution_by_PL())
# print("----------------------")
# print(pdm.iteration_by_policy(gamma = 0.9))
# print("----------------------")
# print(pdm.iteration_by_value(gamma = 0.9))


######### TEST SUR LE MULTI CRITERE ##############

# g = GeneratorGrid(2, 2, proba_walls = 0)
# pdm = PDM(g, multi_obj = True) 
# print(pdm.PLMO(pure_politic = False))
# print(pdm.PLMO(pure_politic = True))

######### TEST SUR LE TEMPS D EXECUTION ##############
# np.set_printoptions(formatter={'float': '{: 0.5f}'.format})
# print(first_test(gam=0.5, p=0.6, size = [(5, 5), (5, 10)], trials = 15))