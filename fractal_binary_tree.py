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
	def __init__(self, ID, x=0, y=0, angle=np.pi/2):
		self.ID = ID
		self.x = x
		self.y = y
		self.angle = angle
		self.d_branch = 0
		self.cell_type = 'straight'
		self.parent = None
		self.children = []

	def update_cell_type(self):
		if self.d_branch >= branch_spacing and len(self.children)==0:
			self.cell_type = 'branch'
			self.d_branch = 0

def reproduce(parent, IDmax):
	children = []
	if parent.cell_type == 'straight':
		angle = parent.angle + angle_rules['straight']
		child = Cell(ID=IDmax, x=parent.x, y=parent.y, angle=angle)
		IDmax += 1
		child.x += np.cos(child.angle)
		child.y += np.sin(child.angle)
		child.parent = parent
		child.d_branch = parent.d_branch + 1
		children.append(child)
	if parent.cell_type == 'branch':
		angle_L, angle_R = angle_rules['branch']
		child = Cell(ID=IDmax, x=parent.x, y=parent.y, angle=parent.angle+angle_L)
		IDmax += 1
		child.x += np.cos(child.angle)
		child.y += np.sin(child.angle)
		child.parent = parent
		child.d_branch = parent.d_branch + 1
		children.append(child)
		child2 = Cell(ID=IDmax, x=parent.x, y=parent.y, angle=parent.angle+angle_R)
		IDmax += 1
		child2.x += np.cos(child2.angle)
		child2.y += np.sin(child2.angle)
		child2.parent = parent
		child2.d_branch = parent.d_branch + 1
		children.append(child2)
	for child in children:
		for pushed in parent.children:
			if np.abs(child.x - pushed.x) < 0.1 and np.abs(child.y - pushed.y) < 0.1:
				parent.children.remove(pushed)
				child.children.append(pushed)
				pushed.parent = child
				recursive_push(pushed, np.cos(child.angle), np.sin(child.angle))
	return children, IDmax

def recursive_push(pushed, dx, dy):
	pushed.x += dx
	pushed.y += dy
	pushed.d_branch += 1
	for cell in pushed.children:
		recursive_push(cell, dx, dy)

def plot_timeseries(plot=True):
	if not plot:
		return
	global t_steps
	alllines = []
	allxs = []
	allys = []
	allcts = []
	alllines.append([(cell0.x, cell0.y), (cell1.x, cell1.y)])
	for cell in cells:
		for child in cell.children:
			alllines.append([(cell.x, cell.y), (child.x, child.y)])
		allxs.append(cell.x)
		allys.append(cell.y)
		allcts.append(cell.cell_type)
	for new in cells_new:
		for child in new.children:
			alllines.append([(new.x, new.y), (child.x, child.y)])
		allxs.append(new.x)
		allys.append(new.y)
		allcts.append(new.cell_type)				
	gridsize = 0.3+np.max([np.max(allxs), np.max(allys)])
	fig, ax = plt.subplots(figsize=((16, 16)))
	ax.set(xlim=((-gridsize/2, gridsize/2)), ylim=((-0.3, gridsize)), title='t=%s'%t_steps)
	lc = mc.LineCollection(alllines, colors='k')
	ax.add_collection(lc)
	colors = np.array(['k' if ct == 'straight' else 'r' for ct in allcts])
	ax.scatter(allxs, allys, c=colors) # , s=300 
	ax.scatter(cell0.x, cell0.y, c='r', marker="D") # , s=300
	plt.axis('off')
	plt.savefig('plots/fractal_binary_tree/timeseries/%s.png'%t_steps)
	plt.close('all')	
	t_steps += 1

'''main'''

t_final = 7
seed = 0
branch_spacing = 1
cell_width = 0.5
angle_rules = {
	'straight': 0,
	'branch': [-np.pi/4, np.pi/4],
	}
rng = np.random.RandomState(seed=seed)
lines = [[] for t in range(1+t_final)]
xs = [[] for t in range(1+t_final)]
ys = [[] for t in range(1+t_final)]
cts = [[] for t in range(1+t_final)]
IDs = [[] for t in range(1+t_final)]
t_steps = 0


# initial conditions ("axiom" in L-systems vocabulary)
cell0 = Cell(ID=0, x=0, y=0)  # inactive branch (not in "cells" list)
cell0.cell_type = 'branch'
cell0.d_branch = 0
cell1 = Cell(ID=1, x=0, y=1)
cell1.parent = cell0
cell1.d_branch = 1
cell0.children = [cell1]
cell2 = Cell(ID=2, x=0, y=2)
cell2.parent = cell0
cell2.d_branch = 2
cell1.children = [cell2]
IDmax = 3
cells = [cell1, cell2]
for cell in cells:
	lines[0].append([(cell0.x, cell0.y), (cell1.x, cell1.y)])
	for child in cell.children:
		lines[0].append([(cell.x, cell.y), (child.x, child.y)])
	xs[0].append(cell.x)
	ys[0].append(cell.y)
	cts[0].append(cell.cell_type)
	IDs[0].append(cell.ID)
cells_new = []
plot_timeseries()

for t in np.arange(1, t_final):
	print('\nt=%s'%(t), 'n_cells=%s' %len(cells))
	sys.setrecursionlimit(np.max([1000, 2*len(cells)]))
	cells_new = []
	for cell in cells:
		cell.update_cell_type()
		children, IDmax = reproduce(cell, IDmax)
		for child in children:
			cell.children.append(child)
			cells_new.append(child)
		plot_timeseries()
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
		# print(cell.ID, '(', cell.x, cell.y, ')', cell.d_branch, cell.cell_type)

for t in range(t_final):
	gridsize = 1+np.max([np.max(xs[t]), np.max(ys[t])])
	fig, ax = plt.subplots(figsize=((16, 16)))
	ax.set(xlim=((-gridsize/2, gridsize/2)), ylim=((0, gridsize)), title='t=%s'%(t))
	lc = mc.LineCollection(lines[t], colors='k')
	ax.add_collection(lc)
	if t < 5:
		colors = np.array(['k' if ct == 'straight' else 'r' for ct in cts[t]])
		ax.scatter(xs[t], ys[t], c=colors) 
		ax.scatter(cell0.x, cell0.y, c='r', marker="D")
	plt.axis('on')
	plt.savefig('plots/fractal_binary_tree/%s.png'%(t))	