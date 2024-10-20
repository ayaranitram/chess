import json
from copy import deepcopy

__version__ = '0.5.0'
__all__ = ['play_chess', 'ChessBoard']

class ChessPiece:
    def __init__(self, color, symbol):
        self.color = color
        self.symbol = symbol
        self.has_moved = False

    def to_dict(self):
        return {
            'color': self.color,
            'symbol': self.symbol,
            'has_moved': self.has_moved,
            'type': self.__class__.__name__
        }

class Pawn(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'P')
        self.en_passant_vulnerable = False
        
    def valid_moves(self, board, pos, check_king_safety=True):
        moves = []
        x, y = pos
        direction = -1 if self.color == 'white' else 1
        
        # Move forward one square
        if 0 <= x + direction < 8 and board.board[x + direction][y] is None:
            moves.append((x + direction, y))
            
            # Initial two-square move
            if not self.has_moved and 0 <= x + 2*direction < 8 and board.board[x + 2*direction][y] is None:
                moves.append((x + 2*direction, y))
        
        # Capture diagonally
        for dy in [-1, 1]:
            if 0 <= x + direction < 8 and 0 <= y + dy < 8:
                target = board.board[x + direction][y + dy]
                if target and target.color != self.color:
                    moves.append((x + direction, y + dy))
                    
        # En passant
        if (self.color == 'white' and x == 3) or (self.color == 'black' and x == 4):
            for dy in [-1, 1]:
                if 0 <= y + dy < 8:
                    target = board.board[x][y + dy]
                    if isinstance(target, Pawn) and target.en_passant_vulnerable:
                        moves.append((x + direction, y + dy))

        if check_king_safety:
            moves = [move for move in moves if not board.would_be_in_check(pos, move, self.color)]
        
        return moves

    def to_dict(self):
        data = super().to_dict()
        data['en_passant_vulnerable'] = self.en_passant_vulnerable
        return data

class Rook(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'R')
        
    def valid_moves(self, board, pos, check_king_safety=True):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0)]
        
        for dx, dy in directions:
            x, y = pos
            while True:
                x, y = x + dx, y + dy
                if not (0 <= x < 8 and 0 <= y < 8):
                    break
                    
                target = board.board[x][y]
                if target is None:
                    moves.append((x, y))
                elif target.color != self.color:
                    moves.append((x, y))
                    break
                else:
                    break

        if check_king_safety:
            moves = [move for move in moves if not board.would_be_in_check(pos, move, self.color)]
                    
        return moves

class Knight(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'N')
        
    def valid_moves(self, board, pos, check_king_safety=True):
        moves = []
        x, y = pos
        possible_moves = [
            (x+2, y+1), (x+2, y-1), (x-2, y+1), (x-2, y-1),
            (x+1, y+2), (x+1, y-2), (x-1, y+2), (x-1, y-2)
        ]
        
        for move in possible_moves:
            x2, y2 = move
            if 0 <= x2 < 8 and 0 <= y2 < 8:
                target = board.board[x2][y2]
                if target is None or target.color != self.color:
                    moves.append(move)
        
        if check_king_safety:
            moves = [move for move in moves if not board.would_be_in_check(pos, move, self.color)]
                    
        return moves

class Bishop(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'B')
        
    def valid_moves(self, board, pos, check_king_safety=True):
        moves = []
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dx, dy in directions:
            x, y = pos
            while True:
                x, y = x + dx, y + dy
                if not (0 <= x < 8 and 0 <= y < 8):
                    break
                    
                target = board.board[x][y]
                if target is None:
                    moves.append((x, y))
                elif target.color != self.color:
                    moves.append((x, y))
                    break
                else:
                    break
        
        if check_king_safety:
            moves = [move for move in moves if not board.would_be_in_check(pos, move, self.color)]
                    
        return moves

class Queen(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'Q')
        
    def valid_moves(self, board, pos, check_king_safety=True):
        moves = []
        directions = [(0, 1), (0, -1), (1, 0), (-1, 0),
                     (1, 1), (1, -1), (-1, 1), (-1, -1)]
        
        for dx, dy in directions:
            x, y = pos
            while True:
                x, y = x + dx, y + dy
                if not (0 <= x < 8 and 0 <= y < 8):
                    break
                    
                target = board.board[x][y]
                if target is None:
                    moves.append((x, y))
                elif target.color != self.color:
                    moves.append((x, y))
                    break
                else:
                    break
        
        if check_king_safety:
            moves = [move for move in moves if not board.would_be_in_check(pos, move, self.color)]
                    
        return moves

class King(ChessPiece):
    def __init__(self, color):
        super().__init__(color, 'K')
        
    def valid_moves(self, board, pos, check_king_safety=True):
        moves = []
        x, y = pos
        possible_moves = [
            (x+1, y), (x-1, y), (x, y+1), (x, y-1),
            (x+1, y+1), (x+1, y-1), (x-1, y+1), (x-1, y-1)
        ]
        
        # Normal moves
        for move in possible_moves:
            x2, y2 = move
            if 0 <= x2 < 8 and 0 <= y2 < 8:
                target = board.board[x2][y2]
                if target is None or target.color != self.color:
                    if not check_king_safety or not board.would_be_in_check(pos, move, self.color):
                        moves.append(move)

        # Castling
        if check_king_safety and not self.has_moved and not board.is_in_check(self.color):
            # Kingside castling
            if (self.can_castle_kingside(board)):
                moves.append((x, y + 2))
            # Queenside castling
            if (self.can_castle_queenside(board)):
                moves.append((x, y - 2))
                    
        return moves

    def can_castle_kingside(self, board):
        row = 7 if self.color == 'white' else 0
        # Check if rook is in place and hasn't moved
        rook = board.board[row][7]
        if not isinstance(rook, Rook) or rook.has_moved:
            return False
        # Check if path is clear
        return (board.board[row][5] is None and 
                board.board[row][6] is None and
                not board.is_square_under_attack((row, 5), self.color) and
                not board.is_square_under_attack((row, 6), self.color))

    def can_castle_queenside(self, board):
        row = 7 if self.color == 'white' else 0
        # Check if rook is in place and hasn't moved
        rook = board.board[row][0]
        if not isinstance(rook, Rook) or rook.has_moved:
            return False
        # Check if path is clear
        return (board.board[row][1] is None and 
                board.board[row][2] is None and
                board.board[row][3] is None and
                not board.is_square_under_attack((row, 2), self.color) and
                not board.is_square_under_attack((row, 3), self.color))

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.current_player = 'white'
        self.move_history = []
        self.setup_board()

    def setup_board(self):
        # Set up pawns
        for y in range(8):
            self.board[1][y] = Pawn('black')
            self.board[6][y] = Pawn('white')
            
        # Set up other pieces
        piece_order = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
        for y in range(8):
            self.board[0][y] = piece_order[y]('black')
            self.board[7][y] = piece_order[y]('white')

    def get_king_position(self, color):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if isinstance(piece, King) and piece.color == color:
                    return (i, j)
        return None

    def is_square_under_attack(self, pos, color):
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color != color:
                    # Check piece's moves without considering king safety to avoid recursion
                    moves = piece.valid_moves(self, (i, j), check_king_safety=False)
                    if pos in moves:
                        return True
        return False

    def is_in_check(self, color):
        king_pos = self.get_king_position(color)
        return self.is_square_under_attack(king_pos, color)

    def would_be_in_check(self, start, end, color):
        # Make a temporary move and check if it puts/leaves the king in check
        temp_board = deepcopy(self)
        temp_board.make_move(start, end, check_rules=False)
        return temp_board.is_in_check(color)

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False
            
        # Check if any piece has valid moves
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color == color:
                    if piece.valid_moves(self, (i, j)):
                        return False
        return True

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False
            
        # Check if any piece has valid moves
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if piece and piece.color == color:
                    if piece.valid_moves(self, (i, j)):
                        return False
        return True

    def handle_castling(self, start, end):
        start_x, start_y = start
        end_x, end_y = end
        
        # Kingside castling
        if isinstance(self.board[start_x][start_y], King) and end_y - start_y == 2:
            # Move rook
            rook = self.board[start_x][7]
            self.board[start_x][5] = rook
            self.board[start_x][7] = None
            rook.has_moved = True
            
        # Queenside castling
        elif isinstance(self.board[start_x][start_y], King) and end_y - start_y == -2:
            # Move rook
            rook = self.board[start_x][0]
            self.board[start_x][3] = rook
            self.board[start_x][0] = None
            rook.has_moved = True

    def handle_en_passant(self, start, end):
        start_x, start_y = start
        end_x, end_y = end
        
        # Reset en passant vulnerability for all pawns
        for i in range(8):
            for j in range(8):
                piece = self.board[i][j]
                if isinstance(piece, Pawn):
                    piece.en_passant_vulnerable = False
        
        # Set en passant vulnerability for two-square pawn moves
        if isinstance(self.board[start_x][start_y], Pawn):
            if abs(end_x - start_x) == 2:
                self.board[start_x][start_y].en_passant_vulnerable = True
            
            # Handle en passant capture
            if end_y != start_y and self.board[end_x][end_y] is None:
                self.board[start_x][end_y] = None  # Remove captured pawn

    def make_move(self, start, end, check_rules=True):
        start_x, start_y = start
        end_x, end_y = end
        
        piece = self.board[start_x][start_y]
        
        if check_rules:
            valid_moves = piece.valid_moves(self, start)
            if end not in valid_moves:
                return False
        
        # Handle special moves
        self.handle_castling(start, end)
        self.handle_en_passant(start, end)
        
        # Make the move
        self.board[end_x][end_y] = piece
        self.board[start_x][start_y] = None
        piece.has_moved = True
        
        return True

    def move_piece(self, start, end):
        piece = self.board[start[0]][start[1]]
        if piece is None or piece.color != self.current_player:
            return False

        if self.make_move(start, end):
            # Record move in history
            self.move_history.append({
                'start': start,
                'end': end,
                'piece': piece.symbol,
                'color': piece.color
            })
            
            # Switch players
            self.current_player = 'black' if self.current_player == 'white' else 'white'
            
            # Check for checkmate or stalemate
            if self.is_checkmate(self.current_player):
                return 'checkmate'
            elif self.is_stalemate(self.current_player):
                return 'stalemate'
            elif self.is_in_check(self.current_player):
                return 'check'
            return True
            
        return False

    def display(self):
        print("\n    a b c d e f g h")
        print("  ┌─────────────────┐")
        for i, row in enumerate(self.board):
            print(f"{8-i} │", end=" ")
            for piece in row:
                if piece is None:
                    print('.', end=' ')
                else:
                    symbol = piece.symbol.lower() if piece.color == 'black' else piece.symbol
                    print(symbol, end=' ')
            print(f"│ {8-i}")
        print("  └─────────────────┘")
        print("    a b c d e f g h")

    def to_dict(self):
        """Convert the board state to a dictionary for saving"""
        return {
            'board': [[piece.to_dict() if piece else None for piece in row] 
                     for row in self.board],
            'current_player': self.current_player,
            'move_history': self.move_history
        }

    @classmethod
    def from_dict(cls, data):
        """Create a board from a saved dictionary state"""
        board = cls()
        board.board = [[None for _ in range(8)] for _ in range(8)]
        
        # Piece type mapping
        piece_types = {
            'Pawn': Pawn,
            'Rook': Rook,
            'Knight': Knight,
            'Bishop': Bishop,
            'Queen': Queen,
            'King': King
        }
        
        # Restore board
        for i in range(8):
            for j in range(8):
                piece_data = data['board'][i][j]
                if piece_data:
                    piece_class = piece_types[piece_data['type']]
                    piece = piece_class(piece_data['color'])
                    piece.has_moved = piece_data['has_moved']
                    if piece_data['type'] == 'Pawn':
                        piece.en_passant_vulnerable = piece_data.get('en_passant_vulnerable', False)
                    board.board[i][j] = piece
        
        board.current_player = data['current_player']
        board.move_history = data['move_history']
        return board

def save_game(board, filename):
    """Save the current game state to a file"""
    with open(filename, 'w') as f:
        json.dump(board.to_dict(), f)

def load_game(filename):
    """Load a game state from a file"""
    with open(filename, 'r') as f:
        data = json.load(f)
    return ChessBoard.from_dict(data)

def parse_move(input_str):
    """Parse various move input formats and return start and end positions"""
    input_str = input_str.lower().strip()
    
    if input_str == 'quit':
        return None, None
    elif input_str == 'save':
        return 'save', None
    elif input_str == 'load':
        return 'load', None
        
    # Try to parse full move format (e.g., "a2 to a4" or "a2a4" or "a2-a4")
    parts = input_str.replace('to', ' ').replace('-', ' ').split()
    
    if len(parts) == 2:
        # We have a full move
        try:
            start_pos = convert_notation_to_index(parts[0])
            end_pos = convert_notation_to_index(parts[1])
            return start_pos, end_pos
        except ValueError:
            raise ValueError("Invalid move format. Use 'letter number' (e.g., 'a2 to a4' or 'a2 a4')")
    elif len(parts) == 1:
        # We have just the start position
        try:
            start_pos = convert_notation_to_index(parts[0])
            return start_pos, None
        except ValueError:
            raise ValueError("Invalid position. Use format 'letter number' (e.g., 'a2')")
    else:
        raise ValueError("Invalid input. Use format 'a2 to a4' or just 'a2'")

def convert_notation_to_index(position):
    """Convert chess notation (e.g., 'a2') to board indices (row, col)"""
    try:
        col = ord(position[0].lower()) - ord('a')
        row = 8 - int(position[1])
        
        if not (0 <= row < 8 and 0 <= col < 8):
            raise ValueError
            
        return row, col
    except:
        raise ValueError("Invalid position. Use format 'letter number' (e.g., 'a2')")

def convert_index_to_notation(row, col):
    """Convert board indices to chess notation"""
    return f"{chr(col + ord('a'))}{8-row}"

def play_chess():
    board = ChessBoard()
    while True:
        board.display()
        print(f"\n{board.current_player}'s turn")
        
        try:
            move = input("Enter move (e.g., 'e2 to e4'), 'save', 'load', or 'quit': ").strip()
            start_pos, end_pos = parse_move(move)
            
            if start_pos == 'save':
                filename = input("Enter filename to save: ")
                save_game(board, filename)
                print(f"Game saved to {filename}")
                continue
            elif start_pos == 'load':
                filename = input("Enter filename to load: ")
                board = load_game(filename)
                print(f"Game loaded from {filename}")
                continue
            elif start_pos is None:  # User typed 'quit'
                break
                
            if end_pos is None:
                # User only entered start position, ask for end position
                end = input("Enter end position (e.g., 'e4'): ").strip()
                if end.lower() == 'quit':
                    break
                end_pos = convert_notation_to_index(end)
            
            result = board.move_piece(start_pos, end_pos)
            if result == 'checkmate':
                start_notation = convert_index_to_notation(start_pos[0], start_pos[1])
                end_notation = convert_index_to_notation(end_pos[0], end_pos[1])
                print(f"Moved from {start_notation} to {end_notation}")
                board.display()
                winner = 'White' if board.current_player == 'black' else 'Black'
                print(f"\nCheckmate! {winner} wins!")
                break
            elif result == 'stalemate':
                start_notation = convert_index_to_notation(start_pos[0], start_pos[1])
                end_notation = convert_index_to_notation(end_pos[0], end_pos[1])
                print(f"Moved from {start_notation} to {end_notation}")
                board.display()
                print("\nStalemate! Game is a draw!")
                break
            elif result == 'check':
                start_notation = convert_index_to_notation(start_pos[0], start_pos[1])
                end_notation = convert_index_to_notation(end_pos[0], end_pos[1])
                print(f"Moved from {start_notation} to {end_notation}")
                print("Check!")
            elif result:
                start_notation = convert_index_to_notation(start_pos[0], start_pos[1])
                end_notation = convert_index_to_notation(end_pos[0], end_pos[1])
                print(f"Moved from {start_notation} to {end_notation}")
            else:
                start_notation = convert_index_to_notation(start_pos[0], start_pos[1])
                end_notation = convert_index_to_notation(end_pos[0], end_pos[1])
                print(f"Invalid move: {start_notation} to {end_notation}")
                
        except ValueError as e:
            print(str(e))
        except FileNotFoundError:
            print("File not found.")
        except json.JSONDecodeError:
            print("Invalid save file format.")
        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    play_chess()