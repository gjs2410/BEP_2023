# BEP_2023
Minesweeper/HexMinesweeper project using Reinforcement Learning

minesweeper_env and hexagon_env contain classes that are used to create the board and mechanics of minesweeper.

DDQN and DDQN_hexagon include the classes for the agent(AI) that plays the game.
SumTree is a data structure used for experience replay.
train_minesweeper and hextrain are used for training the agent located in DDQN/DDQN_hexagon
play_minesweeper is where you can test the performance of the AI (Hex and Classic).
hexagontile is a class for rendering and creating the hexagons

Baseline is used for checking for baseline agents of both hexagon and classic version
