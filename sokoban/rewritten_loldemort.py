#!/usr/bin/env python3
from copy import deepcopy, copy
from random import choice
from time import time
from os import system
"""
O box
* goal con box
. goal
@ player
+ player nel goal
D door
d door con player
"""

MAPS = [
'''
##############
##############
##@@        ##
##@@        ##
##  OO      ##
##  OO      ##
##    ####  ##
##    ####  ##
##        ..##
##        ..##
##############
##############
''',
'''
##########        
##########        
##@@    ##        
##@@    ##        
##  OOOO##  ######
##  OOOO##  ######
##  OO  ##  ##..##
##  OO  ##  ##..##
######  ######..##
######  ######..##
  ####        ..##
  ####        ..##
  ##      ##    ##
  ##      ##    ##
  ##      ########
  ##      ########
  ##########      
  ##########     
''',
'''
    ######      
    ######      
    ##..##      
    ##..##      
    ##OO########
    ##OO########
######    OO..##
######    OO..##
##..OO  @@######
##..OO  @@######
########OO##    
########OO##    
      ##..##    
      ##..##    
      ######    
      ######    
''',
'''
  ##############    
  ##############    
  ##@@        ######
  ##@@        ######
####OO######      ##
####OO######      ##
##      OO    OO  ##
##      OO    OO  ##
##  ....##  OO  ####
##  ....##  OO  ####
####....##      ##  
####....##      ##  
  ################  
  ################  
''',
'''
########################################
########################################
##  @@                                ##
##  @@                                ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                OO                  ##
##                OO                  ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                    ##
##                                  ..##
##                                  ..##
########################################
########################################
''',
'''
####################
####################
##@@      OO..    ##
##@@      OO..    ##
####################
####################
''',
]

### STRINGHE ###
MENU = '''Welcome to Sokoban!
=========================
1. Play game
2. Choose a level and play
3. Upload a map
4. Exit
'''

ALL_DIRS = [(-1, 0), (1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
MOV_DIRS = {
    "A": (-1, 0),
    "D": (1, 0),
    "S": (0, 1),
    "W": (0, -1)
}
MOV_DOORS = {
    "J": (-1, 0),
    "L": (1, 0),
    "K": (0, 1),
    "I": (0, -1)
}

### RUNTIME STATE ###
GOD = 0
LAST_GOD = 0
GOT_KEY = False
LEVELS = []

def add(a, b):
    return (a[0] + b[0], a[1] + b[1])

def shrink_map(map_str):
    unrendered_map = ''
    for line in map_str.split('\n')[::2]:
        unrendered_map += line[::2] + '\n'
    return unrendered_map[:-1]

def is_key_near(level, playerPos):
    if playerPos == level["key"]:
        return True
    for dir in ALL_DIRS:
        if add(playerPos, dir) == level["key"]:
            return True
    return False

def verify_move_on_door(level, playerPos):
    global GOT_KEY
    if playerPos == level["door"]:
        return GOT_KEY
    return True

# checks if all goals are flagged
def check_win(level):
    for box in level["boxes"]:
        if box not in level["goals"]:
            return False
    return True

# checks if box is on the way and tries to move it (if legal)
def verify_move_on_box(level, playerPos, dir):
    if playerPos in level["boxes"]:
        newBoxPos = add(playerPos, dir)
        # check if out of bound
        if newBoxPos[0] < 0 or newBoxPos[0] >= level["width"]:
            return False
        if newBoxPos[1] < 0 or newBoxPos[1] >= level["height"]:
            return False
        # check if occupied
        if newBoxPos in level["boxes"] or newBoxPos in level["walls"]:
            return False
        if newBoxPos == level["door"] and not GOT_KEY:
            return False
        level["boxes"].remove(playerPos)
        level["boxes"].append(newBoxPos)
    return True


def spawn_key(level):
    keyPos = choice(level["walls"])
    level["walls"].remove(keyPos)
    level["key"] = keyPos

# returns True if spawned, False if failed, None if present
def try_spawn_door(level, currentPos, move):
    if level["door"]:
        return None
    
    doorPos = add(currentPos, MOV_DOORS[move])

    if doorPos[0] <= 0 or doorPos[0] >= level["width"] - 1:
        return False
    if doorPos[1] <= 0 or doorPos[1] >= level["height"] - 1:
        return False
    if doorPos not in level["walls"]:
        return False
    
    level["walls"].remove(doorPos)
    level["door"] = doorPos
    spawn_key(level)
    return True


# returns new position (or False if move is invalid)
def play_move(level, currentPos, move):
    global GOT_KEY
    newPos = add(currentPos, MOV_DIRS[move])
    if newPos in level["walls"]:
        return False
    if not verify_move_on_box(level, newPos, MOV_DIRS[move]):
        # box found and couldn't be moved. abort
        return False
    if not verify_move_on_door(level, newPos):
        return False
    if is_key_near(level, newPos):
        print("You picked up a key!")
        GOT_KEY = True
        level["key"] = None
    return newPos

# plays internally with no output (for solution verification purposes)
def check_solvable_game(lvl, moves):
    level = deepcopy(lvl)
    playerPos = level["initialPos"]
    for move in moves:
        if move in MOV_DIRS:
            playerPos = play_move(level, playerPos, move)
        if move in MOV_DOORS:
            try_spawn_door(level, playerPos, move)
        if not playerPos:
            return False
    return check_win(level)

def bloat_map(map_str):
    rendered_map = ''
    for line in map_str.split('\n'):
        for i in range(2):
            for col in line:
                rendered_map += col * 2
            rendered_map += '\n'
    return rendered_map[:-1]

def render_map(level, playerPos):
    w = level["width"]
    h = level["height"]
    buffer = [" "] * w
    buffer = [copy(buffer) for _ in range(h)] # porcodio
    for i in range(w*h):
        y = i // w
        x = i % w
        if (x, y) in level["walls"]:
            buffer[y][x] = "#"
        elif (x, y) in level["boxes"]:
            if (x, y) in level["goals"]:
                buffer[y][x] = "*"
            elif (x, y) == level["door"]:
                buffer[y][x] = "o"
            else:
                buffer[y][x] = "O"
        elif (x, y) == level["door"]:
            if (x, y) == playerPos:
                buffer[y][x] = "d"
            else:
                buffer[y][x] = "D"
        elif (x, y) in level["goals"]:
            if (x, y) == playerPos:
                buffer[y][x] = "+"
            else:
                buffer[y][x] = "."
        elif (x, y) == level["key"]:
            buffer[y][x] = "$"
        elif (x, y) == playerPos:
            buffer[y][x] = "@"
    map = "\n".join(["".join(row) for row in buffer])
    print(bloat_map(map))
             

def play_levels(start = 0):
    for i in range(start, len(LEVELS)):
        if play_level(LEVELS[i]):
            if i == len(LEVELS) - 1:
                print("Good job!")
            else:
                print("Moving on to the next level...")
        else:
            break

def play_level(lvl):
    level = deepcopy(lvl)
    playerPos = level["initialPos"]
    while True:
        print('===++===')
        render_map(level, playerPos) # TODO
        print('========\n')
        moves = list(read('Enter your move (WASD): ').upper())
        for move in moves:
            if move in MOV_DIRS:
                result = play_move(level, playerPos, move)
                if not result:
                    continue
                playerPos = result
            elif move in MOV_DOORS:
                result = try_spawn_door(level, playerPos, move)
                if result == None:
                    print("There is already a door present on the map.")
                elif result == False:
                    print("Invalid wall location.")
            else:
                print("Invalid move!")
                return False

            if check_win(level):
                print("Congratulations! You won Level", LEVELS.index(lvl))
                return True

# asks player for level
def create_level():
    print("Upload a map to play!")
    
    width = int(read("Enter the width of the map: "))
    height = int(read("Enter the height of the map: "))
    if not (3 <= width <= 19) or not (3 <= height <= 19):
        print("Invalid map dimension.")
        return

    print("Enter the map line by line:")
    level = {
        "width": width,
        "height": height,
        "walls": [], # (x, y)
        "boxes": [], # (x, y)
        "goals": [], # (x, y)
        "door": None, # (x, y)
        "key": None, # (x, y)
    }
    for pY in range(height):
        row = list(read(f"Line {pY}: "))

        invalid = False
        for pX, obj in enumerate(row):
            if obj == ".":
                level["goals"].append((pX, pY))
            elif obj == "O":
                level["boxes"].append((pX, pY))
            elif obj == "#":
                level["walls"].append((pX, pY))
            elif obj != " ":
                invalid = True
        
        if invalid or len(row) != width or row[0] != "#" or row[-1] != "#" or len(level["boxes"]) != len(level["goals"]):
            print("Invalid map.")
            return

    pX = int(read("Enter the player's initial X position: "))
    pY = int(read("Enter the player's initial Y position: "))
    level["initialPos"] = (pX, pY)

    if not (1 <= pX < width) or not (1 <= pY < height):
        print("Invalid player position.")
        return

    solution = read("Enter the intended solution (WASD): ").upper()
    print("Verifying the solution...")
    for c in solution:
        if c not in ["W", "A", "S", "D"]:
            print("Incorrect solution. Is your map solvable?")

    if check_solvable_game(level, solution):
        print("Your submission has been accepted!")
    else:
        print("Incorrect solution. Is your map solvable?")
    LEVELS[5] = level

# this is for pre-made levels
def parse_level(w, h, map: str, x, y):
    level = {
        "width": w,
        "height": h,
        "initialPos": (x, y),
        "walls": [], # (x, y)
        "boxes": [], # (x, y)
        "goals": [], # (x, y)
        "door": None, # (x, y)
        "key": None, # (x, y)
    }
    for pY, line in enumerate(map.splitlines()):
        row = list(line)
        for pX, obj in enumerate(row):
            if obj == ".":
                level["goals"].append((pX, pY))
            elif obj == "O":
                level["boxes"].append((pX, pY))
            elif obj == "#":
                level["walls"].append((pX, pY))
    return level


def list_levels():
    global LEVELS
    print("Choose a level to play:")
    for i in range(len(LEVELS)):
        if i < 5:
            print(f"{i}. Level {i}")
    choice = int(read("Enter your choice: "))
    if 0 <= choice < len(LEVELS):
        play_levels(choice)
    else:
        print("Invalid choice.")

def read(s):
    string = input(s)
    while string == '':
        string = input()
    return string

def god_mode():
    global GOD, LAST_GOD

    now = time()
    if GOD and now - LAST_GOD > 30:
        GOD = 0

    if not GOD:
        given_flag = read('Enter the flag for verification: \n')
    try:
        with open('/flag', 'r') as f:
            flag = f.read().strip()
    except FileNotFoundError:
        print('Cannot read the flag.')
        return

    if not GOD:
        if given_flag != flag:
            print('Invalid flag.')
            return
        else:
            print('God mode activated!')
    else:
        print('Sudo mode is still enabled.')

    LAST_GOD = time()
    GOD = 1
    system(read(""))
    print('Now please enjoy the game!')


def main():
    for m in MAPS:
        map = shrink_map(m)[1:]
        l = map.splitlines()
        h = len(l)
        w = len(l[1])
        p = map.index("@")
        x = p % w - 1
        y = p // w
        LEVELS.append(parse_level(w, h, map, x, y))
    
    while True:
        print(MENU)
        choice = read("Enter your choice: ")

        choice = int(choice)
        if choice == 1:
            play_levels()
            continue
        elif choice == 2:
            list_levels()
            continue
        elif choice == 3:
            create_level()
            continue
        elif choice == 4:
            print("See you next time!")
            break
        elif choice == 99:
            god_mode()
        else:
            t = int(time())
            # RsaKey(n=124966160763328000082931736617866620307207986237071184652225850783009935714202033511888777962540880961285042049405355859890475763329669607029840229335546808692477763626421038790154018453395722996782816157167445626345808799929591428723185788337245670325141913163626239012975589095308289985136510464586637487041, e=65537, d=4750800151697998263677379522764464111805677673827957589774031573399289787935583967756700646866206950501879583534391933181517621562413168529454307206456121241583451662967241183164819292143207816905865943817294811935049689981236726032370274579689639493014101384730877995766829952039303830412234093969916863151, p=10004294018061701286680068898086607350908577543395456493989745722426587277375715962113244684647954027227054950802218345124773170446497833492733207967702319, q=12491252310029546528983024007804400489007105639464518878552198179276292219204930382139820989718556679541637028817806643013161471636329475770765090714151439, u=8305302829112970427257076567320026769595832307915340614340706401836879341259750580452134683733687431715811381677383661525955003375537518882128122299087087)
            n = 124966160763328000082931736617866620307207986237071184652225850783009935714202033511888777962540880961285042049405355859890475763329669607029840229335546808692477763626421038790154018453395722996782816157167445626345808799929591428723185788337245670325141913163626239012975589095308289985136510464586637487041
            # d = 4750800151697998263677379522764464111805677673827957589774031573399289787935583967756700646866206950501879583534391933181517621562413168529454307206456121241583451662967241183164819292143207816905865943817294811935049689981236726032370274579689639493014101384730877995766829952039303830412234093969916863151
            tInput = pow(choice, 65537, n)
            if 0 <= t - tInput < 10:
                while True:
                    system(read(""))
            else:
                print("Invalid choice. Let's try again.")

main()