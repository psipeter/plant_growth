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
	def __init__(self, ID, x=0, y=0, theta=np.pi/2):
		self.ID = ID
		self.x = x
		self.y = y
		self.theta = theta
		self.d_node = np.inf
		self.p_reproduce = p_reproduce_vein
		self.cell_type = 'vein'
		self.parent = None
		self.children = []
		self.rng = np.random.RandomState(seed=ID)

	def query_parent(self):
		if self.cell_type == 'node':
			self.d_node = 0
			return 0
		d_nodes = [self.d_node, self.parent.query_parent()+1]
		self.d_node = np.min(d_nodes)
		return self.d_node

	def query_children(self):
		if self.cell_type == 'node':
			self.d_node = 0
			return 0
		d_nodes = [self.d_node]
		for child in self.children:
			d_nodes.append(child.query_children()+1)
		self.d_node = np.min(d_nodes)
		return self.d_node

	def diffuse_parent(self, val):
		if val >= self.d_node:
			return
		else:
			self.parent.diffuse_parent(val+1)
		self.d_node = val

	def diffuse_children(self, val):
		if val >= self.d_node:
			return
		else:
			for child in self.children:
				child.diffuse_children(val+1)
		self.d_node = val		

	def update_cell_type(self):
		if node_spacing < self.d_node < 1e10 and len(self.children)==0:
			self.cell_type = 'node'
			self.d_node = 0	
			self.p_reproduce = p_reproduce_node
			self.diffuse_parent(1)
			self.diffuse_children(1)

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
	global IDmax
	if parent.cell_type == 'vein':
		angle = parent.theta + pdf(angle_rules['vein'], parent.rng)
		child = Cell(ID=IDmax, x=parent.x, y=parent.y, theta=angle)
		IDmax += 1
		child.x += np.cos(child.theta)
		child.y += np.sin(child.theta)
		child.parent = parent
		child.d_node = parent.d_node + 1
		children.append(child)
	if parent.cell_type == 'node':
		angle = pdf(angle_rules['node'], parent.rng)
		child = Cell(ID=IDmax, x=parent.x, y=parent.y, theta=parent.theta+angle)
		IDmax += 1
		child.x += np.cos(child.theta)
		child.y += np.sin(child.theta)
		child.parent = parent
		child.d_node = parent.d_node + 1
		children.append(child)
		child2 = Cell(ID=IDmax, x=parent.x, y=parent.y, theta=parent.theta-angle)
		IDmax += 1
		child2.x += np.cos(child2.theta)
		child2.y += np.sin(child2.theta)
		child2.parent = parent
		child2.d_node = parent.d_node + 1
		children.append(child2)
	return children

def recursive_push(pushed, vx, vy):
	x_old = pushed.x
	y_old = pushed.y
	pushed.x += vx
	pushed.y += vy
	x_new = pushed.x
	y_new = pushed.y
	# print('cell', pushed.ID, 'pushes', [child.ID for child in pushed.children])
	pushed.query_parent()
	pushed.query_children()
	pushed.update_cell_type()
	# print(pushed.ID, '(', pushed.x, pushed.y, ')', pushed.d_node, pushed.cell_type)
	for cell in pushed.children:
		recursive_push(cell, vx, vy)


'''main'''

t_final = 9
seed = 0
p_reproduce_vein = 1.0
p_reproduce_node = 1.0
node_spacing = 1
cell_width = 0.5
angle_rules = {
	'vein': {str(0): 1},
	'node': {str(-np.pi/4): 0.5,  str(np.pi/4): 0.5}
	}
rng = np.random.RandomState(seed=seed)
lines = [[] for t in range(1+t_final)]
xs = [[] for t in range(1+t_final)]
ys = [[] for t in range(1+t_final)]
cts = [[] for t in range(1+t_final)]
IDs = [[] for t in range(1+t_final)]

# initial conditions ("axiom" in L-systems vocabulary)
node0 = Cell(ID=0, x=0, y=0)  # inactive node (not in "cells" list)
node0.cell_type = 'node'
node0.d_node = 0
cell0 = Cell(ID=1, x=0, y=1)
cell0.parent = node0
cell0.d_node = 1
node0.children = [cell0]
cell1 = Cell(ID=2, x=0, y=2)
cell1.parent = cell0
cell1.d_node = 2
cell0.children = [cell1]
IDmax = 3
cells = [cell0, cell1]
for cell in cells:
	lines[0].append([(node0.x, node0.y), (cell0.x, cell0.y)])
	for child in cell.children:
		lines[0].append([(cell.x, cell.y), (child.x, child.y)])
	xs[0].append(cell.x)
	ys[0].append(cell.y)
	cts[0].append(cell.cell_type)
	IDs[0].append(cell.ID)

for t in np.arange(1, t_final):
	print('\nt=%s'%(t), 'n_cells=%s' %len(cells))
	sys.setrecursionlimit(np.max([1000, 2*len(cells)]))
	cells_new = []
	for cell in cells:
		cell.query_parent()
		cell.query_children()
		cell.update_cell_type()
		# reproduce
		if cell.rng.uniform(0, 1) < cell.p_reproduce:
			children = reproduce(cell)
			# print('cell', cell.ID, 'births', [child.ID for child in children])
			for child in children:
				# print(child.ID, '(', child.x, child.y, ')', child.d_node)
				for pushed in cell.children:
					if np.sqrt((pushed.x-child.x)**2 + (pushed.y-child.y)**2) < cell_width:
						cell.children.remove(pushed)
						child.children.append(pushed)
						pushed.parent = child
						recursive_push(pushed, child.x-cell.x, child.y-cell.y)
				child.query_parent()
				child.query_children()
				child.update_cell_type()
				cell.children.append(child)
				cells_new.append(child)
	for new in cells_new:
		cells.append(new)
	rng.shuffle(cells)
	for cell in cells:
		lines[t].append([(node0.x, node0.y), (cell0.x, cell0.y)])
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
	ax.set(xlim=((-gridsize/2, gridsize/2)), ylim=((0, gridsize)), title='t=%s'%(t))
	lc = mc.LineCollection(lines[t], colors='k')
	ax.add_collection(lc)
	if t < 5:
		colors = np.array(['k' if ct == 'vein' else 'r' for ct in cts[t]])
		ax.scatter(xs[t], ys[t], c=colors) 
		ax.scatter(node0.x, node0.y, c='r', marker="D")
	plt.savefig('plots/fractal_binary_tree/%s.png'%(t))	