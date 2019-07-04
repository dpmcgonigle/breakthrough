# -*- coding: utf-8 -*-
####################################################################################
#	minimax.py
#
#	Created on Mon Mar 18 10:49:03 2019
#
#	This is the class that holds the agent program for  minimax search
#
#	@authors: Juefei Yuan and Daniel McGonigle
####################################################################################

import numpy as np
from model import *


class MinimaxAgent:
    #
    #	constructor args: 8 x 8 integer matrix representing board (1 for black - player 1 - and 2 for white)
    #		turn - 1 for player 1 (black), 2 for player 2
    #		depth represents depth of search
    #		function represents heuristic to use
    #
    def __init__(self, boardmatrix, turn, depth, function, type=0):
        self.boardmatrix = boardmatrix
        self.turn = turn
        self.maxdepth = depth
        self.function = function
        self.type = type
        self.nodes = 0
        self.piece_num = 0

    def max_value(self, state, depth):
        if depth == self.maxdepth or state.isgoalstate() != 0:
            #print("utility", state.utility(self.turn))
            return state.utility(self.turn)
        # 	defined in model.py:MINNUM = -float("inf")
        v = MINNUM
        for action in state.available_actions():
            # print(state.transfer(action).getMatrix())
            v = max(v, self.min_value(state.transfer(action), depth + 1))
            self.nodes += 1
        return v

    def min_value(self, state, depth):
        if depth == self.maxdepth or state.isgoalstate() != 0:
            #print("utility", state.utility(self.turn))
            return state.utility(self.turn)
        # 	defined in model.py:MAXNUM = float("inf")
        v = MAXNUM
        for action in state.available_actions():
            v = min(v, self.max_value(state.transfer(action), depth + 1))
            self.nodes += 1

        return v

    #
    #	method that implements the decision of the agent program
    #		returns the board state, number of nodes expanded, and pieces left
    #
    def minimax_decision(self):
        final_action = None
        if self.type == 0:
            initialstate = State(boardmatrix=self.boardmatrix, turn=self.turn, function=self.function)
        else:
            initialstate = State(boardmatrix=self.boardmatrix, turn=self.turn, function=self.function, height=3, width=10)
        # 	defined in model.py:MINNUM = -float("inf")
        v = MINNUM
        for action in initialstate.available_actions():
            self.nodes += 1
            new_state = initialstate.transfer(action)
            if new_state.isgoalstate():
                final_action = action
                break
            minresult = self.min_value(new_state, 1)
            if minresult > v:
                final_action = action
                v = minresult
        if self.turn == 1:
            self.piece_num = initialstate.transfer(final_action).white_num
        elif self.turn == 2:
            self.piece_num = initialstate.transfer(final_action).black_num
        print(final_action.getString())
        return initialstate.transfer(final_action), self.nodes, self.piece_num



