# Philip Carlsson-Coulombe
# 40208572
# COEN 472 Artificial Intelligence
# Deliverable 1 (H vs H)

import math
import copy
import time
import argparse

class MiniChess:
    def __init__(self):
        self.current_game_state = self.init_board()

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
        game_state["board"][start_row][start_col] = '.'
        game_state["board"][end_row][end_col] = piece
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
                exit(1)

            move = self.parse_input(move)
            if not move or not self.is_valid_move(self.current_game_state, move):
                print("Invalid move. Try again.")
                continue

            target = self.is_capture(self.current_game_state, move)
            if (target) in ['wK', 'bK']:
                print(' ** GAME OVER **')
                break

            self.make_move(self.current_game_state, move)

if __name__ == "__main__":
    game = MiniChess()
    game.play()
