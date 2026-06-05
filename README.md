# Tic Tac Toe AI

A clean, playable Tic Tac Toe desktop game built with Python. The project includes a polished Tkinter interface, three computer difficulty levels, score tracking, light/dark themes, and optional sound effects.

## Features

- Clean desktop UI built with Python Tkinter
- Easy, Medium, and Hard difficulty modes
- Player vs Computer gameplay
- Light and dark theme toggle
- Sound toggle for move, win, lose, and draw feedback
- Scoreboard for Player, Computer, and Draws
- Reset board and new match controls
- No third-party packages required

## Screens

The game opens as a desktop window with:

- A 3 x 3 game board on the left
- Status, marks, difficulty, scoreboard, and controls on the right
- Theme and sound controls in the header

## Project Structure

```text
.
|-- main.py
|-- game_ui.py
|-- game_logic.py
|-- requirements.txt
|-- LICENSE
`-- README.md
```

## How to Run

Make sure Python 3.10 or newer is installed.

```bash
python main.py
```

You can also run the UI file directly:

```bash
python game_ui.py
```

## Controls

- Click an empty square to place `X`
- Press `R` to reset the current board
- Press `N` to start a new match
- Use the Sound button to turn sound on or off
- Use the Theme button to switch between light and dark mode
- Choose Easy, Medium, or Hard before or during a match

## Difficulty Levels

- Easy: Chooses from available moves randomly
- Medium: Looks for immediate wins and blocks immediate threats
- Hard: Uses the strongest available decision strategy

## Requirements

This project uses only Python's standard library.

- Python 3.10+
- Tkinter, included with most Python installations

## Author

M. Mansoor Ur Rehman

GitHub: [imnxr](https://github.com/imnxr)

## License

This project is licensed under the MIT License.
