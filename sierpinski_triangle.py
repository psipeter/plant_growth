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
	def __init__(self, ID, x1=0, x2=0, y1=0, y2=0, angle1=0, angle2=0):
		self.ID = ID
		self.x1 = x1  # point on L
		self.y1 = y1
		self.x2 = x2  # point on R
		self.y2 = y2
		self.angle1 = angle1  # orientation of the line pointing towards (x1, y1)
		self.angle2 = angle2  # orientation of the line pointing towards (x2, y2)
		self.cell_type = None
		self.L = None
		self.R = None

def reproduce(parent, IDmax):
	child_L = Cell(ID=IDmax, x1=parent.x1, y1=parent.y1, x2=parent.x1, y2=parent.y1, angle1=parent.angle1, angle2=parent.angle1+np.pi)
	child_R = Cell(ID=IDmax+1, x1=parent.x2, y1=parent.y2, x2=parent.x2, y2=parent.y2, angle2=parent.angle2, angle1=parent.angle2+np.pi)
	child_L.R = parent
	child_R.L = parent
	print('parent', parent.ID, 'L', child_L.ID, 'R', child_R.ID)
	if parent.cell_type == 'A':
		child_L.cell_type = 'B'
		child_R.cell_type = 'B'
	if parent.cell_type == 'B':
		child_L.cell_type = 'A'
		child_R.cell_type = 'A'
	d_angle_L, d_angle_R = angle_rules[parent.cell_type]
	child_L.angle1 += d_angle_L
	child_L.angle2 += d_angle_L
	child_R.angle1 += d_angle_R
	child_R.angle2 += d_angle_R
	child_L.x1 += np.cos(child_L.angle1)
	child_L.y1 += np.sin(child_L.angle1)
	child_R.x2 += np.cos(child_R.angle2)
	child_R.y2 += np.sin(child_R.angle2)
	print('parent', parent.angle1/np.pi*180, parent.angle2/np.pi*180)
	print('L', child_L.angle1/np.pi*180, child_L.angle2/np.pi*180)
	print('R', child_R.angle1/np.pi*180, child_R.angle2/np.pi*180)
	if parent.L is not None:
		recursive_push(child_L, parent.L, child_L.angle1, 'L')
	if parent.R is not None:
		recursive_push(child_R, parent.R, child_R.angle2, 'R')
	parent.L = child_L
	parent.R = child_R
	return child_R, child_L, IDmax+2

def recursive_push(pusher, pushed, angle, direction):
	pushed.x1 += np.cos(angle)
	pushed.x2 += np.cos(angle)
	pushed.y1 += np.sin(angle)
	pushed.y2 += np.sin(angle)
	if direction == 'L':
		pushed.R = pusher
		if pushed.L is not None:
			recursive_push(pushed, pushed.L, angle, direction)
	elif direction == 'R':
		pushed.L = pusher
		if pushed.R is not None:
			recursive_push(pushed, pushed.R, angle, direction)

'''main'''

t_final = 3
seed = 0
angle_rules = {
	'A': [np.pi/3, -np.pi/3],
	'B': [-np.pi/3, np.pi/3],
	# 'A': [np.pi + np.pi/3, -np.pi/3],
	# 'B': [np.pi - np.pi/3, np.pi/3],
	}
rng = np.random.RandomState(seed=seed)
lines = [[] for t in range(1+t_final)]
xs = [[] for t in range(1+t_final)]
ys = [[] for t in range(1+t_final)]
cts = [[] for t in range(1+t_final)]
IDs = [[] for t in range(1+t_final)]

# initial conditions ("axiom" in L-systems vocabulary)
cell0 = Cell(ID=0, x1=0, x2=1, y1=0, y2=0, angle1=np.pi, angle2=0)
cell0.cell_type = 'A'
IDmax = 1
cells = [cell0]
for cell in cells:
	lines[0].append([(cell0.x1, cell0.y1), (cell0.x2, cell0.y2)])
	xs[0].append(cell0.x1)
	xs[0].append(cell0.x2)
	ys[0].append(cell0.y1)
	ys[0].append(cell0.y2)
	cts[0].append(cell.cell_type)
	IDs[0].append(cell.ID)

for t in np.arange(1, t_final):
	print('\nt=%s'%(t), 'n_cells=%s' %len(cells))
	cells_new = []
	for cell in cells:
		child_L, child_R, IDmax = reproduce(cell, IDmax)
		cells_new.append(child_L)
		cells_new.append(child_R)
	for new in cells_new:
		cells.append(new)
	# rng.shuffle(cells)
	for cell in cells:
		lines[t].append([(cell.x1, cell.y1), (cell.x2, cell.y2)])
		xs[t].append(cell.x1)
		xs[t].append(cell.x2)
		ys[t].append(cell.y1)
		ys[t].append(cell.y2)
		cts[t].append(cell.cell_type)
		IDs[t].append(cell.ID)

for t in range(t_final):
	gridsize = 1+np.max([np.max(xs[t]), np.max(ys[t])])
	fig, ax = plt.subplots(figsize=((16, 16)))
	ax.set(xlim=((-gridsize, gridsize)), ylim=((-gridsize, gridsize)), title='t=%s'%(t))
	lc = mc.LineCollection(lines[t], colors='k')
	ax.add_collection(lc)
	plt.savefig('plots/sierpinski_triangle/%s.png'%(t))	