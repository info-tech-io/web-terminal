import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from solution import is_palindrome


def test_racecar():
    assert is_palindrome("racecar") is True

def test_hello():
    assert is_palindrome("hello") is False

def test_madam_mixed_case():
    assert is_palindrome("Madam") is True

def test_empty():
    assert is_palindrome("") is True

def test_single_char():
    assert is_palindrome("a") is True

def test_two_chars_no():
    assert is_palindrome("ab") is False
