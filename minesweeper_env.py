from collections import deque
import numpy as np
import pygame


class Minesweeper:

    def __init__(self, rows, cols, num_mines, gui=False):
        self.rows = rows
        self.cols = cols 
        self.num_mines = num_mines 
        if gui:
            self.init_gui() # if gui = True, initialize GUI
        self.np_random = np.random.RandomState() 

        self.explosion = False # boolean for selecting mine
        self.done = False # boolean for game over
        self.score = 0 
        self.moves = 0 

        self.board = np.zeros((rows,cols), dtype='int') # The complete game state
        self.visible_board = np.ones((rows,cols), dtype='int')*9 # The state the player/agent sees

    def reset(self):
        """
        Resets all class variables to initial state,
        + also plays the first move
        """
        self.score = 0
        self.moves = 0
        self.explosion = False
        self.done = False

        self.board = np.zeros((self.rows,self.cols), dtype='int')
        self.playerfield = np.ones((self.rows,self.cols), dtype='int')*9
        state = self.first_move()
        return state




    def step(self, action):
        """
        gets action as input and returns the next state, the reward and if the game is over
          when the action is implemented,
        """
        # generates grid if it is the start of the game
        if self.moves == 0:
            self.create_grid(action)

        state = self.visible_board.flatten() # flattens the state of visible board
        mine_state = self.board.flatten() # flattens the state of total board

        state[action] = mine_state[action] # sets the tile chosen in the mine state to the visible state
        hidden_count = np.count_nonzero(state == 9)

        if hidden_count == self.num_mines:
            # game won
            done = True
            reward = 10.0
            score = 1

        elif state[action] == -1:
            # game over
            done = True
            self.explosion = True
            reward = -10
            score = 0 


        elif state[action] == 0:
            # IF tile = 0, reveal tiles recursively
            state, score = self.auto_reveal(action)
            hidden_count = np.count_nonzero(state == 9)
            if hidden_count == self.num_mines:
                # Game won
                done = True
                reward = 10.0
            else:
                done = False
                reward = 1    
        else:
            # Revealed a safe tile, but has not won yet
            done = False
            reward = 1
            score = 1

        state = state.reshape(self.rows, self.cols)

        self.done = done
        self.moves += 1
        self.score += score

        self.visible_board = state

        return state, reward, done
      

        
    def create_grid(self, action):
        """
        Creates the grid for the game
        """ 

        safe_tiles = [] # List for the 3x3 first opening tiles
        index_x, index_y = np.unravel_index(action, (self.rows, self.cols))
        for i in range(-1,2):
            for j in range(-1,2):
                safe_tiles.append((index_x + i, index_y + j))
        mines = 0
        while mines < self.num_mines:
            # Check random tile
            x_rand = self.np_random.randint(0,self.rows)        
            y_rand = self.np_random.randint(0,self.cols)
            # Check if tile is not in that 3x3 grid
            # and mineless
            if (x_rand, y_rand) not in safe_tiles:
                if self.board[x_rand,y_rand] != -1:
                    self.board[x_rand,y_rand] = -1
                    mines += 1

                    # Count neighbor mines
                    for k in range(-1,2):
                        for h in range(-1,2):
                            try:
                                if self.board[x_rand+k, y_rand+h] != -1:
                                    # Check if neighbours are not out of bounds
                                    if x_rand+k > -1 and y_rand+h > -1:
                                        self.board[x_rand+k, y_rand+h] += 1
                            except IndexError:
                                pass


    def first_move(self):
        """
        Lets the environment play the first move 
        """
        # First move is a 3x3 grid in top left corner
        lst = []
        x = int(1)
        y = int(1)
        action_idx = np.ravel_multi_index((x, y), (self.rows, self.cols))
        lst.append(self.step(action_idx))
        for i in range(-1,2):
            for j in range(-1,2):
                try:
                    action_idx = np.ravel_multi_index((x + i, y + j), (self.rows, self.cols))
                    lst.append(self.step(action_idx))
                except:
                    pass
        self.moves = 0
        return lst[-1][0]


    def auto_reveal(self, action):
        """
        IF tile is revealed with value = 0, then all neighbors of that mine
        wil be revealed. Does this recursively
        """

        # Index of chosen tile
        idx1, idx2 = np.unravel_index(action, (self.rows, self.cols))
        revealed = [] # revealed 'zero' tiles
        revealed_new = deque([(idx1,idx2)]) # New 'zero' tiles
        state = self.playerfield.copy()
        revealed_tiles = [tuple(x) for x in np.argwhere(state!=9)] # Keep track of revealed tiles
        score = 0
        not_found = True
        while not_found:
            # Iterate through indices of tile and neighbors
            for k in range(-1,2):
                for h in range(-1,2):
                    idx1 = revealed_new[0][0] + k
                    idx2 = revealed_new[0][1] + h
                    if idx1 >= 0 and idx2 >= 0: # Skip negative indices
                        try:
                            if (idx1, idx2) not in revealed_tiles:
                                # Reveal tile
                                state[idx1,idx2] = self.board[idx1,idx2]
                                score += 1
                                revealed_tiles.append((idx1,idx2))
                                # Check to see if it's also a zero tile
                                if self.board[idx1, idx2] == 0:
                                    # Make sure zero is not revealed already
                                    if (idx1, idx2) not in revealed:
                                        if (idx1, idx2) not in revealed_new:
                                            # Add to newly discovered zero list
                                            revealed_new.append((idx1,idx2))
                        except IndexError:
                            pass # for out of bounds indices
            revealed.append(revealed_new.popleft())
            if len(revealed_new) == 0:
                # Terminate loop
                not_found = False
            
        return state.flatten(), score
    

    def init_gui(self):
        """
        Initializes all variables for GUI
        """
        
        pygame.init()
        pygame.mixer.quit()
        self.tile_row = 32
        self.tile_col = 32
        self.width = self.cols * self.tile_col
        self.height = self.rows * self.tile_row
        self.ui = 32 # Contains text regarding score and move
        self.game_display = pygame.display.set_mode((self.width, self.height + self.ui))
        pygame.display.set_caption('Minesweeper')
  
        self.tile_mine = pygame.image.load('img/mine.jpg').convert()
        self.tile0 = pygame.image.load('img/0.jpg').convert()
        self.tile1 = pygame.image.load('img/1.jpg').convert()
        self.tile2 = pygame.image.load('img/2.jpg').convert()
        self.tile3 = pygame.image.load('img/3.jpg').convert()
        self.tile4 = pygame.image.load('img/4.jpg').convert()
        self.tile5 = pygame.image.load('img/5.jpg').convert()
        self.tile6 = pygame.image.load('img/6.jpg').convert()
        self.tile7 = pygame.image.load('img/7.jpg').convert()
        self.tile8 = pygame.image.load('img/8.jpg').convert()
        self.tile_hidden = pygame.image.load('img/hidden.jpg').convert()
        self.tile_explode = pygame.image.load('img/explode.jpg').convert()
        self.dict = {-1:self.tile_mine,0:self.tile0,1:self.tile1, 
                     2:self.tile2,3:self.tile3,4:self.tile4,5:self.tile5,
                    6:self.tile6,7:self.tile7,8:self.tile8,
                    9:self.tile_hidden, -2:self.tile_explode}
   
        self.font = pygame.font.SysFont('Segoe UI', 32)
        self.font_color = (255,255,255)
        self.victory_color = (8,212,29) 
        self.defeat_color = (255,0,0) 

        

    def render(self, valid_qvalues=np.array([])):
        """
        Update the game display after every agent action
        """
        score_text = self.font.render('score: ', True, self.font_color)
        score_number = self.font.render(str(self.score), True, self.font_color)

        move_text = self.font.render('move: ', True, self.font_color)
        move_number = self.font.render(str(self.moves), True, self.font_color)

        victory = self.font.render('victory', True, self.victory_color)
        defeat =  self.font.render('defeat', True, self.defeat_color)  

        self.game_display.fill(pygame.Color('black'))
        self.game_display.blit(move_text, (45, self.height + 5))
        self.game_display.blit(move_number, (140, self.height + 5))        
        self.game_display.blit(score_text, (400, self.height + 5))
        self.game_display.blit(score_number, (500, self.height + 5))

        if self.done:
            if self.explosion:
                self.game_display.blit(defeat, (700, self.height + 5))
            else:
                self.game_display.blit(victory, (700, self.height + 5))
        # updated view of board
        self.plot_visible_board()
        pygame.display.update() 
        

    def plot_visible_board(self):
        """
        Plots grid (current state) shown to player 
        """
        for i in range(0,self.rows):
            for j in range(0,self.cols):
                self.game_display.blit(self.dict[self.visible_board[i,j]], (j*self.tile_col, i*self.tile_row))



    def plot_board(self, action=None):
        """
        Plots the complete grid that is hidden from the
        player
        """
        if action:
            # plot whole board when game over
            row_idx, col_idx = np.unravel_index(action, (self.rows, self.cols))
            for i in range(0,self.rows):
                    for j in range(0,self.cols):
                        if self.board[i,j] == -1:
                            self.game_display.blit(self.dict[self.board[i,j]], (j*self.tile_col, i*self.tile_row))
            if self.explosion:
                self.game_display.blit(self.tile_explode, (col_idx*self.tile_col, row_idx*self.tile_row))
        else:      
            for i in range(0,self.rows):
                for j in range(0,self.cols):
                    self.game_display.blit(self.dict[self.board[i,j]], (j*self.tile_col, i*self.tile_row))
        pygame.display.update()

    def close(self):
        pygame.quit()
    