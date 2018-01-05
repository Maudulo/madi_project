import numpy as np
from grid import *
import copy
import sys

class Node:

	def __init__(self, ID, weight):
		self.ID = ID
		self.path = []
		self.length_path = sys.maxsize
		self.weight = weight

	def setPath(self, path):
		self.path = path

	def setLengthPath(self, length_path):
		self.length_path = length_path

	def reinit():
		self.path = []
		self.length_path = sys.maxsize


class Dijkstra:

	def __init__(self, grid, goal):
		self.directions = [-1 for _ in range(self.grid.height * self.grid.width)]
		self.grid = grid
		self.nodes = []
		self.goal = [goal] # tableau contenant les coordonnées du but

		for y in range(self.grid.height):
			self.nodes.append([])
			for x in range(self.grid.width):
				self.nodes[y].append(Node([y, x], self.grid[y][x].score))

	def politic_decision(self):

		init_node = initial_node()
		
		# tant qu'il reste un noeud qui n'a pas de direction, on réapplique l'algo
		while(init_node != None):

			self.to_explore = []
			self.s = [init_node]
			developped_node = init_node

			# réinitialisation des chemins/distance des noeuds
			self.reinit_nodes()

			# si l'on atteint un noeud qui a déjà une direction optimale
			while(developped_node not in goal):

				# ajoute les voisins du noeud développé
				self.neighbors_node(developped_node)

				# prendre le noeud dont la distance est minimale (mise à jour effectuée dans la fonction)
				developped_node = closest_node()

				# ajoute ce noeud à la liste s et le retire de la liste des noeuds à explorer
				self.s.append(developped_node)
				del self.to_explore.index(developped_node)

			# ajoute la direction des noeuds du chemin
			self.update_direction(developped_node.path)

			# recalcul du noeud intial
			init_node = initial_node()


	def initial_node(self):
		# prend le premier noeud qui n'a pas encore de direction
		for y in range(self.grid.height):
			for x in range(self.grid.width):
				if self.directions[self.grid.height * y + x] == -1:
					return self.nodes[y][x]
		return None

	def neighbors_node(self, node):
		# récupère l'id du noeud et ajoute à la liste des noeuds à explorer les voisins qui ne sont pas encore dans cette liste, sinon, met à jour leur connaissance
		neighbors = []
		if node.ID[0] > 0:
			neighbors.append(self.nodes[node.ID[0] - 1][node.ID[1]])
		if node.ID[0] < self.grid.height - 1:
			neighbors.append(self.nodes[node.ID[0] + 1][node.ID[1]])
		if node.ID[1] > 0:
			neighbors.append(self.nodes[node.ID[0]][node.ID[1] - 1])
		if node.ID[1] < self.grid.width - 1:
			neighbors.append(self.nodes[node.ID[0]][node.ID[1] + 1])

		for neighbor in neighbors:
			if neighbor not in self.s or neighbor not in self.to_explore:
				neighbor.path = copy.deepcopy(node.path)
				neighbor.path.append(node)

				neighbor.length_path = copy.deepcopy(node.length_path)
				neighbor.length_path += neighbor.weight

				self.to_explore.append(neighbor)

			elif neighbor in self.to_explore:
				if neighbor.length_path > node.length_path + neighbor.weight:
					neighbor.path = copy.deepcopy(node.path)
					neighbor.path.append(node)

					neighbor.length_path = copy.deepcopy(node.length_path)
					neighbor.length_path += neighbor.weight

	def reinit_nodes():
		# réinitialise tous les noeuds
		for y in range(self.grid.height):
			for x in range(self.grid.width):
				self.nodes[y][x].reinit()

	def closest_node(self):
		# retourne le noeud dont la distance est minimale
		min_path = sys.maxsize
		min_node = None
		for node in self.to_explore:
			if node.length_path < min_path:
				min_path = copy.deepcopy(node.length_path)
				min_node = node
		return node

		

	def update_direction(self, path):
		# retrouve les directions en fonction du chemin du dernier noeud visité
		
		for i in range(len(path)-1):
			cur_node = path[i]
			next_node = path[i+1]

			# direction vers le bas
			if(cur_node.ID[0] < next_node.ID[0]):
				self.directions[self.grid.height * cur_node.ID[0] + cur_node.ID[1]] = 1

			# direction vers le haut
			elif(cur_node.ID[0] > next_node.ID[0]):
				self.directions[self.grid.height * cur_node.ID[0] + cur_node.ID[1]] = 0

			# direction vers la droite
			elif(cur_node.ID[1] < next_node.ID[1]):
				self.directions[self.grid.height * cur_node.ID[0] + cur_node.ID[1]] = 3

			# direction vers la gauche
			else:
				self.directions[self.grid.height * cur_node.ID[0] + cur_node.ID[1]] = 2
