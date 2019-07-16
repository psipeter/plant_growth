'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import copy
import sys

class Cell():
	def __init__(self, ID, x=0, y=0, theta=0):
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

	def update_d_node(self):
		if self.cell_type == 'node2':
			self.d_node = 0
			return
		d_node_min = np.min([self.d_node, self.parent.d_node])
		for child in self.children:
			d_node_min = np.min([d_node_min, child.d_node])
		self.d_node = int(d_node_min + 1)

	def update_cell_type(self):
		if self.d_node == node_spacing:
			self.cell_type = 'node2'
			self.d_node = 0	
			self.p_reproduce = p_reproduce_node	
		# print(self.d_node == node_spacing)

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
		children.append(child)
		parent.p_reproduce *= reproduce_decay
	if parent.cell_type == 'node':
		angle = parent.theta + pdf(angle_rules['node'], parent.rng)
		child = Cell(ID=IDmax, x=parent.x, y=parent.y, theta=angle)
		IDmax += 1
		child.x += np.cos(child.theta)
		child.y += np.sin(child.theta)
		children.append(child)
		parent.p_reproduce *= reproduce_decay
	if parent.cell_type == 'node2':
		angle = pdf(angle_rules['node2'], parent.rng)
		child = Cell(ID=IDmax, x=parent.x, y=parent.y, theta=parent.theta+angle)
		IDmax += 1
		child.x += np.cos(child.theta)
		child.y += np.sin(child.theta)
		children.append(child)
		child2 = Cell(ID=IDmax, x=parent.x, y=parent.y, theta=parent.theta-angle)
		IDmax += 1
		child2.x += np.cos(child2.theta)
		child2.y += np.sin(child2.theta)
		children.append(child2)
		parent.p_reproduce *= reproduce_decay
	return children

def recursive_push(pushed, vx, vy):
	x_old = pushed.x
	y_old = pushed.y
	pushed.x += vx
	pushed.y += vy
	x_new = pushed.x
	y_new = pushed.y
	for cell in pushed.children:
		recursive_push(cell, vx, vy)
	pushed.update_d_node()
	pushed.update_cell_type()


'''main'''
t_final = 12
seed = 0
p_reproduce_vein = 0.8
p_reproduce_node = 1.0
node_spacing = 5
cell_width = 0.5
reproduce_decay = 0.5
angle_rules = {
	'vein': {str(0): 1},
	'node': {str(-np.pi/4): 0.45, str(0): 0.1, str(np.pi/4): 0.45},
	'node2': {str(-np.pi/4): 0.5,  str(np.pi/4): 0.5}
	}
rng = np.random.RandomState(seed=seed)
node0 = Cell(ID=0, x=0, y=0)  # inactive node (not in cells)
node0.cell_type = 'node2'
node0.d_node = 0
cell0 = Cell(ID=1, x=1, y=0)
cell0.parent = node0
cell0.d_node = 1
cells = [cell0]
xs = [[] for t in range(t_final)]
ys = [[] for t in range(t_final)]
cts = [[] for t in range(t_final)]
IDs = [[] for t in range(t_final)]
IDmax = 2

for t in range(t_final):
	print('t=%s'%(t+1), 'n_cells=%s' %len(cells))
	sys.setrecursionlimit(np.max([1000, 2*len(cells)]))
	cells_new = []
	for cell in cells:
		cell.update_d_node()
		cell.update_cell_type()
		# reproduce
		if cell.rng.uniform(0, 1) < cell.p_reproduce:
			children = reproduce(cell)
			for child in children:
				for pushed in cell.children:
					if np.sqrt((pushed.x-child.x)**2 + (pushed.y-child.y)**2) < cell_width:
						cell.children.remove(pushed)
						child.children.append(pushed)
						pushed.parent = child
						recursive_push(pushed, child.x-cell.x, child.y-cell.y)					
				child.parent = cell
				cell.children.append(child)
				cells_new.append(child)
				# update distance to nearest node
				child.update_d_node()
				child.update_cell_type()
				cell.update_d_node()
				cell.update_cell_type()
				child.update_d_node()
				child.update_cell_type()
	for new in cells_new:
		cells.append(new)
	rng.shuffle(cells)
	for cell in cells:
		xs[t].append(cell.x)
		ys[t].append(cell.y)
		cts[t].append(cell.cell_type)
		IDs[t].append(cell.ID)

# to pass list of markers as an argument to scatter
# https://github.com/matplotlib/matplotlib/issues/11155
def mscatter(x,y,ax=None, m=None, **kw):
    import matplotlib.markers as mmarkers
    if not ax: ax=plt.gca()
    sc = ax.scatter(x,y,**kw)
    if (m is not None) and (len(m)==len(x)):
        paths = []
        for marker in m:
            if isinstance(marker, mmarkers.MarkerStyle):
                marker_obj = marker
            else:
                marker_obj = mmarkers.MarkerStyle(marker)
            path = marker_obj.get_path().transformed(
                        marker_obj.get_transform())
            paths.append(path)
        sc.set_paths(paths)
    return sc

for t in range(t_final):
	gridsize = 1+np.max([np.max(xs[t]), np.max(ys[t])])
	# sizes = np.array([np.sqrt(gridsize) if ct == 'vein' else 5*np.sqrt(gridsize) for ct in cts[t]])
	shapes = np.array(["o" if ct == 'vein' else "D" for ct in cts[t]])
	colors = np.array(IDs[t])/IDmax   # color=cm.rainbow(colors), ax=ax
	colors = np.array(['k' if ct == 'vein' else 'r' for ct in cts[t]])
	fig, ax = plt.subplots(figsize=((16, 16)))
	ax.set(xlim=((0, gridsize)), ylim=((-gridsize/2, gridsize/2)),
		xticks=[0, gridsize], yticks=[-gridsize/2, gridsize/2], title='t=%s'%t)
	mscatter(xs[t], ys[t], m=shapes, c=colors) 
	# ax.scatter(xs[t], ys[t], s=sizes, marker=shapes, color=cm.rainbow(colors))
	ax.scatter(node0.x, node0.y, c='r', marker="D")
	plt.savefig('plots/%s.png'%t)