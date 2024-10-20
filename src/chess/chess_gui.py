import tkinter as tk
from PIL import Image, ImageTk
from copy import deepcopy
import json
import os

from chess_game import ChessBoard

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Game")
        
        # Board dimensions
        self.SQUARE_SIZE = 80
        self.BOARD_SIZE = self.SQUARE_SIZE * 8
        
        # Colors for the board squares
        self.light_square = "#F0D9B5"
        self.dark_square = "#B58863"
        self.highlight_color = "#7B61FF"
        self.move_highlight_color = "#AAD26B"
        
        # Initialize the chess board logic
        self.chess_board = ChessBoard()
        
        # Dictionary to store piece images
        self.piece_images = {}
        
        # Create the main frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack(padx=20, pady=20)
        
        # Create info frame
        self.info_frame = tk.Frame(self.main_frame)
        self.info_frame.pack(side=tk.TOP, pady=(0, 10))
        
        # Create status label
        self.status_label = tk.Label(
            self.info_frame,
            text="White's turn",
            font=('Arial', 14)
        )
        self.status_label.pack(side=tk.LEFT, padx=10)
        
        # Create buttons frame
        self.button_frame = tk.Frame(self.main_frame)
        self.button_frame.pack(side=tk.BOTTOM, pady=(10, 0))
        
        # Create buttons
        tk.Button(self.button_frame, text="New Game", command=self.new_game).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Save Game", command=self.save_game).pack(side=tk.LEFT, padx=5)
        tk.Button(self.button_frame, text="Load Game", command=self.load_game).pack(side=tk.LEFT, padx=5)
        
        # Create the main canvas
        self.canvas = tk.Canvas(
            self.main_frame,
            width=self.BOARD_SIZE,
            height=self.BOARD_SIZE,
            background="white"
        )
        self.canvas.pack()
        
        # Game state variables
        self.selected_square = None
        self.valid_moves = []
        
        # Create placeholder images for pieces
        self.create_piece_images()
        
        # Draw the board and pieces
        self.draw_board()
        self.update_pieces()
        
        # Bind mouse events
        self.canvas.bind('<Button-1>', self.on_square_click)

    def create_piece_images(self):
        # Create colored rectangles as placeholder pieces
        piece_symbols = {
            'K': 'king',
            'Q': 'queen',
            'R': 'rook',
            'B': 'bishop',
            'N': 'knight',
            'P': 'pawn'
        }
        
        for color in ['white', 'black']:
            color_code = 'w' if color == 'white' else 'b'
            fill_color = '#FFFFFF' if color == 'white' else '#000000'
            outline_color = '#000000' if color == 'white' else '#FFFFFF'
            
            for symbol, name in piece_symbols.items():
                img = Image.new('RGBA', (self.SQUARE_SIZE - 20, self.SQUARE_SIZE - 20), fill_color)
                # Add piece symbol text
                piece_key = color + symbol
                self.piece_images[piece_key] = ImageTk.PhotoImage(img)

    def draw_board(self):
        self.canvas.delete("squares")
        for row in range(8):
            for col in range(8):
                x1 = col * self.SQUARE_SIZE
                y1 = row * self.SQUARE_SIZE
                x2 = x1 + self.SQUARE_SIZE
                y2 = y1 + self.SQUARE_SIZE
                
                # Alternate square colors
                color = self.light_square if (row + col) % 2 == 0 else self.dark_square
                
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color,
                    outline="",
                    tags="squares"
                )
                
                # Add coordinate labels
                if col == 0:  # Rank numbers (1-8)
                    self.canvas.create_text(
                        x1 + 10,
                        y1 + 10,
                        text=str(8 - row),
                        fill=self.dark_square if (row + col) % 2 == 0 else self.light_square,
                        font=('Arial', 10),
                        tags="squares"
                    )
                if row == 7:  # File letters (a-h)
                    self.canvas.create_text(
                        x2 - 10,
                        y2 - 10,
                        text=chr(col + 97),
                        fill=self.dark_square if (row + col) % 2 == 0 else self.light_square,
                        font=('Arial', 10),
                        tags="squares"
                    )

    def update_pieces(self):
        self.canvas.delete("pieces")
        for row in range(8):
            for col in range(8):
                piece = self.chess_board.board[row][col]
                if piece:
                    x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
                    piece_key = piece.color + piece.symbol
                    self.canvas.create_image(
                        x, y,
                        image=self.piece_images[piece_key],
                        tags="pieces"
                    )
                    # Add piece symbol text
                    symbol_color = '#000000' if piece.color == 'white' else '#FFFFFF'
                    self.canvas.create_text(
                        x, y,
                        text=piece.symbol,
                        fill=symbol_color,
                        font=('Arial', 24, 'bold'),
                        tags="pieces"
                    )

    def highlight_square(self, row, col, color):
        x1 = col * self.SQUARE_SIZE
        y1 = row * self.SQUARE_SIZE
        x2 = x1 + self.SQUARE_SIZE
        y2 = y1 + self.SQUARE_SIZE
        self.canvas.create_rectangle(
            x1, y1, x2, y2,
            outline=color,
            width=3,
            tags="highlight"
        )

    def highlight_moves(self, moves):
        self.canvas.delete("move_dots")
        for row, col in moves:
            x = col * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            y = row * self.SQUARE_SIZE + self.SQUARE_SIZE // 2
            self.canvas.create_oval(
                x - 10, y - 10,
                x + 10, y + 10,
                fill=self.move_highlight_color,
                tags="move_dots"
            )

    def clear_highlights(self):
        self.canvas.delete("highlight")
        self.canvas.delete("move_dots")

    def get_square_from_coord(self, event):
        col = event.x // self.SQUARE_SIZE
        row = event.y // self.SQUARE_SIZE
        return row, col

    def on_square_click(self, event):
        row, col = self.get_square_from_coord(event)
        
        if not self.selected_square:
            piece = self.chess_board.board[row][col]
            if piece and piece.color == self.chess_board.current_player:
                self.selected_square = (row, col)
                self.valid_moves = piece.valid_moves(self.chess_board, (row, col))
                self.clear_highlights()
                self.highlight_square(row, col, self.highlight_color)
                self.highlight_moves(self.valid_moves)
        else:
            start_row, start_col = self.selected_square
            if (row, col) in self.valid_moves:
                result = self.chess_board.move_piece(self.selected_square, (row, col))
                self.clear_highlights()
                self.update_pieces()
                
                if result == 'checkmate':
                    winner = 'White' if self.chess_board.current_player == 'black' else 'Black'
                    self.status_label.config(text=f"Checkmate! {winner} wins!")
                elif result == 'stalemate':
                    self.status_label.config(text="Stalemate! Game is a draw!")
                elif result == 'check':
                    self.status_label.config(text=f"{self.chess_board.current_player.capitalize()}'s turn - Check!")
                elif result:
                    self.status_label.config(text=f"{self.chess_board.current_player.capitalize()}'s turn")
            
            self.selected_square = None
            self.valid_moves = []
            self.clear_highlights()
            
        self.root.update()

    def new_game(self):
        self.chess_board = ChessBoard()
        self.selected_square = None
        self.valid_moves = []
        self.clear_highlights()
        self.update_pieces()
        self.status_label.config(text="White's turn")

    def save_game(self):
        filename = tk.filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            save_game(self.chess_board, filename)

    def load_game(self):
        filename = tk.filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.chess_board = load_game(filename)
                self.selected_square = None
                self.valid_moves = []
                self.clear_highlights()
                self.update_pieces()
                self.status_label.config(text=f"{self.chess_board.current_player.capitalize()}'s turn")
            except Exception as e:
                tk.messagebox.showerror("Error", f"Failed to load game: {str(e)}")

def play_chess_gui():
    root = tk.Tk()
    gui = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    play_chess_gui()
