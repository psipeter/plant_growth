'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
# import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
# matplotlib.use("Agg")
import copy

class Cell():
	def __init__(self, id, x=0, y=0, theta=0):
		self.id = id
		self.x = x
		self.y = y
		self.theta = theta
		self.to_node = to_node
		self.cell_type = 'vein'
		self.bonds = []
		self.rng = np.random.RandomState(seed=id)

	def reproduce(self, id):
		angle = self.theta + pdf(self.rng)*(self.cell_type == 'node')
		offspring = Cell(id=id, x=self.x, y=self.y, theta=angle)
		offspring.update_to_node(self.to_node-1)
		offspring.update_cell_type()
		return offspring

	def update_to_node(self, val):
		self.to_node = np.max([0, val])

	def update_cell_type(self):
		if self.to_node == 0:
			self.cell_type = 'node'
			self.to_node = to_node

	def prune_bonds(self):
		for bound in self.bonds:
			if np.abs(self.x - bound.x) > 1 or np.abs(self.y - bound.y) > 1:
				self.bonds.remove(bound)

def pdf(rng):
	# rule = {str(0): 1}
	rule = {str(-np.pi/2): 0.5, str(np.pi/2): 0.5}
	# rule = {str(-np.pi/2): 0.05, str(0): 0.9, str(np.pi/2): 0.05}
	sample = rng.uniform(0, 1)
	total = 0
	for key, value in rule.items():
		if total < sample < total+value:
			result = np.float(key)
		total += value
	assert total <= 1.0
	return result

def recursive_push(pusher, pushed, grid, vx, vy, add=True):
	# print('pusher', pusher)
	# print('pushed', pushed)
	if add:
		pusher.bonds.append(pushed)
	x_old = int(pushed.x)
	y_old = int(pushed.y)
	pushed.x += vx
	pushed.y += vy
	x_new = int(pushed.x)
	y_new = int(pushed.y)
	# print(pushed, x_new, y_new)
	# print(len(grid[x_new][y_new]))
	grid[x_old][y_old].remove(pushed)
	# push all cells bound to pushed
	pushed.prune_bonds()
	for cell in pushed.bonds:
		# print('pushed', pushed)
		# print('cell', cell)
		grid = recursive_push(pushed, cell, grid, vx, vy, add=False)
	# push all cells on the grid space where push was moved
	while len(grid[x_new][y_new]) > 0:
		cell = grid[x_new][y_new][0]
		grid = recursive_push(pushed, cell, grid, vx, vy)
	grid[x_new][y_new].append(pushed)
	return grid


'''main loop'''

t_final = 15
xmax = 100
ymax = 100
seed = 0
p_offspring = 0.5
to_node = 3
rng = np.random.RandomState(seed=seed)
grid0 = [[[] for x in range(xmax)] for y in range(ymax)]
cell0 = Cell(id=0, x=1, y=ymax/2)
grid0[int(cell0.x)][int(cell0.y)].append(cell0)
cells = [cell0]
grid_history = [copy.deepcopy(grid0)]
cell_history = [copy.deepcopy(cells)]
grid = grid0
idmax = 0

for t in range(t_final):
	print('t=%s'%t)
	offsprings = []
	for cell in cells:
		if rng.uniform(0, 1) < p_offspring:
			idmax += 1
			offspring = cell.reproduce(idmax)
			offsprings.append(offspring)
			grid[int(offspring.x)][int(offspring.y)].append(offspring)
			grid = recursive_push(cell, offspring, grid,
				np.cos(offspring.theta), np.sin(offspring.theta))
	for offspring in offsprings:
		cells.append(offspring)
	# rng.shuffle(cells)
	cell_history.append(copy.deepcopy(cells))
	grid_history.append(copy.deepcopy(grid))
	print('n_cells=%s' %len(cells))
	# print('nonzero grid', np.count_nonzero(np.array(grid)))
	# print('where nonzero', np.nonzero(np.array(grid)))

for t, grid in enumerate(cell_history):
	fig, ax = plt.subplots()
	ax.set(xlim=((0, xmax)), ylim=((0, ymax)), title='t=%s'%t)
	ax.axis('off')
	xs = np.array([cell.x for cell in grid])
	ys = np.array([cell.y for cell in grid])
	ss = np.array([3 if cell.cell_type == 'vein' else 10 for cell in grid])
	cs = np.array([cell.id/len(cells) if cell.cell_type == 'vein' else 1 for cell in grid])
	ax.scatter(xs, ys, s=ss, c=cs, cmap='brg')
	plt.savefig('plots/%s.png'%t)
	print(t, xs)

# def update_plot(i, cell_history, scat):
# 	xs = np.array([cell.x for cell in cell_history[i]])
# 	ys = np.array([cell.y for cell in cell_history[i]])
# 	ss = np.array([3 if cell.cell_type == 'vein' else 10 for cell in cell_history[i]])
# 	cs = np.array([cell.id if cell.cell_type == 'vein' else 1 for cell in cell_history[i]]).ravel()
# 	scat.set_array(cs)
# 	scat.set_offsets(np.array([xs, ys]).T)
# 	scat.set_sizes(ss)
# 	scat.set(cmap='brg')
# 	return scat,
# fig, ax = plt.subplots()
# ax.set(xlim=((0, xmax)), ylim=((0, ymax)))
# ax.axis('off')
# xs = np.array([0 for cell in cell_history[-1]])
# ys = np.array([0 for cell in cell_history[-1]])
# scat = ax.scatter(xs, ys)
# anim = animation.FuncAnimation(fig, update_plot, frames=t_final+1, interval=1, fargs=(cell_history, scat))
# anim.save('animation.mp4', fps=1, extra_args=['-vcodec', 'libx264'])