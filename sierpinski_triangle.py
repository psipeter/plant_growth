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

def reproduce(parent):
	global IDmax
	child_L = Cell(ID=IDmax, x1=parent.x1, y1=parent.y1, x2=parent.x1, y2=parent.y1, angle1=parent.angle1, angle2=parent.angle1+np.pi)
	child_R = Cell(ID=IDmax+1, x1=parent.x2, y1=parent.y2, x2=parent.x2, y2=parent.y2, angle2=parent.angle2, angle1=parent.angle2+np.pi)
	IDmax += 2
	child_L.R = parent
	child_R.L = parent
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
	if parent.L is not None:
		recursive_push(child_L, parent.L, child_L.angle1, 'L')
	if parent.R is not None:
		recursive_push(child_R, parent.R, child_R.angle2, 'R')
	parent.L = child_L
	parent.R = child_R
	return child_R, child_L

def recursive_push(pusher, pushed, angle, direction):
	pushed.x1 += np.cos(angle)
	pushed.x2 += np.cos(angle)
	pushed.y1 += np.sin(angle)
	pushed.y2 += np.sin(angle)
	if direction == 'L':
		pushed.R = pusher
		pusher.L = pushed
		if pushed.L is not None:
			recursive_push(pushed, pushed.L, angle, direction)
	elif direction == 'R':
		pushed.L = pusher
		pusher.R = pushed
		if pushed.R is not None:
			recursive_push(pushed, pushed.R, angle, direction)

def plot_timeseries(plot=False):
	if not plot:
		return
	global t_steps
	alllines = []
	allxs = []
	allys = []
	for cell in cells:
		alllines.append([(cell.x1, cell.y1), (cell.x2, cell.y2)])
		allxs.append(cell.x1)
		allxs.append(cell.x2)
		allys.append(cell.y1)
		allys.append(cell.y2)				
	gridsize = 1+np.max([np.max(allxs), np.max(allys)])
	fig, ax = plt.subplots(figsize=((16, 16)))
	ax.set(xlim=((-gridsize, gridsize)), ylim=((-gridsize, gridsize)), title='t=%s'%t_steps)
	lc = mc.LineCollection(alllines, colors='k')
	ax.add_collection(lc)
	plt.axis('off')
	plt.savefig('plots/sierpinski_triangle/timeseries/%s.png'%t_steps)
	plt.close('all')	
	t_steps += 1

def update_lists(t):
	global cells, lines, xs, ys, cts, IDs
	for cell in cells:
		lines[t].append([(cell.x1, cell.y1), (cell.x2, cell.y2)])
		xs[t].append(cell.x1)
		xs[t].append(cell.x2)
		ys[t].append(cell.y1)
		ys[t].append(cell.y2)
		cts[t].append(cell.cell_type)
		IDs[t].append(cell.ID)

def update_plots(t):
	global lines, xs, ys, cts, IDs
	fig, ax = plt.subplots(figsize=((16, 16)))
	# gridsize = np.max([np.max(xs[t]), np.max(ys[t])])
	# gridsize = np.max(np.abs(ys[t]))
	gridsize = 1 + 2**t
	ax.set(xlim=((-gridsize/2, gridsize/2)), ylim=((0, gridsize)), title='t=%s'%(t))
	lc = mc.LineCollection(lines[t], colors='k')
	ax.add_collection(lc)
	plt.savefig('plots/sierpinski_triangle/%s.png'%(t))	

# model parameters
t_final = 9
seed = 0
rng = np.random.RandomState(seed=seed)
angle_rules = {
	'A': [np.pi/3, -np.pi/3],
	'B': [-np.pi/3, np.pi/3],
	}

# initial conditions
cell0 = Cell(ID=0, x1=-0.5, x2=0.5, y1=1, y2=1, angle1=np.pi, angle2=0)
cell0.cell_type = 'A'
cells = [cell0]
IDmax = 1
t_steps = 0
lines = [[] for t in range(1+t_final)]
xs = [[] for t in range(1+t_final)]
ys = [[] for t in range(1+t_final)]
cts = [[] for t in range(1+t_final)]
IDs = [[] for t in range(1+t_final)]
plot_timeseries()
update_lists(0)
update_plots(0)

# simulation loop
for t in np.arange(1, t_final):
	print('t=%s, n_cells=%s \n' %(t, len(cells)))
	sys.setrecursionlimit(np.max([1000, 3*len(cells)]))
	for c in range(len(cells)):
		cell = cells[c]
		child_L, child_R = reproduce(cell)
		cells.append(child_L)
		cells.append(child_R)
		plot_timeseries()
	rng.shuffle(cells)
	update_lists(t)
	update_plots(t)