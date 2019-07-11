'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("TkAgg")

class cell():

	def __init__(self, v=0, theta=0, x=0, y=0):
		self.v = v
		self.theta = theta
		self.x = x  # center of square
		self.y = y
		self.grid = []

	def set_xy(self, dx, dy):
		self.x += dx
		self.y += dy

	def set_v(self, dv):
		self.v += dv

	def make_offspring(self):
		return


class world():
	def __init__(self, xmax=10, ymax=20):
		self.xmax = xmax
		self.ymax = ymax
		self.world = np.zeros((int(xmax), int(ymax)))

def update_grid(cell, world):
	x = cell.x
	y = cell.y
	cell.grid = []
	left = 1.0 * (np.mod(x, 1) < 0.5)
	right = 1.0 * (np.mod(x, 1) > 0.5)
	up = 1.0 * (np.mod(y, 1) > 0.5)
	down = 1.0 * (np.mod(y, 1) < 0.5)
	dx = right - left
	dy = up - down
	cell.grid.append([int(x), int(y)])
	cell.grid.append([int(x), int(y+dy)])
	cell.grid.append([int(x+dx), int(y)])
	cell.grid.append([int(x+dx), int(y+dy)])
	xbig = 0.5 + left*np.mod(x, 1) + right*(1.0-np.mod(x, 1))
	xsmall = 0.5 - left*np.mod(x, 1) - right*(1.0-np.mod(x, 1))
	ybig = 0.5 + down*np.mod(y, 1) + up*(1.0-np.mod(y, 1))
	ysmall = 0.5 - down*np.mod(y, 1) - up*(1.0-np.mod(y, 1))
	world.world[int(x), int(y)] += xbig*ybig
	world.world[int(x), int(y+dy)] += xbig*ysmall
	world.world[int(x+dx), int(y)] += xsmall*ybig
	world.world[int(x+dx), int(y+dy)] += xsmall*ysmall


world1 = world()
cells = []
rng = np.random.RandomState(seed=0)
n_cells = 30
for n in range(n_cells):
	cells.append(cell(x=rng.uniform(1, world1.world.shape[0]-1), y=rng.uniform(1, world1.world.shape[1]-1)))
	update_grid(cells[-1], world1)

fig, ax = plt.subplots()
ax.imshow(world1.world.T, cmap='gray_r', aspect='equal', origin='lower')  # , vmin=0, vmax=np.max(self.world)
ax.set(xticks=range(world1.world.shape[0]), yticks=range(world1.world.shape[1]),
	xlim=((0, world1.world.shape[0])), ylim=((0, world1.world.shape[1])))
for n in range(n_cells):
	ax.scatter(cells[n].x-0.5, cells[n].y-0.5, c='r', marker='s')
plt.show()