#! /usr/bin/env python
# -*- coding: utf-8 -*-
####################################################################################
#	breakthroughgame.py
#
#	Created on Mon Mar 18 10:49:03 2019
#
#	This is the driver script for the breakthrough game, 
#	and it also holds the BreakthroughGame class, which controls the game flow
#		You can think of the BreakthroughGame class as the "environment" for this AI system
#
#	@authors: Juefei Yuan and Daniel McGonigle
####################################################################################

import pygame
import sys, os, math
from minimax_agent import *
from model import *
from alpha_beta_agent import *
import time

class BreakthroughGame:
    def __init__(self):
        #
        #	pygame graphical parameters
        #		unit for width, height and sizeofcell is pixels, screen.fill creates white background
        #
        pygame.init()
        self.width, self.height = 700, 560
        self.sizeofcell = int(560/8)
        self.screen = pygame.display.set_mode((self.width, self.height))
        self.screen.fill([255, 255, 255])
        #
        #	chessboard and related image variables
        #		board will hold the graphical board image, blackchess represents the jpg images for player 1's pieces, whitechess for player 2
        #		outline is just a jpg image for the chess board border, while reset is for the reset button; winner is a celebration dance!
        #
        self.board = 0
        self.blackchess = 0
        self.whitechess = 0
        self.outline = 0
        self.reset = 0
        self.winner = 0

        #
        # 	status 0: origin;  1: ready to move; 2: end
        #	turn 1: black(max) 2: white(min)
        #
        self.status = 0
        self.turn = 1
        # Variable for moving
        self.ori_x = 0
        self.ori_y = 0
        self.new_x = 0
        self.new_y = 0

        #
        # 	matrix for position of chess, 0 - empty, 1 - black, 2 - white
        #
        self.boardmatrix = [[1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0],
                            [2, 2, 2, 2, 2, 2, 2, 2],
                            [2, 2, 2, 2, 2, 2, 2, 2]]

        #
        #	nodes keeps track of the expandable game nodes when searching for the next move
        #
        self.total_nodes_1 = 0
        self.total_nodes_2 = 0
        self.total_time_1 = 0
        self.total_time_2 = 0
        self.total_step_1 = 0
        self.total_step_2 = 0
        self.eat_piece = 0
        # Caption
        pygame.display.set_caption("Breakthrough Game")

        # initialize pygame clock
        self.clock = pygame.time.Clock()
        self.initgraphics()

    #
    #	Start the game!
    #
    def run(self):
        self.clock.tick(60)

        # clear the screen
        self.screen.fill([255, 255, 255])

        # Heuristics: 1 = OH1, 2 = DH1, 3 = OH2, 4 = DH2
        # Status 5 = Game Method 1 ( Minimax (Offensive Heuristic 1) vs Alpha-beta (Offensive Heuristic 1) )
        # Status 6 = Game Method 2 ( Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 1) )
        # Status 7 = Game Method 3 ( Alpha-beta (Defensive Heuristic 2) vs Alpha-beta (Offensive Heuristic 1) ) 
        # Status 8 = Game Method 4 ( Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Offensive Heuristic 1) ) 
        # Status 9 = Game Method 5 ( Alpha-beta (Defensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 1) ) 
        # Status 10 = Game Method 6 ( Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 2) ) 
        if self.status in  [5,6,7,8,9,10]:
		
            player1search = 2
            player2search = 2
            if self.status == 5:
                player1search = 1
                player1func = 1
                player2func = 1
            elif self.status == 6:
                player1func = 3
                player2func = 2
            elif self.status == 7:
                player1func = 4
                player2func = 1
            elif self.status == 8:
                player1func = 3
                player2func = 1
            elif self.status == 9:
                player1func = 4
                player2func = 2
            elif self.status == 10:
                player1func = 3
                player2func = 4
		
            # Black
            if self.turn == 1:
                start = time.clock()
                self.ai_move(player1search, player1func)
                self.total_time_1 += (time.clock() - start)
                self.total_step_1 += 1
                print('total_step_1 = ', self.total_step_1,
                      'total_nodes_1 = ', self.total_nodes_1,
                      'node_per_move_1 = ', self.total_nodes_1 / self.total_step_1,
                      'time_per_move_1 = ', self.total_time_1 / self.total_step_1,
                      'have_eaten = ', self.eat_piece)
            elif self.turn == 2:
                start = time.clock()
                self.ai_move(player2search, player2func)
                self.total_time_2 += (time.clock() - start)
                self.total_step_2 += 1
                print('total_step_2 = ', self.total_step_2,
                      'total_nodes_2 = ', self.total_nodes_2,
                      'node_per_move_2 = ', self.total_nodes_2 / self.total_step_2,
                      'time_per_move_2 = ', self.total_time_2 / self.total_step_2,
                      'have_eaten: ', self.eat_piece)
					  
        # Events accepting
        for event in pygame.event.get():
            # Quit if close the windows
            if event.type == pygame.QUIT:
                exit()
            # reset button pressed
            elif event.type == pygame.MOUSEBUTTONDOWN and self.isreset(event.pos):
                self.boardmatrix = [[1, 1, 1, 1, 1, 1, 1, 1],
                            [1, 1, 1, 1, 1, 1, 1, 1],
                            [0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0, 0, 0, 0],
                            [2, 2, 2, 2, 2, 2, 2, 2],
                            [2, 2, 2, 2, 2, 2, 2, 2]]
                self.turn = 1
                self.status = 0

            elif event.type == pygame.MOUSEBUTTONDOWN and self.ismatchup(1, event.pos):
                print("Game type 1: Minimax (Offensive Heuristic 1) vs Alpha-beta (Offensive Heuristic 1)")
                self.status = 5
            elif event.type == pygame.MOUSEBUTTONDOWN and self.ismatchup(2, event.pos):
                print("Game type 2: Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 1)")
                self.status = 6
            elif event.type == pygame.MOUSEBUTTONDOWN and self.ismatchup(3, event.pos):
                print("Game type 3: Alpha-beta (Defensive Heuristic 2) vs Alpha-beta (Offensive Heuristic 1")
                self.status = 7
            elif event.type == pygame.MOUSEBUTTONDOWN and self.ismatchup(4, event.pos):
                print("Game type 4: Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Offensive Heuristic 1)")
                self.status = 8
            elif event.type == pygame.MOUSEBUTTONDOWN and self.ismatchup(5, event.pos):
                print("Game type 5: Alpha-beta (Defensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 1")
                self.status = 9
            elif event.type == pygame.MOUSEBUTTONDOWN and self.ismatchup(6, event.pos):
                print("Game type 6: Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 2)")
                self.status = 10

        self.display()
        # update the screen
        pygame.display.flip()

    #
    #	load the graphics and rescale them to the appropriate sizes/locations
    #
    def initgraphics(self):
        self.board = pygame.image.load_extended(os.path.join('src', 'chessboard.jpg'))
        self.board = pygame.transform.scale(self.board, (560, 560))
        self.blackchess = pygame.image.load_extended(os.path.join('src', 'blackchess.png'))
        self.blackchess = pygame.transform.scale(self.blackchess, (self.sizeofcell- 20, self.sizeofcell - 20))
        self.whitechess = pygame.image.load_extended(os.path.join('src', 'whitechess.png'))
        self.whitechess = pygame.transform.scale(self.whitechess, (self.sizeofcell - 20, self.sizeofcell - 20))
        self.outline = pygame.image.load_extended(os.path.join('src', 'square-outline.png'))
        self.outline = pygame.transform.scale(self.outline, (self.sizeofcell, self.sizeofcell))
        self.reset = pygame.image.load_extended(os.path.join('src', 'reset.jpg'))
        self.reset = pygame.transform.scale(self.reset, (80, 80))
        self.winner = pygame.image.load_extended(os.path.join('src', 'winner.png'))
        self.winner = pygame.transform.scale(self.winner, (250, 250))
        self.matchup1 = pygame.image.load_extended(os.path.join('src', 'matchup1.png'))
        self.matchup1 = pygame.transform.scale(self.matchup1, (80, 40))
        self.matchup2 = pygame.image.load_extended(os.path.join('src', 'matchup2.png'))
        self.matchup2 = pygame.transform.scale(self.matchup2, (80, 40))
        self.matchup3 = pygame.image.load_extended(os.path.join('src', 'matchup3.png'))
        self.matchup3 = pygame.transform.scale(self.matchup3, (80, 40))
        self.matchup4 = pygame.image.load_extended(os.path.join('src', 'matchup4.png'))
        self.matchup4 = pygame.transform.scale(self.matchup4, (80, 40))
        self.matchup5 = pygame.image.load_extended(os.path.join('src', 'matchup5.png'))
        self.matchup5 = pygame.transform.scale(self.matchup5, (80, 40))
        self.matchup6 = pygame.image.load_extended(os.path.join('src', 'matchup6.png'))
        self.matchup6 = pygame.transform.scale(self.matchup6, (80, 40))
    #
    #	display the graphics in the window
    #
    def display(self):
        self.screen.blit(self.board, (0, 0))
        self.screen.blit(self.reset, (590, 50))
        self.screen.blit(self.matchup1, (590, 300))
        self.screen.blit(self.matchup2, (590, 340))
        self.screen.blit(self.matchup3, (590, 380))
        self.screen.blit(self.matchup4, (590, 420))
        self.screen.blit(self.matchup5, (590, 460))
        self.screen.blit(self.matchup6, (590, 500))
        #
        #	Place the game pieces based on the value of the cell in boardmatrix
        #
        for i in range(8):
            for j in range(8):
                if self.boardmatrix[i][j] == 1:
                    self.screen.blit(self.blackchess, (self.sizeofcell * j + 10, self.sizeofcell * i + 10))
                elif self.boardmatrix[i][j] == 2:
                    self.screen.blit(self.whitechess, (self.sizeofcell * j + 10, self.sizeofcell * i + 10))
        #
        #	Status 1 means ready to move
        #
        if self.status == 1:
            #
            #	only downward moves are considered for player 1 (which corresponds to value 1 in boardmatrix)
            #
            if self.boardmatrix[self.ori_x][self.ori_y] == 1:
                x1 = self.ori_x + 1
                y1 = self.ori_y - 1
                x2 = self.ori_x + 1
                y2 = self.ori_y + 1
                x3 = self.ori_x + 1
                y3 = self.ori_y
                # left down
                if y1 >= 0 and self.boardmatrix[x1][y1] != 1:
                    self.screen.blit(self.outline,
                                     (self.sizeofcell * y1, self.sizeofcell * x1))
                # right down
                if y2 <= 7 and self.boardmatrix[x2][y2] != 1:
                    self.screen.blit(self.outline,
                                     (self.sizeofcell * y2, self.sizeofcell * x2))
                # down
                if x3 <= 7 and self.boardmatrix[x3][y3] == 0:
                    self.screen.blit(self.outline,
                                     (self.sizeofcell * y3, self.sizeofcell * x3))

            #
            #	Now check legal moves for player 2, which corresponds to value 2 in the boardmatrix
            #
            if self.boardmatrix[self.ori_x][self.ori_y] == 2:
                x1 = self.ori_x - 1
                y1 = self.ori_y - 1
                x2 = self.ori_x - 1
                y2 = self.ori_y + 1
                x3 = self.ori_x - 1
                y3 = self.ori_y
                # left up
                if y1 >= 0 and self.boardmatrix[x1][y1] != 2:
                    self.screen.blit(self.outline,
                                     (self.sizeofcell * y1, self.sizeofcell * x1))
                # right up
                if y2 <= 7 and self.boardmatrix[x2][y2] != 2:
                    self.screen.blit(self.outline,
                                     (self.sizeofcell * y2, self.sizeofcell * x2))
                # up
                if x3 >= 0 and self.boardmatrix[x3][y3] == 0:
                    self.screen.blit(self.outline,
                                     (self.sizeofcell * y3, self.sizeofcell * x3))
        #
        #	Status 3 means winner, winner, chicken dinner!
        #
        if self.status == 3:
            self.screen.blit(self.winner, (100, 100))

    #
    #	Checks to see if the event click was within the pixel range of the reset button
    #		input is the position tuple of (x, y) pixels
    #
    def isreset(self, pos):
        x, y = pos
        if 670 >= x >= 590 and 50 <= y <= 130:
            return True
        return False
    #
    #	Checks to see if the event click was within the pixel range of the specified matchup button
    #		input is the number of the matchup button and position tuple of (x, y) pixels
    #
    def ismatchup(self, matchup, pos):
        x, y = pos
        if 590 <= x <= 670 and (300 + ((matchup - 1) * 40)) <= y <= (340 + ((matchup - 1) * 40)):
            return True
        return False

    #
    #	Calls the appropriate agent search based on search type and heuristic 
    #
    def ai_move(self, searchtype, evaluation):
        if searchtype == 1:
            return self.ai_move_minimax(evaluation)
        elif searchtype == 2:
            return self.ai_move_alphabeta(evaluation)

    #
    #	invoke the MinimaxAgent to find the best move with minimax_decision, which returns the board state, number of nodes expanded, and pieces left
    #		input is the function type, which determines what heuristic to use for a given player move
    #
    def ai_move_minimax(self, function_type):
        board, nodes, piece = MinimaxAgent(self.boardmatrix, self.turn, 3, function_type).minimax_decision()
        self.boardmatrix = board.getMatrix()
        if self.turn == 1:
            self.total_nodes_1 += nodes
            self.turn = 2
        elif self.turn == 2:
            self.total_nodes_2 += nodes
            self.turn = 1
        self.eat_piece = 16 - piece
        if self.isgoalstate():
            self.status = 3
            #print(self.boardmatrix)

    #
    #	invoke the AlphaBetaAgent to find the best move with alpha_beta_decision, which returns the board state, number of nodes expanded, 
    #		and pieces left.  Alpha-beta is similar to minimax, but also implements pruning to speed the algorithm up.  This allows deeper search.
    #		input is the function type, which determines what heuristic to use for a given player move
    #
    def ai_move_alphabeta(self, function_type):
        board, nodes, piece = AlphaBetaAgent(self.boardmatrix, self.turn, 4, function_type).alpha_beta_decision()
        self.boardmatrix = board.getMatrix()
        # update number of nodes for each player
        if self.turn == 1:
            self.total_nodes_1 += nodes
            self.turn = 2
        elif self.turn == 2:
            self.total_nodes_2 += nodes
            self.turn = 1
        self.eat_piece = 16 - piece
        if self.isgoalstate():
            self.status = 3

    #
    #	Tests for goal state (if a 1 is in the last row, or a 2 is in the first row)
    #
    def isgoalstate(self, base=0):
        if base == 0:
            if 2 in self.boardmatrix[0] or 1 in self.boardmatrix[7]:
                return True
            else:
                for line in self.boardmatrix:
                    if 1 in line or 2 in line:
                        return False
            return True
        else:
            count = 0
            for i in self.boardmatrix[0]:
                if i == 2:
                    count += 1
            if count == 3:
                return True
            count = 0
            for i in self.boardmatrix[7]:
                if i == 1:
                    count += 1
            if count == 3:
                return True
            count1 = 0
            count2 = 0
            for line in self.boardmatrix:
                for i in line:
                    if i == 1:
                        count1 += 1
                    elif i == 2:
                        count2 += 1
            if count1 <= 2 or count2 <= 2:
                return True
        return False

####################################################################################
#	main(): Breakthrough Game Driver.  Calls an infinite loop of running the game!
####################################################################################
def main():
    print("******************************************************************************************")
    print("*	Welcome to AI Breakthrough! Game options below implement the following heuristics:")
    print("******************************************************************************************")
    print("*	Offensive Heuristic 1: 2 * (30 - # enemy pieces)")
    print("*	Defensive Heuristic 1: 2 * # your pieces")
    print("*	Offensive Heuristic 2: 1 * # your pieces - 2 * # enemy pieces")
    print("*	Defensive Heuristic 2: 2 * # your pieces - 1 * # enemy pieces")
    print("******************************************************************************************")
    print("*	Game Method 1 ( Minimax (Offensive Heuristic 1) vs Alpha-beta (Offensive Heuristic 1) )")
    print("*		***note: Game method 1 uses minimax search with search depth 3 for player 1(black)")
    print("*		***note: All other game methods and players use alphabeta pruning with search depth 4")
    print("*	Game Method 2 ( Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 1) )")
    print("*	Game Method 3 ( Alpha-beta (Defensive Heuristic 2) vs Alpha-beta (Offensive Heuristic 1) ) ")
    print("*	Game Method 4 ( Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Offensive Heuristic 1) ) ")
    print("*	Game Method 5 ( Alpha-beta (Defensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 1) ) ")
    print("*	Game Method 6 ( Alpha-beta (Offensive Heuristic 2) vs Alpha-beta (Defensive Heuristic 2) ) ")
    print("******************************************************************************************")

    game = BreakthroughGame()
    while 1:
        game.run()

if __name__ == '__main__':
    main()

