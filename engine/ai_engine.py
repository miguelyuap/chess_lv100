"""Chess AI Engine module for Chess Lv.100.

Implements Minimax algorithm with Alpha-Beta pruning, Piece-Square Tables (PST),
move ordering (MVV-LVA), level calibration (1-100), and asynchronous threaded computation.
"""

import random
import threading
from typing import Callable, Optional, Tuple, List
import chess

# Material Values (in centipawns)
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Piece-Square Tables (PST) from White's perspective (index 0 = a8, index 63 = h1)
PAWN_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
     5,  5, 10, 25, 25, 10,  5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5, -5,-10,  0,  0,-10, -5,  5,
     5, 10, 10,-20,-20, 10, 10,  5,
     0,  0,  0,  0,  0,  0,  0,  0
]

KNIGHT_TABLE = [
   -50,-40,-30,-30,-30,-30,-40,-50,
   -40,-20,  0,  0,  0,  0,-20,-40,
   -30,  0, 10, 15, 15, 10,  0,-30,
   -30,  5, 15, 20, 20, 15,  5,-30,
   -30,  0, 15, 20, 20, 15,  0,-30,
   -30,  5, 10, 15, 15, 10,  5,-30,
   -40,-20,  0,  5,  5,  0,-20,-40,
   -50,-40,-30,-30,-30,-30,-40,-50
]

BISHOP_TABLE = [
   -20,-10,-10,-10,-10,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5, 10, 10,  5,  0,-10,
   -10,  5,  5, 10, 10,  5,  5,-10,
   -10,  0, 10, 10, 10, 10,  0,-10,
   -10, 10, 10, 10, 10, 10, 10,-10,
   -10,  5,  0,  0,  0,  0,  5,-10,
   -20,-10,-10,-10,-10,-10,-10,-20
]

ROOK_TABLE = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
]

QUEEN_TABLE = [
   -20,-10,-10, -5, -5,-10,-10,-20,
   -10,  0,  0,  0,  0,  0,  0,-10,
   -10,  0,  5,  5,  5,  5,  0,-10,
    -5,  0,  5,  5,  5,  5,  0, -5,
     0,  0,  5,  5,  5,  5,  0, -5,
   -10,  5,  5,  5,  5,  5,  0,-10,
   -10,  0,  5,  0,  0,  0,  0,-10,
   -20,-10,-10, -5, -5,-10,-10,-20
]

KING_MIDGAME_TABLE = [
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -30,-40,-40,-50,-50,-40,-40,-30,
   -20,-30,-30,-40,-40,-30,-30,-20,
   -10,-20,-20,-20,-20,-20,-20,-10,
    20, 20,  0,  0,  0,  0, 20, 20,
    20, 30, 10,  0,  0, 10, 30, 20
]


class AIEngine:
    """Chess AI algorithm provider with Minimax, Alpha-Beta pruning, and level scaling."""

    def __init__(self) -> None:
        self.is_thinking: bool = False

    @staticmethod
    def evaluate_board(board: chess.Board) -> int:
        """Evaluates the current board position from White's perspective in centipawns.

        Args:
            board: The python-chess Board object to evaluate.

        Returns:
            Evaluation score integer (positive favors White, negative favors Black).
        """
        if board.is_checkmate():
            return -30000 if board.turn == chess.WHITE else 30000
        if board.is_stalemate() or board.is_insufficient_material() or board.is_fifty_moves():
            return 0

        score = 0

        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if not piece:
                continue

            # Base material value
            val = PIECE_VALUES[piece.piece_type]

            # Positional score from table
            rank = chess.square_rank(square)
            file = chess.square_file(square)

            # White PST index vs Black PST index (flipped vertically)
            sq_idx = (7 - rank) * 8 + file if piece.color == chess.WHITE else rank * 8 + file

            pst_val = 0
            if piece.piece_type == chess.PAWN:
                pst_val = PAWN_TABLE[sq_idx]
            elif piece.piece_type == chess.KNIGHT:
                pst_val = KNIGHT_TABLE[sq_idx]
            elif piece.piece_type == chess.BISHOP:
                pst_val = BISHOP_TABLE[sq_idx]
            elif piece.piece_type == chess.ROOK:
                pst_val = ROOK_TABLE[sq_idx]
            elif piece.piece_type == chess.QUEEN:
                pst_val = QUEEN_TABLE[sq_idx]
            elif piece.piece_type == chess.KING:
                pst_val = KING_MIDGAME_TABLE[sq_idx]

            total_piece_score = val + pst_val

            if piece.color == chess.WHITE:
                score += total_piece_score
            else:
                score -= total_piece_score

        return score

    def _order_moves(self, board: chess.Board, moves: List[chess.Move]) -> List[chess.Move]:
        """Orders moves to optimize Alpha-Beta cutoffs (captures first, MVV-LVA)."""
        def move_priority(m: chess.Move) -> int:
            priority = 0
            if board.is_capture(m):
                attacker = board.piece_at(m.from_square)
                victim = board.piece_at(m.to_square)
                att_val = PIECE_VALUES.get(attacker.piece_type, 100) if attacker else 100
                vic_val = PIECE_VALUES.get(victim.piece_type, 100) if victim else 100
                priority += 1000 + (vic_val * 10 - att_val)
            if m.promotion:
                priority += 800
            if board.gives_check(m):
                priority += 500
            return priority

        return sorted(moves, key=move_priority, reverse=True)

    def minimax(self, board: chess.Board, depth: int, alpha: int, beta: int, is_maximizing: bool) -> Tuple[int, Optional[chess.Move]]:
        """Minimax search with Alpha-Beta pruning.

        Args:
            board: Current python-chess Board.
            depth: Remaining search depth.
            alpha: Best score for maximizing player.
            beta: Best score for minimizing player.
            is_maximizing: True if maximizing turn (White), False if minimizing (Black).

        Returns:
            Tuple of (best score, best move).
        """
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None

        legal_moves = list(board.legal_moves)
        ordered_moves = self._order_moves(board, legal_moves)

        best_move: Optional[chess.Move] = None

        if is_maximizing:
            max_eval = -99999
            for move in ordered_moves:
                board.push(move)
                eval_val, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()

                if eval_val > max_eval:
                    max_eval = eval_val
                    best_move = move

                alpha = max(alpha, eval_val)
                if beta <= alpha:
                    break  # Beta cutoff
            return max_eval, best_move
        else:
            min_eval = 99999
            for move in ordered_moves:
                board.push(move)
                eval_val, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()

                if eval_val < min_eval:
                    min_eval = eval_val
                    best_move = move

                beta = min(beta, eval_val)
                if beta <= alpha:
                    break  # Alpha cutoff
            return min_eval, best_move

    def get_best_move(self, board: chess.Board, level: int) -> Optional[chess.Move]:
        """Calculates the best move calibrated for difficulty level (1-100).

        Args:
            board: Current python-chess Board state.
            level: Difficulty level (1 to 100).

        Returns:
            The selected chess.Move or None if no legal moves exist.
        """
        legal_moves = list(board.legal_moves)
        if not legal_moves:
            return None

        # Level to Search Depth mapping
        if level <= 15:
            depth = 1
        elif level <= 45:
            depth = 2
        elif level <= 75:
            depth = 3
        elif level <= 90:
            depth = 4
        else:
            depth = 4  # Depth 4 + strict evaluation

        is_maximizing = (board.turn == chess.WHITE)
        _, best_move = self.minimax(board.copy(), depth, -99999, 99999, is_maximizing)

        # Introduce stochastic error for lower levels (1-30)
        if level < 30 and random.random() < ((30 - level) / 35.0):
            # Pick a semi-random legal move occasionally
            captures = [m for m in legal_moves if board.is_capture(m)]
            if captures and random.random() < 0.5:
                return random.choice(captures)
            return random.choice(legal_moves)

        return best_move or random.choice(legal_moves)

    def get_best_move_async(
        self,
        board: chess.Board,
        level: int,
        callback: Callable[[Optional[chess.Move]], None]
    ) -> None:
        """Launches threaded background computation for AI move.

        Args:
            board: Current board state.
            level: Difficulty level (1-100).
            callback: Function to invoke with the calculated move on completion.
        """
        self.is_thinking = True

        def worker():
            board_copy = board.copy()
            move = self.get_best_move(board_copy, level)
            self.is_thinking = False
            callback(move)

        thread = threading.Thread(target=worker, daemon=True)
        thread.start()
