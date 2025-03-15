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
        # initialize the game
        self.current_game_state = self.init_board()
        self.turn_number = 1  # now represents a full turn (White + Black)
        self.timeout = 360  # time limit per move (seconds)
        self.max_turns = 20  # max number of moves without capture before declaring a draw (this value is in half-moves)
        self.play_mode = "H-H"  # default mode
        self.trace_file = None
        self.eval_choice = None  # "e0" for board evaluation, "e1" for capture value
        self.moves_without_capture = 0  # counter for moves with no capture

    def init_board(self):
        state = {
            "board": 
            [['bK', 'bQ', 'bB', 'bN', '.'], 
             ['.', '.', 'bp', 'bp', '.'], 
             ['.', '.', '.', '.', '.'],     
             ['.', 'wp', 'wp', '.', '.'],    
             ['.', 'wN', 'wB', 'wQ', 'wK']], 
            "turn": 'white',  # white goes first
        }
        return state

    def display_board(self, game_state):
        print()
        for i, row in enumerate(game_state["board"], start=1):
            print(str(6 - i) + "  " + ' '.join(piece.rjust(3) for piece in row))
        print()
        print("     A   B   C   D   E")
        print()

    def display_valid_moves(self, game_state):
        moves = self.valid_moves(game_state)
        move_strings = [f"{self.move_to_string(move_dict['move'])}:{move_dict['value']}" for move_dict in moves]
        print("List of Valid Moves: " + " - ".join(move_strings))

    def calculate_e1_value(self, target):
        """
        Calculate the move value based on the target piece (e1 evaluation).
        Uses capture_values: king=999, queen=9, bishop=3, knight=3, pawn=1.
        """
        capture_values = {'k': 999, 'q': 9, 'b': 3, 'n': 3, 'p': 1}
        if target != '.' and len(target) > 1:
            cap_type = target[1].lower()
            return capture_values.get(cap_type, 0)
        return 0

    def calculate_e0_value(self, board):
        """
        Evaluate the board position (e0 evaluation) as:
        (#wp + 3*#wB + 3*#wN + 9*#wQ + 999*#wK) -
        (#bp + 3*#bB + 3*#bN + 9*#bQ + 999*#bK)
        The values 1, 3, 9, and 999 are taken from the capture_values mapping.
        """
        capture_values = {'k': 999, 'q': 9, 'b': 3, 'n': 3, 'p': 1}
        total = 0
        for row in board:
            for piece in row:
                if piece != '.':
                    piece_val = capture_values.get(piece[1].lower(), 0)
                    if piece[0] == 'w':
                        total += piece_val
                    else:
                        total -= piece_val
        return total

    def valid_moves(self, game_state):
        board = game_state["board"]
        turn = game_state["turn"]
        moves = []  # This will store dictionaries with "move" and "value" keys

        piece_valid_moves = {
            'K': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],
            'Q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],
            'N': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
            'B': [(1, 1), (-1, -1), (1, -1), (-1, 1)],
        }

        for row in range(5):
            for col in range(5):
                piece = board[row][col]
                if piece == '.':
                    continue

                piece_type = piece[1]
                piece_color = "white" if piece[0] == 'w' else "black"

                if piece_color != turn:
                    continue

                if piece_type in piece_valid_moves:
                    for d_row, d_col in piece_valid_moves[piece_type]:
                        for step in range(1, 5):
                            n_row, n_col = row + d_row * step, col + d_col * step
                            if not (0 <= n_row < 5 and 0 <= n_col < 5):
                                break
                            target = board[n_row][n_col]
                            if self.eval_choice == "e1":
                                if target == '.':
                                    moves.append({"move": ((row, col), (n_row, n_col)), "value": 0})
                                elif target[0] != piece[0]:
                                    value = self.calculate_e1_value(target)
                                    moves.append({"move": ((row, col), (n_row, n_col)), "value": value})
                                    break
                                else:
                                    break
                            elif self.eval_choice == "e0":
                                new_state = copy.deepcopy(game_state)
                                new_state = self.make_move(new_state, ((row, col), (n_row, n_col)))
                                value = self.calculate_e0_value(new_state["board"])
                                if game_state["turn"] == "black":
                                    value = -value
                                moves.append({"move": ((row, col), (n_row, n_col)), "value": value})
                                if target != '.':
                                    break
                            if piece_type in "KN":
                                break

                elif piece_type == 'p': 
                    direction = -1 if piece_color == "white" else 1
                    # Pawn forward move
                    n_row, n_col = row + direction, col
                    if 0 <= n_row < 5 and board[n_row][n_col] == '.':
                        if self.eval_choice == "e1":
                            moves.append({"move": ((row, col), (n_row, n_col)), "value": 0})
                        elif self.eval_choice == "e0":
                            new_state = copy.deepcopy(game_state)
                            new_state = self.make_move(new_state, ((row, col), (n_row, n_col)))
                            value = self.calculate_e0_value(new_state["board"])
                            if game_state["turn"] == "black":
                                value = -value
                            moves.append({"move": ((row, col), (n_row, n_col)), "value": value})
                    # Pawn diagonal capture moves
                    for d_col in [-1, 1]:
                        n_row, n_col = row + direction, col + d_col
                        if 0 <= n_row < 5 and 0 <= n_col < 5 and board[n_row][n_col] != '.':
                            if board[n_row][n_col][0] != piece[0]:
                                if self.eval_choice == "e1":
                                    move_value = self.calculate_e1_value(board[n_row][n_col])
                                    moves.append({"move": ((row, col), (n_row, n_col)), "value": move_value})
                                elif self.eval_choice == "e0":
                                    new_state = copy.deepcopy(game_state)
                                    new_state = self.make_move(new_state, ((row, col), (n_row, n_col)))
                                    value = self.calculate_e0_value(new_state["board"])
                                    if game_state["turn"] == "black":
                                        value = -value
                                    moves.append({"move": ((row, col), (n_row, n_col)), "value": value})
        moves.sort(key=lambda m: m["value"], reverse=True)
        return moves

    def is_valid_move(self, game_state, move):
        for move_dict in self.valid_moves(game_state):
            if move_dict["move"] == move:
                return True
        return False

    def is_capture(self, game_state, move):
        start, end = move
        piece = game_state["board"][start[0]][start[1]]
        target = game_state["board"][end[0]][end[1]]
        if target != '.' and target[0] != piece[0]:
            return target
        return 'none'

    def is_queening(self, game_state, move):
        start, end = move
        piece = game_state["board"][start[0]][start[1]]
        if piece[1] == 'p' and (end[0] == 0 or end[0] == 4):
            return True

    def make_move(self, game_state, move):
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        piece = game_state["board"][start_row][start_col]

        if piece[1] == 'p' and ((piece[0] == 'w' and end_row == 0) or (piece[0] == 'b' and end_row == 4)):
            game_state["board"][end_row][end_col] = piece[0] + 'Q'
        else:
            game_state["board"][end_row][end_col] = piece 
        game_state["board"][start_row][start_col] = '.'
        # Toggle the turn.
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white" 
        return game_state

    def parse_input(self, move):
        try:
            start, end = move.split()
            start = (5 - int(start[1]), ord(start[0].upper()) - ord('A'))
            end = (5 - int(end[1]), ord(end[0].upper()) - ord('A'))
            return (start, end)
        except:
            return None

    def write_trace_file(self, move):
        if not self.trace_file:
            filename = f"gameTrace-false-{self.timeout}-{self.max_turns}.txt"
            self.trace_file = open(filename, "w")
            self.trace_file.write("Game Parameters:\n")
            self.trace_file.write(f"Timeout: {self.timeout} seconds\n")
            self.trace_file.write(f"Max Turns (moves without capture): {self.max_turns}\n")
            self.trace_file.write(f"Play Mode: {self.play_mode}\n\n")
            self.trace_file.write("Initial Board Configuration:\n")
            self.trace_file.write(self.board_to_string(self.current_game_state["board"]) + "\n\n")

        if move is not None:
            # In the trace file, we still report the turn number as stored.
            next_turn = self.current_game_state['turn'].capitalize()
            next_turn = "White" if next_turn == "Black" else "Black"
            self.trace_file.write(f"Turn #{self.turn_number}: {next_turn} to move\n")
            self.trace_file.write(f"Action: {self.move_to_string(move)}\n")
            self.trace_file.write("New Board Configuration:\n")
            self.trace_file.write(self.board_to_string(self.current_game_state["board"]) + "\n\n")

    def move_to_string(self, move):
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        return f"{chr(ord('A') + start_col)}{5 - start_row} {chr(ord('A') + end_col)}{5 - end_row}"

    def board_to_string(self, board):
        lines = []
        for i, row in enumerate(board, start=1):
            line = f"{6 - i}  " + ' '.join(piece.rjust(3) for piece in row)
            lines.append(line)
        lines.append("     A   B   C   D   E")
        return "\n".join(lines)

    def play(self):
        print("\n\nWelcome to Mini Chess!")
        print("Please Select Game Mode: [0] H-H, [1] H-Ai, [2] Ai-Ai")
        
        enable = True
        while enable:
            mode = input("input: ")
            if mode == "0":
                enable = False
            else:
                print("\nFeatures currently not available")
                print("Please Select Game Mode: [0] H-H, [1] H-Ai, [2] Ai-Ai")

        # Choose evaluation method for move values
        eval_enable = True
        while eval_enable:
            choice = input("Choose evaluation type for move values: [0] e0, [1] e1: ")
            if choice == "0":
                self.eval_choice = "e0"
                eval_enable = False
            elif choice == "1":
                self.eval_choice = "e1"
                eval_enable = False
            else:
                print("Invalid choice. Please enter 0 or 1.")

        self.write_trace_file(None)
        # Reset turn_number; now it represents full turns.
        self.turn_number = 1
        
        while True:
            self.display_board(self.current_game_state)
            self.display_valid_moves(self.current_game_state)
            # Store current mover (either "white" or "black")
            current_mover = self.current_game_state["turn"]
            move = input(f"Turn {self.turn_number}: {current_mover.capitalize()} to move: ")
            if move.lower() == 'exit':
                print("Game exited.")
                if self.trace_file:
                    self.trace_file.close()
                exit(1)

            move = self.parse_input(move)
            if not move or not self.is_valid_move(self.current_game_state, move):
                print("Invalid move. Try again.")
                continue

            # Check for capture before applying the move
            target = self.is_capture(self.current_game_state, move)
            if target in ['wK', 'bK']:
                self.make_move(self.current_game_state, move)
                self.write_trace_file(move)
                print(' ** GAME OVER **')
                if self.trace_file:
                    next_turn = self.current_game_state['turn'].capitalize()
                    next_turn = "White" if next_turn == "Black" else "Black"
                    self.trace_file.write(f"Game Over: {next_turn} wins!\n")
                    self.trace_file.close()
                exit(1)

            # Update moves_without_capture counter.
            if target != 'none':
                print('Capture! ', target, 'is enslaved.')
                self.moves_without_capture = 0
            else:
                self.moves_without_capture += 1

            # Check if draw condition is met.
            if self.moves_without_capture >= self.max_turns:
                print("** DRAW **")
                if self.trace_file:
                    self.trace_file.write("Game Over: DRAW\n")
                    self.trace_file.close()
                exit(0)

            if self.is_queening(self.current_game_state, move):
                start, end = move
                piece = self.current_game_state["board"][start[0]][start[1]]
                self.current_game_state["board"][end[0]][end[1]] = piece[0] + 'Q'
                print('Queening! Pawn promoted to Queen.')

            # Execute the move.
            self.make_move(self.current_game_state, move)
            self.write_trace_file(move)
            
            # If Black just moved, increment the turn number (as a full turn is complete)
            if current_mover == "black":
                self.turn_number += 1

if __name__ == "__main__":
    game = MiniChess()
    game.play()
