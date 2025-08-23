"""
Calculates the "Toxicity Score" of a piece of code.

The toxicity score is a measure of the code's health, based on metrics
like cyclomatic complexity and line count. A lower score is better.
"""
from radon.visitors import ComplexityVisitor
from radon.raw import analyze

def calculate_average_complexity(code: str) -> float:
    """
    Calculates the average cyclomatic complexity of a block of code,
    including functions and methods in classes.
    """
    if not code.strip():
        return 0.0

    try:
        visitor = ComplexityVisitor.from_code(code)

        total_complexity = 0
        num_blocks = 0

        # Add complexity of top-level functions
        if visitor.functions:
            total_complexity += sum(f.complexity for f in visitor.functions)
            num_blocks += len(visitor.functions)

        # Add complexity of methods in classes
        if visitor.classes:
            for cls in visitor.classes:
                total_complexity += sum(m.complexity for m in cls.methods)
                num_blocks += len(cls.methods)

        if num_blocks == 0:
            return 1.0 # Default complexity for code with no functions/methods

        return total_complexity / num_blocks
    except Exception:
        # If radon fails to parse, assign a high complexity score
        return 25.0

def calculate_lines_of_code(code: str) -> int:
    """
    Calculates the number of logical lines of code.
    """
    if not code.strip():
        return 0
    try:
        return analyze(code).lloc
    except SyntaxError:
        # If the code has a syntax error, we can't measure LLOC.
        # We can either return a high number or estimate from raw lines.
        return len(code.splitlines()) * 2 # Penalize syntax errors

def calculate_toxicity_score(code: str) -> float:
    """
    Calculates a toxicity score for a given piece of code.

    The score is a weighted sum of various code metrics.
    A lower score indicates "healthier" code (less toxic).

    Args:
        code: A string containing the Python code to analyze.

    Returns:
        A float representing the toxicity score.
    """
    # Define weights for each metric. These can be tuned over time.
    WEIGHT_COMPLEXITY = 2.0
    WEIGHT_LOC = 0.1

    avg_complexity = calculate_average_complexity(code)
    loc = calculate_lines_of_code(code)

    # The score is a simple weighted sum.
    # We penalize high complexity more than a high line count.
    score = (avg_complexity * WEIGHT_COMPLEXITY) + (loc * WEIGHT_LOC)

    # print(f"DEBUG: complexity={avg_complexity}, loc={loc}, score={score}")
    return score
