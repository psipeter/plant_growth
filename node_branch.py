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
	def __init__(self, ID, x=0, y=0, theta=0):
		self.ID = ID
		self.x = x
		self.y = y
		self.theta = theta
		self.d_node = np.inf
		self.cell_type = 'vein'
		self.parent = None
		self.children = []
		self.rng = np.random.RandomState(seed=ID)

	def update_d_node(self):
		if self.cell_type == 'node':
			self.d_node = 0
			return
		d_node_min = np.min([self.d_node, self.parent.d_node])
		for child in self.children:
			d_node_min = np.min([d_node_min, child.d_node])
		self.d_node = int(d_node_min + 1)

	def update_cell_type(self):
		if self.d_node == node_spacing:
			self.cell_type = 'node'
			self.d_node = 0		
		# print(self.d_node == node_spacing)

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

def recursive_push(pushed, vx, vy):
	x_old = pushed.x
	y_old = pushed.y
	pushed.x += vx
	pushed.y += vy
	grid[x_old][y_old].remove(pushed)
	x_new = pushed.x
	y_new = pushed.y
	for cell in pushed.children:
		recursive_push(cell, vx, vy)
	pushed.update_d_node()
	pushed.update_cell_type()
	grid[x_new][y_new].append(pushed)


'''main'''

t_final = 6
xmax = 100
ymax = 100
seed = 0
p_child = 1.0
node_spacing = 4
rng = np.random.RandomState(seed=seed)
# initialization
grid0 = [[[] for x in range(xmax)] for y in range(ymax)]
node0 = Cell(ID=0, x=0, y=int(ymax/2))  # inactive node (not in cells)
node0.cell_type = 'node'
node0.d_node = 0
cell0 = Cell(ID=1, x=1, y=int(ymax/2))
cell0.parent = node0
cell0.d_node = 1
# node0.children.append(cell0)
grid0[int(cell0.x)][int(cell0.y)].append(cell0)
cells = [cell0]
cell_history = [copy.deepcopy(cells)]
grid = grid0
IDmax = 1
# loop
for t in range(t_final):
	print('t=%s'%(t+1))
	cells_new = []
	for cell in cells:
		# find distance to nearest node, maybe become a node
		cell.update_d_node()
		cell.update_cell_type()
		# reproduce
		if rng.uniform(0, 1) < p_child:
			IDmax += 1
			child = Cell(ID=IDmax, x=cell.x, y=cell.y, theta=cell.theta+pdf(cell.rng)*(cell.cell_type == 'node'))
			cells_new.append(child)
			cell.children.append(child)
			child.parent = cell
			vx, vy = int(np.cos(child.theta)), int(np.sin(child.theta))  # todo: non-right angles
			child.x += vx
			child.y += vy
			# push cells in offspring spawn point away
			for pushed in grid[child.x][child.y]:
				cell.children.remove(pushed)
				child.children.append(pushed)
				pushed.parent = child
				recursive_push(pushed, vx, vy)
			# update child.d_node
			child.update_d_node()
			child.update_cell_type()
			cell.update_d_node()
			cell.update_cell_type()
			child.update_d_node()
			child.update_cell_type()
			grid[child.x][child.y].append(child)
			# print(cell.ID, 'births', child.ID)
			# print(cell.ID, '(', cell.x, cell.y, ')', cell.d_node, cell.cell_type)
			# print(child.ID, '(', child.x, child.y, ')', child.d_node, child.cell_type)
	for new in cells_new:
		cells.append(new)
	rng.shuffle(cells)
	cell_history.append(copy.deepcopy(cells))
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
	cs = np.array([cell.ID/len(cell_history[-1]) for cell in grid])
	ax.scatter(xs, ys, s=ss, color=cm.rainbow(cs))
	ax.scatter(node0.x, node0.y, s=40, color='b')
	plt.savefig('plots/%s.png'%t)