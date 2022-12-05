"""
Creates a tree of pacman junctions
"""

import queue
from MCTNode import MCTNode, Tactic
from game import Directions
import time
import util

class PacmanTree():
	def __init__(self, game_state):
		self.walls = game_state.getWalls()
		self.position = game_state.getPacmanPosition()
		self.root = MCTNode(position=self.position)
		self.tactic = Tactic.SURVIVAL
		self.successors_lookup = {}
		self.legal_lookup = {}
		self.maze_distance_lookup = {}

	def is_junction(self, pos):
		# Check if the position is a junction
		# A junction is a position with more than 2 non-wall neighbours
		# A junction is not a wall
		if self.walls[pos[0]][pos[1]]:
			return False
		else:
			# Adjacent positions
			adjacent = [(pos[0]+1, pos[1]), (pos[0]-1, pos[1]), (pos[0], pos[1]+1), (pos[0], pos[1]-1)]

			non_walls = [pos for pos in adjacent if not self.walls[pos[0]][pos[1]]]

			return len(non_walls) > 2

	def get_legal_actions(self, pos):
		# Legal actions do not move into a wall
		# Does not use any game state information, only depends on the position and the walls

		if pos in self.legal_lookup:
			return self.legal_lookup[pos]

		if self.walls[pos[0]][pos[1]]:
			self.legal_lookup[pos] = []
			return []

		# Adjacent positions
		adjacent = {(pos[0]+1, pos[1]): Directions.EAST, (pos[0]-1, pos[1]): Directions.WEST, (pos[0], pos[1]+1): Directions.NORTH, (pos[0], pos[1]-1): Directions.SOUTH}
		# Legal actions are the adjacent positions that are not walls
		legal_actions = [action for (adj_pos, action) in adjacent.items() if not self.walls[adj_pos[0]][adj_pos[1]]]
		self.legal_lookup[pos] = legal_actions
		return legal_actions

	def reset(self, state):
		self.root = MCTNode(state.getPacmanPosition())

	def update(self, new_state, timestep_discount):
		new_pos = new_state.getPacmanPosition()
		if self.is_junction(new_pos):
			# If the new state is a junction, check if any of the direct children of the root are the new state
			for child in self.root.children:
				if child.position == new_pos:
					# If the child is the new state, update the root to be the child
					child.parent = None
					self.root = child
					break
			else:
				self.reset(new_state)
				return
		else:
			# Check if the successors of the new state are the root's children
			successors = [pos for (pos, actions) in self.successors(new_pos)]
			child_positions = [child.position for child in self.root.children]

			# Check if the previous state was a junction
			if self.is_junction(self.root.position):
				# Find the child that is the new state based on the action taken
				action = new_state.getPacmanState().getDirection()
				new_root = None
				for child in self.root.children:
					if child.actions[0] == action:
						if child.position == new_pos:
							new_root = child
							break
						# new_root = MCTNode(position=new_pos, actions=[action])
						# new_root.visits = self.root.visits
						# break
				if new_root is None:
					self.reset(new_state)
					return
				
				old_root = self.root.copy()
				self.root = new_root
				self.root.parent = None
				
				# Remove new root from old root's children
				if new_root in old_root.children:
					old_root.children.remove(new_root)
				
				for (pos, actions) in self.successors(new_root.position):
					if pos == old_root.position:
						old_root.actions = actions
						new_root.addChild(old_root)
					if pos in child_positions:
						new_child = old_root.children[child_positions.index(pos)].copy()
						new_child.actions = actions
						new_root.addChild(new_child)

			# If the previous state was a tunnel, we should be on the same tunnel
			else:
				if set(successors) == set(child_positions):
					# Update the position of the root to be the new state
					self.root.position = new_pos
					# Update the actions of the children to be the actions to get to the child from the new state
					for child in self.root.children:
						for (pos, actions) in self.successors(new_pos):
							if pos == child.position:
								child.actions = actions
								break
				else:
					self.reset(new_state)
					return
				
		self.root.apply_discount(timestep_discount)


	def successors(self, position):
		# Returns a list of (position, actions) tuples
		# positions are the next junctions after taking the action from the position
		# actions is the sequence of actions to get to junction from the position

		# Check if the node's position is in the lookup
		if position in self.successors_lookup:
			return self.successors_lookup[position]

		successors = []

		# Get the legal actions from the node's position
		legal_actions = self.get_legal_actions(position)

		# Get the next junctions after taking the legal actions
		for action in legal_actions:
			next_pos = self.next_position(position, action)
			actions = [action]
			while not self.is_junction(next_pos) and len(self.get_legal_actions(next_pos)) > 1:
				# Find the legal actions at this position (should be 2), and choose the one that is not the reverse of the last action
				actions.append([action for action in self.get_legal_actions(next_pos) if action != Directions.REVERSE[actions[-1]]][0])
				next_pos = self.next_position(next_pos, actions[-1])
			successors.append((next_pos, actions))

		self.successors_lookup[position] = successors

		return successors

	def next_position(self, pos, action):
		action_offsets = {Directions.NORTH: (0, 1), Directions.SOUTH: (0, -1), Directions.EAST: (1, 0), Directions.WEST: (-1, 0)}

		# Get the offset for the action
		offset = action_offsets[action]
		return (pos[0] + offset[0], pos[1] + offset[1])

	def get_successors(self, node):
		return self.successors(node.position)

	def maze_distance(self, start, end):
		# Returns the distance between two positions along the maze, along with the actions to get there
		# Uses an A* search where the heuristic is the manhattan distance
		# Returns inf if the end position is not reachable from the start position

		# Check if the start and end positions are the same
		if start == end:
			return 0, []

		# Check if the start and end positions are in the lookup
		if (start, end) in self.maze_distance_lookup:
			return self.maze_distance_lookup[(start, end)]

		# A* search

		# Initialize the frontier with the start position
		frontier = queue.PriorityQueue()
		frontier.put((0, start))

		# Initialize the explored set
		explored = set()

		# Initialize the actions dictionary
		actions = {}

		# Initialize the cost dictionary
		costs = {}

		# Initialize the cost of the start position to be 0
		costs[start] = 0

		# Initialize the actions of the start position to be empty
		actions[start] = []

		result = None

		# While the frontier is not empty
		while not frontier.empty():
			# Get the next position from the frontier
			current_cost, current_pos = frontier.get()

			# Check if the current position is the end position
			if current_pos == end:
				# Return the cost and actions to get to the end position
				result = (current_cost, actions[current_pos])
				break

			# Add the current position to the explored set
			explored.add(current_pos)

			# Get the next reachable positions from the current position
			for next_action in self.get_legal_actions(current_pos):
				next_pos = self.next_position(current_pos, next_action)

				# Check if the next position is in the explored set
				if next_pos in explored:
					continue

				# Get the cost of the next position
				next_cost = current_cost + 1

				# Check if the next position is in the frontier
				if next_pos not in costs or next_cost < costs[next_pos]:
					# Update the cost of the next position
					costs[next_pos] = next_cost

					# Update the actions of the next position
					actions[next_pos] = actions[current_pos] + [next_action]

					# Add the next position to the frontier
					frontier.put((next_cost + util.manhattanDistance(next_pos, end), next_pos))

		# Check if the result is None
		if result is None:
			# Return inf
			result = (float('inf'), [])
		
		# Add the result to the lookup
		self.maze_distance_lookup[(start, end)] = result

		reversed_actions = [Directions.REVERSE[action] for action in reversed(result[1])]

		self.maze_distance_lookup[(end, start)] = (result[0], reversed_actions)

		return result

