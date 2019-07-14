'''
Peter Duggins
ECE/SYDE 750: Artificial Life and Computation
July 2019
Final Project
'''

import numpy as np
# import matplotlib
import matplotlib.pyplot as plt
from matplotlib import animation
# matplotlib.use("Agg")
import copy

class Cell():
	def __init__(self, id, x=0, y=0, vx=0, vy=0, theta=0, to_node=10):
		self.id = id
		self.x = x
		self.y = y
		self.vx = vx
		self.vy = vy
		self.theta = theta
		self.to_node = to_node
		self.cell_type = 'vein' if to_node > 0 else 'node'
		self.rng = np.random.RandomState(seed=id)

	def wiggle(self, v=1.0):
		self.x += self.rng.uniform(0, v) * np.cos(self.rng.uniform(0, 2*np.pi))
		self.y += self.rng.uniform(0, v) * np.sin(self.rng.uniform(0, 2*np.pi))

	def reproduce(self, id, vx=0, vy=0):
		if self.cell_type == 'vein':
			angle = self.theta
			return Cell(id=id, x=self.x, y=self.y, vx=np.cos(angle), vy=np.sin(angle), theta=self.theta, to_node=self.to_node-1)
		elif self.cell_type == 'node':
			angle = self.theta+pdf(self.rng)
			return Cell(id=id, x=self.x, y=self.y, vx=np.cos(angle), vy=np.sin(angle), theta=angle)

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

def recursive_move(cell, cells, grid):
	x_old = int(cell.x)
	y_old = int(cell.y)
	cell.x += cell.vx
	cell.y += cell.vy
	x_new = int(cell.x)
	y_new = int(cell.y)
	if x_old != x_new or y_old != y_new:
		grid[x_old][y_old].remove(cell)
		grid[x_new][y_new].append(cell)
		pushed_cells = grid[x_new][y_new]
		for pushed_cell in pushed_cells:
			if pushed_cell is not cell:
				# print(cell.id, cell.x, cell.y, cell.vx, cell.vy)
				# print('pushes')
				# print(pushed_cell.id, pushed_cell.x, pushed_cell.y, pushed_cell.vx, pushed_cell.vy)
				pushed_cell.vx += cell.vx
				pushed_cell.vy += cell.vy
				grid = recursive_move(pushed_cell, cells, grid)
	cell.vx = 0
	cell.vy = 0
	return grid


'''main loop'''

t_final = 6
xmax = 100
ymax = 100
seed = 0
rng = np.random.RandomState(seed=seed)
grid0 = [[[] for x in range(xmax)] for y in range(ymax)]
cell0 = Cell(id=0, x=0, y=ymax/2)
grid0[int(cell0.x)][int(cell0.y)].append(cell0)
cells = [cell0]
grid_history = [copy.deepcopy(grid0)]
cell_history = [copy.deepcopy(cells)]
grid = grid0
idmax = 0

for t in range(t_final):
	print('t=%s'%t)
	offsprings = []
	for cell in cells:
		if cell.vx > 0 or cell.vy > 0:
			grid = recursive_move(cell, cells, grid)
			# cell.move(grid)  # move cell according to velocity and angle
			# # cell.wiggle()
			# grid[int(cell.x)][int(cell.y)].append(cell)  # update world grid to account for new position
			# for pushed_cell in grid[int(cell.x)][int(cell.y)]:  # push cells displaced by move
			# 	if pushed_cell is not cell:
			# 		pushed_cell.v += 1
		if rng.uniform(0, 1) < 1.0:
			idmax += 1
			offspring = cell.reproduce(idmax)
			offsprings.append(offspring)
			grid[int(offspring.x)][int(offspring.y)].append(offspring)
			# offspring.move(grid)
			# for pushed_cell in grid[int(offspring.x)][int(offspring.y)]:  # push cells displaced by move
			# 	if pushed_cell is not offspring:
			# 		pushed_cell.v += 1
	for offspring in offsprings:
		cells.append(offspring)
	# rng.shuffle(cells)
	cell_history.append(copy.deepcopy(cells))
	grid_history.append(copy.deepcopy(grid))
	print('n_cells=%s' %len(cells))

# plotting
def update_plot(i, cell_history, scat):
	xs = np.array([cell.x for cell in cell_history[i]])
	ys = np.array([cell.y for cell in cell_history[i]])
	ss = np.array([1 if cell.cell_type == 'vein' else 10 for cell in cell_history[i]])
	cs = np.array([0 if cell.cell_type == 'vein' else 1 for cell in cell_history[i]])
	scat.set_offsets(np.array([xs, ys]).T)
	scat.set_sizes(ss)
	scat.set_array(cs)
	scat.set(cmap='brg')
	return scat,
fig, ax = plt.subplots()
ax.set(xlim=((0, xmax)), ylim=((0, ymax)))
ax.axis('off')
xs = np.array([0 for cell in cell_history[-1]])
ys = np.array([0 for cell in cell_history[-1]])
scat = ax.scatter(xs, ys)
anim = animation.FuncAnimation(fig, update_plot, frames=t_final, interval=1, fargs=(cell_history, scat))
# plt.show()
anim.save('animation.mp4', fps=5, extra_args=['-vcodec', 'libx264'])