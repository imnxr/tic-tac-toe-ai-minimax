"""
Clean Tic Tac Toe UI with difficulty modes, themes, and sound.

Run:
    python game_ui.py

The game rules stay in a separate logic file. This file only handles the
visual interface, clicks, sounds, score display, and screen updates.
"""

from __future__ import annotations

import ctypes
import threading
import tkinter as tk
from tkinter import messagebox

try:
    import winsound
except ImportError:
    winsound = None

from game_logic import (
    DIFFICULTY_EASY,
    DIFFICULTY_HARD,
    DIFFICULTY_MEDIUM,
    DRAW,
    EMPTY,
    PLAYER_O,
    PLAYER_X,
    WINNING_LINES,
    check_winner,
    create_board,
    get_ai_move,
    make_move,
)


WINDOW_WIDTH = 1180
WINDOW_HEIGHT = 760

LIGHT_THEME = {
    "background": "#f5f7fb",
    "surface": "#ffffff",
    "surface_soft": "#f8fafc",
    "surface_hover": "#eef6ff",
    "border": "#d8e1ec",
    "divider": "#e8edf5",
    "shadow": "#dbe3ef",
    "text": "#111827",
    "muted": "#64748b",
    "x": "#2563eb",
    "x_soft": "#93c5fd",
    "o": "#db2777",
    "o_soft": "#f9a8d4",
    "success": "#16a34a",
    "warning": "#d97706",
    "danger": "#dc2626",
    "selected_fill": "#111827",
    "selected_text": "#ffffff",
}

DARK_THEME = {
    "background": "#0f172a",
    "surface": "#111827",
    "surface_soft": "#1f2937",
    "surface_hover": "#243b53",
    "border": "#334155",
    "divider": "#263549",
    "shadow": "#020617",
    "text": "#f8fafc",
    "muted": "#94a3b8",
    "x": "#60a5fa",
    "x_soft": "#bfdbfe",
    "o": "#f472b6",
    "o_soft": "#fbcfe8",
    "success": "#4ade80",
    "warning": "#fbbf24",
    "danger": "#f87171",
    "selected_fill": "#f8fafc",
    "selected_text": "#111827",
}


def enable_dpi_awareness() -> None:
    """Make Tkinter look sharper on high-DPI Windows displays."""
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        try:
            ctypes.windll.user32.SetProcessDPIAware()
        except Exception:
            pass


class TicTacToeUI:
    def __init__(self) -> None:
        enable_dpi_awareness()

        self.root = tk.Tk()
        self.root.title("Tic Tac Toe")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.minsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self.root.maxsize(WINDOW_WIDTH, WINDOW_HEIGHT)
        self._center_window()

        self.canvas = tk.Canvas(
            self.root,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0,
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.theme_name = "light"
        self.theme = LIGHT_THEME
        self.sound_enabled = True
        self.difficulty = DIFFICULTY_HARD

        self.board = create_board()
        self.game_over = False
        self.ai_thinking = False
        self.hover_cell: int | None = None
        self.winning_line: tuple[int, int, int] | None = None
        self.scores = {"human": 0, "ai": 0, "draw": 0}

        self.board_x = 108
        self.board_y = 178
        self.cell_size = 148
        self.gap = 22
        self.cells = self._build_cells()

        self.sound_button = (850, 44, 988, 86)
        self.theme_button = (1002, 44, 1132, 86)
        self.difficulty_buttons = {
            DIFFICULTY_EASY: (740, 344, 850, 390),
            DIFFICULTY_MEDIUM: (862, 344, 982, 390),
            DIFFICULTY_HARD: (994, 344, 1094, 390),
        }
        self.reset_button = (740, 614, 914, 666)
        self.new_match_button = (930, 614, 1094, 666)

        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Leave>", self.on_leave)
        self.root.bind("<r>", lambda _event: self.reset_board())
        self.root.bind("<R>", lambda _event: self.reset_board())
        self.root.bind("<n>", lambda _event: self.new_match())
        self.root.bind("<N>", lambda _event: self.new_match())

        self.apply_theme()
        self.draw()

    def _center_window(self) -> None:
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = max(0, (screen_width - WINDOW_WIDTH) // 2)
        y = max(0, (screen_height - WINDOW_HEIGHT) // 2)
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}+{x}+{y}")

    def _build_cells(self) -> list[tuple[int, int, int, int]]:
        cells: list[tuple[int, int, int, int]] = []
        for row in range(3):
            for col in range(3):
                x1 = self.board_x + col * (self.cell_size + self.gap)
                y1 = self.board_y + row * (self.cell_size + self.gap)
                cells.append((x1, y1, x1 + self.cell_size, y1 + self.cell_size))
        return cells

    def run(self) -> None:
        self.root.mainloop()

    def apply_theme(self) -> None:
        self.root.configure(bg=self.theme["background"])
        self.canvas.configure(bg=self.theme["background"])

    def draw(self) -> None:
        self.canvas.delete("all")
        self._draw_header()
        self._draw_board_card()
        self._draw_side_card()
        self._draw_footer()

    def _draw_header(self) -> None:
        self.canvas.create_text(
            64,
            50,
            text="Tic Tac Toe",
            fill=self.theme["text"],
            font=("Segoe UI", 34, "bold"),
            anchor="w",
        )
        self.canvas.create_text(
            66,
            90,
            text="Choose a level and play against the computer",
            fill=self.theme["muted"],
            font=("Segoe UI", 13),
            anchor="w",
        )

        self._button(self.sound_button, self._sound_label(), selected=False)
        self._button(self.theme_button, self._theme_label(), selected=False)

    def _draw_board_card(self) -> None:
        self._card(54, 126, 664, 690)

        for index, rect in enumerate(self.cells):
            self._draw_cell(index, rect)

        for index, rect in enumerate(self.cells):
            mark = self.board[index]
            is_winner = self.winning_line is not None and index in self.winning_line
            if mark == PLAYER_X:
                self._draw_x(rect, is_winner)
            elif mark == PLAYER_O:
                self._draw_o(rect, is_winner)
            elif self.hover_cell == index and not self.ai_thinking and not self.game_over:
                self._draw_x(rect, False, ghost=True)

        if self.winning_line is not None:
            self._draw_winning_line()

    def _draw_cell(self, index: int, rect: tuple[int, int, int, int]) -> None:
        x1, y1, x2, y2 = rect
        is_empty = self.board[index] == EMPTY
        is_hovered = self.hover_cell == index and is_empty and not self.game_over
        is_winner = self.winning_line is not None and index in self.winning_line

        fill = self.theme["surface_soft"]
        outline = self.theme["border"]
        if is_hovered and not self.ai_thinking:
            fill = self.theme["surface_hover"]
            outline = self.theme["x"]
        if is_winner:
            fill = "#ecfdf5" if self.theme_name == "light" else "#113525"
            outline = self.theme["success"]

        self.canvas.create_rectangle(
            x1 + 7,
            y1 + 8,
            x2 + 7,
            y2 + 8,
            fill=self.theme["shadow"],
            outline="",
        )
        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=fill,
            outline=outline,
            width=2,
        )

    def _draw_x(self, rect: tuple[int, int, int, int], is_winner: bool, ghost: bool = False) -> None:
        x1, y1, x2, y2 = rect
        pad = 46
        color = self.theme["success"] if is_winner else self.theme["x"]
        width = 8

        if ghost:
            color = self.theme["x_soft"]
            width = 5

        self.canvas.create_line(
            x1 + pad,
            y1 + pad,
            x2 - pad,
            y2 - pad,
            fill=color,
            width=width,
            capstyle=tk.ROUND,
        )
        self.canvas.create_line(
            x2 - pad,
            y1 + pad,
            x1 + pad,
            y2 - pad,
            fill=color,
            width=width,
            capstyle=tk.ROUND,
        )

    def _draw_o(self, rect: tuple[int, int, int, int], is_winner: bool) -> None:
        x1, y1, x2, y2 = rect
        pad = 42
        color = self.theme["success"] if is_winner else self.theme["o"]
        self.canvas.create_oval(
            x1 + pad,
            y1 + pad,
            x2 - pad,
            y2 - pad,
            outline=color,
            width=8,
        )

    def _draw_winning_line(self) -> None:
        assert self.winning_line is not None
        start = self._center(self.cells[self.winning_line[0]])
        end = self._center(self.cells[self.winning_line[-1]])
        self.canvas.create_line(
            start[0],
            start[1],
            end[0],
            end[1],
            fill=self.theme["success"],
            width=5,
            capstyle=tk.ROUND,
        )

    def _draw_side_card(self) -> None:
        self._card(704, 126, 1126, 690)

        status, status_color = self._status_text()
        self.canvas.create_text(
            740,
            170,
            text="Status",
            fill=self.theme["muted"],
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )
        self.canvas.create_text(
            740,
            210,
            text=status,
            fill=status_color,
            font=("Segoe UI", 25, "bold"),
            anchor="w",
        )

        self.canvas.create_text(
            740,
            262,
            text="Marks",
            fill=self.theme["muted"],
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        self._mark_chip(740, 282, 910, 320, "Player", PLAYER_X, self.theme["x"])
        self._mark_chip(924, 282, 1094, 320, "Computer", PLAYER_O, self.theme["o"])

        self.canvas.create_text(
            740,
            332,
            text="Difficulty",
            fill=self.theme["muted"],
            font=("Segoe UI", 10, "bold"),
            anchor="w",
        )
        for label, rect in self.difficulty_buttons.items():
            self._button(rect, label, selected=label == self.difficulty)

        self._divider(740, 420, 1094)
        self.canvas.create_text(
            740,
            456,
            text="Scoreboard",
            fill=self.theme["text"],
            font=("Segoe UI", 17, "bold"),
            anchor="w",
        )
        self._score_row(740, 500, "Player", self.scores["human"], self.theme["x"])
        self._score_row(740, 540, "Computer", self.scores["ai"], self.theme["o"])
        self._score_row(740, 580, "Draws", self.scores["draw"], self.theme["warning"])

        self._button(self.reset_button, "Reset board", selected=True)
        self._button(self.new_match_button, "New match", selected=False)

    def _mark_chip(
        self,
        x1: int,
        y1: int,
        x2: int,
        y2: int,
        label: str,
        mark: str,
        color: str,
    ) -> None:
        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=self.theme["surface_soft"],
            outline=self.theme["border"],
            width=1,
        )
        self.canvas.create_text(
            x1 + 16,
            (y1 + y2) / 2,
            text=label,
            fill=self.theme["text"],
            font=("Segoe UI", 11, "bold"),
            anchor="w",
        )
        self.canvas.create_text(
            x2 - 18,
            (y1 + y2) / 2,
            text=mark,
            fill=color,
            font=("Segoe UI", 17, "bold"),
            anchor="e",
        )

    def _score_row(self, x: int, y: int, label: str, score: int, color: str) -> None:
        self.canvas.create_text(
            x,
            y,
            text=label,
            fill=self.theme["text"],
            font=("Segoe UI", 12, "bold"),
            anchor="w",
        )
        self.canvas.create_text(
            1094,
            y,
            text=str(score),
            fill=color,
            font=("Segoe UI", 17, "bold"),
            anchor="e",
        )
        self.canvas.create_line(x, y + 22, 1094, y + 22, fill=self.theme["divider"])

    def _button(self, rect: tuple[int, int, int, int], text: str, selected: bool) -> None:
        x1, y1, x2, y2 = rect
        fill = self.theme["selected_fill"] if selected else self.theme["surface"]
        outline = self.theme["selected_fill"] if selected else self.theme["border"]
        text_color = self.theme["selected_text"] if selected else self.theme["text"]

        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=fill,
            outline=outline,
            width=2 if selected else 1,
        )
        self.canvas.create_text(
            (x1 + x2) / 2,
            (y1 + y2) / 2,
            text=text,
            fill=text_color,
            font=("Segoe UI", 11, "bold"),
        )

    def _draw_footer(self) -> None:
        self.canvas.create_text(
            64,
            724,
            text="Click an empty square to play. Press R to reset, N for a new match.",
            fill=self.theme["muted"],
            font=("Segoe UI", 11),
            anchor="w",
        )

    def _card(self, x1: int, y1: int, x2: int, y2: int) -> None:
        self.canvas.create_rectangle(
            x1 + 6,
            y1 + 8,
            x2 + 6,
            y2 + 8,
            fill=self.theme["shadow"],
            outline="",
        )
        self.canvas.create_rectangle(
            x1,
            y1,
            x2,
            y2,
            fill=self.theme["surface"],
            outline=self.theme["border"],
            width=1,
        )

    def _divider(self, x1: int, y: int, x2: int) -> None:
        self.canvas.create_line(x1, y, x2, y, fill=self.theme["divider"])

    def _sound_label(self) -> str:
        return "Sound: On" if self.sound_enabled else "Sound: Off"

    def _theme_label(self) -> str:
        return "Dark theme" if self.theme_name == "light" else "Light theme"

    def _status_text(self) -> tuple[str, str]:
        result = check_winner(self.board)
        if self.ai_thinking:
            return "Computer thinking...", self.theme["o"]
        if result == PLAYER_X:
            return "Player wins", self.theme["success"]
        if result == PLAYER_O:
            return "Computer wins", self.theme["danger"]
        if result == DRAW:
            return "Draw game", self.theme["warning"]
        return "Player turn", self.theme["x"]

    def on_motion(self, event: tk.Event) -> None:
        hovered = self._cell_at(event.x, event.y)
        if hovered != self.hover_cell:
            self.hover_cell = hovered
            self.draw()

        self.canvas.configure(cursor="hand2" if self._is_clickable(event.x, event.y) else "")

    def on_leave(self, _event: tk.Event) -> None:
        self.hover_cell = None
        self.canvas.configure(cursor="")
        self.draw()

    def on_click(self, event: tk.Event) -> None:
        if self._point_in_rect(event.x, event.y, self.sound_button):
            self.toggle_sound()
            return

        if self._point_in_rect(event.x, event.y, self.theme_button):
            self.toggle_theme()
            return

        for difficulty, rect in self.difficulty_buttons.items():
            if self._point_in_rect(event.x, event.y, rect):
                self.difficulty = difficulty
                self.draw()
                return

        if self._point_in_rect(event.x, event.y, self.reset_button):
            self.reset_board()
            return

        if self._point_in_rect(event.x, event.y, self.new_match_button):
            self.new_match()
            return

        if self.game_over or self.ai_thinking:
            return

        cell = self._cell_at(event.x, event.y)
        if cell is None:
            return

        if make_move(self.board, cell, PLAYER_X):
            self.play_sound("move")
            self.after_human_move()

    def after_human_move(self) -> None:
        result = check_winner(self.board)
        if result is not None:
            self.finish_game(result)
            return

        self.ai_thinking = True
        self.hover_cell = None
        self.draw()
        self.root.after(320, self.play_computer_turn)

    def play_computer_turn(self) -> None:
        computer_move = get_ai_move(self.board, PLAYER_O, self.difficulty)
        if computer_move is not None:
            make_move(self.board, computer_move, PLAYER_O)
            self.play_sound("move")

        self.ai_thinking = False
        result = check_winner(self.board)
        if result is not None:
            self.finish_game(result)
        else:
            self.draw()

    def finish_game(self, result: str) -> None:
        self.game_over = True
        self.winning_line = self._find_winning_line()

        if result == PLAYER_X:
            self.scores["human"] += 1
            self.root.after(90, lambda: self.play_sound("win"))
        elif result == PLAYER_O:
            self.scores["ai"] += 1
            self.root.after(90, lambda: self.play_sound("lose"))
        elif result == DRAW:
            self.scores["draw"] += 1
            self.root.after(90, lambda: self.play_sound("draw"))

        self.draw()

    def toggle_sound(self) -> None:
        self.sound_enabled = not self.sound_enabled
        if self.sound_enabled:
            self.play_sound("move")
        self.draw()

    def toggle_theme(self) -> None:
        if self.theme_name == "light":
            self.theme_name = "dark"
            self.theme = DARK_THEME
        else:
            self.theme_name = "light"
            self.theme = LIGHT_THEME

        self.apply_theme()
        self.draw()

    def reset_board(self) -> None:
        self.board = create_board()
        self.game_over = False
        self.ai_thinking = False
        self.hover_cell = None
        self.winning_line = None
        self.canvas.configure(cursor="")
        self.draw()

    def new_match(self) -> None:
        self.scores = {"human": 0, "ai": 0, "draw": 0}
        self.reset_board()

    def play_sound(self, sound_type: str) -> None:
        if not self.sound_enabled:
            return

        if winsound is None:
            self.root.bell()
            return

        patterns = {
            "move": [(660, 55)],
            "win": [(740, 80), (880, 90), (1040, 130)],
            "lose": [(420, 110), (330, 180)],
            "draw": [(520, 90), (520, 90)],
        }

        def play_pattern() -> None:
            for frequency, duration in patterns.get(sound_type, patterns["move"]):
                winsound.Beep(frequency, duration)

        threading.Thread(target=play_pattern, daemon=True).start()

    def _is_clickable(self, x: int, y: int) -> bool:
        if self._point_in_rect(x, y, self.sound_button):
            return True
        if self._point_in_rect(x, y, self.theme_button):
            return True
        if self._point_in_rect(x, y, self.reset_button):
            return True
        if self._point_in_rect(x, y, self.new_match_button):
            return True
        if any(self._point_in_rect(x, y, rect) for rect in self.difficulty_buttons.values()):
            return True

        cell = self._cell_at(x, y)
        return (
            cell is not None
            and self.board[cell] == EMPTY
            and not self.game_over
            and not self.ai_thinking
        )

    def _find_winning_line(self) -> tuple[int, int, int] | None:
        for line in WINNING_LINES:
            first, second, third = line
            if (
                self.board[first] != EMPTY
                and self.board[first] == self.board[second] == self.board[third]
            ):
                return line
        return None

    def _cell_at(self, x: int, y: int) -> int | None:
        for index, rect in enumerate(self.cells):
            if self._point_in_rect(x, y, rect):
                return index
        return None

    @staticmethod
    def _center(rect: tuple[int, int, int, int]) -> tuple[float, float]:
        return ((rect[0] + rect[2]) / 2, (rect[1] + rect[3]) / 2)

    @staticmethod
    def _point_in_rect(x: int, y: int, rect: tuple[int, int, int, int]) -> bool:
        x1, y1, x2, y2 = rect
        return x1 <= x <= x2 and y1 <= y <= y2


def main() -> None:
    try:
        app = TicTacToeUI()
        app.run()
    except tk.TclError as error:
        messagebox.showerror("UI Error", f"Could not start the interface:\n{error}")


if __name__ == "__main__":
    main()
