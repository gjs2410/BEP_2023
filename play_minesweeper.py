import numpy as np
from keras.models import load_model
from minesweeper_env import Minesweeper
from DDQN_hexagon import DoubleDQNAgent
import time
from hexagon_env import HexSweeper
#from DDQN import DoubleDQNAgent

def run_minesweeper(env, agent):
    """c
    Runs the game and shows winrate
    """
    win_count = 0
    steps = []
    for episode_idx in range(NUM_GAMES):
            state = env.reset()
            if GUI: env.render()
            for t in range(ROWDIM*COLDIM):
                action, _, valid_qvalues = agent.act(state)
                if GUI:
                    env.render()
                    time.sleep(MOVE_DELAY)
                state, reward, done = env.step(action)
                if done:
                    if GUI:
                        env.render()
                        time.sleep(MOVE_DELAY)
                        #env.plot_minefield(action)
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
    average_steps = sum(steps) / NUM_GAMES
    win_ratio = win_count / NUM_GAMES * 100
    print('Average amount of steps of {} +  The agent won {} out of {} games for a win ratio of {:.2f}%'
          .format(average_steps, win_count, NUM_GAMES, win_ratio))

    return steps


def init_agent():
    """
    Return parameters to agent
    """
    agent_kwargs = {
        'ROWDIM' : ROWDIM,
        'COLDIM' : COLDIM,
        'LR_PIECEWISE' : [1,0],
        'LR_DECAY_STEPS' : [0,1],
        'GAMMA' : 0, 
        'EPSILON_INITIAL' : 0, 
        'EPSILON_DECAY' : 0,
        'EPSILON_MIN' : 0,
        'TAU' : 1,
        'EXPERIENCE_REPLAY_BATCH_SIZE' : 0,
        'AGENT_MEMORY_LIMIT' : 1,
        'NUM_HOLDOUT_STATES' : 0,
        'PER_ALPHA' : 1,
        'PER_BETA_MIN' : 0,
        'PER_BETA_MAX' : 1,
        'PER_BETA_ANNEAL_STEPS' : 1,
        'PER_EPSILON' : 1,
        }
    agent = DoubleDQNAgent(ONLINE_NETWORK, ONLINE_NETWORK, **agent_kwargs)
    return agent
    



# minesweeper game parameters
ROWDIM = 8
COLDIM = 8
MINE_COUNT = 10

# Load agent model
ONLINE_NETWORK = load_model('model/8x8hex.h5')
MOVE_DELAY = 0 # seconds per move

NUM_GAMES = 1000 # number of games to play
GUI = True # True if u want to see the game

# Set up agent and environment
agent = init_agent()
env = HexSweeper(ROWDIM, COLDIM, MINE_COUNT, gui=GUI)
test = run_minesweeper(env, agent)

