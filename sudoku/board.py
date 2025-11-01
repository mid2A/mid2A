from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Sequence


class InvalidSudokuBoardError(ValueError):
    """Raised when the provided board does not have a valid Sudoku shape."""


@dataclass
class SudokuBoard:
    """Represents a 9x9 Sudoku board with immutable initial clues."""

    board: List[List[int]]
    fixed_cells: List[List[bool]] = field(init=False)
    initial_board: List[List[int]] = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._validate_board(self.board)
        normalized_board = [[int(value) for value in row] for row in self.board]
        self.initial_board = [row[:] for row in normalized_board]
        self.board = [row[:] for row in normalized_board]
        self.fixed_cells = [[value != 0 for value in row] for row in self.initial_board]

    @staticmethod
    def _validate_board(board: Sequence[Sequence[int]]) -> None:
        if len(board) != 9:
            raise InvalidSudokuBoardError("A Sudoku board must have 9 rows.")
        for row in board:
            if len(row) != 9:
                raise InvalidSudokuBoardError("Each Sudoku row must contain 9 values.")
            for value in row:
                if not (0 <= int(value) <= 9):
                    raise InvalidSudokuBoardError(
                        "Sudoku values must be integers in the range 0..9."
                    )

    def is_valid_move(self, row: int, column: int, value: int) -> bool:
        """Return True if placing ``value`` at ``(row, column)`` respects Sudoku rules."""

        if not (0 <= row < 9 and 0 <= column < 9):
            return False
        if not (1 <= value <= 9):
            return False
        if self.fixed_cells[row][column] and self.board[row][column] != value:
            return False

        # Check row
        if any(
            self.board[row][c] == value and c != column
            for c in range(9)
        ):
            return False

        # Check column
        if any(
            self.board[r][column] == value and r != row
            for r in range(9)
        ):
            return False

        # Check 3x3 block
        start_row = (row // 3) * 3
        start_col = (column // 3) * 3
        for r in range(start_row, start_row + 3):
            for c in range(start_col, start_col + 3):
                if (r, c) != (row, column) and self.board[r][c] == value:
                    return False

        return True

    def apply_move(self, row: int, column: int, value: int) -> None:
        """Place ``value`` on the board at ``(row, column)``."""

        if not (0 <= row < 9 and 0 <= column < 9):
            raise IndexError("Row and column must be in the range 0..8.")
        if not (1 <= value <= 9):
            raise ValueError("Sudoku values must be between 1 and 9.")
        if self.fixed_cells[row][column] and self.board[row][column] != value:
            raise ValueError("Cannot change the value of a fixed cell.")
        if not self.is_valid_move(row, column, value):
            raise ValueError("Invalid move for the given row, column, and value.")
        self.board[row][column] = value

    def clear_move(self, row: int, column: int) -> None:
        """Clear the value at ``(row, column)`` if it is not a fixed cell."""

        if not (0 <= row < 9 and 0 <= column < 9):
            raise IndexError("Row and column must be in the range 0..8.")
        if self.fixed_cells[row][column]:
            raise ValueError("Cannot clear a fixed cell.")
        self.board[row][column] = 0

    def is_complete(self) -> bool:
        """Return True if the board is completely and validly filled."""

        for row in range(9):
            for column in range(9):
                value = self.board[row][column]
                if value == 0:
                    return False
                if not self.is_valid_move(row, column, value):
                    return False
        return True


def load_puzzle(puzzle_id: str) -> SudokuBoard:
    """Load a puzzle by ``puzzle_id`` from ``puzzles.json`` and return its board."""

    path = Path(__file__).with_name("puzzles.json")
    with path.open("r", encoding="utf-8") as fp:
        data = json.load(fp)

    puzzles = data.get("puzzles", [])
    for puzzle in puzzles:
        if puzzle.get("id") == puzzle_id:
            board = puzzle.get("board")
            if board is None:
                break
            return SudokuBoard(board)

    raise KeyError(f"Puzzle '{puzzle_id}' not found in puzzles.json")
