import random
import time
import copy
import argparse
import os

TURN = {True: '1', False: '2'}

# Places
class Place(object):
    def __init__(self, label, position):
        self.label = label
        self.position = position
        self.entity = None

PLACES = {
    "a1": Place("a1", [1,1]),"a2": Place("a2", [1,2]),"a3": Place("a3", [1,3]),"a4": Place("a4", [1,4]),
    "a5": Place("a5", [1,5]),"a6": Place("a6", [1,6]),"a7": Place("a7", [1,7]),"a8": Place("a8", [1,8]),

    "b1": Place("b1", [2,1]),"b2": Place("b2", [2,2]),"b3": Place("b3", [2,3]),"b4": Place("b4", [2,4]),
    "b5": Place("b5", [2,5]),"b6": Place("b6", [2,6]),"b7": Place("b7", [2,7]),"b8": Place("b8", [2,8]),

    "c1": Place("c1", [3,1]),"c2": Place("c2", [3,2]),"c3": Place("c3", [3,3]),"c4": Place("c4", [3,4]),
    "c5": Place("c5", [3,5]),"c6": Place("c6", [3,6]),"c7": Place("c7", [3,7]),"c8": Place("c8", [3,8]),

    "d1": Place("d1", [4,1]),"d2": Place("d2", [4,2]),"d3": Place("d3", [4,3]),"d4": Place("d4", [4,4]),
    "d5": Place("d5", [4,5]),"d6": Place("d6", [4,6]),"d7": Place("d7", [4,7]),"d8": Place("d8", [4,8]),

    "e1": Place("e1", [5,1]),"e2": Place("e2", [5,2]),"e3": Place("e3", [5,3]),"e4": Place("e4", [5,4]),
    "e5": Place("e5", [5,5]),"e6": Place("e6", [5,6]),"e7": Place("e7", [5,7]),"e8": Place("e8", [5,8]),

    "f1": Place("f1", [6,1]),"f2": Place("f2", [6,2]),"f3": Place("f3", [6,3]),"f4": Place("f4", [6,4]),
    "f5": Place("f5", [6,5]),"f6": Place("f6", [6,6]),"f7": Place("f7", [6,7]),"f8": Place("f8", [6,8]),

    "g1": Place("g1", [7,1]),"g2": Place("g2", [7,2]),"g3": Place("g3", [7,3]),"g4": Place("g4", [7,4]),
    "g5": Place("g5", [7,5]),"g6": Place("g6", [7,6]),"g7": Place("g7", [7,7]),"g8": Place("g8", [7,8]),

    "h1": Place("h1", [8,1]),"h2": Place("h2", [8,2]),"h3": Place("h3", [8,3]),"h4": Place("h4", [8,4]),
    "h5": Place("h5", [8,5]),"h6": Place("h6", [8,6]),"h7": Place("h7", [8,7]),"h8": Place("h8", [8,8]),
}

# Environment containing Places

class Environment(object):
    def __init__(self):
        self.places = copy.deecopy(PLACES)

# Actions

ACTIONS = {
                    "nnw": [-1, 2],              "nne": [1, 2], 
    "wnw": [-2, 1], "nw":  [-1, 1], "n": [0, 1], "ne" : [1, 1], "ene": [2, 1]
                    "w":   [-1, 0],              "e" :  [1, 0],
    "wsw": [-2,-1], "sw":  [-1,-1], "n": [0,-1], "se" : [1,-1], "ese": [2,-1]
                    "ssw": [-1,-2],              "sse": [1,-2]
}

DIAG_ACTIONS = (ACTIONS["nw"], ACTIONS["ne"], ACTIONS["sw"], ACTIONS["se"])
STRAIGHT_ACTIONS = (ACTIONS["w"], ACTIONS["n"], ACTIONS["e"], ACTIONS["s"])
DIAG_STRAIGHT_ACTIONS = DIAG_ACTIONS + STRAIGHT_ACTIONS
EL_ACTIONS = (ACTIONS["ene"], ACTIONS["nne"], ACTIONS["nnw"], ACTIONS["wnw"],
    ACTIONS["ese"], ACTIONS["sse"], ACTIONS["ssw"], ACTIONS["wsw"],)

# Policies containing Actions

POLICIES ; {
    "King": {"capture_direction": DIAG_STRAIGHT_ACTIONS, "move_direction":DIAG_STRAIGHT_ACTIONS, "range": 1},
    "Queen": {"capture_direction": DIAG_STRAIGHT_ACTIONS, "move_direction": DIAG_STRAIGHT_ACTIONS, "range": 7},
    "Bishop": {"capture_direction": DIAG_ACTIONS, "move_direction": DIAG_ACTIONS, "range": 7},
    "Knight": {"capture_direction": EL_ACTIONS, "move_direction": EL_ACTIONS, "range": 1},
    "Rook": {"capture_direction": STRAIGHT_ACTIONS, "move_direction": STRAIGHT_ACTIONS, "range": 7},
    "Pawn": {"capture_direction": ("nw", "ne"), "move_direction": ("n",), "range": 1},
}

# Pieces containing Policies

class Entity(object):
    def __init__(self, name, type, label, place, policy):
        self.name = ""
        self.type = ""
        self.label = ""
        self.place = ""
        self.potential_places = []
        self.policy = policy



# Agents containing Pieces

class Agent(object):
    def __init__(self, name):
        self.name = name
        self.color = None
        self.pieces = []
        self.captured_pieces = []

# Main Module Class containing Environment and Agents

class ReinforceLearn(object):
    def __init__(self, algorithm):
        self.environment = Environment()
        self.agents = {
            "agent1": Agent("1"),
            "agent2": Agent("2"),
        }
        self.state = "init"
        self.agent1_turn = True

    def setup(self):
        self.setup_environment()
        self.setup_agents()

    def setup_environment(self):


    def run(self):
        while len(self.valid_actions) > 0:
            self.advance()
        self.info()

    def advance(self):
        time.sleep(0.1)
        self.print_info()
        self.choose_action()
        if self.action not in self.valid_actions:
            print("ERROR: Invalid Action. Valid Action Are:", self.valid_actions)
            return
        self.apply_action()
        self.update_valid_actions()
        self.update_potential_envstates()

    def print_info(self):
        pass

    def choose_action(self):
        self.action = self.algorithm()
        print("INFO: Action Chosen", self.action)

    def algorithm_random(self):
        action = random.choice(self.valid_actions)
        return action

    def algorithm_input(self):
        choices_str = input("Enter Valid Action Choice: ")
        choice = int(choices_str)
        action = self.valid_actions[choice]
        return action

    def algorithm_rl(self):
        action = self.valid_actions[0]
        return action

    def apply_action(self):
        pass
        
    def update_valid_actions(self):
        pass

    def update_potential_envstates(self):
        pass

def main(algorithm_choice):
    algorithm_choices = 'irl'
    if algorithm_choice not in algorithm_choices:
        print("ERROR: Invalid Algorithm Choice. Options: i=input,r=random,l=rl")
    else:
        opl = ReinforceLearn(algorithm_choice)
        opl.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='ChessGame',
            description='Chess Game',
    )
    parser.add_argument("-a","--algorithm", default='r', help="i=input,r=random,l=rl")
    args = parser.parse_args()
    main(args.algorithm)