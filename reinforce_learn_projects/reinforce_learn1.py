import random
import time

STATE_REWARDS = {
	1: [
		[1,2,3],[4,5,6],[7,8,9],
		[1,4,7],[2,5,8],[3,6,9],
		[1,5,9],[3,5,7],
	],
	0.8: [
		[1,2],[2,3],
		[4,5],[5,6],
		[7,8],[8,9],
		[1,4],[4,7],
		[2,5],[5,8],
		[3,6],[6,9],
		[1,5],[5,9],
		[3,5],[5,7],
	],
	0.5: [
		[5]
	]
}
STATE_WINS = STATE_REWARDS[1]
TURN = {True:'x', False:'o'}

class TicTacToeGame(object):
	def __init__(self):
		self.envstate = {x+1:"_" for x in range(9)}
		self.num_x = 5
		self.num_o = 4
		self.agent_x_turn = True
		self.empty_spaces = []
		self.empty_spaces = set(range(1,10))
		self.position = 5
		self.agent_x = []
		self.agent_o = []
		self.winner = "draw"

	def run(self):
		while len(self.empty_spaces) > 0 and self.winner == "draw":
			self.advance()

	def advance(self):
		if self.agent_x_turn:
			self.agent_x_action()
		else:
			self.agent_o_action()

		self.update_envstate()

	def agent_x_action(self):
		self.position = self.algorithm_rl(self.agent_x, self.agent_o)
		self.agent_x.append(self.position)
		if self.check_winning_status(self.agent_x):
			self.winner = 'x'

	def agent_o_action(self):
		self.position = self.algorithm_input()
		self.agent_o.append(self.position)
		if self.check_winning_status(self.agent_o):
			self.winner = 'o'

	def algorithm_rl(self, agent_x, agent_o):
		position = random.choice(list(self.empty_spaces))
		max_reward = 0
		for avail_pos in self.empty_spaces:
			avail_envstate_x = set(agent_x + [avail_pos])
			avail_envstate_o = set(agent_o + [avail_pos])
			for reward in STATE_REWARDS.keys():
				for envstate in STATE_REWARDS[reward]:
					if set(envstate).issubset(avail_envstate_x) or set(envstate).issubset(avail_envstate_o):
						if reward > max_reward:
							position = avail_pos
							max_reward = reward
							if max_reward == 1:
								return position

		return position

	def algorithm_input(self):
		position = 0
		while position not in self.empty_spaces:
			position_str = input("Enter a valid position: ")
			position = int(position_str)
		return position

	def algorithm_random(self):
		position = random.choice(list(self.empty_spaces))
		return position

	def check_winning_status(self, agent):
		tiar = False
		for envstate in STATE_WINS:
			if set(envstate).issubset(set(agent)):
				tiar = True
				break
		return tiar

	def update_envstate(self):
		self.envstate[self.position] = TURN[self.agent_x_turn]
		self.empty_spaces.remove(self.position)

		print("DEBUG: agent_x:", self.agent_x,"agent_o:", self.agent_o)
		print(" ", self.envstate[1], self.envstate[2], self.envstate[3])
		print(" ", self.envstate[4], self.envstate[5], self.envstate[6])
		print(" ", self.envstate[7], self.envstate[8], self.envstate[9])
		print("Winner:", self.winner)

		self.agent_x_turn  = not self.agent_x_turn

def main():
	t = TicTacToeGame()
	t.run()

if __name__ == "__main__":
	main()




