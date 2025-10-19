I would like to create an online game as described below:

# Robot-Flower-Princess-Back

## Goal
The robot delivers all flowers to the princess. The player has to guide the robot to navigate to pick flowers, then give them to princess.

## Game

### Game Board
Board : 2D grid configurable from 3x3 to 50x50
Board Cases :
* 🤖 Robot (R) : Controlled by the player, always placed at top left at beginning of the game
* 👑 Princesse (P) : Destination of flowers delivery, always placed at bottom right at beginning of the game
* 🌸 Fleur (F) : To be picked, random position, multiple but maximum 10% on the game board
* 🗑️ Obstacles (O) : Obstacles, cleanable, around 30% on the game board
* ⬜ Empty (E) : Empty cases

### Rules

Actions: There are 5 types of actions the robot can do :

↩️ Rotate : the robot turn on itself to be oriented toward a specified direction (east, south, west, north).
🚶‍♂️ Moving : only the robot can move, one case at a time. It can move only to adjacent empty case, east, west, north or south. It can move while holding flowers. The robot has to be oriented toward the empty case. If the robot tries to move beyond the board, it’s an invalid action.
⛏️🌸 Picking flower : the robot can only pick a flower at the adjacent case. It can pick multiple flowers, up to 12. The robot has to be oriented toward the flower. If the robot tries to pick something other than flower, it’s an invalid action
🫳🌸 Drop flower: the robot can only pick a flower on an adjacent empty case. The robot has to be oriented toward an empty case. If the robot tries to drop a flower on other than an empty case, it’s an invalid action
🫴🏼🌸 Give Flower: the robot can only give flowers it holds in hands to the princess, as a bouquet composed of maximum 12 flowers. The robot has to be oriented toward the princess. If the robot tries to give a flower toward something else than a princess, it’s an invalid action
🗑️ Cleaning : when facing an obstacle, it can clean it in the direction it is oriented. If it holds one or more flowers, it cannot do cleaning. The robot has to be oriented toward the obstacle. If the robot tries to clean something other than an obstacle, it’s an invalid action
Victory : the game is considered victory only when all flowers are delivered to the princess.
Game Over : A game over occurs when the robot execute an invalid action, against any rule above

### API
1. Any of the actions above could be commanded from the frontend.
2. In addition to the action above, add an auto-play command so an AI player can resolve the game to trying to win automatically.
3. For any game created and played, add a command to retrieve a full sequence of board states step-by-step for animation purpose on the frontend.
4. For any of the actions above, a command is received from a frontend through an API call. If there is any invalid action, return an error with error code and message in the response body.

Can you help me create a python project with best practice with below guidelines:
* expose an API using FastAPI framework run at localhost:8000
* codebase structured with the hexagonal architecture
* code covered properly by tests
* use docker to build and run
* use unicorn to run inside docker or in dev mode
* use of pyenv
* use of latest python version
* include ci workflow with github action
* project name is Robot-Flower-Princess-Back

At last, I would like to be able to download the full project packaged as a zip.