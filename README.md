# **COEN 472 - Artificial Intelligence Project: Mini Chess**

### **Team Members**
- **Philip Carlsson-Coulombe** (ID: 40208572)
- **David R Cronin** (ID: 28840024)

---

## **Project Overview**
This project is a simplified version of chess, called **Mini Chess**, designed for the COEN 472 Artificial Intelligence course. The game is played on a 5x5 board with a limited set of pieces. The goal is to create a functional two-player chess game where humans can play against each other (H-H mode). The game includes features like move validation, pawn promotion, and capturing pieces, as well as logging the game to a trace file.

---

## **Features**
- **Human vs Human (H-H) Mode**: Two players can take turns making moves.
- **Move Validation**: Ensures that all moves are legal according to the rules of Mini Chess.
- **Pawn Promotion**: Promotes a pawn to a queen when it reaches the last row.
- **Capture Detection**: Detects when a piece is captured and announces it.
- **Game Logging**: Logs the game state and moves to a trace file for review.
- **Exit Option**: Players can type "exit" to quit the game at any time.

---

## **How to Run the Game**
1. **Prerequisites**:
   - Ensure you have Python 3 installed on your system.

2. **Running the Game**:
   - Unzip the project folder.
   - Navigate to the project directory in your terminal or command prompt.
   - Run the following command:
     ```bash
     python mini_chess.py
     ```
   - Follow the on-screen instructions to play the game.

3. **Gameplay**:
   - The game will prompt you to select a mode. For now, only **Human vs Human (H-H)** mode is available.
   - Players take turns entering moves in the format `[Column][Row] [Column][Row]` (e.g., `B2 B3`).
   - The game will display the board after each move and announce captures or pawn promotions.
   - To exit the game, type `exit` during your turn.

---

## **File Structure**
- `mini_chess.py`: The main Python script containing the game logic.
- `README.md`: This file, providing an overview of the project and instructions.
- `gameTrace-false-[timeout]-[max_turns].txt`: A log file generated during gameplay (created automatically).

---

## **Trace File**
The game automatically generates a trace file named `gameTrace-false-[timeout]-[max_turns].txt`. This file contains:
- Game parameters (timeout, max turns, play mode).
- Initial board configuration.
- A log of each move, including the new board state after the move.
- The final result of the game (if applicable).