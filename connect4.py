# Nicole Thomas
# November 15, 2025,
# Connect 4 Game


import tkinter as tk
from tkinter import messagebox
import random
import math
import copy

ROWS, COLS, CELL_SIZE = 6, 7, 80
DEPTH = 4  # AI search depth


class Connect4GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Connect 4 (Tkinter)")
        self.current_player = "R"
        self.board = [["" for _ in range(COLS)] for _ in range(ROWS)]
        self.vs_ai = True  # Enable AI opponent

        self.canvas = tk.Canvas(root, width=COLS * CELL_SIZE, height=ROWS * CELL_SIZE, bg="blue")
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.handle_click)

        self.reset_button = tk.Button(root, text="Reset Game", command=self.reset_game)
        self.reset_button.pack(pady=10)

        self.draw_board()

    def draw_board(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x1, y1 = c * CELL_SIZE + 10, r * CELL_SIZE + 10
                x2, y2 = (c + 1) * CELL_SIZE - 10, (r + 1) * CELL_SIZE - 10
                color = "white"
                if self.board[r][c] == "R":
                    color = "red"
                elif self.board[r][c] == "Y":
                    color = "yellow"
                self.canvas.create_oval(x1, y1, x2, y2, fill=color, outline="black")

    def handle_click(self, event):
        col = event.x // CELL_SIZE
        if col < 0 or col >= COLS:
            return
        row = self.get_open_row(col)
        if row is None:
            return
        self.board[row][col] = self.current_player
        self.draw_board()

        if self.check_winner(self.current_player):
            messagebox.showinfo("Game Over", f"{self.get_player_name()} Wins!")
            self.disable_clicks()
            return

        if self.board_full():
            messagebox.showinfo("Game Over", "It's a tie!")
            self.disable_clicks()
            return

        self.switch_player()

        # AI Move
        if self.vs_ai and self.current_player == "Y":
            self.ai_move()

    def ai_move(self):
        col = self.get_best_move()
        if col is None:
            return
        row = self.get_open_row(col)
        self.board[row][col] = self.current_player
        self.draw_board()

        if self.check_winner(self.current_player):
            messagebox.showinfo("Game Over", f"{self.get_player_name()} Wins!")
            self.disable_clicks()
            return

        if self.board_full():
            messagebox.showinfo("Game Over", "It's a tie!")
            self.disable_clicks()
            return

        self.switch_player()

    def get_best_move(self):
        _, col = self.minimax(copy.deepcopy(self.board), DEPTH, -math.inf, math.inf, True)
        return col

    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        valid_cols = self.get_valid_columns(board)
        is_terminal = self.check_winner("R") or self.check_winner("Y") or len(valid_cols) == 0

        if depth == 0 or is_terminal:
            if is_terminal:
                if self.check_winner("Y"):
                    return (1000000, None)
                elif self.check_winner("R"):
                    return (-1000000, None)
                else:
                    return (0, None)
            else:
                return (self.evaluate_board(board), None)

        if maximizingPlayer:
            value = -math.inf
            best_col = random.choice(valid_cols)
            for col in valid_cols:
                temp_board = copy.deepcopy(board)
                row = self.get_open_row(col, temp_board)
                temp_board[row][col] = "Y"
                new_score, _ = self.minimax(temp_board, depth - 1, alpha, beta, False)
                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break
            return value, best_col
        else:
            value = math.inf
            best_col = random.choice(valid_cols)
            for col in valid_cols:
                temp_board = copy.deepcopy(board)
                row = self.get_open_row(col, temp_board)
                temp_board[row][col] = "R"
                new_score, _ = self.minimax(temp_board, depth - 1, alpha, beta, True)
                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return value, best_col

    def evaluate_board(self, board):
        score = 0
        # Center column preference
        center_array = [board[r][COLS // 2] for r in range(ROWS)]
        score += center_array.count("Y") * 3

        # Horizontal scoring
        for r in range(ROWS):
            row_array = board[r]
            for c in range(COLS - 3):
                window = row_array[c:c + 4]
                score += self.score_window(window, "Y")
                score -= self.score_window(window, "R")

        # Vertical scoring
        for c in range(COLS):
            col_array = [board[r][c] for r in range(ROWS)]
            for r in range(ROWS - 3):
                window = col_array[r:r + 4]
                score += self.score_window(window, "Y")
                score -= self.score_window(window, "R")

        # Diagonal scoring
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r + i][c + i] for i in range(4)]
                score += self.score_window(window, "Y")
                score -= self.score_window(window, "R")

        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                window = [board[r + 3 - i][c + i] for i in range(4)]
                score += self.score_window(window, "Y")
                score -= self.score_window(window, "R")

        return score

    def score_window(self, window, player):
        score = 0
        opp = "R" if player == "Y" else "Y"
        if window.count(player) == 4:
            score += 100
        elif window.count(player) == 3 and window.count("") == 1:
            score += 5
        elif window.count(player) == 2 and window.count("") == 2:
            score += 2
        if window.count(opp) == 3 and window.count("") == 1:
            score -= 4
        return score

    def get_valid_columns(self, board):
        return [c for c in range(COLS) if self.get_open_row(c, board) is not None]

    def get_open_row(self, col, board=None):
        if board is None:
            board = self.board
        for r in reversed(range(ROWS)):
            if board[r][col] == "":
                return r
        return None

    def switch_player(self):
        self.current_player = "Y" if self.current_player == "R" else "R"

    def get_player_name(self):
        return "Red" if self.current_player == "R" else "Yellow"

    def board_full(self):
        return all(self.board[0][c] != "" for c in range(COLS))

    def check_winner(self, p):
        b = self.board
        # Horizontal
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(b[r][c + i] == p for i in range(4)):
                    return True
        # Vertical
        for c in range(COLS):
            for r in range(ROWS - 3):
                if all(b[r + i][c] == p for i in range(4)):
                    return True
        # Diagonal \
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if all(b[r + i][c + i] == p for i in range(4)):
                    return True
        # Diagonal /
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if all(b[r - i][c + i] == p for i in range(4)):
                    return True
        return False

    def reset_game(self):
        self.board = [["" for _ in range(COLS)] for _ in range(ROWS)]
        self.current_player = "R"
        self.canvas.bind("<Button-1>", self.handle_click)
        self.draw_board()

    def disable_clicks(self):
        self.canvas.unbind("<Button-1>")


if __name__ == "__main__":
    root = tk.Tk()
    app = Connect4GUI(root)
    root.mainloop()
