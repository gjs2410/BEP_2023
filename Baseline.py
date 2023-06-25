import numpy as np
import time
from minesweeper_env import Minesweeper
from hexagon_env import HexSweeper

num_games = 1000
GUI = False
move_delay = 0
rowdim =8
coldim  = 8
mine_count = 10
env = Minesweeper(rowdim, coldim, mine_count, gui=GUI)


def base_act(state):
        """
        The agent chooses a random action
        """
        flattened_state = state.flatten()
        valid_actions = np.where(flattened_state == 9)[0]
        return np.random.choice(valid_actions), valid_actions

def hex_base_act(state):
        """
        The agent chooses a random action
        """
        numbers = [hexagon.number for hexagon in state]
        numbers = np.array(numbers)
        numbers.shape = (numbers.size//coldim, coldim)
        flattened_state = numbers.flatten()
        valid_actions = np.where(flattened_state == 7)[0]
        return np.random.choice(valid_actions), valid_actions


def run_minesweeper(env):
    """c
    Runs the game and shows winrate
    """
    win_count = 0
    steps = []
    for episode_idx in range(num_games):
            state = env.reset()
            if GUI: env.render()
            for t in range(rowdim*coldim):
                action, valid_actions = base_act(state)
                if GUI:
                    env.render()
                    time.sleep(move_delay)
                state, reward, done = env.step(action)
                if done:
                    if GUI:
                        env.render(valid_actions)
                        time.sleep(move_delay)
                        env.plot_minefield(action)
                    if not env.explosion: 
                        win_count += 1
                        result = 'win'
                    else:
                        result = 'loss'
                    print("Episode {} finished after {} moves with a score of {} ({}) WR = {:.2f}%"
                          .format(episode_idx+1, t+2, env.score, result, win_count/(episode_idx+1)*100))
                    steps.append(t+2)
                    if GUI: time.sleep(5)
                    break
    env.close()
    average_steps = sum(steps) / num_games
    win_ratio = win_count / num_games * 100
    print('Average amount of steps of {} +  The agent won {} out of {} games for a win ratio of {:.2f}%'
          .format(average_steps, win_count, num_games, win_ratio))
    

test = run_minesweeper(env)