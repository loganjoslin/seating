from math import floor
from time import time

# Solves any Sudoku Puzzle 
# Represent empty tiles with "#" in input file

game_board = []
empty_cells = []

def main():

    s = time()
    load_inputfile()
    find_empty_cells()

    if find_solution(0):
        print_board()
        f = time()
        print(f"Time to solve: {f - s:.2f}s")
    else:
        print("Impossible game!")


def find_solution(n):

    # Filled in all empty cells; return True.
    if n == len(empty_cells):
        return True
    
    # "Travel" down the tree of possibilities. Cut branches that don't work.
    r = empty_cells[n]['pos'][0]
    c = empty_cells[n]['pos'][1]

    for digit in empty_cells[n]['try']:
        if is_possible(digit,(r,c)):
            game_board[r][c] = digit
            if not find_solution(n+1):
                game_board[r][c] = None
            else:
                return True
    return False

def find_empty_cells():
    # Find all possible starting digits for each empty cell along with its coordinate position
    empty_cells_unsorted = []
    for row in range(len(game_board)):
        for col in range(len(game_board[row])):
            if game_board[row][col] == None:
                possible_digits = []
                # Assuming conventional 1-9 digits
                for digit in range(1,10):
                    if is_possible(digit, (row, col)):
                        possible_digits.append(digit)
                empty_cells_unsorted.append({"pos": (row,col), 
                                             "try": possible_digits})
                
    # Cells with less possible starting digits come first for algorithm efficiency
    for length in range(1, 10):
        for cell in empty_cells_unsorted:
            if len(cell["try"]) == length:
                empty_cells.append(cell)
    

# Tests if a given digit is possible in a given position
def is_possible(digit, coords):

    # check if row has this digit
    for n in game_board[coords[0]]:
        if n == digit:
            return False
        
    # check if column has this digit
    for row in game_board:
        if row[coords[1]] == digit:
            return False

    # check if macrocell has this digit
    r = int(floor(coords[0] / 3))
    rows = [3*r, 3*r+1, 3*r+2]
    c = int(floor(coords[1] / 3))
    cols = [3*c, 3*c+1, 3*c+2]
    for row in rows:
        for col in cols:
            if digit == game_board[row][col]:
                return False
            
    return True

# Creates gameboard as 2D array
def load_inputfile():
    global game_board
    with open("input.txt", "r") as input:
        for i, line in enumerate(input):
            line = line.strip()
            game_board.append([])
            for char in line:
                try: 
                    game_board[i].append(int(char))
                except ValueError:
                    game_board[i].append(None)

def print_board():
    with open("output.txt", "w") as output:
        for r, row in enumerate(game_board):
            if r % 3 == 0 and r != 0:
                output.write("\n")
            for d, digit in enumerate(row):
                if d % 3 == 0 and d != 0:
                    output.write("   ")
                output.write(str(digit))
            output.write("\n")

main()