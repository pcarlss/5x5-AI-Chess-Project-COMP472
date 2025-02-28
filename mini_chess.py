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
        self.turn_number = 1  # how many turns have been played
        self.timeout = 360  # time limit per move (seconds)
        self.max_turns = 100  # max number of turns
        self.play_mode = "H-H"  # default mode
        self.trace_file = None

    # initial board state
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

    # display state of the board
    def display_board(self, game_state):
        print()
        for i, row in enumerate(game_state["board"], start=1):
            print(str(6-i) + "  " + ' '.join(piece.rjust(3) for piece in row))
        print()
        print("     A   B   C   D   E")
        print()

    # NEW: display the list of valid moves (for debugging/display purposes)
    def display_valid_moves(self, game_state):
        moves = self.valid_moves(game_state)
        # Build a list of move strings formatted as "B2 B3:0"
        move_strings = [f"{self.move_to_string(move_dict['move'])}:{move_dict['value']}" for move_dict in moves]
        # Print all moves on one line separated by " - "
        print("List of Valid Moves: " + " - ".join(move_strings))


    # generate all valid moves that turn
    def valid_moves(self, game_state, add_bonus=True):
        board = game_state["board"]
        turn = game_state["turn"]
        moves = []  # This will store dictionaries with "move" and "value" keys

        # Mapping for capture values: king=5, queen=4, bishop=3, knight=2, pawn=1.
        capture_values = {'k': 5, 'q': 4, 'b': 3, 'n': 2, 'p': 1}

        # how each piece can move
        piece_valid_moves = {
            'K': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],  # King moves
            'Q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],  # Queen moves
            'N': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],  # Knight moves
            'B': [(1, 1), (-1, -1), (1, -1), (-1, 1)],  # Bishop moves
        }

        # loop through the board, finding all valid moves for each piece
        for row in range(5):
            for col in range(5):
                piece = board[row][col]  # value of specific piece at that point in loop
                if piece == '.':  # skip empty squares
                    continue
                
                piece_type = piece[1]  # get piece type
                piece_color = "white" if piece[0] == 'w' else "black"

                if piece_color != turn:  # skip piece if not its turn
                    continue

                if piece_type in piece_valid_moves:
                    for d_row, d_col in piece_valid_moves[piece_type]:
                        for step in range(1, 5):  # board is 5x5 cells
                            n_row, n_col = row + d_row * step, col + d_col * step
                            if not (0 <= n_row < 5 and 0 <= n_col < 5):  # out of bound
                                break
                            target = board[n_row][n_col]
                            # Determine the base value: 0 if no capture; if capture then use mapping
                            if target == '.':  # no capture
                                base_value = 0
                            elif target[0] != piece[0]:  # capture detected
                                cap_type = target[1].lower()  # captured piece type in lowercase
                                base_value = capture_values.get(cap_type, 0)
                            else:
                                break

                            candidate_move = ((row, col), (n_row, n_col))
                            
                            # Lookahead bonus: simulate the move and check for next-move capture opportunities.
                            if add_bonus:
                                temp_state = copy.deepcopy(game_state)
                                temp_state = self.make_move(temp_state, candidate_move)
                                # Reset turn to the mover to check for immediate capture opportunities.
                                temp_state["turn"] = turn
                                next_moves = self.valid_moves(temp_state, add_bonus=False)
                                # Instead of a fixed bonus, add the maximum capture value from the next moves.
                                bonus = max([m["value"] for m in next_moves], default=0)
                                base_value += bonus

                            moves.append({"move": candidate_move, "value": base_value})
                            # For capture moves, stop looking further in that direction.
                            if target != '.' and target[0] != piece[0]:
                                break
                            if piece_type in "KN":  # knights and kings move only one step
                                break

                elif piece_type == 'p': 
                    direction = -1 if piece_color == "white" else 1  # pawn moves forward
                    # Forward move (non-capture)
                    n_row, n_col = row + direction, col
                    if 0 <= n_row < 5 and board[n_row][n_col] == '.':
                        base_value = 0
                        candidate_move = ((row, col), (n_row, n_col))
                        if add_bonus:
                            temp_state = copy.deepcopy(game_state)
                            temp_state = self.make_move(temp_state, candidate_move)
                            temp_state["turn"] = turn
                            next_moves = self.valid_moves(temp_state, add_bonus=False)
                            bonus = max([m["value"] for m in next_moves], default=0)
                            base_value += bonus
                        moves.append({"move": candidate_move, "value": base_value})
                    # Diagonal capture moves for pawn
                    for d_col in [-1, 1]:
                        n_row, n_col = row + direction, col + d_col
                        if 0 <= n_row < 5 and 0 <= n_col < 5 and board[n_row][n_col] != '.':
                            if board[n_row][n_col][0] != piece[0]:
                                cap_type = board[n_row][n_col][1].lower()
                                base_value = capture_values.get(cap_type, 0)
                                candidate_move = ((row, col), (n_row, n_col))
                                if add_bonus:
                                    temp_state = copy.deepcopy(game_state)
                                    temp_state = self.make_move(temp_state, candidate_move)
                                    temp_state["turn"] = turn
                                    next_moves = self.valid_moves(temp_state, add_bonus=False)
                                    bonus = max([m["value"] for m in next_moves], default=0)
                                    base_value += bonus
                                moves.append({"move": candidate_move, "value": base_value})
        # Order the moves from highest to lowest value.
        moves.sort(key=lambda m: m["value"], reverse=True)
        return moves

    
    # Modified is_valid_move to work with dictionary data structure in valid_moves
    def is_valid_move(self, game_state, move):
        for move_dict in self.valid_moves(game_state):
            if move_dict["move"] == move:
                return True
        return False

    def is_capture(self, game_state, move):
        start, end = move
        piece = game_state["board"][start[0]][start[1]]
        target = game_state["board"][end[0]][end[1]]
        if target != '.' and target[0] != piece[0]:  # If the target is an opponent's piece
            return target
        return 'none'

    def is_queening(self, game_state, move):
        start, end = move
        piece = game_state["board"][start[0]][start[1]]
        if piece[1] == 'p' and (end[0] == 0 or end[0] == 4):  # Pawn reaches the last row
            return True

    # update the board after move
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
        game_state["board"][start_row][start_col] = '.'  # replace current position with empty square
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white" 

        return game_state

    # user input transform -> board coordinates
    def parse_input(self, move):
        try:
            start, end = move.split()
            start = (5-int(start[1]), ord(start[0].upper()) - ord('A'))
            end = (5-int(end[1]), ord(end[0].upper()) - ord('A'))
            return (start, end)
        except:
            return None

    # log game to file
    def write_trace_file(self, move):
        if not self.trace_file:
            # Write the game parameters
            filename = f"gameTrace-false-{self.timeout}-{self.max_turns}.txt"
            self.trace_file = open(filename, "w")
            self.trace_file.write(f"Game Parameters:\n")
            self.trace_file.write(f"Timeout: {self.timeout} seconds\n")
            self.trace_file.write(f"Max Turns: {self.max_turns}\n")
            self.trace_file.write(f"Play Mode: {self.play_mode}\n\n")
            # Write initial board configuration
            self.trace_file.write("Initial Board Configuration:\n")
            self.trace_file.write(self.board_to_string(self.current_game_state["board"]) + "\n\n")

        # Log the move and update the board
        if move is not None:
            # Update the current_game_state['turn'] variable
            value = self.current_game_state['turn'].capitalize()
            if value == "Black": value = "White"
            else: value = "Black"
            self.trace_file.write(f"Turn #{self.turn_number}: {value} to move\n")
            self.trace_file.write(f"Action: {self.move_to_string(move)}\n")
            self.trace_file.write("New Board Configuration:\n")
            self.trace_file.write(self.board_to_string(self.current_game_state["board"]) + "\n\n")

    def move_to_string(self, move):
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        return f"{chr(ord('A') + start_col)}{5 - start_row} {chr(ord('A') + end_col)}{5 - end_row}"

    def board_to_string(self, board):
        # Build a list of rows with left-side row numbers (5 to 1) and column header at the bottom
        lines = []
        for i, row in enumerate(board, start=1):
            # Row number is displayed as 6 - i (to count 5 to 1)
            line = f"{6 - i}  " + ' '.join(piece.rjust(3) for piece in row)
            lines.append(line)
        # Add column headers (A to E)
        lines.append("     A   B   C   D   E")
        return "\n".join(lines)

    # MAIN LOOP
    def play(self):
        print("\n\nWelcome to Mini Chess!")
        print("Please Select Game Mode: [0] H-H, [1] H-AI, [2] AI-AI")
        
        # Update the mode selection to support H-AI (and optionally AI-AI)
        while True:
            mode = input("input: ")
            if mode == "0":
                self.play_mode = "H-H"
                break
            elif mode == "1":
                self.play_mode = "H-AI"
                break
            elif mode == "2":
                self.play_mode = "AI-AI"
                break
            else:
                print("Invalid selection. Please choose [0] H-H, [1] H-AI, or [2] AI-AI")

        # Write the initial game state to the trace file.
        self.write_trace_file(None)
        self.turn_number = 1

        while True:
            self.display_board(self.current_game_state)
            self.display_valid_moves(self.current_game_state)
            
            # If we are in H-AI mode and it is black's turn (or in AI-AI mode), let the AI choose the move.
            if (self.play_mode == "H-AI" and self.current_game_state["turn"] == "black") or (self.play_mode == "AI-AI"):
                valid_moves = self.valid_moves(self.current_game_state)
                if not valid_moves:
                    print("No valid moves available for AI. Game over.")
                    break
                move = valid_moves[0]["move"]
                print(f"AI ({self.current_game_state['turn']}) chooses move: {self.move_to_string(move)}")
            else:
                # Otherwise, ask the human player for input.
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
            if target in ['wK', 'bK']:
                self.make_move(self.current_game_state, move)
                self.write_trace_file(move)
                print(' ** GAME OVER **')
                if self.trace_file:
                    # Determine the winner: if the move captured the king, the winning side is the opposite of the current turn.
                    winning_side = "White" if self.current_game_state['turn'] == "black" else "Black"
                    self.trace_file.write(f"Game Over: {winning_side} wins!\n")
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
            self.write_trace_file(move)
            self.turn_number += 1
   

if __name__ == "__main__":
    game = MiniChess()
    game.play()
