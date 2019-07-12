'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
matplotlib.use("TkAgg")
import scipy.stats as st
import copy

class cell():
	def __init__(self, ID, v=1, theta=0, x=0, y=0):
		self.ID = ID
		self.v = v
		self.theta = theta
		self.x = x  # center of square
		self.y = y
		self.grid_old = []
		self.grid_new = []
		self.move()

	def move(self):
		self.x += self.v * np.cos(self.theta)
		self.y += self.v * np.sin(self.theta)
		# self.v = 0
		self.grid_old = self.grid_new
		self.grid_new = []
		left = 1.0 * (np.mod(self.x, 1) < 0.5)
		right = 1.0 * (np.mod(self.x, 1) > 0.5)
		up = 1.0 * (np.mod(self.y, 1) > 0.5)
		down = 1.0 * (np.mod(self.y, 1) < 0.5)
		dx = right - left
		dy = up - down
		self.grid_new.append([int(self.x), int(self.y)])
		self.grid_new.append([int(self.x), int(self.y+dy)])
		self.grid_new.append([int(self.x+dx), int(self.y)])
		self.grid_new.append([int(self.x+dx), int(self.y+dy)])

class world():
	def __init__(self, xmax=40, ymax=20):
		self.xmax = xmax
		self.ymax = ymax
		self.world = np.empty((int(xmax), int(ymax)), dtype=list)
		for x in range(xmax):
			for y in range(ymax):
				self.world[x,y] = []
		self.density = np.zeros((int(xmax), int(ymax)), dtype=float)

	def update(self, cell):
		for grid in cell.grid_old:
			self.world[grid[0], grid[1]].remove(cell.ID)
			self.density[grid[0], grid[1]] -= 1
		for grid in cell.grid_new:
			self.world[grid[0], grid[1]].append(cell.ID)
			self.density[grid[0], grid[1]] += 1


# def update_grid(cell, world):
# 	x = cell.x
# 	y = cell.y
# 	cell.grid = []
# 	left = 1.0 * (np.mod(x, 1) < 0.5)
# 	right = 1.0 * (np.mod(x, 1) > 0.5)
# 	up = 1.0 * (np.mod(y, 1) > 0.5)
# 	down = 1.0 * (np.mod(y, 1) < 0.5)
# 	dx = right - left
# 	dy = up - down
# 	cell.grid.append([int(x), int(y)])
# 	cell.grid.append([int(x), int(y+dy)])
# 	cell.grid.append([int(x+dx), int(y)])
# 	cell.grid.append([int(x+dx), int(y+dy)])
# 	xbig = 0.5 + left*np.mod(x, 1) + right*(1.0-np.mod(x, 1))
# 	xsmall = 0.5 - left*np.mod(x, 1) - right*(1.0-np.mod(x, 1))
# 	ybig = 0.5 + down*np.mod(y, 1) + up*(1.0-np.mod(y, 1))
# 	ysmall = 0.5 - down*np.mod(y, 1) - up*(1.0-np.mod(y, 1))
# 	world.world[int(x), int(y)] += xbig*ybig
# 	world.world[int(x), int(y+dy)] += xbig*ysmall
# 	world.world[int(x+dx), int(y)] += xsmall*ybig
# 	world.world[int(x+dx), int(y+dy)] += xsmall*ysmall

def make_offspring(parent, world, pdf_theta):
	d_theta = pdf(pdf_theta)
	x_new = parent.x + parent.v*np.cos(parent.theta+d_theta)
	y_new = parent.y + parent.v*np.sin(parent.theta+d_theta)
	v_new = parent.v
	theta_new = parent.theta + d_theta
	offspring = cell(v_new, theta_new, x_new, y_new)
	update_grid(offspring, world)
	return offspring

def pdf(pdfdict, seed=None):
	rng = np.random.RandomState(seed=seed) if seed else np.random.RandomState()
	sample = rng.uniform(0, 1)
	total = 0
	for key, value in pdfdict.items():
		if total < sample < total+value:
			result = np.float(key)
		total += value
	assert total <= 1.0
	return result

straight = {"0": 1}
split = {str(-np.pi/4): 0.5, str(np.pi/4): 0.5}
straight_split = {str(-np.pi/8): 0.1, str(0): 0.8, str(np.pi/8): 0.1}

t_final = 20
xmax = 40
ymax = 20
worlds = [world(xmax, ymax)]
cells = [cell(ID=0, x=10, y=5)]
worlds[-1].update(cells[-1])
for t in range(t_final):
	for cell in cells:
		cell.move()
		world_new = copy.deepcopy(worlds[-1])
		world_new.update(cell)
		worlds.append(world_new)

fig, ax = plt.subplots()
ax.set(xticks=range(xmax), yticks=range(ymax), xlim=((0, xmax)), ylim=((0, ymax)))
im = plt.imshow(worlds[0].density.T, cmap='gray_r', aspect='equal', origin='lower')
def init():
	im.set_data(worlds[0].density.T)
	return [im]
def animate(i):
	im.set_array(worlds[i].density.T)
	return [im]
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=t_final, interval=1, blit=True)
anim.save('animation.mp4', fps=2, extra_args=['-vcodec', 'libx264'])