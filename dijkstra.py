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

    def reinit(self):
        self.path = []
        self.length_path = sys.maxsize


class Dijkstra:

    def __init__(self, grid, goal):
        self.grid = grid
        self.directions = [-1 for _ in range(self.grid.height * self.grid.width)]
        self.nodes = []
        self.goal = goal
        self.goals = [goal] # tableau contenant les coordonnées du but

        for y in range(self.grid.height):
            self.nodes.append([])
            for x in range(self.grid.width):
                self.nodes[y].append(Node([y, x], self.grid.grid[y][x].score))

    def politic_decision(self):

        init_node = self.initial_node()
        
        # tant qu'il reste un noeud qui n'a pas de direction, on réapplique l'algo
        while(init_node != None):

            # réinitialisation des chemins/distance des noeuds
            self.reinit_nodes()

            self.to_explore = []
            self.s = [init_node]
            developped_node = init_node
            self.nodes[developped_node[0]][developped_node[1]].setLengthPath(0)

            # si l'on atteint un noeud qui a déjà une direction optimale
            while(developped_node not in self.goals):

                # ajoute les voisins du noeud développé
                self.neighbors_node(developped_node)

                # prendre le noeud dont la distance est minimale (mise à jour effectuée dans la fonction)
                developped_node = self.closest_node()

                # ajoute ce noeud à la liste s et le retire de la liste des noeuds à explorer
                
                if developped_node != None:
                    self.s.append(developped_node)
                    del self.to_explore[self.to_explore.index(developped_node)]

            # ajoute la direction des noeuds du chemin
            self.update_direction(self.nodes[developped_node[0]][developped_node[1]].ID, self.nodes[developped_node[0]][developped_node[1]].path)

            # recalcul du noeud intial
            init_node = self.initial_node()



    def initial_node(self):
        # prend le premier noeud qui n'a pas encore de direction
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                if not (self.goal[0] == x and self.goal[1] == y):
                    if self.directions[self.grid.height * y + x] == -1:
                        return self.nodes[y][x].ID
        return None

    def neighbors_node(self, node):
        # récupère l'id du noeud et ajoute à la liste des noeuds à explorer les voisins qui ne sont pas encore dans cette liste, sinon, met à jour leur connaissance
        
        neighbors = []
        if node[0] > 0:
            neighbors.append([node[0] - 1,node[1]])
        if node[0] < self.grid.height - 1:
            neighbors.append([node[0] + 1,node[1]])
        if node[1] > 0:
            neighbors.append([node[0],node[1] - 1])
        if node[1] < self.grid.width - 1:
            neighbors.append([node[0],node[1] + 1])

        for neighbor in neighbors:
            # si le noeud n'a jamais été ajouté
            if self.grid.grid[neighbor[0]][neighbor[1]].type_location == "normal":
                if neighbor not in self.s and neighbor not in self.to_explore:
                    # mise à jour du chemin
                    self.nodes[neighbor[0]][neighbor[1]].path = copy.deepcopy(self.nodes[node[0]][node[1]].path)
                    self.nodes[neighbor[0]][neighbor[1]].path.append(node)

                    # mise à jour de la taille du chemin
                    self.nodes[neighbor[0]][neighbor[1]].length_path = copy.deepcopy(self.nodes[node[0]][node[1]].length_path)
                    self.nodes[neighbor[0]][neighbor[1]].length_path += copy.deepcopy(self.nodes[neighbor[0]][neighbor[1]].weight)

                    self.to_explore.append(neighbor)

                # si le noeud est dans la liste des noeuds à explorer
                elif neighbor in self.to_explore:

                    # si le chemin est plus court que le chemin déjà rencontré
                    if self.nodes[neighbor[0]][neighbor[1]].length_path > self.nodes[node[0]][node[1]].length_path + self.nodes[neighbor[0]][neighbor[1]].weight:
                        self.nodes[neighbor[0]][neighbor[1]].path = copy.deepcopy(self.nodes[node[0]][node[1]].path)
                        self.nodes[neighbor[0]][neighbor[1]].path.append(node)

                        self.nodes[neighbor[0]][neighbor[1]].length_path = copy.deepcopy(self.nodes[node[0]][node[1]].length_path)
                        self.nodes[neighbor[0]][neighbor[1]].length_path += copy.deepcopy(self.nodes[neighbor[0]][neighbor[1]].weight)

    def reinit_nodes(self):
        # réinitialise tous les noeuds

        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.nodes[y][x].reinit()

    def closest_node(self):
        # retourne le noeud dont la distance est minimale

        min_path = sys.maxsize
        min_node = None
        for node in self.to_explore:
            if self.nodes[node[0]][node[1]].length_path < min_path:
                min_path = copy.deepcopy(self.nodes[node[0]][node[1]].length_path)
                min_node = node
        return min_node
        

    def update_direction(self, goal, path):
        # retrouve les directions en fonction du chemin du dernier noeud visité

        path.append(goal)
        for i in range(len(path)-1):
            cur_node = path[i]
            next_node = path[i+1]

            # direction vers le bas
            if(cur_node[0] < next_node[0]):
                self.directions[self.grid.width * cur_node[0] + cur_node[1]] = 1

            # direction vers le haut
            elif(cur_node[0] > next_node[0]):
                self.directions[self.grid.width * cur_node[0] + cur_node[1]] = 0

            # direction vers la droite
            elif(cur_node[1] < next_node[1]):
                self.directions[self.grid.width * cur_node[0] + cur_node[1]] = 3

            # direction vers la gauche
            else:
                self.directions[self.grid.width * cur_node[0] + cur_node[1]] = 2

            if cur_node not in self.goals:
                self.goals.append(cur_node)

    def getDirections(self):

        solution = [[0 for _ in range(4)] for _ in range(self.grid.width * self.grid.height)]
        for i in range(len(self.directions)):
            solution[i][self.directions[i]] = 1
        return solution



g = GeneratorGrid(2, 2, proba_walls = 0)
d = Dijkstra(g, [1, 1])
d.politic_decision()
print(d.getDirections())