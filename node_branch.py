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
	def __init__(self, id, x=0, y=0, theta=0):
		self.id = id
		self.x = x
		self.y = y
		self.theta = theta
		self.to_node = to_node  # todo: 2-way communication to ensure even spacing
		self.cell_type = 'vein'
		self.parent = []
		self.children = []
		self.up = None
		self.down = None
		self.left = None
		self.right = None
		self.rng = np.random.RandomState(seed=id)

	def update_to_node(self, val):
		self.to_node = np.max([0, val])

	def update_cell_type(self):
		if self.to_node == 0:
			self.cell_type = 'node'
			self.to_node = to_node

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
	grid[x_new][y_new].append(pushed)


# def recursive_push(pusher, pushed, children, vx, vy):
# 	x_old = pushed.x
# 	y_old = pushed.y
# 	pushed.x += vx
# 	pushed.y += vy
# 	grid[x_old][y_old].remove(pushed)
# 	x_new = pushed.x
# 	y_new = pushed.y

# 	for cell in grid[x_new][y_new]:
# 		children.append(cell)
# 		new_children = recursive_push(pushed, cell, copy.deepcopy(cell.children), vx, vy)
# 	grid[x_new][y_new].append(pushed)
# 	pushed.parent.append(pusher)

# 	for cell in grid[x_new][y_new]:
# 		pushed.children.append(cell)
# 		if cell in pusher.children:
# 			pusher.children.remove(cell)
# 	# print(pushed.children)
# 	for cell in pushed.children:
# 		recursive_push(pushed, cell, vx, vy)
# 	grid[x_new][y_new].append(pushed)
# 	pushed.parent.append(pusher)
# 	pusher.children.append(pushed)

'''main loop'''
t_final = 7
xmax = 100
ymax = 100
seed = 0
p_child = 1.0
to_node = 3
rng = np.random.RandomState(seed=seed)
grid0 = [[[] for x in range(xmax)] for y in range(ymax)]
cell0 = Cell(id=0, x=1, y=int(ymax/2))
grid0[int(cell0.x)][int(cell0.y)].append(cell0)
cells = [cell0]
grid_history = [copy.deepcopy(grid0)]
cell_history = [copy.deepcopy(cells)]
grid = grid0
idmax = 0
for t in range(t_final):
	print('t=%s'%(t+1))
	children = []
	for cell in cells:
		if rng.uniform(0, 1) < p_child:
			idmax += 1
			child = Cell(id=idmax, x=cell.x, y=cell.y, theta=cell.theta+pdf(cell.rng)*(cell.cell_type == 'node'))
			child.update_to_node(cell.to_node-1)
			child.update_cell_type()
			children.append(child)
			cell.children.append(child)
			vx, vy = int(np.cos(child.theta)), int(np.sin(child.theta))  # todo: non-right angles
			child.x += vx
			child.y += vy
			for pushed in grid[child.x][child.y]:
				cell.children.remove(pushed)  # try block?
				child.children.append(pushed)
				pushed.parent.append(child)
				recursive_push(pushed, vx, vy)
			grid[child.x][child.y].append(child)
			# recursive_push(cell, child, vx, vy)
	for child in children:
		cells.append(child)
	# rng.shuffle(cells)
	cell_history.append(copy.deepcopy(cells))
	grid_history.append(copy.deepcopy(grid))
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
	cs = np.array([cell.id/len(cell_history[-1]) for cell in grid])
	ax.scatter(xs, ys, s=ss, color=cm.rainbow(cs))
	plt.savefig('plots/%s.png'%t)