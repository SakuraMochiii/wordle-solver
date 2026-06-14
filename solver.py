import sys
from pathlib import Path


def load_words():
    """Load 5-letter words from the bundled word list."""
    script_dir = Path(__file__).parent
    word_file = script_dir / "words.txt"

    if not word_file.exists():
        print("Error: words.txt not found. Place it in the same directory as solver.py")
        sys.exit(1)

    words = []
    with open(word_file) as f:
        for line in f:
            word = line.strip().lower()
            if len(word) == 5 and word.isalpha():
                words.append(word)

    return words


def parse_guess(guess_str):
    """
    Parse a guess input like: crane gYggg

    Returns (word, feedback) where feedback is a list of 'green', 'yellow', 'grey'.
    Feedback codes: g = green, y = yellow, x = grey
    """
    parts = guess_str.strip().split()
    if len(parts) != 2:
        return None, None

    word = parts[0].lower()
    feedback_str = parts[1].lower()

    if len(word) != 5 or len(feedback_str) != 5:
        return None, None

    feedback = []
    for ch in feedback_str:
        if ch == 'g':
            feedback.append('green')
        elif ch == 'y':
            feedback.append('yellow')
        elif ch == 'x':
            feedback.append('grey')
        else:
            return None, None

    return word, feedback


def build_constraints(guesses):
    """
    From a list of (word, feedback) pairs, derive filtering constraints.

    Handles duplicate letters correctly:
    - If a letter appears multiple times in a guess and some are green/yellow
      while others are grey, the grey tells us the EXACT count of that letter
      in the target (equal to the number of green+yellow instances).
    - If no instances are grey, we only know the MINIMUM count.

    Returns:
        green: dict of position -> letter (must be this letter at this position)
        yellow: dict of position -> set of letters (letter is in word but NOT here)
        min_counts: dict of letter -> int (target has at least this many)
        max_counts: dict of letter -> int (target has at most this many)
    """
    green = {}
    yellow = {i: set() for i in range(5)}
    min_counts = {}
    max_counts = {}

    for word, feedback in guesses:
        letter_confirmed = {}
        letter_greyed = {}

        for i, (ch, fb) in enumerate(zip(word, feedback)):
            if fb == 'green':
                green[i] = ch
                letter_confirmed[ch] = letter_confirmed.get(ch, 0) + 1
            elif fb == 'yellow':
                yellow[i].add(ch)
                letter_confirmed[ch] = letter_confirmed.get(ch, 0) + 1
            else:
                letter_greyed[ch] = letter_greyed.get(ch, 0) + 1

        # Grey on a duplicate letter also excludes that position
        for i, (ch, fb) in enumerate(zip(word, feedback)):
            if fb == 'grey' and letter_confirmed.get(ch, 0) > 0:
                yellow[i].add(ch)

        for ch in set(word):
            confirmed = letter_confirmed.get(ch, 0)
            greyed = letter_greyed.get(ch, 0)

            if ch in min_counts:
                min_counts[ch] = max(min_counts[ch], confirmed)
            else:
                min_counts[ch] = confirmed

            # A grey instance means "no more of this letter beyond what's confirmed"
            if greyed > 0:
                if ch in max_counts:
                    max_counts[ch] = min(max_counts[ch], confirmed)
                else:
                    max_counts[ch] = confirmed

    return green, yellow, min_counts, max_counts


def filter_words(words, green, yellow, min_counts, max_counts):
    """Filter the word list using all derived constraints."""
    results = []

    for word in words:
        if not matches_constraints(word, green, yellow, min_counts, max_counts):
            continue
        results.append(word)

    return sorted(results)


def matches_constraints(word, green, yellow, min_counts, max_counts):
    for pos, letter in green.items():
        if word[pos] != letter:
            return False

    for pos, excluded_letters in yellow.items():
        if word[pos] in excluded_letters:
            return False

    for letter, count in min_counts.items():
        if word.count(letter) < count:
            return False

    for letter, count in max_counts.items():
        if word.count(letter) > count:
            return False

    return True


def display_results(results):
    """Print results in columns."""
    if not results:
        print("  No matching words found.")
        return

    print(f"  {len(results)} possible words:")
    if len(results) <= 60:
        for i in range(0, len(results), 6):
            print("  " + "  ".join(f"{w:<7}" for w in results[i:i+6]))
    else:
        for i in range(0, 60, 6):
            print("  " + "  ".join(f"{w:<7}" for w in results[i:i+6]))
        print(f"  ... and {len(results) - 60} more")


def display_guesses(guesses):
    """Show current guesses with color indicators."""
    if not guesses:
        return
    print("  Current guesses:")
    for word, feedback in guesses:
        colored = ""
        for ch, fb in zip(word, feedback):
            if fb == 'green':
                colored += f"[{ch.upper()}]"
            elif fb == 'yellow':
                colored += f"({ch.upper()})"
            else:
                colored += f" {ch.upper()} "
        print(f"    {colored}")
    print()


def main():
    print("=== Wordle Solver ===")
    print()
    print("Enter guesses as:  word feedback")
    print("  g = green (correct position)")
    print("  y = yellow (wrong position, in word)")
    print("  x = grey (not in word)")
    print()
    print("  Example: crane xyxgx")
    print()
    print("Commands: solve, show, undo, reset, quit")
    print()

    words = load_words()
    print(f"Loaded {len(words)} words.\n")

    guesses = []

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        cmd = line.lower()

        if cmd == 'quit' or cmd == 'q':
            break

        if cmd == 'reset':
            guesses = []
            print("Reset. Enter new guesses.\n")
            continue

        if cmd == 'undo':
            if guesses:
                removed = guesses.pop()
                print(f"  Removed: {removed[0]}")
            else:
                print("  Nothing to undo.")
            continue

        if cmd == 'show':
            display_guesses(guesses)
            continue

        if cmd == 'solve':
            if not guesses:
                print("  No guesses entered yet.\n")
                continue
            green, yellow, min_counts, max_counts = build_constraints(guesses)
            results = filter_words(words, green, yellow, min_counts, max_counts)
            display_results(results)
            print()
            continue

        word, feedback = parse_guess(line)
        if word is None:
            print("  Invalid format. Use: word feedback (e.g., crane xyxgx)")
            print("  Type 'quit' to exit.\n")
            continue

        guesses.append((word, feedback))
        print(f"  Added: {word} [{' '.join(fb[0] for fb in feedback)}]")

        green, yellow, min_counts, max_counts = build_constraints(guesses)
        results = filter_words(words, green, yellow, min_counts, max_counts)

        display_results(results)
        print()


if __name__ == "__main__":
    main()
