"""Game state module encapsulating python-chess functionality.

Manages board representation, move validation, move history, and game status.
"""

from typing import List, Optional
import chess


class GameState:
    """Encapsulates python-chess Board logic and history for the application."""

    def __init__(self, fen: Optional[str] = None) -> None:
        """Initialize the game state.

        Args:
            fen: Optional FEN string to initialize board position.
        """
        self._board: chess.Board = chess.Board(fen) if fen else chess.Board()

    @property
    def board(self) -> chess.Board:
        """Returns the underlying python-chess Board instance."""
        return self._board

    @property
    def turn(self) -> chess.Color:
        """Returns the side whose turn it is to move (chess.WHITE or chess.BLACK)."""
        return self._board.turn

    @property
    def last_move(self) -> Optional[chess.Move]:
        """Returns the last executed move if available."""
        return self._board.peek() if self._board.move_stack else None

    def get_piece_at(self, square: int) -> Optional[chess.Piece]:
        """Gets the piece at the specified square index (0-63)."""
        return self._board.piece_at(square)

    def get_legal_moves_for_square(self, square: int) -> List[chess.Move]:
        """Returns all legal moves originating from the given square index.

        Args:
            square: Board square index (0-63).

        Returns:
            List of legal python-chess Move objects from the square.
        """
        return [move for move in self._board.legal_moves if move.from_square == square]

    def make_move(self, move: chess.Move) -> bool:
        """Attempts to execute a move on the board if legal.

        Args:
            move: The python-chess Move to execute.

        Returns:
            True if move was legal and executed, False otherwise.
        """
        if move in self._board.legal_moves:
            self._board.push(move)
            return True
        return False

    def undo_move(self) -> Optional[chess.Move]:
        """Pops the last executed move from the stack if available.

        Returns:
            The undone Move object, or None if stack is empty.
        """
        if self._board.move_stack:
            return self._board.pop()
        return None

    def reset(self) -> None:
        """Resets the board to the standard starting position."""
        self._board.reset()

    def is_game_over(self) -> bool:
        """Checks if the game has ended (checkmate, stalemate, insufficient material, etc.)."""
        return self._board.is_game_over()

    def get_status_text(self) -> str:
        """Generates a human-readable status string for the current game state."""
        if self._board.is_checkmate():
            winner = "Negras" if self.turn == chess.WHITE else "Blancas"
            return f"¡Jaque Mate! Ganan las {winner}."
        if self._board.is_stalemate():
            return "Tablas por Ahogado."
        if self._board.is_insufficient_material():
            return "Tablas por Material Insuficiente."
        if self._board.is_fifty_moves():
            return "Tablas por Regla de 50 Movimientos."
        if self._board.is_repetition():
            return "Tablas por Triple Repetición."
        if self._board.is_check():
            turn_str = "Blancas" if self.turn == chess.WHITE else "Negras"
            return f"¡Jaque a las {turn_str}!"
        
        turn_str = "Blancas" if self.turn == chess.WHITE else "Negras"
        return f"Turno de las {turn_str}"
