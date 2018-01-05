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
		self.position_robot = 0
		self.origin_robot = 0
		self.goal_position = 0
		self.init_locations(proba_walls, proba_colors)
		self.init_position_robot()
		self.init_goal_position()

	def init_locations(self, proba_walls, proba_colors):
		for y in range(self.height):
			self.grid.append([])
			for x in range(self.width):

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
				
				self.grid[y].append(Location(y, x, score, color, type_location = type_location))

	def init_position_robot(self):
		position = 0
		possible_positions = []
		for y in range(self.height):
			for x in range(self.width):
				if self.grid[y][x].type_location in "normal":
					possible_positions.append(position)
				position +=1
		self.position_robot = random.choice(possible_positions)
		self.origin_robot = self.position_robot

	def init_goal_position(self):
		position = 0
		possible_positions = []
		for y in range(self.height):
			for x in range(self.width):
				if self.grid[y][x].type_location in "normal" and position != self.position_robot:
					possible_positions.append(position)
				position +=1
		self.goal_position = random.choice(possible_positions)

	def export_grid(self, file_name):

		with open(file_name, "w") as file:
			file.write(str(self.height) + " " + str(self.width) + "\n")
			for y in range(self.height):
				for x in range(self.width):
					file.write(str(self.grid[y][x].score) + " " + str(self.grid[y][x].color) + " " + str(self.grid[y][x].type_location) + "\n")
			file.write(str(self.position_robot) + "\n")
			file.write(str(self.goal_position))


		

class Grid_Project:

	def __init__(self):
		self.grid = []
		self.width = None
		self.height = None
		self.position_robot_x = None
		self.position_robot_y = None
		self.score = [0,0,0,0]
		self.origin_robot_x = None
		self.origin_robot_y = None
		self.goal_x = None
		self.goal_y = None

	def load_grid(self, file_name):
		with open(file_name, "r") as file:
			line = file.readline().split(" ")
			self.height = int(line[0])
			self.width = int(line[1])

			self.score = [0,0,0,0]

			for y in range(self.height):
				self.grid.append([])
				for x in range(self.width):
					line = file.readline().split(" ")
					score = int(line[0])
					color = int(line[1])
					type_location = str(line[2])
					self.grid[y].append(Location(x, y, score, color, type_location = type_location))
			position_robot = int(file.readline())
			goal_position = int(file.readline())
			self.position_robot_x = position_robot % self.width
			self.position_robot_y = int(position_robot / self.width)
			self.origin_robot_x = self.position_robot_x
			self.origin_robot_y = self.position_robot_y
			self.goal_x = goal_position % self.height
			self.goal_y = int(goal_position / self.width)

	def display_score(self):
		return "vert:" + str(self.score[0]) + " bleu:" + str(self.score[1]) + " rouge:" + str(self.score[2]) + " noire:" + str(self.score[3])

	def relocate_goal_position(self, x, y):
		self.goal_x = x
		self.goal_y = y

	def relocate_start_position(self, x, y):
		self.origin_robot_x = x
		self.origin_robot_y = y
		self.position_robot_x = x
		self.position_robot_y = y


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
