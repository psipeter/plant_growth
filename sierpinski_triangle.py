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
	def __init__(self, ID, x=0, y=0, angle=0):
		self.ID = ID
		self.x = x
		self.y = y
		self.angle = angle  # indicates angle between parent and self
		self.d_left = np.inf
		self.d_right = np.inf
		self.reproduce_countdown = 0
		self.cell_type = 'straight'  # indicates angle of child
		self.parent = None
		self.child = None
		self.rng = np.random.RandomState(seed=ID)

	def update_cell_type(self):
		if self.d_right != 5 and self.d_left != 5:
			self.cell_type = self.parent.cell_type
		elif self.d_right == 5:
			self.cell_type = 'right'
		elif self.d_left == 5:
			self.cell_type = 'left'
		if self.cell_type == 'left':
			self.d_left = 0
		elif self.cell_type == 'right':
			self.d_right = 0

def pdf(rule, rng):
	sample = rng.uniform(0, 1)
	total = 0
	for key, value in rule.items():
		if total < sample < total+value:
			result = np.float(key)
		total += value
	assert total <= 1.0
	return result

def reproduce(parent, IDmax):
	parent.reproduce_countdown = 8
	child = Cell(ID=IDmax, x=parent.x, y=parent.y, angle=parent.angle)
	child.parent = parent
	child.d_right = parent.d_right + 1
	child.d_left = parent.d_left + 1
	child.update_cell_type()
	d_angle = pdf(angle_rules[parent.cell_type], parent.rng)
	child.angle += d_angle
	child.x += np.cos(child.angle)
	child.y += np.sin(child.angle)
	if parent.child is not None:
		recursive_push(child, parent.child)
	parent.child = child
	return child, IDmax+1

def recursive_push(pusher, pushed):
	pusher.child = pushed
	pushed.parent = pusher
	pushed.d_right += 1
	pushed.d_left += 1
	pushed.update_cell_type()
	d_angle = pdf(angle_rules[pusher.cell_type], pusher.rng)
	pushed.angle += d_angle
	pushed.x += np.cos(pushed.angle)
	pushed.y += np.sin(pushed.angle)
	if pushed.child is not None:
		recursive_push(pushed, pushed.child)


'''main'''

t_final = 14
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
cell0.angle = -np.pi/3
cell1 = Cell(ID=1, x=0, y=0)
cell1.cell_type = 'left'
cell1.d_left = 0
cell1.d_right = 2
cell1.angle = -np.pi/3
cell1.parent = cell0
IDmax = 2
cells = [cell1]
lines[0].append([(cell0.x, cell0.y), (cell1.x, cell1.y)])
for cell in cells:
	if cell.child is not None:
		lines[0].append([(cell.x, cell.y), (cell.child.x, cell.child.y)])
	xs[0].append(cell.x)
	ys[0].append(cell.y)
	cts[0].append(cell.cell_type)
	IDs[0].append(cell.ID)

for t in np.arange(1, t_final):
	print('\nt=%s'%(t), 'n_cells=%s' %len(cells))
	cells_new = []
	for cell in cells:
		if cell.reproduce_countdown == 0:
			child, IDmax = reproduce(cell, IDmax)
			cells_new.append(child)
		else:
			cell.reproduce_countdown -= 1
	for new in cells_new:
		cells.append(new)
	rng.shuffle(cells)
	for cell in cells:
		lines[t].append([(cell0.x, cell0.y), (cell1.x, cell1.y)])
		if cell.child is not None:
			lines[t].append([(cell.x, cell.y), (cell.child.x, cell.child.y)])
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
	if t < 20:
		colors = np.array(['r' if ct == 'left' else 'b' for ct in cts[t]])
		ax.scatter(xs[t], ys[t], c=colors) 
	plt.savefig('plots/sierpinski_triangle/%s.png'%(t))	