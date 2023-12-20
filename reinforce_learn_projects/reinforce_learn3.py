import sys
import random
import time
import copy
import argparse
import os

# Actions
MOTION = {
                    "nnw": [-1, 2],              "nne": [1, 2], 
    "wnw": [-2, 1], "nw":  [-1, 1], "n": [0, 1], "ne" : [1, 1], "ene": [2, 1],   
                    "w":   [-1, 0],              "e" :  [1, 0],
    "wsw": [-2,-1], "sw":  [-1,-1], "s": [0,-1], "se" : [1,-1], "ese": [2,-1],
                    "ssw": [-1,-2],              "sse": [1,-2]
}
DIAG_MOTION = (MOTION["nw"], MOTION["ne"], MOTION["sw"], MOTION["se"])
STRAIGHT_MOTION = (MOTION["w"], MOTION["n"], MOTION["e"], MOTION["s"])
DIAG_STRAIGHT_MOTION = DIAG_MOTION + STRAIGHT_MOTION
EL_MOTION = (MOTION["ene"], MOTION["nne"], MOTION["nnw"], MOTION["wnw"],
    MOTION["ese"], MOTION["sse"], MOTION["ssw"], MOTION["wsw"],)

# Policies containing Actions
POLICIES = {
    "King":   {"cap": DIAG_STRAIGHT_MOTION,         "move": DIAG_STRAIGHT_MOTION,  "range": 1},
    "Queen":  {"cap": DIAG_STRAIGHT_MOTION,         "move": DIAG_STRAIGHT_MOTION,  "range": 7},
    "Bishop": {"cap": DIAG_MOTION,                  "move": DIAG_MOTION,           "range": 7},
    "Knight": {"cap": EL_MOTION,                    "move": EL_MOTION,             "range": 1},
    "Rook":   {"cap": STRAIGHT_MOTION,              "move": STRAIGHT_MOTION,       "range": 7},
    "wPawn":  {"cap": (MOTION["nw"], MOTION["ne"]), "move": (MOTION["n"],),        "range": 1},
    "bPawn":  {"cap": (MOTION["sw"], MOTION["se"]), "move": (MOTION["s"],),        "range": 1},
}

# Entities containing Policies
class Entity(object):
    def __init__(self, agent, name, _type, value, policy, label):
        self.agent = agent
        self.name = name
        self.type = _type
        self.val = value
        self.pol = policy
        self.lab = label
        self.loc = None
        self.intel = {
            "paths": set([]), 
            "targets": {},
            "threats": set([]), 
            "wards": set([]), 
            "support": set([]),
            "shield": set([]),
            "target_paths": set([])
        }
        self.color = name[0]
        self.moved = False
        
ENTITIES = {
    "baR": Entity(2, "baR","Rook",   5, POLICIES["Rook"  ],"r2"),
    "bbN": Entity(2, "bbN","Knight", 3, POLICIES["Knight"],"n2"),
    "bcB": Entity(2, "bcB","Bishop", 4, POLICIES["Bishop"],"b2"),
    "bdQ": Entity(2, "baR","Queen",  9, POLICIES["Queen" ],"Q2"),
    "beK": Entity(2, "beK","King",   99,POLICIES["King"  ],"K2"),
    "bfB": Entity(2, "bfB","Bishop", 4, POLICIES["Bishop"],"b2"),
    "bgN": Entity(2, "bgN","Knight", 3, POLICIES["Knight"],"n2"),
    "bhR": Entity(2, "bhR","Rook",   5, POLICIES["Rook"  ],"r2"),

    "baP": Entity(2, "baP","Pawn",   1, POLICIES["bPawn"], "p2"),
    "bbP": Entity(2, "bbP","Pawn",   1, POLICIES["bPawn"], "p2"),
    "bcP": Entity(2, "bcP","Pawn",   1, POLICIES["bPawn"], "p2"),
    "bdP": Entity(2, "bdP","Pawn",   1, POLICIES["bPawn"], "p2"),
    "beP": Entity(2, "beP","Pawn",   1, POLICIES["bPawn"], "p2"),
    "bfP": Entity(2, "bfP","Pawn",   1, POLICIES["bPawn"], "p2"),
    "bgP": Entity(2, "bgP","Pawn",   1, POLICIES["bPawn"], "p2"),
    "bhP": Entity(2, "bhP","Pawn",   1, POLICIES["bPawn"], "p2"),

    "waP": Entity(1, "waP","Pawn",   1, POLICIES["wPawn"], "p1"),
    "wbP": Entity(1, "wbP","Pawn",   1, POLICIES["wPawn"], "p1"),
    "wcP": Entity(1, "wcP","Pawn",   1, POLICIES["wPawn"], "p1"),
    "wdP": Entity(1, "wdP","Pawn",   1, POLICIES["wPawn"], "p1"),
    "weP": Entity(1, "weP","Pawn",   1, POLICIES["wPawn"], "p1"),
    "wfP": Entity(1, "wfP","Pawn",   1, POLICIES["wPawn"], "p1"),
    "wgP": Entity(1, "wgP","Pawn",   1, POLICIES["wPawn"], "p1"),
    "whP": Entity(1, "whP","Pawn",   1, POLICIES["wPawn"], "p1"),

    "waR": Entity(1, "waR","Rook",   5, POLICIES["Rook"  ], "r1"),
    "wbN": Entity(1, "wbN","Knight", 3, POLICIES["Knight"], "n1"),
    "wcB": Entity(1, "wcB","Bishop", 4, POLICIES["Bishop"], "b1"),
    "wdQ": Entity(1, "wdQ","Queen",  9, POLICIES["Queen" ], "Q1"),
    "weK": Entity(1, "weK","King",   99,POLICIES["King"  ], "K1"),
    "wfB": Entity(1, "wfB","Bishop", 4, POLICIES["Bishop"], "b1"),
    "wgN": Entity(1, "wgN","Knight", 3, POLICIES["Knight"], "n1"),
    "whR": Entity(1, "whR","Rook",   5, POLICIES["Rook"  ], "r1"),
}
EXTRA_QUEENS2 = {
    "biQ": Entity(2, "biR","Queen",  9, POLICIES["Queen" ], "q2"),
    "bjQ": Entity(2, "bjR","Queen",  9, POLICIES["Queen" ], "q2"),
    "bkQ": Entity(2, "bkR","Queen",  9, POLICIES["Queen" ], "q2"),
    "blQ": Entity(2, "blR","Queen",  9, POLICIES["Queen" ], "q2"),
    "bmQ": Entity(2, "bmR","Queen",  9, POLICIES["Queen" ], "q2"),
    "boQ": Entity(2, "bnR","Queen",  9, POLICIES["Queen" ], "q2"),
    "bpQ": Entity(2, "boR","Queen",  9, POLICIES["Queen" ], "q2"),
    "bqQ": Entity(2, "bpR","Queen",  9, POLICIES["Queen" ], "q2"),
}
EXTRA_QUEENS2_NAMES = list(EXTRA_QUEENS2.keys())
EXTRA_QUEENS1 = {
    "wiQ": Entity(1, "wiQ","Queen",  9, POLICIES["Queen" ], "q1"),
    "wjQ": Entity(1, "wjQ","Queen",  9, POLICIES["Queen" ], "q1"),
    "wkQ": Entity(1, "wkQ","Queen",  9, POLICIES["Queen" ], "q1"),
    "wlQ": Entity(1, "wlQ","Queen",  9, POLICIES["Queen" ], "q1"),
    "wmQ": Entity(1, "wmQ","Queen",  9, POLICIES["Queen" ], "q1"),
    "wnQ": Entity(1, "wnQ","Queen",  9, POLICIES["Queen" ], "q1"),
    "woQ": Entity(1, "woQ","Queen",  9, POLICIES["Queen" ], "q1"),
    "wpQ": Entity(1, "wpQ","Queen",  9, POLICIES["Queen" ], "q1"),
}
EXTRA_QUEENS1_NAMES = list(EXTRA_QUEENS1.keys())
PRINT_FMT_ENV = "%s %s %s %s %s %s %s %s"

# Locations containing entities
LOCATIONS_ORIG = {

    "a8": {"pos":[1,8],"ent": "baR", "path_ent": set([])},
    "b8": {"pos":[2,8],"ent": "bbN", "path_ent": set([])},
    "c8": {"pos":[3,8],"ent": "bcB", "path_ent": set([])},
    "d8": {"pos":[4,8],"ent": "bdQ", "path_ent": set([])},
    "e8": {"pos":[5,8],"ent": "beK", "path_ent": set([])},
    "f8": {"pos":[6,8],"ent": "bfB", "path_ent": set([])},
    "g8": {"pos":[7,8],"ent": "bgN", "path_ent": set([])},
    "h8": {"pos":[8,8],"ent": "bhR", "path_ent": set([])},

    "a7": {"pos":[1,7],"ent": "baP", "path_ent": set([])},
    "b7": {"pos":[2,7],"ent": "bbP", "path_ent": set([])},
    "c7": {"pos":[3,7],"ent": "bcP", "path_ent": set([])},
    "d7": {"pos":[4,7],"ent": "bdP", "path_ent": set([])},
    "e7": {"pos":[5,7],"ent": "beP", "path_ent": set([])},
    "f7": {"pos":[6,7],"ent": "bfP", "path_ent": set([])},
    "g7": {"pos":[7,7],"ent": "bgP", "path_ent": set([])},
    "h7": {"pos":[8,7],"ent": "bhP", "path_ent": set([])},

    "a6": {"pos":[1,6],"ent": None, "path_ent": set([])},
    "b6": {"pos":[2,6],"ent": None, "path_ent": set([])},
    "c6": {"pos":[3,6],"ent": None, "path_ent": set([])},
    "d6": {"pos":[4,6],"ent": None, "path_ent": set([])},
    "e6": {"pos":[5,6],"ent": None, "path_ent": set([])},
    "f6": {"pos":[6,6],"ent": None, "path_ent": set([])},
    "g6": {"pos":[7,6],"ent": None, "path_ent": set([])},
    "h6": {"pos":[8,6],"ent": None, "path_ent": set([])},

    "a5": {"pos":[1,5],"ent": None, "path_ent": set([])},
    "b5": {"pos":[2,5],"ent": None, "path_ent": set([])},
    "c5": {"pos":[3,5],"ent": None, "path_ent": set([])},
    "d5": {"pos":[4,5],"ent": None, "path_ent": set([])},
    "e5": {"pos":[5,5],"ent": None, "path_ent": set([])},
    "f5": {"pos":[6,5],"ent": None, "path_ent": set([])},
    "g5": {"pos":[7,5],"ent": None, "path_ent": set([])},
    "h5": {"pos":[8,5],"ent": None, "path_ent": set([])},

    "a4": {"pos":[1,4],"ent": None, "path_ent": set([])},
    "b4": {"pos":[2,4],"ent": None, "path_ent": set([])},
    "c4": {"pos":[3,4],"ent": None, "path_ent": set([])},
    "d4": {"pos":[4,4],"ent": None, "path_ent": set([])},
    "e4": {"pos":[5,4],"ent": None, "path_ent": set([])},
    "f4": {"pos":[6,4],"ent": None, "path_ent": set([])},
    "g4": {"pos":[7,4],"ent": None, "path_ent": set([])},
    "h4": {"pos":[8,4],"ent": None, "path_ent": set([])},

    "a3": {"pos":[1,3],"ent": None, "path_ent": set([])},
    "b3": {"pos":[2,3],"ent": None, "path_ent": set([])},
    "c3": {"pos":[3,3],"ent": None, "path_ent": set([])},
    "d3": {"pos":[4,3],"ent": None, "path_ent": set([])},
    "e3": {"pos":[5,3],"ent": None, "path_ent": set([])},
    "f3": {"pos":[6,3],"ent": None, "path_ent": set([])},
    "g3": {"pos":[7,3],"ent": None, "path_ent": set([])},
    "h3": {"pos":[8,3],"ent": None, "path_ent": set([])},

    "a2": {"pos":[1,2],"ent": "waP", "path_ent": set([])},
    "b2": {"pos":[2,2],"ent": "wbP", "path_ent": set([])},
    "c2": {"pos":[3,2],"ent": "wcP", "path_ent": set([])},
    "d2": {"pos":[4,2],"ent": "wdP", "path_ent": set([])},
    "e2": {"pos":[5,2],"ent": "weP", "path_ent": set([])},
    "f2": {"pos":[6,2],"ent": "wfP", "path_ent": set([])},
    "g2": {"pos":[7,2],"ent": "wgP", "path_ent": set([])},
    "h2": {"pos":[8,2],"ent": "whP", "path_ent": set([])},

    "a1": {"pos":[1,1],"ent": "waR", "path_ent": set([])},
    "b1": {"pos":[2,1],"ent": "wbN", "path_ent": set([])},
    "c1": {"pos":[3,1],"ent": "wcB", "path_ent": set([])},
    "d1": {"pos":[4,1],"ent": "wdQ", "path_ent": set([])},
    "e1": {"pos":[5,1],"ent": "weK", "path_ent": set([])},
    "f1": {"pos":[6,1],"ent": "wfB", "path_ent": set([])},
    "g1": {"pos":[7,1],"ent": "wgN", "path_ent": set([])},
    "h1": {"pos":[8,1],"ent": "whR", "path_ent": set([])},
}

LOCATIONS_NO_PAWNS = {

    "a8": {"pos":[1,8],"ent": "baR", "path_ent": set([])},
    "b8": {"pos":[2,8],"ent": "bbN", "path_ent": set([])},
    "c8": {"pos":[3,8],"ent": "bcB", "path_ent": set([])},
    "d8": {"pos":[4,8],"ent": "bdQ", "path_ent": set([])},
    "e8": {"pos":[5,8],"ent": "beK", "path_ent": set([])},
    "f8": {"pos":[6,8],"ent": "bfB", "path_ent": set([])},
    "g8": {"pos":[7,8],"ent": "bgN", "path_ent": set([])},
    "h8": {"pos":[8,8],"ent": "bhR", "path_ent": set([])},

    "a7": {"pos":[1,7],"ent": None, "path_ent": set([])},
    "b7": {"pos":[2,7],"ent": None, "path_ent": set([])},
    "c7": {"pos":[3,7],"ent": None, "path_ent": set([])},
    "d7": {"pos":[4,7],"ent": None, "path_ent": set([])},
    "e7": {"pos":[5,7],"ent": None, "path_ent": set([])},
    "f7": {"pos":[6,7],"ent": None, "path_ent": set([])},
    "g7": {"pos":[7,7],"ent": None, "path_ent": set([])},
    "h7": {"pos":[8,7],"ent": None, "path_ent": set([])},

    "a6": {"pos":[1,6],"ent": None, "path_ent": set([])},
    "b6": {"pos":[2,6],"ent": None, "path_ent": set([])},
    "c6": {"pos":[3,6],"ent": None, "path_ent": set([])},
    "d6": {"pos":[4,6],"ent": None, "path_ent": set([])},
    "e6": {"pos":[5,6],"ent": None, "path_ent": set([])},
    "f6": {"pos":[6,6],"ent": None, "path_ent": set([])},
    "g6": {"pos":[7,6],"ent": None, "path_ent": set([])},
    "h6": {"pos":[8,6],"ent": None, "path_ent": set([])},

    "a5": {"pos":[1,5],"ent": None, "path_ent": set([])},
    "b5": {"pos":[2,5],"ent": None, "path_ent": set([])},
    "c5": {"pos":[3,5],"ent": None, "path_ent": set([])},
    "d5": {"pos":[4,5],"ent": None, "path_ent": set([])},
    "e5": {"pos":[5,5],"ent": None, "path_ent": set([])},
    "f5": {"pos":[6,5],"ent": None, "path_ent": set([])},
    "g5": {"pos":[7,5],"ent": None, "path_ent": set([])},
    "h5": {"pos":[8,5],"ent": None, "path_ent": set([])},

    "a4": {"pos":[1,4],"ent": None, "path_ent": set([])},
    "b4": {"pos":[2,4],"ent": None, "path_ent": set([])},
    "c4": {"pos":[3,4],"ent": None, "path_ent": set([])},
    "d4": {"pos":[4,4],"ent": None, "path_ent": set([])},
    "e4": {"pos":[5,4],"ent": None, "path_ent": set([])},
    "f4": {"pos":[6,4],"ent": None, "path_ent": set([])},
    "g4": {"pos":[7,4],"ent": None, "path_ent": set([])},
    "h4": {"pos":[8,4],"ent": None, "path_ent": set([])},

    "a3": {"pos":[1,3],"ent": None, "path_ent": set([])},
    "b3": {"pos":[2,3],"ent": None, "path_ent": set([])},
    "c3": {"pos":[3,3],"ent": None, "path_ent": set([])},
    "d3": {"pos":[4,3],"ent": None, "path_ent": set([])},
    "e3": {"pos":[5,3],"ent": None, "path_ent": set([])},
    "f3": {"pos":[6,3],"ent": None, "path_ent": set([])},
    "g3": {"pos":[7,3],"ent": None, "path_ent": set([])},
    "h3": {"pos":[8,3],"ent": None, "path_ent": set([])},

    "a2": {"pos":[1,2],"ent": None, "path_ent": set([])},
    "b2": {"pos":[2,2],"ent": None, "path_ent": set([])},
    "c2": {"pos":[3,2],"ent": None, "path_ent": set([])},
    "d2": {"pos":[4,2],"ent": None, "path_ent": set([])},
    "e2": {"pos":[5,2],"ent": None, "path_ent": set([])},
    "f2": {"pos":[6,2],"ent": None, "path_ent": set([])},
    "g2": {"pos":[7,2],"ent": None, "path_ent": set([])},
    "h2": {"pos":[8,2],"ent": None, "path_ent": set([])},

    "a1": {"pos":[1,1],"ent": "waR", "path_ent": set([])},
    "b1": {"pos":[2,1],"ent": "wbN", "path_ent": set([])},
    "c1": {"pos":[3,1],"ent": "wcB", "path_ent": set([])},
    "d1": {"pos":[4,1],"ent": "wdQ", "path_ent": set([])},
    "e1": {"pos":[5,1],"ent": "weK", "path_ent": set([])},
    "f1": {"pos":[6,1],"ent": "wfB", "path_ent": set([])},
    "g1": {"pos":[7,1],"ent": "wgN", "path_ent": set([])},
    "h1": {"pos":[8,1],"ent": "whR", "path_ent": set([])},
}

LOCATIONS_BLACKROOK = {

    "a8": {"pos":[1,8],"ent": None, "path_ent": set([])},
    "b8": {"pos":[2,8],"ent": None, "path_ent": set([])},
    "c8": {"pos":[3,8],"ent": None, "path_ent": set([])},
    "d8": {"pos":[4,8],"ent": None, "path_ent": set([])},
    "e8": {"pos":[5,8],"ent": None, "path_ent": set([])},
    "f8": {"pos":[6,8],"ent": None, "path_ent": set([])},
    "g8": {"pos":[7,8],"ent": None, "path_ent": set([])},
    "h8": {"pos":[8,8],"ent": None, "path_ent": set([])},

    "a7": {"pos":[1,7],"ent": None, "path_ent": set([])},
    "b7": {"pos":[2,7],"ent": None, "path_ent": set([])},
    "c7": {"pos":[3,7],"ent": None, "path_ent": set([])},
    "d7": {"pos":[4,7],"ent": None, "path_ent": set([])},
    "e7": {"pos":[5,7],"ent": None, "path_ent": set([])},
    "f7": {"pos":[6,7],"ent": None, "path_ent": set([])},
    "g7": {"pos":[7,7],"ent": None, "path_ent": set([])},
    "h7": {"pos":[8,7],"ent": None, "path_ent": set([])},

    "a6": {"pos":[1,6],"ent": None, "path_ent": set([])},
    "b6": {"pos":[2,6],"ent": None, "path_ent": set([])},
    "c6": {"pos":[3,6],"ent": None, "path_ent": set([])},
    "d6": {"pos":[4,6],"ent": None, "path_ent": set([])},
    "e6": {"pos":[5,6],"ent": None, "path_ent": set([])},
    "f6": {"pos":[6,6],"ent": None, "path_ent": set([])},
    "g6": {"pos":[7,6],"ent": None, "path_ent": set([])},
    "h6": {"pos":[8,6],"ent": None, "path_ent": set([])},

    "a5": {"pos":[1,5],"ent": None, "path_ent": set([])},
    "b5": {"pos":[2,5],"ent": None, "path_ent": set([])},
    "c5": {"pos":[3,5],"ent": None, "path_ent": set([])},
    "d5": {"pos":[4,5],"ent": None, "path_ent": set([])},
    "e5": {"pos":[5,5],"ent": None, "path_ent": set([])},
    "f5": {"pos":[6,5],"ent": None, "path_ent": set([])},
    "g5": {"pos":[7,5],"ent": None, "path_ent": set([])},
    "h5": {"pos":[8,5],"ent": None, "path_ent": set([])},

    "a4": {"pos":[1,4],"ent": None, "path_ent": set([])},
    "b4": {"pos":[2,4],"ent": None, "path_ent": set([])},
    "c4": {"pos":[3,4],"ent": None, "path_ent": set([])},
    "d4": {"pos":[4,4],"ent": None, "path_ent": set([])},
    "e4": {"pos":[5,4],"ent": None, "path_ent": set([])},
    "f4": {"pos":[6,4],"ent": None, "path_ent": set([])},
    "g4": {"pos":[7,4],"ent": None, "path_ent": set([])},
    "h4": {"pos":[8,4],"ent": None, "path_ent": set([])},

    "a3": {"pos":[1,3],"ent": None, "path_ent": set([])},
    "b3": {"pos":[2,3],"ent": None, "path_ent": set([])},
    "c3": {"pos":[3,3],"ent": None, "path_ent": set([])},
    "d3": {"pos":[4,3],"ent": "beK", "path_ent": set([])},
    "e3": {"pos":[5,3],"ent": "bhP", "path_ent": set([])},
    "f3": {"pos":[6,3],"ent": None, "path_ent": set([])},
    "g3": {"pos":[7,3],"ent": None, "path_ent": set([])},
    "h3": {"pos":[8,3],"ent": None, "path_ent": set([])},

    "a2": {"pos":[1,2],"ent": "baR", "path_ent": set([])},
    "b2": {"pos":[2,2],"ent": None, "path_ent": set([])},
    "c2": {"pos":[3,2],"ent": None, "path_ent": set([])},
    "d2": {"pos":[4,2],"ent": None, "path_ent": set([])},
    "e2": {"pos":[5,2],"ent": None, "path_ent": set([])},
    "f2": {"pos":[6,2],"ent": None, "path_ent": set([])},
    "g2": {"pos":[7,2],"ent": None, "path_ent": set([])},
    "h2": {"pos":[8,2],"ent": None, "path_ent": set([])},

    "a1": {"pos":[1,1],"ent": None, "path_ent": set([])},
    "b1": {"pos":[2,1],"ent": None, "path_ent": set([])},
    "c1": {"pos":[3,1],"ent": None, "path_ent": set([])},
    "d1": {"pos":[4,1],"ent": None, "path_ent": set([])},
    "e1": {"pos":[5,1],"ent": "weK", "path_ent": set([])},
    "f1": {"pos":[6,1],"ent": None, "path_ent": set([])},
    "g1": {"pos":[7,1],"ent": None, "path_ent": set([])},
    "h1": {"pos":[8,1],"ent": None, "path_ent": set([])},
}

LOCATIONS =  {
    "orig": LOCATIONS_ORIG,
    "nopawn": LOCATIONS_NO_PAWNS,
    "min": LOCATIONS_BLACKROOK
}

RANGE_1_8 = range(1,9)
RANGE_8_1 = range(8,0,-1)
LETTERS_A_H = 'abcdefgh'
LOCATIONS_ORDER = [[letter + str(num) for letter in LETTERS_A_H ] for num in RANGE_8_1]
RANGE_1_8 = range(1,9)
GRID = []

PROMOTION_LOC = ["a1","b1","c1","d1","e1","f1","g1","h1","a8","b8","c8","d8","e8","f8","g8","h8"]
for x in RANGE_1_8:
    for y in RANGE_1_8:
        GRID.append([x, y])

# Function
def get_loc(pos):

    letter = LETTERS_A_H[pos[0]-1]
    num = str(pos[1])
    return letter + num


# Main Module Class containing Environment and Agents
class ReinforceLearn3(object):
    def __init__(self, algorithm_choices, debug, locations):
        self.state = "init"
        self.loc = copy.deepcopy(LOCATIONS[locations])
        self.loc_list = self.loc.keys()
        self.ent = copy.deepcopy(ENTITIES)
        self.ent_list = self.ent.keys()
        self.agent_turn = 2        
        self.algirithms = {
            "r1": self.algorithm_random,
            "r2": self.algorithm_random_prompt,
            'i':  self.algorithm_input,
            'rl': self.algorithm_reinforce_learn,
            "l1": self.algorithm_logic1
        }
        choice1, choice2 = algorithm_choices.split(",")
        self.agents = {
            1: {"algorithm": self.algirithms[choice1]},
            2: {"algorithm": self.algirithms[choice2]} 
        }
        self.action = ["i9","i9"]
        self.valid_actions = [['e1','e1'],]
        self.cap = []
        self.debug = debug
        self.king_check = False
        self.shield_loc = set([])
        self.game_ends = False

    def setup(self):
        for key in self.loc.keys():
            ent_name = self.loc[key]["ent"]
            if ent_name in self.ent_list:
                self.ent[ent_name].loc = key

    def run(self):
        while not self.game_ends:
            self.advance()
    def advance(self):
        self.agent_turn = 3 - self.agent_turn
        self.reset_intel()
        self.update_paths()
        self.info()
        if self.game_ends:
            return
        while not self.choose_action():
            print("ERROR: Invalid Action. Valid Action are below:")
            for i, action in enumerate(self.valid_actions):
                print(i, action)
            continue
        self.apply_action()

    def reset_intel(self):
        self.shield_loc = set([])
        for loc_name in self.loc_list:
            self.loc[loc_name]["path_ent"] = set([])
        for ent_name in self.ent_list:
            self.ent[ent_name].intel["threats"] = set([])
            self.ent[ent_name].intel["support"] = set([])
            self.ent[ent_name].intel["shield"] = set([])

    def update_paths(self):
        self.valid_actions = []
        for ent_name in self.ent_list:
            if self.ent[ent_name].loc:
                self.update_move_path(self.ent[ent_name])
                self.update_capture_path(self.ent[ent_name])

        self.evaluate_king_state()


    def update_move_path(self, ent):
        ent.intel["paths"] = set([])
        pos = self.loc[ent.loc]["pos"]
        loc = get_loc(pos)

        # Move Paths
        for move in ent.pol["move"]:
            rng = ent.pol["range"]
            # Adjust Pawn's initial move path
            if ent.type == "Pawn" and not ent.moved:
                rng += 1
            for r in range(1,rng+1):
                dest_pos = [ pos[0] + r*move[0], pos[1] + r*move[1]]
                if dest_pos in GRID:
                    dest_loc = get_loc(dest_pos)
                    dest_ent_name = self.loc[dest_loc]["ent"]
                    if not dest_ent_name:
                        ent.intel["paths"].add(dest_loc)
                        self.loc[dest_loc]["path_ent"].add(ent.name)
                        if ent.agent == self.agent_turn:
                            self.valid_actions.append([loc, dest_loc])
                    else:
                        break
                else:
                    break

    def update_capture_path(self, ent):
        # Init
        pos = self.loc[ent.loc]["pos"]
        loc = get_loc(pos)

        # Capture Paths
        ent.intel["targets"] = {}
        ent.intel["wards"] = set([])

        if ent.type == "Pawn":
            ent.intel["target_paths"] = set([])

        entity_shield = [None, None]
        for cap in ent.pol["cap"]:
            entity_shield = [None, None]
            for r in range(1, ent.pol["range"]+1):
                dest_pos = [ pos[0] + r*cap[0], pos[1] + r*cap[1]]
                if dest_pos in GRID:
                    dest_loc = get_loc(dest_pos)
                    dest_ent_name = self.loc[dest_loc]["ent"]
                    if dest_ent_name:
                        if self.ent[dest_ent_name].agent != ent.agent:

                            # Update King Shielded by Target
                            if entity_shield[0]:
                                self.ent[dest_ent_name].intel["shield"].add(entity_shield[1])
                                self.ent[entity_shield[0]].intel["wards"].add(dest_ent_name)
                                ent.intel["targets"][entity_shield[1]]["l2targets"] = dest_loc
                                self.shield_loc.add(entity_shield[1])
                                break

                            # Update Targeted Entity Threats
                            entity_shield = [dest_ent_name, dest_loc]
                            ent.intel["targets"][dest_loc] = {
                                    "ent_name": dest_ent_name, 
                                    "l2paths": set([]), 
                                    "l2targets": None
                            }
                            self.ent[dest_ent_name].intel["threats"].add(dest_loc)
                            if ent.agent == self.agent_turn:
                                self.valid_actions.append([loc, dest_loc])

                        else:
                            ent.intel["wards"].add(dest_loc)
                            # Update Targetted Entity Threats
                            self.ent[dest_ent_name].intel["support"].add(dest_loc)
                            break
                    else:
                        if entity_shield[0]:
                            ent.intel["targets"][entity_shield[1]]["l2paths"].add(dest_loc)
                        if ent.type == "Pawn":
                            ent.intel["target_paths"].add(dest_loc)
                else:
                    break
        

    def evaluate_king_state(self):

        # Remove Protecting Entity Locations from Valid Moves
        for action in self.valid_actions:
            if action[0] in self.shield_loc:
                self.valid_actions.remove(action)

        self.king_check = False
        if self.agent_turn == 1:
            king_name = "weK"
        else:
            king_name = "beK"

        # Remove King Paths opposite and inline with Threats
        for ent_name in self.ent_list:
            for target in self.ent[ent_name].intel["targets"].keys():
                for path in self.ent[ent_name].intel["targets"][target]["l2paths"]:
                    if path in self.ent[king_name].intel["paths"]:
                        self.ent[king_name].intel["paths"].remove(path)

        # Remove King Targets in Opponent Path
        king_targets = copy.deepcopy(list(self.ent[king_name].intel["targets"].keys()))

        for target in king_targets:
            for ent_name in self.ent_list:
                if ent_name != king_name and target in self.ent[ent_name].intel["wards"]: 
                    self.ent[king_name].intel["targets"].pop(target)
                    break    

        # Remove King Paths in Opponent Path
        king_paths = copy.deepcopy(self.ent[king_name].intel["paths"])
        for path in king_paths:
            for ent_name in self.ent_list:
                if ent_name != king_name and self.ent[ent_name].agent != self.ent[king_name].agent and \
                        (path in self.ent[ent_name].intel["paths"] or path in self.ent[ent_name].intel["target_paths"]):
                    self.ent[king_name].intel["paths"].remove(path)
                    break

        # Remove Targets, Paths from Valid Actions
        valid_loc = list(self.ent[king_name].intel["targets"].keys()) + list(self.ent[king_name].intel["paths"])
        valid_actions = copy.deepcopy(self.valid_actions)

        for action in valid_actions:
            src_loc, dest_loc = action
            if src_loc == self.ent[king_name].loc and dest_loc not in valid_loc:
                self.valid_actions.remove(action)

        # Determine King Check
        if len(self.ent[king_name].intel["threats"]) > 0:
            self.valid_actions = []
            for path_loc in list(self.ent[king_name].intel["targets"]) + list(self.ent[king_name].intel["paths"]):
                self.valid_actions.append([self.ent[king_name].loc, path_loc])

            self.king_check = True
            print("INFO: Check !. Threats", self.ent[king_name].intel["threats"] )

        # Determine Draw or Check Mate
        if len(self.valid_actions) == 0:
            if self.king_check:
                print("INFO: CheckMate !!!")
            else:
                print("INFO: Draw !!!")
            self.game_ends = True

    def info(self):
        time.sleep(0.1)
        #if not self.debug:
        os.system("cls")

        for num in RANGE_1_8:
            labels = []
            for x in LOCATIONS_ORDER[num-1]:
                label = ". "
                if self.loc[x]["ent"]:
                    label = self.ent[self.loc[x]["ent"]].lab
                labels.append(label)
            locations_print = tuple(labels)
            print(PRINT_FMT_ENV % locations_print, 9-num)

        print(" a  b  c  d  e  f  g  h")
        print("Captured Entities:", self.cap)
        print("Agent Turn:", self.agent_turn)

        if self.debug:
            # Print Intel
            print("DEBUG: ent, loc, paths, wards, targets, threats, support, shield")
            for ent_name in self.ent_list:
                if self.ent[ent_name].loc:
                    print(
                        "   ", 
                        ent_name, 
                        self.ent[ent_name].loc, 
                        self.ent[ent_name].intel,
                    )
            # Print Valid Actions:
            print( "valid_actions", [(i, x) for i,x in enumerate(self.valid_actions)])

    def choose_action(self):
        self.action = self.agents[self.agent_turn]["algorithm"]()
        if self.action[0] == "x":
            sys.exit()
        print("INFO: Chosen Action", self.action)
        valid_action = self.action in self.valid_actions
        return valid_action

    def apply_action(self):
        # Init
        src_loc, dest_loc = self.action
        src_ent_name = self.loc[src_loc]["ent"]
        dest_ent_name = self.loc[dest_loc]["ent"]

        # Move Dest Location entity to Agent Confinement
        if dest_ent_name:
            self.loc[dest_loc]["ent"] = None
            self.ent[dest_ent_name].loc = None
            self.cap.append(dest_ent_name)

        # Remove Source Location Entity from Source Location
        self.loc[src_loc]["ent"] = None

        # Add Source Location Entity to Destination Location
        self.loc[dest_loc]["ent"] = src_ent_name
        self.ent[src_ent_name].loc = dest_loc
        self.ent[src_ent_name].moved = True

        #Check for Promotion
        if self.ent[src_ent_name].type == "Pawn":

            if dest_loc.find("1") > -1:
                ent_name = EXTRA_QUEENS2_NAMES[0]
                self.ent[ent_name] = EXTRA_QUEENS2.pop(ent_name)

                self.ent[ent_name].loc = dest_loc
                self.loc[dest_loc]["ent"] = ent_name

                print("INFO: Promotion!")
            
            elif dest_loc.find("8") > -1:
                ent_name = EXTRA_QUEENS1_NAMES[0]
                self.ent[ent_name] = EXTRA_QUEENS1.pop(ent_name)

                self.ent[ent_name].loc = dest_loc
                self.loc[dest_loc]["ent"] = ent_name

                print("INFO: Promotion!")
    
        print("INFO: Applied Action", self.action, )

    def algorithm_random(self):
        time.sleep(0.1)
        input("Enter for Random Choice")
        action = random.choice(self.valid_actions)
        return action

    def algorithm_random_prompt(self):
        time.sleep(0.1)
        action = random.choice(self.valid_actions)
        return action

    def algorithm_input(self):
        choice_str = input("Enter Valid Action Choice (x,=exit): ")
        if choice_str == "":
            action = random.choice(self.valid_actions)
        elif choice_str.find(",") > -1:
            action = choice_str.split(",")
        else:
            choice = int(choice_str)
            action = self.valid_actions[choice]
        return action

    def algorithm_logic1(self):
        max_value = 0
        action = random.choice(self.valid_actions)
        for valid_action in self.valid_actions:
            if self.loc[valid_action[1]]["ent"]:
                ent_name = self.loc[valid_action[1]]["ent"]
                if self.ent[ent_name].val > max_value:
                    max_value = self.ent[ent_name].val
                    action = valid_action
        return action

    def algorithm_reinforce_learn(self):
        action = random.choice(self.valid_actions)
        return action

def main(algorithm_choices, debug, locations):
    rl3 = ReinforceLearn3(algorithm_choices, debug, locations)
    rl3.setup()
    rl3.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
            prog='ReinforceLearn3',
            description='Reinforcement Learning Project 3',

    )
    parser.add_argument("-a","--algorithms", default="r2,i", help="r1,r2,i,fl,l1")
    parser.add_argument("-d","--debug", action='store_true')
    parser.add_argument("-l","--locations", default="orig")
    args = parser.parse_args()
    main(args.algorithms, args.debug, args.locations)
