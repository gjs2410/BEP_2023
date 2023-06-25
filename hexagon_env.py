
from hexagontile import HexagonTile
import copy
import numpy as np
import random
from collections import deque
import pygame

def hide_tiles(hexagons):
        for hexagon in hexagons:
            hexagon.number = 7
        return hexagons

def get_random_colour(min_=150, max_=255):
    """Returns a random RGB colour with each component between min_ and max_"""
    return tuple(random.choices(list(range(min_, max_)), k=3))

def create_hexagon(position, radius=12, number=0) -> HexagonTile:
    """Creates a hexagon tile at the specified position"""
    class_ = HexagonTile
    return class_(position, radius, number)

def init_hexagons(num_x, num_y, flat_top=False):
    """Creates a hexaogonal tile map of size num_x * num_y"""
    leftmost_hexagon = create_hexagon(position=(50, 0))
    hexagons = [leftmost_hexagon]
    for x in range(num_y):
        if x:
            # alternate between bottom left and bottom right vertices of hexagon above
            index = 2 if x % 2 == 1 else 4
            position = leftmost_hexagon.vertices[index]
            leftmost_hexagon = create_hexagon(position)
            hexagons.append(leftmost_hexagon)

        # place hexagons to the left of leftmost hexagon, with equal y-values.
        hexagon = leftmost_hexagon
        for i in range(num_x - 1):
            x, y = hexagon.position  # type: ignore
            if flat_top:
                pass
            else:
                position = (x + hexagon.minimal_radius * 2, y)
            hexagon = create_hexagon(position, )
            hexagons.append(hexagon)

    return hexagons

class HexSweeper:

    def __init__(self, width, height, mine_count, gui=False) -> None:
        self.width = width
        self.height = height
        self.mine_count = mine_count
        self.score = 0
        self.num_moves = 0
        self.done = False
        self.explosion = False
        self.grid = np.zeros([height, width])
        self.player_grid = np.ones([height, width]) * 7
        self.board = init_hexagons(width, height)
        self.visible_board = hide_tiles(copy.deepcopy(self.board))
        if gui:
            self.init_gui() # if gui = True, initialize GUI
    
    def step(self, action):
        """
        gets action as input and returns the next state, the reward and if the game is over
        when the action is implemented,
        """
        # generates minefield if it is the start of the game
        if self.num_moves == 0: self.generate_field(action, self.board)

        numbers = [hexagon.number for hexagon in self.visible_board]
        numbers = np.array(numbers)

        naw = [hexagon.number for hexagon in self.board]
        naw = np.array(naw)


        numbers[action] = naw[action].copy() # sets the tile chosen in the minefield state to the playerfield state
        for i in range(len(numbers)):
            self.visible_board[i].number = numbers[i]

        num_hidden_tiles = np.count_nonzero(numbers == 7)
        if numbers[action] == -1:
            # Tile was a mine, game over
            done = True
            self.explosion = True
            reward = -1
            score = 0 
        elif num_hidden_tiles == self.mine_count:
            # Game won when all safe tiles revealed
            done = True
            reward = 1.0
            score = 1
        elif numbers[action] == 0:
            # IF tile = 0, reveal tiles recursively
            state, score = self.auto_reveal_tiles(action, self.visible_board)
            num_hidden_tiles = np.count_nonzero(state == 7)
            if num_hidden_tiles == self.mine_count:
                # Game won
                done = True
                reward = 1.0
            else:
                done = False
                reward = 0.1
        else:
            # Revealed a safe tile, but has not won yet
            done = False
            reward = 0.1
            score = 1
        # Update parameters + reshape
        
        for i in range(len(self.visible_board)):
            self.visible_board[i].number = numbers[i]


        #self.visible_board = state
        self.score += score
        self.done = done
        self.num_moves += 1
        return self.visible_board, reward, done
       
    
    def play_first_move(self):
        """
        Lets the environment play the first move 
        """

        # List for all the safe tiles in top left corner 3x3 grid
        safe_lst = [0, 1, 2, self.width, self.width + 1, self.width + 2, 2*self.width, 2*self.width + 1, 2*self.width + 2]
        for i in safe_lst:
            state, reward, done = self.step(i)
        return state
    
    def reset(self):
        """
        Resets all class variables to initial state,
        + also plays the first move
        """
        self.score = 0
        self.num_moves = 0
        self.explosion = False
        self.done = False
        self.board = init_hexagons(self.width, self.height)
        self.visible_board = hide_tiles(copy.deepcopy(self.board))
        #state = self.play_first_move()
        state = self.visible_board
        return state

    def generate_field(self, action, hexagons):
        """
        Generates minefield using seed
        """ 

        # Index of the tiles of safe moves
        safe_lst = [0, 1, 2, self.width, self.width + 1, self.width + 2, 2*self.width, 2*self.width + 1, 2*self.width + 2]
        num_mines = 0
        while num_mines < self.mine_count:
            # Pick random tile
            tile = random.choice(hexagons)
            # Check if tile is not first move
            if not any(tile == hexagons[a] for a in safe_lst):
                if tile.number != -1:
                    tile.number = -1
                    num_mines += 1

            # Count neighbor mines
                for hexagon in tile.compute_neighbours(hexagons):
                     if hexagon.number != -1:
                        hexagon.number += 1

    def auto_reveal_tiles(self, action, hexagons):
        """
        IF tile is revealed with value = 0, then all neighbors of that mine
        wil be revealed. Does this recursively
        """
        i = 0
        # Index of chosen tile

        tile = hexagons[action]
        old_zeros = [] # Keep track of already revealed zeros
        new_zeros = deque([tile]) # Keep track of newly discovered zeros
        state = self.visible_board.copy()
        revealed_tiles = []
        for hexagon in state:
            if hexagon.number != 7:
                revealed_tiles.append(hexagon)
        score = 0
        zero_found = True
        while zero_found:
            for hexagon in tile.compute_neighbours(state):
                if hexagon.position >= (0,0) and hexagon not in revealed_tiles:
                    self.visible_board[i].number = hexagon.number
                    score += 1
                    revealed_tiles.append(hexagon)
                    if hexagon.number == 0:
                        if hexagon not in old_zeros:
                            if hexagon not in new_zeros:
                                new_zeros.append(hexagon)
                i += 1
            old_zeros.append(new_zeros.popleft())
            if len(new_zeros) == 0:
                zero_found = False

        return self.visible_board, score
    
    def init_gui(self):
        # Initialize all PyGame and GUI parameters
        pygame.init()
        #pygame.mixer.quit() # Fixes bug with high PyGame CPU usage
        self.tile_rowdim = 32 # pixels per tile along the horizontal
        self.tile_coldim = 32 # pixels per tile along the vertical
        self.ui_height = 32 # Contains text regarding score and move #
        self.gameDisplay = pygame.display.set_mode((750, 350))
        pygame.display.set_caption('Hexagon Minesweeper')
        # Load Minesweeper tileset
        # Set font and font color
        self.myfont = pygame.font.SysFont('Segoe UI', 32)
        self.tilefont = pygame.font.SysFont("Segoe UI", 15)
        self.font_color = (255,255,255) # White
        self.victory_color = (8,212,29) # Green
        self.defeat_color = (255,0,0) # Red
        # Create selection surface to show what tile the agent is choosing
        self.selectionSurface = pygame.Surface((self.tile_rowdim, self.tile_coldim))
        self.selectionSurface.set_alpha(128) # Opacity from 255 (opaque) to 0 (transparent)
        self.selectionSurface.fill((245, 245, 66)) # Yellow

    def plot_playerfield(self):
        """
        Plots minefield (current state) shown to player 
        """
        for hexagon in self.visible_board:
        #hexagon = pygame.transform.scale(hexagon, (1280, 720))
            hexagon.render(self.gameDisplay)
            label = self.tilefont.render(str(hexagon.number), 1, (0,0,0))
            self.gameDisplay.blit(label, hexagon.centre)
    
    def render(self):
        """
        Update the game display after every agent action
        """
        text_score = self.myfont.render('SCORE: ', True, self.font_color)
        text_score_number = self.myfont.render(str(self.score), True, self.font_color)
        text_move = self.myfont.render('MOVE: ', True, self.font_color)
        text_move_number = self.myfont.render(str(self.num_moves), True, self.font_color)
        text_victory = self.myfont.render('VICTORY!', True, self.victory_color)
        text_defeat =  self.myfont.render('DEFEAT!', True, self.defeat_color)         
        self.gameDisplay.fill(pygame.Color('black')) # Clear screen
        self.gameDisplay.blit(text_move, (45, self.height+5))
        self.gameDisplay.blit(text_move_number, (140, self.height+5))        
        self.gameDisplay.blit(text_score, (400, self.height+5))
        self.gameDisplay.blit(text_score_number, (500, self.height+5))
        if self.done:
            if self.explosion:
                self.gameDisplay.blit(text_defeat, (700, self.height+5))
            else:
                self.gameDisplay.blit(text_victory, (700, self.height+5))
        # updated view of minefield
        self.plot_playerfield()
        #if valid_qvalues.size > 0:
            # surface showing agent selection and Q-value representations
        #    self.selection_animation(np.argmax(valid_qvalues))
        self.update_screen() 

    def update_screen(self):
        pygame.display.update()


    def close(self):
        pygame.quit()
