# Philip Carlsson-Coulombe
# 40208572

# David R Cronin
# 28840024

# COEN 472 Artificial Intelligence
# Deliverable 2

import math
import copy
import time
import argparse
from typing import List, Dict, Tuple, Optional, Any

BOARD_SIZE: int = 5
RECURSION_DEPTH: int = 4  # Depth for minimax searches
CAPTURE_VALUES: Dict[str, int] = {'k': 999, 'q': 9, 'b': 3, 'n': 3, 'p': 1}

class MiniChess:
    def __init__(self) -> None:
        """
        Initialize the MiniChess game with default parameters.
        """
        self.current_game_state: Dict[str, Any] = self.init_board()
        self.turn_number: int = 1  # Full turn (White + Black)
        self.timeout: int = 360  # Time limit per move in seconds
        self.max_turns: int = 20  # Maximum number of half-moves without capture before a draw
        self.play_mode: Optional[str] = None  # "H-H", "H-Ai", or "Ai-Ai"
        self.trace_file: Optional[Any] = None  # File object for writing the game trace
        self.eval_choice: Optional[str] = None  # "e0", "e1", "e2", or "e3"
        self.moves_without_capture: int = 0  # Counter for half-moves with no capture

    def init_board(self) -> Dict[str, Any]:
        """
        Initialize and return the starting game state.
        """
        state: Dict[str, Any] = {
            "board": [
                ['bK', 'bQ', 'bB', 'bN', '.'],
                ['.', '.', 'bp', 'bp', '.'],
                ['.', '.', '.', '.', '.'],
                ['.', 'wp', 'wp', '.', '.'],
                ['.', 'wN', 'wB', 'wQ', 'wK']
            ],
            "turn": 'white'  # White starts
        }
        return state

    def display_board(self, game_state: Dict[str, Any]) -> None:
        """
        Display the current state of the board.
        """
        print()
        for i, row in enumerate(game_state["board"], start=1):
            print(str(BOARD_SIZE + 1 - i) + "  " + ' '.join(piece.rjust(3) for piece in row))
        print()
        print("     A   B   C   D   E")
        print()

    def display_valid_moves(self, game_state: Dict[str, Any]) -> None:
        """
        Display the list of valid moves.
        """
        moves: List[Dict[str, Any]] = self.valid_moves(game_state, static_eval=False)
        move_strings: List[str] = [f"{self.move_to_string(m['move'])}:{m['value']}" for m in moves]
        print("List of Valid Moves: " + " - ".join(move_strings))

    def calculate_e1_value(self, target: str) -> int:
        """
        Calculate the move value based on the target piece (e1 evaluation).
        Uses CAPTURE_VALUES mapping.
        """
        if target != '.' and len(target) > 1:
            cap_type: str = target[1].lower()
            return CAPTURE_VALUES.get(cap_type, 0)
        return 0

    def calculate_e0_value(self, board: List[List[str]]) -> int:
        """
        Evaluate the board (e0 evaluation) as:
          (#wp + 3*#wB + 3*#wN + 9*#wQ + 999*#wK) -
          (#bp + 3*#bB + 3*#bN + 9*#bQ + 999*#bK)
        """
        total: int = 0
        for row in board:
            for piece in row:
                if piece != '.':
                    piece_val: int = CAPTURE_VALUES.get(piece[1].lower(), 0)
                    if piece[0] == 'w':
                        total += piece_val
                    else:
                        total -= piece_val
        return total

    def is_terminal(self, game_state: Dict[str, Any]) -> bool:
        """
        Return True if the game is in a terminal state (i.e. one king is missing).
        """
        board: List[List[str]] = game_state["board"]
        white_king: bool = any('wK' in row for row in board)
        black_king: bool = any('bK' in row for row in board)
        return not (white_king and black_king)

    def negamax(self, game_state: Dict[str, Any], depth: int, static_eval: bool = False) -> int:
        """
        Plain negamax search (minimax without pruning) to a given depth.
        Returns the evaluation value from the perspective of the current player.
        When static_eval is True, valid_moves uses only static evaluation (e0).
        """
        if depth == 0 or self.is_terminal(game_state):
            return self.calculate_e0_value(game_state["board"])
        best_value: int = -float('inf')
        for move_dict in self.valid_moves(game_state, static_eval=static_eval):
            new_state: Dict[str, Any] = copy.deepcopy(game_state)
            new_state = self.make_move(new_state, move_dict["move"])
            value: int = -self.negamax(new_state, depth - 1, static_eval=static_eval)
            best_value = max(best_value, value)
        return best_value

    def negamax_alphabeta(self, game_state: Dict[str, Any], depth: int,
                           alpha: int, beta: int, static_eval: bool = False) -> int:
        """
        Negamax search with alpha–beta pruning to a given depth.
        Returns the evaluation value from the perspective of the current player.
        """
        if depth == 0 or self.is_terminal(game_state):
            return self.calculate_e0_value(game_state["board"])
        best_value: int = -float('inf')
        for move_dict in self.valid_moves(game_state, static_eval=static_eval):
            new_state: Dict[str, Any] = copy.deepcopy(game_state)
            new_state = self.make_move(new_state, move_dict["move"])
            value: int = -self.negamax_alphabeta(new_state, depth - 1, -beta, -alpha, static_eval=static_eval)
            best_value = max(best_value, value)
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_value

    def evaluate_move(self, game_state: Dict[str, Any],
                      move: Tuple[Tuple[int, int], Tuple[int, int]],
                      piece: str, target: str,
                      static_eval: bool = False) -> int:
        """
        Evaluate a candidate move according to the chosen heuristic.
        If static_eval is True, always use the static evaluation (e0).
        For e1 (when static_eval is False): directly compute the capture value.
        For e0, e2, and e3 (when static_eval is False): perform a deep copy, simulate the move,
        and then evaluate the resulting board. For e2 and e3, minimax searches are used.
        If it is Black’s turn in the original state, the evaluation is negated.
        """
        if static_eval:
            new_state: Dict[str, Any] = copy.deepcopy(game_state)
            new_state = self.make_move(new_state, move)
            value: int = self.calculate_e0_value(new_state["board"])
            if game_state["turn"] == "black":
                value = -value
            return value

        # Non-static evaluation mode: use the chosen heuristic.
        if self.eval_choice == "e1":
            if target == '.':
                return 0
            elif target[0] != piece[0]:
                return self.calculate_e1_value(target)
            else:
                return 0
        elif self.eval_choice == "e0":
            new_state = copy.deepcopy(game_state)
            new_state = self.make_move(new_state, move)
            value = self.calculate_e0_value(new_state["board"])
            if game_state["turn"] == "black":
                value = -value
            return value
        elif self.eval_choice == "e2":
            new_state = copy.deepcopy(game_state)
            new_state = self.make_move(new_state, move)
            # Use plain negamax search with static_eval=True so that internal moves use e0.
            value = self.negamax(new_state, RECURSION_DEPTH, static_eval=True)
            if game_state["turn"] == "black":
                value = -value
            return value
        elif self.eval_choice == "e3":
            new_state = copy.deepcopy(game_state)
            new_state = self.make_move(new_state, move)
            # Use negamax with alpha-beta pruning with static_eval=True.
            value = self.negamax_alphabeta(new_state, RECURSION_DEPTH, -int(1e9), int(1e9), static_eval=True)
            if game_state["turn"] == "black":
                value = -value
            return value
        else:
            return 0

    def valid_moves(self, game_state: Dict[str, Any], static_eval: bool = False) -> List[Dict[str, Any]]:
        """
        Generate and return a list of valid moves for the current game state.
        Each move is represented as a dictionary with keys "move" and "value".
        The parameter static_eval indicates whether to use static evaluation (e0) for move values.
        """
        board: List[List[str]] = game_state["board"]
        turn: str = game_state["turn"]
        moves: List[Dict[str, Any]] = []

        piece_valid_moves: Dict[str, List[Tuple[int, int]]] = {
            'K': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],
            'Q': [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (-1, -1), (1, -1), (-1, 1)],
            'N': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
            'B': [(1, 1), (-1, -1), (1, -1), (-1, 1)]
        }

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece: str = board[row][col]
                if piece == '.':
                    continue

                piece_type: str = piece[1]
                piece_color: str = "white" if piece[0] == 'w' else "black"
                if piece_color != turn:
                    continue

                if piece_type in piece_valid_moves:
                    for d_row, d_col in piece_valid_moves[piece_type]:
                        for step in range(1, BOARD_SIZE + 1):
                            n_row: int = row + d_row * step
                            n_col: int = col + d_col * step
                            if not (0 <= n_row < BOARD_SIZE and 0 <= n_col < BOARD_SIZE):
                                break
                            target: str = board[n_row][n_col]
                            move_tuple: Tuple[Tuple[int, int], Tuple[int, int]] = ((row, col), (n_row, n_col))
                            move_value: int = self.evaluate_move(game_state, move_tuple, piece, target, static_eval)
                            moves.append({"move": move_tuple, "value": move_value})
                            if target != '.':
                                break
                            if piece_type in "KN":
                                break
                elif piece_type == 'p':
                    direction: int = -1 if piece_color == "white" else 1
                    # Pawn forward move.
                    n_row, n_col = row + direction, col
                    if 0 <= n_row < BOARD_SIZE and board[n_row][n_col] == '.':
                        move_tuple = ((row, col), (n_row, n_col))
                        move_value = self.evaluate_move(game_state, move_tuple, piece, board[n_row][n_col], static_eval)
                        moves.append({"move": move_tuple, "value": move_value})
                    # Pawn diagonal capture moves.
                    for d_col in [-1, 1]:
                        n_row, n_col = row + direction, col + d_col
                        if 0 <= n_row < BOARD_SIZE and 0 <= n_col < BOARD_SIZE and board[n_row][n_col] != '.':
                            if board[n_row][n_col][0] != piece[0]:
                                move_tuple = ((row, col), (n_row, n_col))
                                move_value = self.evaluate_move(game_state, move_tuple, piece, board[n_row][n_col], static_eval)
                                moves.append({"move": move_tuple, "value": move_value})
        moves.sort(key=lambda m: m["value"], reverse=True)
        return moves

    def is_valid_move(self, game_state: Dict[str, Any],
                      move: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
        """
        Return True if the move is in the list of valid moves.
        """
        for move_dict in self.valid_moves(game_state, static_eval=False):
            if move_dict["move"] == move:
                return True
        return False

    def is_capture(self, game_state: Dict[str, Any],
                   move: Tuple[Tuple[int, int], Tuple[int, int]]) -> str:
        """
        Check if a move results in a capture.
        Returns the target piece if a capture occurs, otherwise 'none'.
        """
        start, end = move
        piece: str = game_state["board"][start[0]][start[1]]
        target: str = game_state["board"][end[0]][end[1]]
        if target != '.' and target[0] != piece[0]:
            return target
        return 'none'

    def is_queening(self, game_state: Dict[str, Any],
                    move: Tuple[Tuple[int, int], Tuple[int, int]]) -> bool:
        """
        Determine if a pawn is promoted (reaches the last row).
        """
        start, end = move
        piece: str = game_state["board"][start[0]][start[1]]
        return piece[1] == 'p' and (end[0] == 0 or end[0] == BOARD_SIZE - 1)

    def make_move(self, game_state: Dict[str, Any],
                  move: Tuple[Tuple[int, int], Tuple[int, int]]) -> Dict[str, Any]:
        """
        Update and return the game state after executing a move.
        """
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        piece: str = game_state["board"][start_row][start_col]
        if piece[1] == 'p' and ((piece[0] == 'w' and end_row == 0) or (piece[0] == 'b' and end_row == BOARD_SIZE - 1)):
            game_state["board"][end_row][end_col] = piece[0] + 'Q'
        else:
            game_state["board"][end_row][end_col] = piece
        game_state["board"][start_row][start_col] = '.'
        # Toggle the turn.
        game_state["turn"] = "black" if game_state["turn"] == "white" else "white"
        return game_state

    def parse_input(self, move: str) -> Optional[Tuple[Tuple[int, int], Tuple[int, int]]]:
        """
        Parse a move input string (e.g., 'A3 B3') into board coordinates.
        """
        try:
            start_str, end_str = move.split()
            start: Tuple[int, int] = (BOARD_SIZE - int(start_str[1]), ord(start_str[0].upper()) - ord('A'))
            end: Tuple[int, int] = (BOARD_SIZE - int(end_str[1]), ord(end_str[0].upper()) - ord('A'))
            return (start, end)
        except (ValueError, IndexError):
            return None

    def write_trace_file(self, move: Optional[Tuple[Tuple[int, int], Tuple[int, int]]]) -> None:
        """
        Write game parameters and moves to a trace file.
        """
        if not self.trace_file:
            filename: str = f"gameTrace-false-{self.timeout}-{self.max_turns}.txt"
            self.trace_file = open(filename, "w")
            self.trace_file.write("Game Parameters:\n")
            self.trace_file.write(f"Timeout: {self.timeout} seconds\n")
            self.trace_file.write(f"Max Turns (half-moves without capture): {self.max_turns}\n")
            self.trace_file.write(f"Play Mode: {self.play_mode}\n")
            self.trace_file.write(f"Heuristic Choice: {self.eval_choice}\n\n")
            self.trace_file.write("Initial Board Configuration:\n")
            self.trace_file.write(self.board_to_string(self.current_game_state["board"]) + "\n\n")
        if move is not None:
            next_turn: str = self.current_game_state['turn'].capitalize()
            next_turn = "White" if next_turn == "Black" else "Black"
            self.trace_file.write(f"Turn #{self.turn_number}: {next_turn} to move\n")
            self.trace_file.write(f"Action: {self.move_to_string(move)}\n")
            self.trace_file.write("New Board Configuration:\n")
            self.trace_file.write(self.board_to_string(self.current_game_state["board"]) + "\n\n")

    def move_to_string(self, move: Tuple[Tuple[int, int], Tuple[int, int]]) -> str:
        """
        Convert a move tuple into a human-readable string.
        """
        start, end = move
        start_row, start_col = start
        end_row, end_col = end
        return f"{chr(ord('A') + start_col)}{BOARD_SIZE - start_row} {chr(ord('A') + end_col)}{BOARD_SIZE - end_row}"

    def board_to_string(self, board: List[List[str]]) -> str:
        """
        Return a string representation of the board.
        """
        lines: List[str] = []
        for i, row in enumerate(board, start=1):
            line: str = f"{BOARD_SIZE + 1 - i}  " + ' '.join(piece.rjust(3) for piece in row)
            lines.append(line)
        lines.append("     A   B   C   D   E")
        return "\n".join(lines)

    def get_ai_move(self, game_state: Dict[str, Any]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        """
        Return the AI-selected move by choosing the first move from the sorted valid moves.
        """
        moves: List[Dict[str, Any]] = self.valid_moves(game_state, static_eval=False)
        if not moves:
            print("No valid moves available for AI.")
            exit(0)
        return moves[0]["move"]

    def play(self) -> None:
        """
        Main game loop handling mode selection, move input, AI moves, and game termination.
        """
        print("\n\nWelcome to Mini Chess!")
        print("Please Select Game Mode: [0] H-H, [1] H-Ai, [2] Ai-Ai")
        mode_valid: bool = False
        while not mode_valid:
            mode_input: str = input("input: ")
            if mode_input == "0":
                self.play_mode = "H-H"
                mode_valid = True
            elif mode_input == "1":
                self.play_mode = "H-Ai"
                mode_valid = True
            elif mode_input == "2":
                self.play_mode = "Ai-Ai"
                mode_valid = True
            else:
                print("Invalid mode. Please enter 0, 1, or 2.")
        eval_enable: bool = True
        while eval_enable:
            
            print("\nChoose heuristic to evaluate moves: [0] e0, [1] e1, [2] e2, [3] e3: ")
            print("\n e0 - Static Mass Evaluation\n e1 - Direct Capture Evaluation\n e2 - Minimax Evaluation\n e3 - Minimax w/ Alpha-Beta Pruning (e3)")
            choice: str = input("input: ")
            if choice == "0":
                self.eval_choice = "e0"
                eval_enable = False
            elif choice == "1":
                self.eval_choice = "e1"
                eval_enable = False
            elif choice == "2":
                self.eval_choice = "e2"
                eval_enable = False
            elif choice == "3":
                self.eval_choice = "e3"
                eval_enable = False
            else:
                print("Invalid choice. Please enter 0, 1, 2 or 3.")
        self.write_trace_file(None)
        self.turn_number = 1
        while True:
            self.display_board(self.current_game_state)
            self.display_valid_moves(self.current_game_state)
            current_mover: str = self.current_game_state["turn"]
            if (self.play_mode == "H-H") or (self.play_mode == "H-Ai" and current_mover == "white"):
                move_input: str = input(f"Turn {self.turn_number}: {current_mover.capitalize()} to move: ")
                if move_input.lower() == 'exit':
                    print("Game exited.")
                    if self.trace_file:
                        self.trace_file.close()
                    exit(1)
                move_option: Optional[Tuple[Tuple[int, int], Tuple[int, int]]] = self.parse_input(move_input)
                if not move_option or not self.is_valid_move(self.current_game_state, move_option):
                    print("Invalid move. Try again.")
                    continue
                move = move_option
            else:
                move = self.get_ai_move(self.current_game_state)
                print(f"Turn {self.turn_number}: {current_mover.capitalize()} (AI) chooses move: {self.move_to_string(move)}")
            target: str = self.is_capture(self.current_game_state, move)
            if target in ['wK', 'bK']:
                self.make_move(self.current_game_state, move)
                self.write_trace_file(move)
                print("****************************")
                print("*         GAME OVER        *")
                print("****************************")
                if self.trace_file:
                    next_turn: str = self.current_game_state['turn'].capitalize()
                    next_turn = "White" if next_turn == "Black" else "Black"
                    self.trace_file.write(f"Game Over: {next_turn} wins!\n")
                    self.trace_file.close()
                exit(1)
            if target != 'none':
                print('Capture! ', target, 'is enslaved.')
                self.moves_without_capture = 0
            else:
                self.moves_without_capture += 1
            if self.moves_without_capture >= self.max_turns:
                print("****************************")
                print("*     DRAW - NO WINNER     *")
                print("****************************")
                if self.trace_file:
                    self.trace_file.write("Game Over: DRAW\n")
                    self.trace_file.close()
                exit(0)
            if self.is_queening(self.current_game_state, move):
                start, end = move
                piece: str = self.current_game_state["board"][start[0]][start[1]]
                self.current_game_state["board"][end[0]][end[1]] = piece[0] + 'Q'
                print('Queening! Pawn promoted to Queen.')
            self.make_move(self.current_game_state, move)
            self.write_trace_file(move)
            if current_mover == "black":
                self.turn_number += 1

if __name__ == "__main__":
    game = MiniChess()
    game.play()
