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
matplotlib.use("Agg")
import scipy.stats as st
import copy

class Cell():
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
		self.v = 0
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

	def brownian(self, v=0.2, rng=np.random.RandomState(seed=0)):
		self.x += rng.uniform(0, v) * np.cos(rng.uniform(0, 2*np.pi))
		self.y += rng.uniform(0, v) * np.sin(rng.uniform(0, 2*np.pi))
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

class World():
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
			try:
				self.world[grid[0], grid[1]].remove(cell)
			except:
				pass
			self.density[grid[0], grid[1]] -= 1
		for grid in cell.grid_new:
			self.world[grid[0], grid[1]].append(cell)
			self.density[grid[0], grid[1]] += 1

	def get_density(self, cell):
		count = []
		for grid in cell.grid_new:
			count.append(self.density[grid[0], grid[1]])
		return np.average(count)



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


def pdf(pdfdict, rng):
	sample = rng.uniform(0, 1)
	total = 0
	for key, value in pdfdict.items():
		if total < sample < total+value:
			result = np.float(key)
		total += value
	assert total <= 1.0
	return result

def p_offspring(avg_density, k=0.4):
	return np.exp(-avg_density*k)

straight = {str(0): 1}
split = {str(-np.pi/4): 0.5, str(np.pi/4): 0.5}
straight_split = {str(-np.pi/8): 0.1, str(0): 0.8, str(np.pi/8): 0.1}


'''main loop'''

t_final = 70
xmax = 40
ymax = 20
seed = 0
rng = np.random.RandomState(seed=seed)
worlds = [World(xmax, ymax)]
cells = [Cell(ID=0, x=0, y=10)]
worlds[-1].update(cells[-1])
ID_max = 0
for t in range(t_final):
	print('t=%s'%t)
	world_new = copy.deepcopy(worlds[-1])
	cells_copy = []
	for cell in cells:
		if cell.v > 0.0:
			cell.move()  # move cell according to velocity and angle
			cell.brownian(rng=rng)  # wiggle
			world_new.update(cell)  # update world grid to account for new position
		avg_density = world_new.get_density(cell)
		if rng.uniform(0, 1) < p_offspring(avg_density):  # reproduction depends on nearby cell density
			ID_max += 1
			offspring = Cell(ID=ID_max, v=1, theta=cell.theta+pdf(straight, rng), x=cell.x, y=cell.y)
			cells_copy.append(offspring)
			world_new.update(offspring)
			cell.brownian(v=0.4, rng=rng)
			world_new.update(cell)
		cells_copy.append(cell)
	cells = cells_copy
	rng.shuffle(cells)
	worlds.append(world_new)
	print('n_cells=%s' %len(cells))

# plotting
fig, ax = plt.subplots()
ax.set(xticks=range(xmax), yticks=range(ymax), xlim=((0, xmax)), ylim=((0, ymax)))
im = plt.imshow(worlds[0].density.T, cmap='gray_r', aspect='equal', origin='lower', vmin=0, vmax=10)  # vmax=np.max(worlds[-1].density)
def init():
	im.set_data(worlds[0].density.T)
	return [im]
def animate(i):
	im.set_array(worlds[i].density.T)
	return [im]
anim = animation.FuncAnimation(fig, animate, init_func=init, frames=t_final, interval=1, blit=True)
anim.save('animation.mp4', fps=int(t_final/10), extra_args=['-vcodec', 'libx264'])