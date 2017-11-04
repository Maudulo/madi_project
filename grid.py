import random
from enum import Enum

import os

class GeneratorGrid:
	''' 
		Permet la génération d'une grille aléatoire selon une taille et des probabilités données
		Génére un fichier txt
		@params height la hauteur de la grille
				width la largeur de la grille
				proba_walls la probabilité q'une case soit un mur
				proba_colors le tuple donnant les probabilité que la case soit (verte, bleue, rouge, noire)

	'''

	def __init__(self, height, width, proba_walls = 0.01, proba_colors = (0.25, 0.25, 0.25, 0.25)):

		self.height = height
		self.width = width
		self.grid = []
		self.init_locations(proba_walls, proba_colors)

	def init_locations(self, proba_walls, proba_colors):
		for i in range(self.height):
			self.grid.append([])
			for j in range(self.height):
				
				score = 0
				color = None

				# génération du type de la case
				type_location_random = random.random()
				type_location = ""
				if type_location_random > proba_walls:
					type_location = "normal"
				else:
					type_location = "wall"

				# génération d'un score aléatoire entre 1 et 9
				score = random.randint(1, 9)

				# generation d'une couleur aléatoire
				color_random = random.random()
				if color_random < proba_colors[0]:
					color = 0
				elif color_random < proba_colors[0] + proba_colors[1]:
					color = 1
				elif color_random < proba_colors[0] + proba_colors[1] + proba_colors[2]:
					color = 2
				else:
					color = 3
				
				self.grid[i].append(Location(i, j, score, color, type_location = type_location))


	def export_grid(self, file_name):

		with open(file_name, "w") as file:
			file.write(str(self.height) + " " + str(self.width) + "\n")
			for i in range(self.height):
				for j in range(self.width):
					file.write(str(self.grid[i][j].score) + " " + str(self.grid[i][j].color) + " " + str(self.grid[i][j].type_location) + "\n")



		

class Grid_Project:

	def __init__(self):
		self.grid = []
		self.width = None
		self.height = None

	def load_grid(self, file_name):
		with open(file_name, "r") as file:
			line = file.readline().split(" ")
			self.height = int(line[0])
			self.width = int(line[1])

			for i in range(self.height):
				self.grid.append([])
				for j in range(self.width):
					line = file.readline().split(" ")
					score = int(line[0])
					color = int(line[1])
					type_location = str(line[2])
					self.grid[i].append(Location(i, j, score, color, type_location = type_location))




class Location:

	def __init__(self, position_x, position_y, score, color, type_location="normal"):
		self.position_x = position_x
		self.position_y = position_y
		self.type_location = type_location
		self.score = score
		self.color = color



# grid = GeneratorGrid(10, 10, proba_walls = 0.2)
# grid.export_grid("test.madi")
# grid2 = Grid_Project()
# grid2.load_grid("test.madi")
