import random
import time
import copy
import argparse
import os

VALID_MOVES = (
    [1,2,4],   [6,5,4],   [13,8,4],   [11,7,4,],
    [4,5,6],   [13,9,6],  [1,3,6],    [15,10,6],
    [4,8,13],  [6,9,13],  [11,12,13], [15,14,13],
    [4,2,1],   [6,3,1],
    [7,4,2],   [9,5,2],
    [10,6,3],  [8,5,3],
    [14,9,5],  [12,8,5],
    [2,4,7],   [9,8,7],
    [3,5,8],   [10,9,8],
    [2,5,9],   [7,8,9],
    [3,6,10],  [8,9,10],
    [4,7,11],  [13,12,11],
    [5,8,12],  [14,13,12],
    [5,9,14],  [12,13,14],
    [6,10,15], [13,14,15],
)
BOARD = {
                   1: 1,
               2: 2,  3: 3,
           4: 4,   5: 5,  6: 6,
        7:7,  8: 8,  9: 9,  10:10,
    11:11,12:12,13:13,14:14,15:15
}

BOARD_FORMAT = "\n     %d\n    %d  %d\n   %d  %d  %d\n  %d  %d  %d %d\n %d %d %d %d %d"

class PegJumpPuzzle(object):
    def __init__(self, algorithm, remove_peg):
        # Init
        self.envstate = copy.deepcopy(BOARD)
        self.envstate_pegs = set(range(1,16))
        self.removed_pegs = set([])
        self.valid_actions = []
        self.action = None
        self.algorithms = {
            'r': self.algorithm_random,
            'i': self.algorithm_input,
            'l': self.algorithm_rl
        }
        self.algorithm = self.algorithms[algorithm]
        self.potential_envstate_pegs = copy.deepcopy(self.envstate_pegs)
        self.action_history = []
        
        # Setup
        self.envstate_pegs.remove(remove_peg)
        self.removed_pegs.add(remove_peg)
        self.envstate[remove_peg] = 0
        self.valid_actions = [x for x in VALID_MOVES if x[2] == remove_peg]

    def run(self):
        while len(self.valid_actions) > 0:
            self.advance()
        self.info()

    def advance(self):
        time.sleep(0.1)
        self.info()
        self.choose_action()
        if self.action not in self.valid_actions:
            print("ERROR: Invalid Move. Valid Moves Are:", self.valid_actions)
            return
        self.apply_action()
        self.update_valid_actions()
        self.update_pot_envstate_pegs()

    def choose_action(self):
        self.action = self.algorithm()
        print("INFO: Move Chosen", self.action)

    def algorithm_random(self):
        action = random.choice(self.valid_actions)
        return action

    def algorithm_input(self):
        choices_str = input("Enter Valid Move Choice: ")
        choice = int(choices_str)
        action = self.valid_actions[choice]
        return action

    def algorithm_rl(self):
        action = self.valid_actions[0]
        return action

    def apply_action(self):
        # Reaction Peg 1
        remove_peg = self.action[0]
        self.envstate_pegs.remove(remove_peg)
        self.removed_pegs.add(remove_peg)
        self.envstate[remove_peg] = 0
        self.potential_envstate_pegs = None

        # Add Peg 3
        add_peg = self.action[2]
        self.envstate_pegs.add(add_peg)
        self.removed_pegs.remove(add_peg)
        self.envstate[add_peg] = add_peg

        # Reaction Peg 2
        remove_peg = self.action[1]
        self.envstate_pegs.remove(remove_peg)
        self.removed_pegs.add(remove_peg)
        self.envstate[remove_peg] = 0

        self.action_history.append(self.action)

    def info(self):
        os.system("clear")
        print("INFO: envstate_pegs:", self.envstate_pegs,
            "removed_pegs:", self.removed_pegs,
        )
        print("envstate:", BOARD_FORMAT % tuple(self.envstate.values()))
        print("Potential Board Pegs" , self.potential_envstate_pegs)
        print("Valid Moves")
        for i, vm in enumerate(self.valid_actions):
            print(i,vm)
        
    def update_valid_actions(self):
        self.valid_actions = []
        test_actions = [x for x in VALID_MOVES if x[2] in self.removed_pegs]
        for tm in test_actions:
            if all([
                self.envstate[tm[0]] > 0, 
                self.envstate[tm[1]] > 0, 
                self.envstate[tm[2]] == 0
            ]):
                self.valid_actions.append(tm)

    def update_pot_envstate_pegs(self):
        self.potential_envstate_pegs = []
        for vm in self.valid_actions:
            print("DEBUG", vm[2])
            potential_envstate_peg = copy.deepcopy(self.envstate_pegs)
            potential_envstate_peg.remove(vm[0])
            potential_envstate_peg.add(vm[2])
            potential_envstate_peg.remove(vm[1])
            self.potential_envstate_pegs.append(potential_envstate_peg)

def main(algorithm_choice, remove_peg):
    algorithm_choices = 'ir'
    if algorithm_choice not in algorithm_choices:
        print("ERROR: Invalid Algotirhm Choice. Range = ir")
    else:
        opl = PegJumpPuzzle(algorithm_choice, remove_peg)
        opl.run()
        print("RESULTS: remove_peg", remove_peg, "action_history", opl.action_history)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='PegJumpPuzzle',
            description='Peg Jump Puzzle',
    )
    parser.add_argument("-a","--algorithm", default='r', help="i=input,r=random, l=reinforcement_learning")
    parser.add_argument("-p","--remove_peg", type=int, default=random.choice(range(1,16)),help='Range=1-15')
    args = parser.parse_args()
    main(args.algorithm, int(args.remove_peg))