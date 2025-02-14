# Philip Carlsson-Coulombe
# 40208572

# David R Cronin
# 28840024

# COEN 472 Artificial Intelligence
# Deliverable 1 (H vs H)

import math
import copy
import time
import argparse

class MiniChess:
    def __init__(self):
        self.current_game_state = self.init_board()
        self.turn_number = 1  # Track the turn number
        self.timeout = 60  # Example timeout value (in seconds)
        self.max_turns = 100  # Example maximum number of turns
        self.play_mode = "H-H"  # Play mode for D1
        self.trace_file = None  # File object for logging

    """
    Initialize the board

    Args:
        - None
    Returns:
        - state: A dictionary representing the state of the game
    """
    def init_board(self):
        state = {
                "board": 
                [['bK', 'bQ', 'bB', 'bN', '.'],
                ['.', '.', 'bp', 'bp', '.'],
                ['.', '.', '.', '.', '.'],
                ['.', 'wp', 'wp', '.', '.'],
                ['.', 'wN', 'wB', 'wQ', 'wK']],
                "turn": 'white',
                }
        return state

    """
    Prints the board
    
    Args:
        - game_state: Dictionary representing the current game state
    Returns:
        - None
    """
    def display_board(self, game_state):
        print()
        for i, row in enumerate(game_state["board"], start=1):
            print(str(6-i) + "  " + ' '.join(piece.rjust(3) for piece in row))
        print()
        print("     A   B   C   D   E")
        print()

    """
    Returns a list of valid moves

    Args:
        - game_state:   dictionary | Dictionary representing the current game state
    Returns:
        - valid moves:   list | A list of nested tuples corresponding to valid moves [((start_row, start_col),(end_row, end_col))]
    """
    def valid_moves(self, game_state):
        board = game_state["board"]
        turn = game_state["turn"]
        moves = []

        piece_valid_moves = {
            'K': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],  # King
            'Q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],  # Queen
            'N': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],  # Knight
            'B': [(1, 1), (-1, -1), (1, -1), (-1, 1)],  # Bishop
        }

        for r in range(5):
            for c in range(5):
                piece = board[r][c] # get piece at position [r,c]
                if piece == '.':
                    continue
                
                piece_type = piece[1] # get first character
                piece_color = "white" if piece[0] == 'w' else "black"

                if piece_color != turn: # ignore pieces if not their turn
                    continue

                if piece_type in piece_valid_moves:
                    for dr, dc in piece_valid_moves[piece_type]:
                        for step in range(1, 5): # max displacement is 4 squares
                            nr, nc = r + dr * step, c + dc * step
                            if not (0 <= nr < 5 and 0 <= nc < 5):  # Out of bounds
                                break
                            target = board[nr][nc]
                            if target == '.':  # Empty square
                                moves.append(((r, c), (nr, nc)))
                            elif target[0] != piece[0]:
                                moves.append(((r, c), (nr, nc)))
                                break
                            else:  # Friendly piece
                                break
                            if piece_type in "KN":  # Knights and Kings move once
                                break

                elif piece_type == 'p':  # Pawn movement
                    direction = -1 if piece_color == "white" else 1
                    nr, nc = r + direction, c
                    if 0 <= nr < 5 and board[nr][nc] == '.':  # Normal move
                        moves.append(((r, c), (nr, nc)))
                    for dc in [-1, 1]:  # Capture diagonally
                        nr, nc = r + direction, c + dc
                        if 0 <= nr < 5 and 0 <= nc < 5 and board[nr][nc] != '.' and board[nr][nc][0] != piece[0]:
                            moves.append(((r, c), (nr, nc)))

        return moves

    """
    Check if the move is valid    
    
    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move which we check the validity of ((start_row, start_col),(end_row, end_col))
    Returns:
        - boolean representing the validity of the move
    """
    def is_valid_move(self, game_state, move):
        return move in self.valid_moves(game_state)

    """
    Check if the move is a capture and if it is GAME OVER    
    
    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move which we check the validity of ((start_row, start_col),(end_row, end_col))
    Returns:
        - returns content of the opponent piece if it is a capture, otherwise None
    """
    def is_capture(self, game_state, move):
        start, end = move
        piece = game_state["board"][start[0]][start[1]]
        target = game_state["board"][end[0]][end[1]]
        if target != '.' and target[0] != piece[0]:
            return target
        return 'none'

    """
    Check if the move is 'queening' to set change from xP to xQ    
    
    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move which we check the validity of ((start_row, start_col),(end_row, end_col))
    Returns:
        - boolean representing if the move is a 'queening'
    """
    def is_queening(self, game_state, move):
        start, end = move
        piece = game_state["board"][start[0]][start[1]]
        if piece[1] == 'p' and (end[0] == 0 or end[0] == 4):
            return True

    """
    Modify the board to make a move

    Args: 
        - game_state:   dictionary | Dictionary representing the current game state
        - move          tuple | the move to perform ((start_row, start_col),(end_row, end_col))
    Returns:
        - game_state:   dictionary | Dictionary representing the modified game state
    """
    def make_move(self, game_state, move):
        start = move[0]
        end = move[1]
        start_row, start_col = start
        end_row, end_col = end
        piece = game_state["board"][start_row][start_col]

        if piece[1] == 'p' and ((piece[0] == 'w' and end_row == 0) or (piece[0] == 'b' and end_row == 4)):
            game_state["board"][end_row][end_col] = piece[0] + 'Q'
        else:
            game_state["board"][end_row][end_col] = piece
        game_state["board"][start_row][start_col] = '.'
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"

        return game_state

    """
    Parse the input string and modify it into board coordinates

    Args:
        - move: string representing a move "B2 B3"
    Returns:
        - (start, end)  tuple | the move to perform ((start_row, start_col),(end_row, end_col))
    """
    def parse_input(self, move):
        try:
            start, end = move.split()
            start = (5-int(start[1]), ord(start[0].upper()) - ord('A'))
            end = (5-int(end[1]), ord(end[0].upper()) - ord('A'))
            return (start, end)
        except:
            return None

    """
    Write the game trace to a file

    Args:
        - move: tuple | the move to perform ((start_row, start_col),(end_row, end_col))
    Returns:
        - None
    """
    def write_trace_file(self, move):
        if not self.trace_file:
            # Create the trace file at the start of the game
            filename = f"gameTrace-false-{self.timeout}-{self.max_turns}.txt"
            self.trace_file = open(filename, "w")
            # Write game parameters
            self.trace_file.write(f"Game Parameters:\n")
            self.trace_file.write(f"Timeout: {self.timeout} seconds\n")
            self.trace_file.write(f"Max Turns: {self.max_turns}\n")
            self.trace_file.write(f"Play Mode: {self.play_mode}\n\n")
            # Write initial board configuration
            self.trace_file.write("Initial Board Configuration:\n")
            self.trace_file.write(self.board_to_string(self.current_game_state["board"]) + "\n\n")

        # Write move details
        self.trace_file.write(f"Turn #{self.turn_number}: {self.current_game_state['turn'].capitalize()} to move\n")
        self.trace_file.write(f"Action: {self.move_to_string(move)}\n")
        self.trace_file.write("New Board Configuration:\n")
        self.trace_file.write(self.board_to_string(self.current_game_state["board"]) + "\n\n")

    """
    Convert a move to string format (e.g., "B2 B3")

    Args:
        - move: tuple | the move to perform ((start_row, start_col),(end_row, end_col))
    Returns:
        - str | the move in string format
    """
    def move_to_string(self, move):
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        return f"{chr(ord('A') + start_col)}{5 - start_row} {chr(ord('A') + end_col)}{5 - end_row}"

    """
    Convert the board to a string representation

    Args:
        - board: list | the board configuration
    Returns:
        - str | the board as a string
    """
    def board_to_string(self, board):
        return '\n'.join([' '.join(piece.rjust(3) for piece in row) for row in board])

    """
    Game loop

    Args:
        - None
    Returns:
        - None
    """
    def play(self):
        print("\n\nWelcome to Mini Chess!\nPlease Select Game Mode: [0] H-H, [1] H-Ai, [2] Ai-Ai")

        enable = True
        while enable:
            mode = input("input: ")
            if mode == "0" : enable = False
            else: print("\nFeatures currently not available\nPlease Select Game Mode: [0] H-H, [1] H-Ai, [2] Ai-Ai")

        while True:
            self.display_board(self.current_game_state)
            move = input(f"{self.current_game_state['turn'].capitalize()} to move: ")
            if move.lower() == 'exit':
                print("Game exited.")
                if self.trace_file:
                    self.trace_file.close()
                exit(1)

            move = self.parse_input(move)
            if not move or not self.is_valid_move(self.current_game_state, move):
                print("Invalid move. Try again.")
                continue

            target = self.is_capture(self.current_game_state, move)
            if (target) in ['wK', 'bK']:
                print(' ** GAME OVER **')
                if self.trace_file:
                    self.trace_file.write(f"Game Over: {self.current_game_state['turn'].capitalize()} wins!\n")
                    self.trace_file.close()
                exit(1)

            if target != 'none':
                print('Capture! ', target, 'is enslaved.')

            if self.is_queening(self.current_game_state, move):
                start, end = move
                piece = self.current_game_state["board"][start[0]][start[1]]
                self.current_game_state["board"][end[0]][end[1]] = piece[0] + 'Q'
                print('Queening! Pawn promoted to Queen.')

            self.make_move(self.current_game_state, move)
            self.write_trace_file(move)  # Log the move
            self.turn_number += 1

if __name__ == "__main__":
    game = MiniChess()
    game.play()