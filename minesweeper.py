#!/usr/bin/env python3
"""A quick implementation of the classic Minesweeper on a console, implemented
as a practice problem before a coding interview. Plenty of room for
improvement.

This program is copyright (c) 2019 by Patrick Mooney. It is licensed under the
terms of the GNU GPL, either version 3 or (at your option) any later version.
See the file LICENSE.md for a copy of this license.

Though I hope that this program is helpful to you, I disclaim ALL
RESPONSIBILITY for the performance of the code. More specifically, I disclaim
all claims of MERCHANTABILITY or FITNESS FOR ANY PARTICULAR PURPOSE. In no case
will the author of this program be liable for damages in excess of the price
paid to the author for purchase.
"""

import random


# constants. #FIXME: make these command-line overrideable.
terminal_width = 80
terminal_height = 24
number_of_mines = 7

# Thanks to FIGlet for these next two.
boom_text = """
    ____  ____  ____  __  _____
   / __ )/ __ \/ __ \/  |/  / /
  / __  / / / / / / / /|_/ / / 
 / /_/ / /_/ / /_/ / /  / /_/  
/_____/\____/\____/_/  /_(_)   
"""

win_text = """
__  __                        _       __
\ \/ /___  __  __   _      __(_)___  / /
 \  / __ \/ / / /  | | /| / / / __ \/ / 
 / / /_/ / /_/ /   | |/ |/ / / / / /_/  
/_/\____/\__,_/    |__/|__/_/_/ /_(_)   
"""

board_width = None      # these will be calculated automatically based on terminal width and height.
board_height = None     # we just want them defined in the global namespace.

# global variables.
board = [][:]           # The actual board, unseen by the player.
display_board = [][:]   # The display that the player sees, containing information the player has deduced.
done = False


def parse_command_line():
    """Parse the command line."""
    pass        #FIXME


def print_spacer_row():
    """Print a row of dashes, e.g. at the top and bottom of the board, and between
    lines.
    """
    print('-' * (1 + 2 * board_width))


def reveal_mines():
    """Print the location of the mines."""
    global board, display_board
    print_spacer_row()
    for y, row in enumerate(board):
        display_row = ['|'] + ['*|' if item else (display_board[y][x] + '|') for x, item in enumerate(row)]
        print(''.join(display_row))
        print_spacer_row()


def display_known_board():
    """Display what the user knows about the board."""
    global board, display_board
    print_spacer_row()
    for row in display_board:
        print('|' + ''.join([item + '|' for item in row]))
        print_spacer_row()


def display_help():
    print("\nAt each iteration, type any of the following commands:\n")
    print("Q:\tReveal the map and quit the game.")
    print("H:\tDisplay this help text again.")
    print("R x,y:\tReveal the contents of the square square at (zero-based) x, y.")
    print("M x,y:\tMark the square at (zero-based) x, y as containing a mine.\n")
    print("\n\nPress ENTER to continue")
    _ = input()


def menu(prompt: str, options: list) -> str:
    """Display PROMPT, then keep asking the user for input until the first character
    of user input is in OPTIONS (case-insensitive match). Returns the user's exact
    input.
    """
    for i in options:
        assert type(i) == type('y'), "ERROR: the OPTIONS list may only contain strings!"
        assert len(i) > 0, "ERROR: the OPTIONS list may not contain empty strings!"
    answered = False
    prompt = prompt.strip() + "  ["
    prompt += ' / '.join([i.upper() if len(i) < 2 else (i[0].upper() + i[1:]) for i in options])
    prompt += "] "
    while not answered:
        ans = input(prompt)
        answered = (len(ans) >= 1) and (ans[0].lower() in [i.lower()[0] for i in options])
    return ans


def intro():
    """Quick overview, then offer UI interaction instructions."""
    print("\n\nMinesweeper 0.2 by Patrick Mooney.\nCopyright 2019, licensed under GPL v3+.\n")
    ans = menu("Instructions?", ['y', 'n'])
    if ans[0] == "y":
        display_help()

def set_up():
    """Set up basic game parameters"""
    global board_height, board_width
    global board, display_board

    parse_command_line()
    board_width = terminal_width // 3
    board_height = (terminal_height - 3) // 3   # We'll need some space at the bottom to interact w/ user!

    intro()

    board = [][:]
    for i in range(0, board_height):
        board.append([False] * board_width)
    num_spaces = board_width * board_height
    mine_positions = random.sample(range(0, num_spaces), number_of_mines)
    for mine in mine_positions:
        board[(mine // board_width)][(mine % board_width)] = True

    display_board = [][:]
    for i in range(0, board_height):
        display_board.append([' '] * board_width)


def count_neighboring_mines(x, y: int) -> int:
    """Count the number of mines in neighboring squares."""
    global board
    count = 0
    for x_pos in range(x-1, x+2):
        for y_pos in range(y-1, y+2):
            try:
                if x_pos > -1 and y_pos > -1:
                    if board[y_pos][x_pos]:
                        count += 1
            except IndexError:
                pass
    return count


def parse_coordinates(entry) -> tuple:
    """"""
    entry = ''.join([i for i in entry if i.isdigit() or i == ','])  # Simplistic, but good enough for now.
    try:
        x, y = tuple(entry.split(','))      # unpack, assuming that the user made a valid entry.
        x, y = int(x), int(y)
    except ValueError:                      # Of course, not all entries are actually parseable.
        print("Error! Coordinates must have two integers separated by a comma.")
        return None, None
    if (x < 0) or (x > (board_width - 1)):
        print("Error! The highest-numbered column is %s." % board_width - 1)
        return None, None
    if (y < 0) or (y > (board_height -1)):
        print("Error! The highest-numbered row is %s." % board_height - 1)
        return None, None
    return x, y

def do_reveal(entry: str):
    """Parse (simply) the user's input (ENTRY) and deal with the results.
    The format of a REVEAL command is R x,y, where x,y is the zero-based location
    of the square to reveal. Note that the comma is mandatory. Note also that the
    menu() function will have assured us that the command does in fact begin with
    the letter R, but not that there are no other characters between that R and
    the first number. We start by stripping everything that's not a digit or comma.
    """
    global done
    global board, display_board
    x, y = parse_coordinates(entry)
    if x == None or y == None:          # We've already printed an error message.
        return
    if board[y][x]:
        print(boom_text)
        reveal_mines()
        done = True
        return
    # Otherwise, calculate new information about the square revealed.
    display_board[y][x] = str(count_neighboring_mines(x, y))


def check_for_win():
    """Check to see if the user has won. If so, print a winning message and
    set the global variable DONE to True to force ending after we return.
    """
    global done
    global board, display_board

    correctly_marked = 0
    for y_pos, row in enumerate(display_board):
        for x_pos, column in enumerate(row):
            if column == "*":
                if not board[y_pos][x_pos]:
                    return                          # One incorrect mark means we're not done.
                else:
                    correctly_marked += 1
    # If we got this far, we don't have any incorrectly marked. Do we have the correct number of marks?
    if correctly_marked == number_of_mines:
        print(win_text)
        done = True


def do_mark(entry: str):
    """Parse the user input for a string of the form M x,y as containing a mine.
    ENTRY is the user's full input, which is broken down and processed. If x,y is
    already marked as containing a mine, unmark it.

    If the user has correctly marked all mines, s/he wins!
    """
    global done
    global board, display_board
    x, y = parse_coordinates(entry)
    if display_board[y][x] == '*':
        display_board[y][x] = ' '
    elif display_board[y][x] == ' ':
        display_board[y][x] = '*'
        check_for_win()
    else:
        print("Error: %s, %s is already known not to contain a mine." % (x, y))


def process_input():
    """Get and process user input."""
    global done
    ans = menu("What now?", ['Q', 'H', 'R x,y', 'M x,y'])
    if ans.lower()[0] == 'q':
        done = True
        reveal_mines()
    elif ans.lower()[0] == "h":
        display_help()
    elif ans.lower()[0] == 'r':
        do_reveal(ans)
    elif ans.lower()[0] == 'm':
        do_mark(ans)
    else:
        raise RuntimeError("menu() is not validating input correctly!")

def main_loop():
    global done
    while not done:
        display_known_board()
        process_input()


def main():
    set_up()
    main_loop()

if __name__ == "__main__":
    main()
