from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, Iterable, List, Sequence

from sudoku.board import SudokuBoard, load_puzzle


PUZZLES_PATH = Path(__file__).parent / "sudoku" / "puzzles.json"


def _load_puzzle_metadata() -> Sequence[Dict[str, object]]:
    with PUZZLES_PATH.open("r", encoding="utf-8") as fp:
        data = json.load(fp)
    puzzles = data.get("puzzles", [])
    if not isinstance(puzzles, list):
        raise ValueError("Invalid puzzles.json format: 'puzzles' must be a list.")
    return puzzles


def _group_puzzles_by_difficulty(puzzles: Iterable[Dict[str, object]]) -> Dict[str, List[str]]:
    difficulties: Dict[str, List[str]] = {}
    for puzzle in puzzles:
        puzzle_id = puzzle.get("id")
        if not isinstance(puzzle_id, str):
            continue
        difficulty = puzzle_id.split("-", 1)[0]
        difficulties.setdefault(difficulty, []).append(puzzle_id)
    return difficulties


def _prompt_difficulty(difficulties: Dict[str, List[str]]) -> str:
    difficulty_names = sorted(difficulties)
    while True:
        print("利用可能な難易度:")
        for index, name in enumerate(difficulty_names, start=1):
            count = len(difficulties[name])
            print(f"  {index}. {name} ({count} 件)")
        choice = input("難易度を番号または名前で選択してください: ").strip().lower()
        if not choice:
            print("入力が空です。再度入力してください。")
            continue
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(difficulty_names):
                return difficulty_names[idx]
            print("番号が範囲外です。")
            continue
        if choice in difficulty_names:
            return choice
        print("無効な難易度です。もう一度お試しください。")


def _display_board(board: SudokuBoard) -> None:
    print("    1 2 3 4 5 6 7 8 9")
    print("  +-------------------+")
    for row_index, row in enumerate(board.board, start=1):
        row_values = []
        for column_index, value in enumerate(row, start=1):
            char = str(value) if value != 0 else "."
            row_values.append(char)
            if column_index % 3 == 0 and column_index != 9:
                row_values.append("|")
        row_str = " ".join(row_values)
        print(f"{row_index} | {row_str} |")
        if row_index % 3 == 0 and row_index != 9:
            print("  |-------+-------+-------|")
    print("  +-------------------+")


def _prompt_move() -> Sequence[int] | None:
    raw = input("行 列 値 (0 でマスを空にする、'q' で終了): ").strip()
    if not raw:
        print("入力が空です。'行 列 値' の形式で入力してください。")
        return None
    if raw.lower() in {"q", "quit", "exit"}:
        raise SystemExit
    parts = raw.split()
    if len(parts) != 3:
        print("入力形式が正しくありません。例: '3 4 9'")
        return None
    try:
        row, column, value = (int(part) for part in parts)
    except ValueError:
        print("行・列・値は数字で入力してください。")
        return None
    if not (1 <= row <= 9 and 1 <= column <= 9):
        print("行と列は 1 から 9 の範囲で指定してください。")
        return None
    if not (0 <= value <= 9):
        print("値は 0 から 9 の範囲で指定してください。")
        return None
    return row - 1, column - 1, value


def _play_single_game(board: SudokuBoard) -> None:
    print("数独を開始します。固定数字は変更できません。")
    _display_board(board)
    while not board.is_complete():
        try:
            move = _prompt_move()
        except SystemExit:
            print("ゲームを終了します。")
            raise
        if move is None:
            continue
        row, column, value = move
        try:
            if value == 0:
                board.clear_move(row, column)
            else:
                board.apply_move(row, column, value)
        except ValueError as exc:
            print(f"エラー: {exc}")
            continue
        except IndexError as exc:
            print(f"エラー: {exc}")
            continue
        _display_board(board)
    print("おめでとうございます！パズルをクリアしました。")


def main() -> None:
    puzzles = _load_puzzle_metadata()
    difficulties = _group_puzzles_by_difficulty(puzzles)
    if not difficulties:
        raise SystemExit("puzzles.json に有効なパズルが見つかりません。")

    while True:
        difficulty = _prompt_difficulty(difficulties)
        puzzle_id = random.choice(difficulties[difficulty])
        print(f"'{difficulty}' のパズル (ID: {puzzle_id}) を読み込みます。")
        board = load_puzzle(puzzle_id)
        try:
            _play_single_game(board)
        except SystemExit:
            return
        while True:
            again = input("別のパズルに挑戦しますか? (y/n): ").strip().lower()
            if again in {"y", "yes"}:
                break
            if again in {"n", "no"}:
                print("ご利用ありがとうございました。")
                return
            print("'y' または 'n' を入力してください。")


if __name__ == "__main__":
    main()
