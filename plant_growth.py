'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import sys

class Cell():
	def __init__(self, x=0, y=0, z=0, theta=0, phi=0, d_branch=0):
		self.x = x
		self.y = y
		self.z = z
		self.theta = theta  # theta = angle between x and y axis
		self.phi = phi  # phi = angle between y and z axis
		self.d_branch = d_branch
		self.cell_type = 'vein'
		self.parent = None
		self.children = []
		self.age = 0

def update(cell):
	if cell.d_branch > branch_spacing and len(cell.children)==0:
		cell.cell_type = 'branch'
		cell.d_branch = 0
	cell.age += 1


def reproduce(parent):
	theta = parent.theta + angles(parent, 'theta')
	phi = parent.phi + angles(parent, 'phi')
	rho = distances(parent)
	child = Cell(x=parent.x, y=parent.y, z=parent.z, theta=theta, phi=phi, d_branch=parent.d_branch+1)
	# this transformation doesn't resepect angles properly, need to do some vector calculus
	child.x += rho*np.sin(child.phi)*np.cos(child.theta)
	child.y += rho*np.sin(child.phi)*np.sin(child.theta)
	child.z += rho*np.cos(child.phi)
	child.parent = parent
	for pushed in parent.children:
		if distance(child, pushed) < cell_radius:
			parent.children.remove(pushed)
			child.children.append(pushed)
			pushed.parent = child
			recursive_push(pushed, child.x-parent.x, child.y-parent.y, child.z-parent.z)
	parent.children.append(child)
	return child

def distance(a, b):
	return np.sqrt((a.x-b.x)**2+(a.y-b.y)**2+(a.z-b.z)**2)

def recursive_push(pushed, dx, dy, dz, add_distance=True):
	pushed.x += dx
	pushed.y += dy
	pushed.z += dz
	if pushed.cell_type != 'branch' and add_distance:
		pushed.d_branch += 1
	else:
		add_distance = False
	for cell in pushed.children:
		recursive_push(cell, dx, dy, dz, add_distance)

def update_plots(t):
	global cells, t_steps
	lines = []
	xs = []
	ys = []
	zs = []
	cts = []
	for cell in cells:
		for child in cell.children:
			lines.append([[cell.x, child.x], [cell.y, child.y], [cell.z, child.z]])
		xs.append(cell.x)
		ys.append(cell.y)
		zs.append(cell.z)
		cts.append(cell.cell_type)
	gridsize = 1+np.max([np.max(xs), np.max(ys), np.max(zs)])
	fig = plt.figure(figsize=((16, 16)))
	ax = fig.add_subplot(111, projection='3d')
	for line in lines:
		ax.plot(line[0], line[1], line[2], c='k')
	colors = []
	for ct in cts:
		if ct == 'vein': colors.append('k')
		if ct == 'branch': colors.append('r')
	ax.scatter(xs, ys, zs, c=np.array(colors)) # , s=300 
	ax.set(xlim=((-gridsize, gridsize)), ylim=((-gridsize, gridsize)), zlim=((0, 1+np.max(zs))), title='t=%s, T=%s'%(t_steps, t))
	# plt.axis('off')
	plt.savefig('plots/plant_growth/%s.png'%t_steps)
	plt.close('all')		

# model parameters
t_final = 7
seed = 1
cell_radius = 0.5
rng = np.random.RandomState(seed=seed)
branch_spacing = 1
def angles(parent, angle):
	if parent.cell_type == 'vein':
		if angle == 'theta':
			return rng.normal(0, 0.01)
		elif angle == 'phi':
			return rng.normal(0, 0.01)
	elif parent.cell_type == 'branch':
		if angle == 'theta':
			return rng.uniform(0, 2*np.pi)
		elif angle == 'phi':
			return rng.normal(np.pi/4, np.pi/32)
def distances(parent):
	if parent.cell_type == 'vein':
		return rng.normal(1, 0.01)
	elif parent.cell_type == 'branch':
		return rng.normal(1, 0.01)

# initial conditions
cell0 = Cell(x=0, y=0, z=0)
cell0.d_branch = 0
cells = [cell0]
t_steps = 0
update_plots(0)

# simulation loop
for t in np.arange(1, t_final):
	print('t=%s, n_cells=%s \n' %(t, len(cells)))
	sys.setrecursionlimit(np.max([1000, 2*len(cells)]))
	for c in range(len(cells)):
		cell = cells[c]
		update(cell)
		if cell.age > 2: continue
		child = reproduce(cell)
		cells.append(child)
		update_plots(t)
		t_steps += 1
	rng.shuffle(cells)