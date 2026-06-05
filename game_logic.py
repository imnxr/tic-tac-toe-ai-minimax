"""
Tic Tac Toe game logic.

This file is intentionally UI-free at the core so it can be imported by a
separate graphical interface. Run it directly to test the logic in a terminal:

    python game_logic.py
"""

from __future__ import annotations

import random
from math import inf


EMPTY = " "
PLAYER_X = "X"
PLAYER_O = "O"
DRAW = "Draw"
DIFFICULTY_EASY = "Easy"
DIFFICULTY_MEDIUM = "Medium"
DIFFICULTY_HARD = "Hard"
DIFFICULTIES = (DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD)

WINNING_LINES = (
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
)

PREFERRED_MOVE_ORDER = (4, 0, 2, 6, 8, 1, 3, 5, 7)


def create_board() -> list[str]:
    """Return a new empty Tic Tac Toe board."""
    return [EMPTY] * 9


def validate_board(board: list[str]) -> None:
    """Raise ValueError if the board is not a valid 9-cell board."""
    if len(board) != 9:
        raise ValueError("Board must contain exactly 9 cells.")

    valid_symbols = {PLAYER_X, PLAYER_O, EMPTY}
    invalid_symbols = [cell for cell in board if cell not in valid_symbols]
    if invalid_symbols:
        raise ValueError("Board cells must be 'X', 'O', or a blank space.")


def available_moves(board: list[str]) -> list[int]:
    """Return all empty cell indexes from 0 to 8."""
    validate_board(board)
    return [index for index, cell in enumerate(board) if cell == EMPTY]


def ordered_available_moves(board: list[str]) -> list[int]:
    """Return available moves with center and corners checked first."""
    open_cells = set(available_moves(board))
    return [move for move in PREFERRED_MOVE_ORDER if move in open_cells]


def make_move(board: list[str], position: int, player: str) -> bool:
    """
    Place player's symbol at position if possible.

    Returns True when the move succeeds and False when the cell is occupied.
    """
    validate_board(board)

    if player not in (PLAYER_X, PLAYER_O):
        raise ValueError("Player must be 'X' or 'O'.")

    if position < 0 or position > 8:
        raise ValueError("Position must be between 0 and 8.")

    if board[position] != EMPTY:
        return False

    board[position] = player
    return True


def check_winner(board: list[str]) -> str | None:
    """
    Return 'X' or 'O' if either player has won.

    Return 'Draw' if the board is full with no winner.
    Return None if the game is still in progress.
    """
    validate_board(board)

    for first, second, third in WINNING_LINES:
        if board[first] != EMPTY and board[first] == board[second] == board[third]:
            return board[first]

    if EMPTY not in board:
        return DRAW

    return None


def is_game_over(board: list[str]) -> bool:
    """Return True if the game has a winner or ends in a draw."""
    return check_winner(board) is not None


def switch_player(player: str) -> str:
    """Return the other Tic Tac Toe player."""
    if player == PLAYER_X:
        return PLAYER_O
    if player == PLAYER_O:
        return PLAYER_X
    raise ValueError("Player must be 'X' or 'O'.")


def score_game_tree(
    board: list[str],
    depth: int,
    is_maximizing: bool,
    ai_player: str,
    human_player: str,
    alpha: float = -inf,
    beta: float = inf,
) -> int:
    """Score the board using recursive game-tree search."""
    result = check_winner(board)

    if result == ai_player:
        return 10 - depth
    if result == human_player:
        return depth - 10
    if result == DRAW:
        return 0

    if is_maximizing:
        best_score = -inf

        for move in ordered_available_moves(board):
            board[move] = ai_player
            score = score_game_tree(
                board,
                depth + 1,
                False,
                ai_player,
                human_player,
                alpha,
                beta,
            )
            board[move] = EMPTY

            best_score = max(best_score, score)
            alpha = max(alpha, score)

            if beta <= alpha:
                break

        return int(best_score)

    best_score = inf

    for move in ordered_available_moves(board):
        board[move] = human_player
        score = score_game_tree(
            board,
            depth + 1,
            True,
            ai_player,
            human_player,
            alpha,
            beta,
        )
        board[move] = EMPTY

        best_score = min(best_score, score)
        beta = min(beta, score)

        if beta <= alpha:
            break

    return int(best_score)


def get_best_move(board: list[str], ai_player: str = PLAYER_O) -> int | None:
    """
    Return the best move index for the AI player.

    The returned index is from 0 to 8. Return None if no move is possible.
    """
    validate_board(board)

    if ai_player not in (PLAYER_X, PLAYER_O):
        raise ValueError("AI player must be 'X' or 'O'.")

    if is_game_over(board):
        return None

    human_player = switch_player(ai_player)
    best_score = -inf
    best_move = None

    for move in ordered_available_moves(board):
        board[move] = ai_player
        score = score_game_tree(board, 0, False, ai_player, human_player)
        board[move] = EMPTY

        if score > best_score:
            best_score = score
            best_move = move

    return best_move


def get_easy_move(board: list[str]) -> int | None:
    """Return a random valid move for the easiest difficulty."""
    if is_game_over(board):
        return None

    moves = available_moves(board)
    if not moves:
        return None
    return random.choice(moves)


def find_immediate_winning_move(board: list[str], player: str) -> int | None:
    """Return a move that lets player win immediately, if one exists."""
    validate_board(board)

    if player not in (PLAYER_X, PLAYER_O):
        raise ValueError("Player must be 'X' or 'O'.")

    for move in ordered_available_moves(board):
        board[move] = player
        is_winning_move = check_winner(board) == player
        board[move] = EMPTY

        if is_winning_move:
            return move

    return None


def get_medium_move(board: list[str], ai_player: str = PLAYER_O) -> int | None:
    """
    Return a balanced move for medium difficulty.

    Medium difficulty wins when it can, blocks immediate danger, then chooses a
    strong-looking move without fully searching every future path.
    """
    validate_board(board)

    if ai_player not in (PLAYER_X, PLAYER_O):
        raise ValueError("AI player must be 'X' or 'O'.")

    if is_game_over(board):
        return None

    human_player = switch_player(ai_player)
    winning_move = find_immediate_winning_move(board, ai_player)
    if winning_move is not None:
        return winning_move

    blocking_move = find_immediate_winning_move(board, human_player)
    if blocking_move is not None:
        return blocking_move

    moves = ordered_available_moves(board)
    if not moves:
        return None

    strong_moves = [move for move in moves if move in (4, 0, 2, 6, 8)]
    if strong_moves:
        return random.choice(strong_moves)

    return random.choice(moves)


def get_ai_move(
    board: list[str],
    ai_player: str = PLAYER_O,
    difficulty: str = DIFFICULTY_HARD,
) -> int | None:
    """Return an AI move for Easy, Medium, or Hard difficulty."""
    validate_board(board)

    if ai_player not in (PLAYER_X, PLAYER_O):
        raise ValueError("AI player must be 'X' or 'O'.")

    normalized_difficulty = difficulty.strip().lower()
    if normalized_difficulty == DIFFICULTY_EASY.lower():
        return get_easy_move(board)
    if normalized_difficulty == DIFFICULTY_MEDIUM.lower():
        return get_medium_move(board, ai_player)
    if normalized_difficulty == DIFFICULTY_HARD.lower():
        return get_best_move(board, ai_player)

    valid_names = ", ".join(DIFFICULTIES)
    raise ValueError(f"Difficulty must be one of: {valid_names}.")


def board_to_rows(board: list[str]) -> list[list[str]]:
    """Convert a flat board list into 3 rows for UI display."""
    validate_board(board)
    return [board[0:3], board[3:6], board[6:9]]


def format_board(board: list[str]) -> str:
    """Return a printable board string for terminal testing."""
    validate_board(board)

    display_cells = [
        str(index + 1) if cell == EMPTY else cell for index, cell in enumerate(board)
    ]

    return (
        f" {display_cells[0]} | {display_cells[1]} | {display_cells[2]} \n"
        "---+---+---\n"
        f" {display_cells[3]} | {display_cells[4]} | {display_cells[5]} \n"
        "---+---+---\n"
        f" {display_cells[6]} | {display_cells[7]} | {display_cells[8]} "
    )


def print_board(board: list[str]) -> None:
    """Print the current board in a readable form."""
    print(format_board(board))


def play_cli() -> None:
    """Simple terminal game for testing the game logic."""
    board = create_board()
    human_player = PLAYER_X
    ai_player = PLAYER_O
    current_player = human_player

    print("Tic Tac Toe AI")
    print("You are X. Enter positions from 1 to 9.")
    print_board(board)

    while not is_game_over(board):
        if current_player == human_player:
            try:
                user_input = input("\nYour move: ").strip()
                move = int(user_input) - 1
            except ValueError:
                print("Please enter a number from 1 to 9.")
                continue

            try:
                if not make_move(board, move, human_player):
                    print("That cell is already occupied. Try again.")
                    continue
            except ValueError as error:
                print(error)
                continue
        else:
            move = get_best_move(board, ai_player)

            if move is None:
                break

            make_move(board, move, ai_player)
            print(f"\nComputer chose position {move + 1}.")

        print()
        print_board(board)
        current_player = switch_player(current_player)

    result = check_winner(board)

    if result == DRAW:
        print("\nResult: Draw.")
    elif result == human_player:
        print("\nResult: You win.")
    else:
        print("\nResult: Computer wins.")


if __name__ == "__main__":
    play_cli()
