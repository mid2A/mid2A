"""Sudoku solving utilities."""
from __future__ import annotations

from typing import Optional, Tuple

from .board import SudokuBoard


def _find_empty_cell(board: SudokuBoard) -> Optional[Tuple[int, int]]:
    """Return the coordinates of the first empty cell or ``None`` if full."""

    for row in range(9):
        for column in range(9):
            if board.board[row][column] == 0:
                return row, column
    return None


def solve(board: SudokuBoard) -> bool:
    """Solve ``board`` in-place using backtracking.

    Args:
        board: The :class:`~sudoku.board.SudokuBoard` instance to solve.

    Returns:
        ``True`` if a solution was found and applied to ``board``, ``False`` otherwise.
    """

    empty_cell = _find_empty_cell(board)
    if empty_cell is None:
        return board.is_complete()

    row, column = empty_cell
    for value in range(1, 10):
        if board.is_valid_move(row, column, value):
            board.apply_move(row, column, value)
            if solve(board):
                return True
            board.clear_move(row, column)

    return False
