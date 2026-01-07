# **COEN 472 - Artificial Intelligence Project: Mini Chess (Demo 2)**

### **Team Members**
- **Philip Carlsson-Coulombe** (ID: 40208572)
- **David R Cronin** (ID: 28840024)

---

## **Project Overview**
This project is a simplified version of chess, called **Mini Chess**, designed for the COEN 472 Artificial Intelligence course. The game is played on a 5x5 board with a limited set of pieces and incorporates artificial intelligence techniques to evaluate moves and make decisions. The project supports both human and AI players, offering multiple game modes and several heuristic evaluation options. The game includes features like move validation, pawn promotion, capturing pieces, and logging the game to a trace file.

---

## **Features**
- **Multiple Game Modes**:
  - **Human vs Human (H-H)**: Two players take turns making moves.
  - **Human vs AI (H-Ai)**: A human player competes against the AI.
  - **AI vs AI (Ai-Ai)**: Two AI agents play against each other.
  - **Move Validation**: Ensures that all moves are legal according to the rules of Mini Chess.
  - **Pawn Promotion**: Promotes a pawn to a queen when it reaches the last row.
  - **Capture Detection**: Detects and announces captures.

- **Heuristic Move Evaluation**:
  - **e0 - Static Mass Evaluation**: Assesses the board using piece values.
  - **e1 - Direct Capture Evaluation**: Evaluates moves based on immediate capture potential.
  - **e2 - Minimax Evaluation**: Uses a minimax search to evaluate moves.
  - **e3 - Minimax with Alpha-Beta Pruning**: Optimizes minimax search using alpha-beta pruning.
  
- **Game Logging**: Logs the game state and moves to a trace file for review, including AI search statistics in AI modes.
- **Exit Option**: Players can type "exit" to quit the game at any time.

---

## **How to Run the Game**
### **Prerequisites**:
- Ensure you have Python 3 installed on your system.

### **Running the Game**:
1. Unzip the project folder.
2. Navigate to the project directory in your terminal or command prompt.
3. Run the following command:
   ```bash
   python mini_chess.py
   ```
4. Follow the on-screen prompts to select the game mode and evaluation heuristic, then play the game.

### **Gameplay**:
- **Game Mode Selection**: Upon starting, you will be prompted to choose one of the following modes:
  - `[0]` H-H: Human vs Human.
  - `[1]` H-Ai: Human vs AI.
  - `[2]` Ai-Ai: AI vs AI.
- **Heuristic Selection**: Next, choose the evaluation heuristic:
  - `[0]` e0 - Static Mass Evaluation
  - `[1]` e1 - Direct Capture Evaluation
  - `[2]` e2 - Minimax Evaluation
  - `[3]` e3 - Minimax with Alpha-Beta Pruning
- **Move Input**: Enter moves in the format `[Column][Row] [Column][Row]` (e.g., `B2 B3`).
- The game displays the board after each move and announces events such as captures and pawn promotions.
- To exit the game, type `exit` during your turn.

---

## **File Structure**
- `mini_chess.py`: The main Python script containing the game logic.
- `README.md`: This file, providing an overview of the project and instructions.
- `gameTrace-false-[timeout]-[max_turns].txt`: A log file generated during gameplay, recording game parameters, moves, board states, and AI search statistics.

---

## **Trace File Details**
The game automatically generates a trace file named `gameTrace-false-[timeout]-[max_turns].txt`. This file contains:
- **Game Parameters**: Timeout duration, maximum turns allowed without capture, selected game mode, and heuristic choice.
- **Initial Board Configuration**: The starting layout of the board.
- **Move Log**: A sequential record of each move along with the board configuration after each move.
- **AI Search Statistics (for e2 and e3 in H-Ai or Ai-Ai modes)**:
  - **Cumulative Number of Game States Explored**: Total states evaluated during AI move selection.
  - **Breakdown by Depth**: A detailed count of states explored at each search depth.
  - **Average Branching Factor**: Insights into the complexity of move exploration.