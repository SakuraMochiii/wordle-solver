# Wordle Solver

A tool that narrows down possible Wordle answers based on your guesses and their feedback. Available as a CLI or a web app.

## Features

- **Constraint-Based Filtering** — enter guesses with green/yellow/grey feedback and see all remaining valid words
- **Duplicate Letter Handling** — correctly handles cases where a letter appears multiple times (e.g., a letter marked yellow in two different positions but only exists once in the target)
- **Auto-Solve** — shows remaining possibilities after each guess entry
- **Undo/Reset** — made a typo? undo your last guess or reset entirely
- **Web App** — visual tile-based interface with click-to-toggle colors and real-time filtering

## How It Works

The solver tracks four types of constraints from your guesses:

| Feedback | Meaning | Constraint |
|----------|---------|------------|
| Green (g) | Correct letter, correct position | Letter must be at this position |
| Yellow (y) | Correct letter, wrong position | Letter is in the word but NOT at this position |
| Grey (x) | Letter not in word (or no more copies) | Letter count capped at confirmed instances |

For duplicate letters: if you guess a word with repeated letters and some are green/yellow while others are grey, the solver infers the exact count of that letter in the target.

## Web App

```bash
cd wordle-solver
python -m http.server
```

Open http://localhost:8000 — type a word, press Enter, then click each tile to toggle its color (grey → yellow → green). Results update in real time.

- **Auto-Coloring** — new guesses are automatically colored based on previous constraints (known greens stay green, confirmed letters get yellow). Just adjust what's wrong.
- **Click-to-Queue** — click any word in the results to load it into the input. Click a different one to replace it. Press Enter to submit.

## CLI

```bash
python solver.py
```

No dependencies required — pure Python 3.

## CLI Usage

Enter each guess as `word feedback` where feedback uses:
- `g` = green (correct position)
- `y` = yellow (in word, wrong position)
- `x` = grey (not in word)

```
=== Wordle Solver ===

Enter guesses as:  word feedback
  g = green (correct position)
  y = yellow (wrong position, in word)
  x = grey (not in word)

  Example: crane xyxgx

Commands: solve, show, undo, reset, quit

Loaded 5757 words.

> crane xygxx
  Added: crane [x y g x x]
  52 possible words:
  brain   drain   frail   grail   grain   trail
  train   wrath   graph   grass   grasp   grant
  ...

> stain xxggg
  Added: stain [x x g x x]
  2 possible words:
  grain   train
```

### Commands

| Command | Action |
|---------|--------|
| `solve` | Show all remaining possible words |
| `show` | Display your current guesses |
| `undo` | Remove your last guess |
| `reset` | Clear all guesses and start over |
| `quit` | Exit the solver |

## Word List

Uses the Stanford GraphBase list of 5757 common five-letter English words.
