# questions.py

def load_questions(path):
    """
    Read the quiz_qa.txt file and return a list of question dicts.

    Expected format in the file (5 lines per question, no blank lines):
        Question text
        A - option text
        B - option text
        C - option text
        Answer: X

    where X is A, B, or C.

    Returns a list of dicts:
        {
            "text": "Question text",
            "A": "option text for A",
            "B": "option text for B",
            "C": "option text for C",
            "correct": "A" / "B" / "C"
        }
    """
    questions = []

    with open(path, encoding="utf-8") as f:
        # Remove empty lines and strip whitespace
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) % 5 != 0:
        raise ValueError(f"File {path} does not contain 5 lines per question.")

    for i in range(0, len(lines), 5):
        q_line, a_line, b_line, c_line, ans_line = lines[i:i + 5]

        def parse_choice(line, expected_prefix):
            # Example line: "A - 3"
            prefix = expected_prefix + " -"
            if not line.startswith(prefix):
                raise ValueError(
                    f"Expected line starting with '{prefix}' but got: {line}"
                )
            return line[len(prefix):].strip()

        a_text = parse_choice(a_line, "A")
        b_text = parse_choice(b_line, "B")
        c_text = parse_choice(c_line, "C")

        # Example answer line: "Answer: A"
        if not ans_line.lower().startswith("answer:"):
            raise ValueError(
                f"Expected answer line like 'Answer: X' but got: {ans_line}"
            )
        correct = ans_line.split(":", 1)[1].strip().upper()

        if correct not in ("A", "B", "C"):
            raise ValueError(
                f"Invalid correct answer '{correct}' at question: {q_line}"
            )

        questions.append({
            "text": q_line,
            "A": a_text,
            "B": b_text,
            "C": c_text,
            "correct": correct,
        })

    return questions


# Small manual test (you can run: python questions.py)
if __name__ == "__main__":
    qs = load_questions("quiz_qa.txt")
    print(f"Loaded {len(qs)} questions.\n")
    for q in qs:
        print(q["text"])
        print("  A:", q["A"])
        print("  B:", q["B"])
        print("  C:", q["C"])
        print("  Correct:", q["correct"])
        print()
