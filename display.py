import sys

from grid import *
from tkinter import *
grid_generator = GeneratorGrid(20, 20, proba_walls = 0.1)
grid_generator.export_grid("test")
grid_display = Grid_Project()
grid_display.load_grid("test")

window = Tk()

button = Button(window, text="Charger", command=window.quit)
button.pack()

height_canvas = 500
width_canvas = 500
canvas = Canvas(window, width = width_canvas, height = height_canvas)
for i in range(grid_display.height):
	for j in range(grid_display.width):
		color = ""
		if "wall" in str(grid_display.grid[i][j].type_location):
			color = 'black'
		elif grid_display.grid[i][j].color == 0:
			color = 'light green'
		elif grid_display.grid[i][j].color == 1:
			color = 'light blue'
		elif grid_display.grid[i][j].color == 2:
			color = 'lightSalmon2'
		else:
			color = 'grey65'

		canvas.create_rectangle(i * (height_canvas / grid_display.height), j * (width_canvas / grid_display.width), (i + 1) * (height_canvas / grid_display.height), (j + 1) * (width_canvas / grid_display.width), fill = color)
canvas.pack()

window.mainloop()