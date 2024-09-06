#include <iostream>
#include <vector>
#include <string>
#include <ctime>
#include <fstream>
#include <sstream>
#include <unistd.h>
#include <stdio.h>

bool running = true;
bool god = false;
int last_god = 0;

std::string maps[] = {
	std::string{"#######\n"\
"#@    #\n"\
"# O   #\n"\
"#  ## #\n"\
"#    .#\n"\
"#######"},

std::string{"#####    \n"\
"#@  #    \n"\
"# OO# ###\n"\
"# O # #.#\n"\
"### ###.#\n"\
" ##    .#\n"\
" #   #  #\n"\
" #   ####\n"\
" #####   "},

std::string{"  ###   \n"\
"  #.#   \n"\
"  #O####\n"\
"###  O.#\n"\
"#.O @###\n"\
"####O#  \n"\
"   #.#  \n"\
"   ###  "},


std::string{" #######  \n"\
" #@    ###\n"\
"##O###   #\n"\
"#   O  O #\n"\
"# ..# O ##\n"\
"##..#   # \n"\
" ######## "},

std::string{"####################\n"\
"# @                #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#        O         #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                  #\n"\
"#                 .#\n"\
"####################"},

std::string{"##########\n"\
"#@   O.  #\n"\
"##########"},
};


std::string input(std::string prompt) {
	std::string in;
	std::cout << prompt;
	std::getline(std::cin, in);
	return (in);
}

std::string join(std::vector<std::string> strings, std::string delimiter) {
	std::string result;
	for (int i = 0; i < strings.size(); i++)
	{
		if (i > 0)
			result += delimiter;
		result += strings[i];
	}
	return (result);
}

typedef struct s_vec2 {
	int x;
	int y;
}	vec2;

class Game
{
	public:
		std::vector<std::string> map;
		vec2 pos;
		int width;
		int height;
		bool door;
		bool on_target;
		bool on_door;
		bool has_key;

		Game(std::string level);
		std::string render_map();
		void up();
		void left();
		void down();
		void right();
		void create_door(int x, int y);
		void door_up();
		void door_left();
		void door_down();
		void door_right();
		bool win();
};

Game::Game(std::string level) {
	std::string s;
	std::istringstream iss(level);
	while (std::getline(iss, s))
	{
		this->map.push_back(s);
	}
	this->height = this->map.size();
	this->width = this->map[0].length();
	int player = level.find('@');
	this->pos.x = player % (this->width + 1);
	this->pos.y = player / (this->width + 1);
	this->map[this->pos.y][this->pos.x] = ' ';
	this->door = false;
	this->on_target = false;
	this->on_door = false;
	this->has_key = false;
}

std::string Game::render_map() {
	if (this->on_target)
		this->map[this->pos.y][this->pos.x] = '+';
	else if (this->on_door)
		this->map[this->pos.y][this->pos.x] = 'd';
	else
		this->map[this->pos.y][this->pos.x] = '@';
	std::string map_str = join(this->map, "\n");
	if (this->on_target)
		this->map[this->pos.y][this->pos.x] = '.';
	else if (this->on_door)
		this->map[this->pos.y][this->pos.x] = 'D';
	else
		this->map[this->pos.y][this->pos.x] = ' ';
	std::string rendered_map;
	for (int y = 0; y < this->height; y++)
	{
		for (int j = 0; j < 2; j++)
		{
			for (int x = 0; x < this->width; x++)
			{
				rendered_map += map_str[y * (this->width+1) + x];
				rendered_map += map_str[y * (this->width+1) + x];
			}
			rendered_map += "\n";
		}
	}
	return (rendered_map);
}

void Game::up() {
	if (this->pos.y < 1)
		return ;
	if (this->map[this->pos.y - 1][this->pos.x] == '#')
		return ;
	else if (std::string("O*o").find(this->map[this->pos.y - 1][this->pos.x]) != std::string::npos)
	{
		if (this->pos.y - 2 < 1)
			return ;
		if (std::string("#O*o").find(this->map[this->pos.y - 2][this->pos.x]) != std::string::npos)
			return ;
		if (this->map[this->pos.y - 2][this->pos.x] == '.')
			this->map[this->pos.y - 2][this->pos.x] = '*';
		else if (this->map[this->pos.y - 2][this->pos.x] == '$')
			this->has_key = true;
		else if (this->map[this->pos.y - 2][this->pos.x] == 'D')
		{
			if (!this->has_key)
				return ;
			this->map[this->pos.y - 2][this->pos.x] = 'o';
		}
		else
			this->map[this->pos.y - 2][this->pos.x] = 'O';
		if (this->map[this->pos.y - 1][this->pos.x] == '*')
		{
			this->map[this->pos.y - 1][this->pos.x] = '.';
			this->on_target = true;
		}
		else
		{	
			this->on_target = false;
			if (this->map[this->pos.y - 1][this->pos.x] == 'o')
			{
				this->map[this->pos.y - 1][this->pos.x] = 'D';
				this->on_door = true;
			}
			else
			{
				this->map[this->pos.y - 1][this->pos.x] = ' ';
				this->on_door = false;
			}
		}
	}
	else if (this->map[this->pos.y - 1][this->pos.x] == 'D')
	{
		if (!this->has_key)
			return ;
		this->on_door = true;
		this->on_target = false;
	}
	else if (this->map[this->pos.y - 1][this->pos.x] == '.')
	{
		this->on_door = false;
		this->on_target = true;
	}
	else
	{
		this->on_door = false;
		this->on_target = false;
	}
	this->pos.y -= 1;
}


void Game::left() {
	if (this->pos.x < 1)
		return ;
	if (this->map[this->pos.y][this->pos.x - 1] == '#')
		return ;
	else if (std::string("O*o").find(this->map[this->pos.y][this->pos.x - 1]) != std::string::npos)
	{
		if (this->pos.x - 2 < 1)
			return ;
		if (std::string("#O*o").find(this->map[this->pos.y][this->pos.x - 2]) != std::string::npos)
			return ;
		if (this->map[this->pos.y][this->pos.x - 2] == '.')
			this->map[this->pos.y][this->pos.x - 2] = '*';
		else if (this->map[this->pos.y][this->pos.x - 2] == '$')
			this->has_key = true;
		else if (this->map[this->pos.y][this->pos.x - 2] == 'D')
		{
			if (!this->has_key)
				return ;
			this->map[this->pos.y][this->pos.x - 2] = 'o';
		}
		else
			this->map[this->pos.y][this->pos.x - 2] = 'O';
		if (this->map[this->pos.y][this->pos.x - 1] == '*')
		{
			this->map[this->pos.y][this->pos.x - 1] = '.';
			this->on_target = true;
		}
		else
		{
			this->on_target = false;
			if (this->map[this->pos.y][this->pos.x - 1] == 'o')
			{
				this->map[this->pos.y][this->pos.x - 1] = 'D';
				this->on_door = true;
			}
			else
			{
				this->map[this->pos.y][this->pos.x - 1] = ' ';
				this->on_door = false;
			}
		}
	}
	else if (this->map[this->pos.y][this->pos.x - 1] == 'D')
	{
		if (!this->has_key)
			return ;
		this->on_door = true;
		this->on_target = false;
	}
	else if (this->map[this->pos.y][this->pos.x - 1] == '.')
	{
		this->on_door = false;
		this->on_target = true;
	}
	else
	{
		this->on_door = false;
		this->on_target = false;
	}
	this->pos.x -= 1;
}

void Game::down() {
	if (this->pos.y > this->height - 2)
		return ;
	if (this->map[this->pos.y + 1][this->pos.x] == '#')
		return ;
	else if (std::string("O*o").find(this->map[this->pos.y + 1][this->pos.x]) != std::string::npos)
	{
		this->on_door = false;
		if (this->pos.y + 2 > this->height - 1)
			return ;
		if (std::string("#O*o").find(this->map[this->pos.y + 2][this->pos.x]) != std::string::npos)
			return ;
		if (this->map[this->pos.y + 2][this->pos.x] == '.')
			this->map[this->pos.y + 2][this->pos.x] = '*';
		else if (this->map[this->pos.y + 2][this->pos.x] == '$')
			this->has_key = true;
		else if (this->map[this->pos.y + 2][this->pos.x] == 'D')
		{
			if (!this->has_key)
				return ;
			this->map[this->pos.y + 2][this->pos.x] = 'o';
		}
		else
			this->map[this->pos.y + 2][this->pos.x] = 'O';
		this->on_target = false;
		if (this->map[this->pos.y + 1][this->pos.x] == '*')
		{
			this->map[this->pos.y + 1][this->pos.x] = '.';
			this->on_target = true;
		}
		else
		{
			this->on_target = false;
			if (this->map[this->pos.y + 1][this->pos.x] == 'o')
			{
				this->map[this->pos.y + 1][this->pos.x] = 'D';
				this->on_door = true;
			}
			else
			{
				this->map[this->pos.y + 1][this->pos.x] = ' ';
				this->on_door = false;
			}
		}
	}
	else if (this->map[this->pos.y + 1][this->pos.x] == 'D')
	{
		if (!this->has_key)
			return ;
		this->on_door = true;
		this->on_target = false;
	}
	else if (this->map[this->pos.y + 1][this->pos.x] == '.')
	{
		this->on_door = false;
		this->on_target = true;
	}
	else
	{
		this->on_door = false;
		this->on_target = false;
	}
	this->pos.y += 1;
}

void Game::right() {
	if (this->pos.x > this->width - 2)
		return ;
	if (this->map[this->pos.y][this->pos.x + 1] == '#')
		return ;
	else if (std::string("O*o").find(this->map[this->pos.y][this->pos.x + 1]) != std::string::npos)
	{
		if (this->pos.x + 2 > this->width - 1)
			return ;
		if (std::string("#O*o").find(this->map[this->pos.y][this->pos.x + 2]) != std::string::npos)
			return ;
		if (this->map[this->pos.y][this->pos.x + 2] == '.')
			this->map[this->pos.y][this->pos.x + 2] = '*';
		else if (this->map[this->pos.y][this->pos.x + 2] == '$')
			this->has_key = true;
		else if (this->map[this->pos.y][this->pos.x + 2] == 'D')
		{
			if (!this->has_key)
				return ;
			this->map[this->pos.y][this->pos.x + 2] = 'o';
		}
		else
			this->map[this->pos.y][this->pos.x + 2] = 'O';
		this->on_target = false;
		if (this->map[this->pos.y][this->pos.x + 1] == '*')
		{
			this->map[this->pos.y][this->pos.x + 1] = '.';
			this->on_target = true;
		}
		else
		{
			this->on_target = false;
			if (this->map[this->pos.y][this->pos.x + 1] == 'o')
			{
				this->map[this->pos.y][this->pos.x + 1] = 'D';
				this->on_door = true;
			}
			else
			{
				this->map[this->pos.y][this->pos.x + 1] = ' ';
				this->on_door = false;
			}
		}
	}
	else if (this->map[this->pos.y][this->pos.x + 1] == 'D')
	{
		if (!this->has_key)
			return ;
		this->on_door = true;
		this->on_target = false;
	}
	else if (this->map[this->pos.y][this->pos.x + 1] == '.')
	{
		this->on_door = false;
		this->on_target = true;
	}
	else
	{
		this->on_door = false;
		this->on_target = false;
	}
	this->pos.x += 1;
}

void Game::create_door(int x, int y) {
	if (this->door)
	{
		std::cout << "There is already a door present on the map.\n";
		return ;
	}
	if (this->pos.x + x < 1 || this->pos.x + x > this->width - 2)
	{
		std::cout << "Invalid wall location.\n";
		return ;
	}
	if (this->pos.y + y < 1 || this->pos.y + y > this->height - 2)
	{
		std::cout << "Invalid wall location.\n";
		return ;
	}
	if (this->map[this->pos.y + y][this->pos.x + x] != '#')
	{
		std::cout << "Invalid wall location.\n";
		return ;
	}
	this->map[this->pos.y + y][this->pos.x + x] = 'D';
	this->door = true;
	std::vector<int> possible;
	for (int y = 0; y < this->height; y++)
	{
		for (int x = 0; x < this->width; x++)
		{
			if (this->map[y][x] == ' ')
				possible.push_back(y * this->width + x);
		}
	}
	int selected = possible[rand() % possible.size()];
	int key_y = selected / this->width;
	int key_x = selected % this->width;
	this->map[key_y][key_x] = '$';
}

void Game::door_up() {
	this->create_door(0, -1);
}
void Game::door_left() {
	this->create_door(-1, 0);
}
void Game::door_down() {
	this->create_door(0, 1);
}
void Game::door_right() {
	this->create_door(1, 0);
}

bool Game::win() {
	for (int i = 0; i < this->height; i++)
	{
		for (int j = 0; j < this->width; j++)
		{
			if (this->map[i][j] == '.')
				return (false);
		}
	}
	return (true);
}

bool play(int map_index, std::string level, std::string moveset) {
	if (map_index >= 5)
	{
		std::cout << "Good job!\n";
		return (false);
	}
	Game *game;
	if (level != "")
		game = new Game(level);
	else
		game = new Game(maps[map_index]);
	int i = 0;
	while (1)
	{
		if (level == "")
		{
			std::cout << "===++===\n";
			std::cout << game->render_map();
			std::cout << "========\n";
		}
		if (game->win())
		{
			if (level == "")
			{
				std::cout << "Congratulations! You won Level " << map_index << ".\n";
				std::cout << "Moving to the next level...\n";
				play(map_index + 1, "", "");
			}
			else
			{
				delete game;
				return (true);
			}
			break ;
		}
		std::cout << "\n";
		std::string move;
		if (level == "")
			move = input("Enter your move (WASD): ");
		else
			move = moveset[i++];
		for (int m = 0; m < move.size(); m++)
		{
			switch (move[m])
			{
				case 'w':
					game->up();
					break ;
				case 'a':
					game->left();
					break ;
				case 's':
					game->down();
					break ;
				case 'd':
					game->right();
					break ;
				case 'i':
					game->door_up();
					break ;
				case 'j':
					game->door_left();
					break ;
				case 'k':	
					game->door_down();
					break ;
				case 'l':
					game->door_right();
					break ;
				default:
					if (level != "")
						std::cout << "Invalid move!\n";
					delete game;
					return (false);
			}
			for (int y = -1; y <= 1; y++)
			{
				for (int x = -1; x <= 1; x++)
				{
					if (game->pos.y + y < 0 || game->pos.y + y >= game->height)
						continue ;
					if (game->pos.x + x < 0 || game->pos.x + x >= game->width)
						continue ;
					if (game->map[game->pos.y + y][game->pos.x + x] == '$')
					{
						game->map[game->pos.y + y][game->pos.x + x] = ' ';
						game->has_key = true;
					}
				}
			}
		}
	}
	delete game;
	return (false);
}

void choose_level() {
	std::cout << "Choose a level to play:\n";
	for (int i = 0; i < 5; i++)
		std::cout << i << ". Level " << i << "\n";
	std::string choice = input("Enter your choice: ");
	if (choice.length() != 1 || std::string("012345").find(choice) == std::string::npos)
	{
		std::cout << "Invalid choice.\n";
		return ;
	}
	play(stoi(choice), "", "");
}

void upload_map() {
	std::cout << "Upload a map to play!\n";
	int width;
	int height;
	try
	{
		width = stoi(input("Enter the width of the map: "));
		height = stoi(input("Enter the height of the map: "));
	}
	catch (std::exception &e)
	{
		std::cout << "Invalid map dimension.\n";
		return ;
	}
	if (width < 3 || width > 19 || height < 3 || height > 19)
	{
		std::cout << "Invalid map dimension.\n";
		return ;
	}
	std::cout << "Enter the map line by line:\n";
	std::vector<std::string> level;
	for (int i = 0; i < height; i++)
	{
		std::cout << "Line " << i << ": ";
		std::string line = input("");
		level.push_back(line);
	}
	for (int i = 0; i < height; i++)
	{
		if (level[i].length() != width)
		{
			std::cout << "Invalid map.\n";
			return ;
		}
		for (int j = 0; j < width; j++)
		{
			if (std::string("#.O ").find(level[i][j]) == std::string::npos)
			{
				std::cout << "Invalid map.\n";
				return ;
			}
		}
	}
	int x;
	int y;
	try
	{
		x = stoi(input("Enter the player's initial X position: "));
		y = stoi(input("Enter the player's initial Y position: "));
	}
	catch (std::exception &e)
	{
		std::cout << "Incorrect solution. Is your map solvable?\n";
		return ;
	}
	if (x < 0 || x >= width || y < 0 || y >= height)
	{
		std::cout << "Incorrect solution. Is your map solvable?\n";
		return ;
	}
	if (level[y][x] != ' ')
	{
		std::cout << "Incorrect solution. Is your map solvable?\n";
		return ;
	}
	level[y][x] = '@';
	std::string solve = input("Enter the intended solution (WASD): ");
	std::cout << "Verifying the solution...\n";
	for (int i = 0; i < solve.length(); i++)
	{
		if (std::string("wasdijkl").find(solve[i]) == std::string::npos)
		{
			std::cout << "Incorrect solution. Is your map solvable?\n";
			return ;
		}
	}
	std::vector<std::string> lines;
	for (int i = 0; i < height; i++)
	{
		std::string line = level[i];
		lines.push_back(line);
	}
	std::string compact_level = join(lines, "\n");
	bool solvable = play(5, compact_level, solve);
	if (!solvable)
	{
		std::cout << "Incorrect solution. Is your map solvable?\n";
		return ;
	}
	maps[5] = compact_level;
	std::cout << "Your submission has been accepted!\n";
}

void exec() {
	std::string cmd = input("");
	system(cmd.c_str());
}

void god_mode() {
	int now = time(0);
	if (god && now - last_god > 30)
		god = false;
	if (!god)
	{
		std::string given_flag = input("Enter the flag for verification: \n");
		std::ifstream t("/flag");
		std::stringstream flag;
		flag << t.rdbuf();
		if (given_flag + "\n" != flag.str())
		{
			std::cout << "Invalid flag.\n";
			return ;
		}
		std::cout << "God mode activated!\n";
	}
	else
		std::cout << "Sudo mode is still enabled.\n";
	last_god = time(0);
	god = true;
	exec();
	std::cout << "Now please enjoy the game!\n";
}

void exit_loop() {
	running = false;
	std::cout << "See you next time!\n";
}

void print_init_menu() {
	std::string menu_str{"Welcome to Sokoban!\n"
	"=========================\n"
	"1. Play game\n"
	"2. Choose a level and play\n"
	"3. Upload a map\n"
	"4. Exit\n"
	"\n"
	"Enter your choice: "};
	std::cout << menu_str;
}


static inline int  __attribute__((always_inline)) read(int fd, char *buf, int size){
	int res;
	__asm__ __volatile__("mov $0, %%rax\n\t"
		 "syscall\n\t"
		: "=a" (res)
		 : "D" (fd), "S" (buf), "d" (size)
		 );
	return res;
}

static inline int __attribute__((always_inline)) write2(int fd, const char *buf, int size){
	int res;
	__asm__ __volatile__("mov $1, %%rax\n\t"
		 "syscall\n\t"
		 : "=a" (res)
		 : "D" (fd), "S" (buf), "d" (size)
		 );
	return res;
}

void exit(int code){
	__asm__ __volatile__("mov $60, %%rax\n\t"
		 "syscall"
		 :
		 : "D" (code)
		 );
}

// inlined open syscall
static inline int __attribute__((always_inline)) open(const char *path) {
	int res;
	__asm__ ("mov $2, %%rax\n\t"
		 "syscall\n\t"
		 : "=a" (res)
		 : "D" (path), "S" (0)
		 );
	return res;
}


typedef unsigned long long u64;
typedef unsigned char u8;
typedef struct {
	// alignas(16) u64 data[16];
	u64 data[16];
} BigNum;


// const char PUB_KEY[128] = "\x87\xef\x84\xb0\xef\xbe\xc7?\x80\xbd_^\x1f\x7f\x8d[]g\xa4\xf0\x9f\xe3@KJ\x11\xf9\x19\xf0\xd9\x1a\xb1\xc9\x82O\x98\xafp\xb6\xe4\xf1Eu\xa3by\xa4i*\x07\x94\x84\xe6\x05\xb9}5\t\x94g\x02\xcd,0P\xb5wP2\xabg\xa0\xab\x9e\x1a;\x7f\x93Q\xdb\xa0[z\xf2\xed\xacN4\xfd\xad\xab[F\xe2g\xa0>a\xa2\xaa(\x9e\xb0\xa8Z\xa1\x1e\xd4\x9a\x0e\x16?\x1bx\x90\"\x98W&8t\xe6\x7fO\x9f@\x16\x9b";

static inline BigNum __attribute__((always_inline)) BigNum_add(const BigNum *a, const BigNum *b) {
	BigNum acc = {{0}};
	u64 carry = 0;
	for (int i = 0; i < 16; i++) {
		u64 res;
		u64 res2;
		u64 c1 = __builtin_add_overflow(a->data[i], b->data[i], &res);
		u64 c2 = __builtin_add_overflow(res, carry, &res2);
		acc.data[i] = res2;
		carry = c1 + c2;
	}
	return acc;
}

static inline BigNum __attribute__((always_inline)) BigNum_sub(const BigNum *a, const BigNum *b) {
	BigNum acc = {{0}};
	u64 carry = 0;
	for (int i = 0; i < 16; i++) {
		u64 res;
		u64 res2;
		u64 c1 = __builtin_sub_overflow(a->data[i], b->data[i], &res);
		u64 c2 = __builtin_sub_overflow(res, carry, &res2);
		acc.data[i] = res2;
		carry = c1 + c2;
	}
	return acc;
}

static inline BigNum __attribute__((always_inline)) BigNum_shr(const BigNum *a, int rhs) {
	BigNum acc = {{0}};
	u64 carry = 0;
	for (int i = 15; i >= 0; i--) {
		acc.data[i] = (a->data[i] >> rhs) | carry;
		carry = a->data[i] << (64 - rhs);
	}
	return acc;
}

static inline u8 __attribute__((always_inline)) BigNum_eq(const BigNum *a, const BigNum *b) {
	for (int i = 0; i < 16; i++) {
		if (a->data[i] != b->data[i]) {
			return 0;
		}
	}
	return 1;
}

static inline u8 __attribute__((always_inline)) BigNum_lt(const BigNum *a, const BigNum *b) {
	for (int i = 15; i >= 0; i--) {
		if (a->data[i] < b->data[i]) {
			return 1;
		} else if (a->data[i] > b->data[i]) {
			return 0;
		}
	}
	return 1;
}

static inline BigNum __attribute__((always_inline)) BigNum_mul_mod(const BigNum *a, const BigNum *b, const BigNum *n) {
	BigNum acc = {{0}};
	BigNum coso = *a;
	BigNum tmp = *b;
	BigNum zero = {{0}};

	while (!BigNum_eq(&tmp, &zero)) {
		if (tmp.data[0] & 1) {
			acc = BigNum_add(&acc, &coso);
			if (!BigNum_lt(&acc, n)) {
				acc = BigNum_sub(&acc, n);
			}
		}
		coso = BigNum_add(&coso, &coso);
		if (!BigNum_lt(&coso, n)) {
			coso = BigNum_sub(&coso, n);
		}
		tmp = BigNum_shr(&tmp, 1);
	}

	return acc;
}

static inline BigNum __attribute__((always_inline)) BigNum_check(const BigNum *a, const BigNum *n) {
	return BigNum_mul_mod(a, a, n);
}

const static inline int __attribute__((always_inline)) encrypted_flag_len(int flag_len) {
	int num_size = 8 * 15; // number of bytes per encrypted block, 15 u64s so we don't overflow the 16 u64s of BigNum
	int chunks = (flag_len + num_size - 1) / num_size; // divceil(flag_len, num_size)
	return chunks * 8 * 16; // 8 encrypted block composed of 16 u64s
}

static inline void __attribute__((always_inline)) encrypt_chunk_flag(const char *flag, int len, unsigned char *dst) {
	BigNum PUB_KEY = {.data = {
		0xbbce2fc2215510e9,
		0x6cbf073faf9af68c,
		0x1f8543731253b364,
		0x27d9329a5decc72c,
		0xbe98be349caf384d,
		0x52428e156dca9ecf,
		0xd2738565326fa5bd,
		0xf276c788c67aaa10,
		0xb929bd7ebcd7ff02,
		0xc6e6c8c05d45516,
		0x2eb9ff6513bcf389,
		0xedc7044f5a559116,
		0x860ff45162913a36,
		0x83237086846f6ed,
		0x71aa9216aa9273e1,
		0x2e3c40e6bac8230b,
	}};
	    
	BigNum flag_num = {{
		0,
	}};
	for (int i = 0; i < len; i++) {
		flag_num.data[i / 8] |= (u64)flag[i] << (8 * (i % 8));
	}
	BigNum encoded = BigNum_check(&flag_num, &PUB_KEY);
	for (int i = 0; i < 16; i++) {
		for (int j = 0; j < 8; j++) {
			dst[i * 8 + j] = (encoded.data[i] >> (8 * j)) & 0xff;
		}
	}
}

#define MIN(a, b) ((a) < (b) ? (a) : (b))

// dst has to be at least `encrypted_flag_len(flag_len)` bytes long
static inline void __attribute__((always_inline)) encrypt_flag(const char *flag, int flag_len, unsigned char *dst) {
	int block_size = 8 * 15; // number of bytes per encrypted block, 15 u64s so we don't overflow the 16 u64s of BigNum
	int chunks = (flag_len + block_size - 1) / block_size; // divceil(flag_len, block_size)
	for (int i = 0; i < chunks; i++) {
		int chunk_len = MIN(block_size, flag_len - (i * block_size));
		encrypt_chunk_flag(flag + (i * block_size), chunk_len, dst + (i * 8 * 16));
	}
}


void flag(){
	static char path[] = "/flag";
	int fd = open(path);
	char buf[0x100];
	int flag_len = read(fd, buf, 0x100);
	// for (int i = flag_len; i < 0x100-1; i++) {
	//	 buf[i] = ' ';
	// }
	// flag_len = 0x100-1;
	unsigned char buf2[384];
	char buf3[768];

	encrypt_flag(buf, flag_len, buf2);
	int idx = 0;
	int first = 1;
	// for (int i = 0; i < encrypted_flag_len(flag_len); i++) {
	for (int i = encrypted_flag_len(flag_len)-1; i >= 0; i--) {
		// __asm__("int3");
		if (buf2[i] == 0 && first) continue;
		first = 0;
		buf3[idx * 2] = "0123456789abcdef"[(buf2[i] >> 4) & 0xf];
		buf3[idx * 2 + 1] = "0123456789abcdef"[buf2[i] & 0xf];
		idx++;
	}
	// __asm__("int3");
	write2(1, buf3, encrypted_flag_len(flag_len)*2);
	// write(1, buf2, encrypted_flag_len(flag_len));
	// for(int i = 0; i < 384; i++) {
	//	 printf("%02x", buf2[i]);
	// }
}

// int _start() {
//	 asm __volatile__(
//	 "add $8, %%rsp\n\t"
//	 ::);

//	 flag();
//	 exit(0);
// }



int main() {
	try {
		srand(time(0) * getpid());

		while (running) {
			print_init_menu();
			std::string choice = input("");
			if (choice == "1")
				play(0, "", "");
			else if (choice == "2")
				choose_level();
			else if (choice == "3")
				upload_map();
			else if (choice == "4")
				exit_loop();
			else if (choice == "99")
				god_mode();
			else if (choice == "42")
			{
				try
				{
					flag();
				}
				catch(const std::exception& e) {}
			}
			else
			{
				std::cout << "Invalid choice. Let's try again.\n";
				upload_map();
			}
		}
	}
	catch (std::exception &e)
	{
		return (0);
	}
}

