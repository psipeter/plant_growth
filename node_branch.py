'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
# import matplotlib
import matplotlib.pyplot as plt
import matplotlib.cm as cm
# from matplotlib import animation
# matplotlib.use("Agg")
import copy

class Cell():
	def __init__(self, id, x=0, y=0, theta=0):
		self.id = id
		self.x = x
		self.y = y
		self.theta = theta
		self.to_node = to_node  # todo: 2-way communication to ensure even spacing
		self.cell_type = 'vein'
		self.children = []
		self.rng = np.random.RandomState(seed=id)

	def update_to_node(self, val):
		self.to_node = np.max([0, val])

	def update_cell_type(self):
		if self.to_node == 0:
			self.cell_type = 'node'
			self.to_node = to_node

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

def recursive_push(pusher, pushed, vx, vy):
	x_old = pushed.x
	y_old = pushed.y
	pushed.x += vx
	pushed.y += vy
	x_new = pushed.x
	y_new = pushed.y
	grid[x_old][y_old].remove(pushed)
	grid[x_new][y_new].append(pushed)
	to_push = []
	for cell in pushed.children:
		to_push.append(cell)
	for cell in grid[x_new][y_new]:
		if cell not in to_push and cell is not pushed:
			to_push.append(cell)
	for cell in to_push:
		recursive_push(pushed, cell, vx, vy)


'''main loop'''
t_final = 7
xmax = 100
ymax = 100
seed = 0
p_offspring = 1.0
to_node = 3
rng = np.random.RandomState(seed=seed)
grid0 = [[[] for x in range(xmax)] for y in range(ymax)]
cell0 = Cell(id=0, x=1, y=int(ymax/2))
grid0[int(cell0.x)][int(cell0.y)].append(cell0)
cells = [cell0]
grid_history = [copy.deepcopy(grid0)]
cell_history = [copy.deepcopy(cells)]
grid = grid0
idmax = 0
for t in range(t_final):
	print('t=%s'%(t+1))
	offsprings = []
	for cell in cells:
		if rng.uniform(0, 1) < p_offspring:
			idmax += 1
			offspring = Cell(id=idmax, x=cell.x, y=cell.y, theta=cell.theta+pdf(cell.rng)*(cell.cell_type == 'node'))
			offspring.update_to_node(cell.to_node-1)
			offspring.update_cell_type()
			grid[offspring.x][offspring.y].append(offspring)
			vx, vy = int(np.cos(offspring.theta)), int(np.sin(offspring.theta))
			recursive_push(cell, offspring, vx, vy)
			for child in cell.children:
				if child.x == offspring.x and child.y == offspring.y:
					cell.children.remove(child)
				if np.abs(cell.x - child.x) > 1 or np.abs(cell.y - child.y) > 1:
					cell.children.remove(child)
			cell.children.append(offspring)
			print(len(cell.children))
			offsprings.append(offspring)
	for offspring in offsprings:
		cells.append(offspring)
	# rng.shuffle(cells)
	cell_history.append(copy.deepcopy(cells))
	grid_history.append(copy.deepcopy(grid))
	print('n_cells=%s' %len(cells))
	print('nonzero grid', np.count_nonzero(np.array(grid)))
	# print('where nonzero', np.nonzero(np.array(grid)))

for t, grid in enumerate(cell_history):
	fig, ax = plt.subplots(figsize=((16, 16)))
	ax.set(xlim=((0, xmax)), ylim=((0, ymax)), title='t=%s'%t)
	ax.axis('off')
	xs = np.array([cell.x for cell in grid])
	ys = np.array([cell.y for cell in grid])
	ss = np.array([10 if cell.cell_type == 'vein' else 40 for cell in grid])
	cs = np.array([cell.id/len(cell_history[-1]) for cell in grid])
	ax.scatter(xs, ys, s=ss, color=cm.rainbow(cs))
	plt.savefig('plots/%s.png'%t)