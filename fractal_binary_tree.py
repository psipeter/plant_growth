'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.collections as mc
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

def update_cell_type(cell):
	if cell.d_branch >= branch_spacing and len(cell.children)==0:
		cell.cell_type = 'branch'
		cell.d_branch = 0

def reproduce(parent):
	global IDmax
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
	parent.children.extend(children)
	return children

def recursive_push(pushed, dx, dy):
	pushed.x += dx
	pushed.y += dy
	pushed.d_branch += 1
	for cell in pushed.children:
		recursive_push(cell, dx, dy)

def plot_timeseries(plot=False):
	if plot:
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

def update_lists(t):
	global cells, lines, xs, ys, cts, IDs
	for cell in cells:
		lines[t].append([(cell0.x, cell0.y), (cell1.x, cell1.y)])
		for child in cell.children:
			lines[t].append([(cell.x, cell.y), (child.x, child.y)])
		xs[t].append(cell.x)
		ys[t].append(cell.y)
		cts[t].append(cell.cell_type)
		IDs[t].append(cell.ID)

def update_plots(t):
	global lines, xs, ys, cts, IDs	
	fig, ax = plt.subplots(figsize=((16, 16)))
	gridsize = 1+np.max([np.max(xs[t]), np.max(ys[t])])
	ax.set(xlim=((-gridsize/2, gridsize/2)), ylim=((0, gridsize)), title='t=%s'%(t))
	lc = mc.LineCollection(lines[t], colors='k')
	ax.add_collection(lc)
	plt.axis('on')
	plt.savefig('plots/fractal_binary_tree/%s.png'%(t))	

# model parameters
t_final = 11
seed = 0
rng = np.random.RandomState(seed=seed)
branch_spacing = 1
angle_rules = {
	'straight': 0,
	'branch': [-np.pi/4, np.pi/4],
	}

# initial conditions
cell0 = Cell(ID=0, x=0, y=0)  # inactive (not in "cells" list)
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
cells = [cell1, cell2]
lines = [[] for t in range(1+t_final)]
xs = [[] for t in range(1+t_final)]
ys = [[] for t in range(1+t_final)]
cts = [[] for t in range(1+t_final)]
IDs = [[] for t in range(1+t_final)]
t_steps = 0
IDmax = 3
plot_timeseries()
update_lists(0)
update_plots(0)

# simulation loop
for t in np.arange(1, t_final):
	print('t=%s, n_cells=%s \n' %(t, len(cells)))
	sys.setrecursionlimit(np.max([1000, 2*len(cells)]))
	for c in range(len(cells)):
		cell = cells[c]
		update_cell_type(cell)
		children = reproduce(cell)
		cells.extend(children)
		plot_timeseries()
	rng.shuffle(cells)
	update_lists(t)
	update_plots(t)
