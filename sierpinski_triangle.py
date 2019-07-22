'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib import collections as mc
import copy
import sys

class Cell():
	def __init__(self, ID, x=0, y=0, theta=0):
		self.ID = ID
		self.x = x
		self.y = y
		self.theta = theta
		self.d_left = np.inf
		self.d_right = np.inf
		self.reproduce_countdown = 0
		self.cell_type = 'straight'
		self.parent = None
		self.children = []
		self.rng = np.random.RandomState(seed=ID)

	def update_cell_type(self):
		if self.parent.cell_type == 'left':
			if self.d_right != 5 and self.d_right != 0:
				self.cell_type = 'left'
				self.d_left = 0
		elif self.parent.cell_type == 'right':
			if self.d_left != 5 and self.d_left != 0:
				self.cell_type = 'right'
				self.d_right = 0
		if self.d_right == 5:
			self.cell_type = 'right'
			self.d_right = 0
		elif self.d_left == 5:
			self.cell_type = 'left'
			self.d_left = 0

def pdf(rule, rng):
	sample = rng.uniform(0, 1)
	total = 0
	for key, value in rule.items():
		if total < sample < total+value:
			result = np.float(key)
		total += value
	assert total <= 1.0
	return result

def reproduce(parent):
	children = []
	if parent.cell_type == 'left':
		angle = parent.theta + pdf(angle_rules['left'], parent.rng)
	elif parent.cell_type == 'right':
		angle = parent.theta + pdf(angle_rules['right'], parent.rng)
	global IDmax
	IDmax += 1
	child = Cell(ID=IDmax, x=parent.x, y=parent.y, theta=angle)
	child.x += np.cos(child.theta)
	child.y += np.sin(child.theta)
	child.parent = parent
	child.d_left = parent.d_left + 1
	child.d_right = parent.d_right + 1
	child.update_cell_type()
	children.append(child)
	return children

def recursive_push(pushed, vx, vy):
	x_old = pushed.x
	y_old = pushed.y
	pushed.x += vx
	pushed.y += vy
	x_new = pushed.x
	y_new = pushed.y
	# print('cell', pushed.ID, 'pushes', [child.ID for child in pushed.children])
	# print(pushed.ID, '(', pushed.x, pushed.y, ')', pushed.d_node, pushed.cell_type)
	for cell in pushed.children:
		recursive_push(cell, vx, vy)


'''main'''

t_final = 12
seed = 0
cell_width = 0.5
angle_rules = {
	'left': {str(np.pi/3): 1},
	'right': {str(-np.pi/3): 1},
	}
rng = np.random.RandomState(seed=seed)
lines = [[] for t in range(1+t_final)]
xs = [[] for t in range(1+t_final)]
ys = [[] for t in range(1+t_final)]
cts = [[] for t in range(1+t_final)]
IDs = [[] for t in range(1+t_final)]

# initial conditions ("axiom" in L-systems vocabulary)
cell0 = Cell(ID=0, x=0, y=0)
cell0.cell_type = 'left'
cell0.d_left = 0
cell0.d_right = 1
cell0.theta = -np.pi/3
cell1 = Cell(ID=1, x=0, y=0)
cell1.cell_type = 'left'
cell1.d_left = 0
cell1.d_right = 2
cell1.theta = -np.pi/3
cell1.parent = cell0
cell1.reproduce_countdown = 0
IDmax = 2
cells = [cell1]
lines[0].append([(cell0.x, cell0.y), (cell1.x, cell1.y)])
for cell in cells:
	for child in cell.children:
		lines[0].append([(cell.x, cell.y), (child.x, child.y)])
	xs[0].append(cell.x)
	ys[0].append(cell.y)
	cts[0].append(cell.cell_type)
	IDs[0].append(cell.ID)

for t in np.arange(1, t_final):
	print('\nt=%s'%(t), 'n_cells=%s' %len(cells))
	cells_new = []
	for cell in cells:
		# cell.update_cell_type()
		if cell.reproduce_countdown == 0:
			# print(cell.ID, cell.d_left, cell.d_right, cell.cell_type)
			children = reproduce(cell)
			cell.reproduce_countdown = 8
			print('cell', cell.ID, 'births', [child.ID for child in children])
			for child in children:
				# print(child.ID, child.d_left, child.d_right, child.cell_type)
				for pushed in cell.children:
					if np.sqrt((pushed.x-child.x)**2 + (pushed.y-child.y)**2) < cell_width:
						cell.children.remove(pushed)
						child.children.append(pushed)
						pushed.parent = child
						recursive_push(pushed, child.x-cell.x, child.y-cell.y)
				cell.children.append(child)
				cells_new.append(child)
		else:
			cell.reproduce_countdown -= 1
	for new in cells_new:
		cells.append(new)
	rng.shuffle(cells)
	for cell in cells:
		lines[t].append([(cell0.x, cell0.y), (cell1.x, cell1.y)])
		for child in cell.children:
			lines[t].append([(cell.x, cell.y), (child.x, child.y)])
		xs[t].append(cell.x)
		ys[t].append(cell.y)
		cts[t].append(cell.cell_type)
		IDs[t].append(cell.ID)
		# print(cell.ID, '(', cell.x, cell.y, ')', cell.d_node)

for t in range(t_final):
	gridsize = 1+np.max([np.max(xs[t]), np.max(ys[t])])
	fig, ax = plt.subplots(figsize=((16, 16)))
	ax.set(xlim=((-gridsize, gridsize)), ylim=((-gridsize, gridsize)), title='t=%s'%(t))
	lc = mc.LineCollection(lines[t], colors='k')
	ax.add_collection(lc)
	if t < 10:
		colors = np.array(['r' if ct == 'left' else 'b' for ct in cts[t]])
		ax.scatter(xs[t], ys[t], c=colors) 
	plt.savefig('plots/sierpinski_triangle/%s.png'%(t))	