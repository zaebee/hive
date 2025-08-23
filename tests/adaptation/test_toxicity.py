"""
Unit tests for the toxicity module.
"""
import pytest
from hive_physics.adaptation.toxicity import calculate_toxicity_score

def test_toxicity_score_simple_function():
    """Tests the toxicity score for a simple, healthy function."""
    code = """
def add(a, b):
    return a + b
"""
    score = calculate_toxicity_score(code)
    # Expected: complexity=1, loc=2. Score = (1 * 2.0) + (2 * 0.1) = 2.2
    assert score == pytest.approx(2.2)

def test_toxicity_score_complex_function():
    """Tests the toxicity score for a more complex function."""
    code = """
def complex_func(a, b, c):
    if a > b:
        if b > c:
            return 1
        else:
            return 2
    else:
        if a > c:
            return 3
        else:
            return 4
"""
    score = calculate_toxicity_score(code)
    # Actual: complexity=4, lloc=11. Score = (4 * 2.0) + (11 * 0.1) = 9.1
    assert score == pytest.approx(9.1)

def test_toxicity_score_empty_code():
    """Tests that an empty code string has a toxicity score of 0."""
    assert calculate_toxicity_score("") == 0.0

def test_toxicity_score_invalid_syntax():
    """Tests that code with invalid syntax gets a high toxicity score."""
    code = "def f(a, b:" # Invalid syntax
    score = calculate_toxicity_score(code)
    # Expected: radon fails, complexity defaults to 25. loc is 1*2=2.
    # Score = (25 * 2.0) + (2 * 0.1) = 50.2
    assert score == pytest.approx(50.2)

def test_toxicity_score_class_method():
    """Tests toxicity score for a class with a method."""
    code = """
class MyClass:
    def my_method(self, x):
        if x > 10:
            return True
        return False
"""
    score = calculate_toxicity_score(code)
    # Expected: complexity=2, loc=5. Score = (2 * 2.0) + (5 * 0.1) = 4.5
    assert score == pytest.approx(4.5)
