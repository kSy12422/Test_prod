import pytest
from app import generate_api_token, levenshtein_distance

@pytest.mark.unit
def test_generate_api_token():
    token = generate_api_token()
    assert len(token) == 128
    assert token.isalnum()

@pytest.mark.unit
def test_levenshtein_distance():
    phrase1 = "hello"
    phrase2 = "hello world"
    distance = levenshtein_distance(phrase1, phrase2)
    assert distance == 6

@pytest.mark.unit
def test_levenshtein_distance_empty_phrase():
    phrase1 = ""
    phrase2 = "hello world!"
    distance = levenshtein_distance(phrase1, phrase2)
    assert distance == len(phrase2)

@pytest.mark.unit
def test_levenshtein_distance_same_phrases():
    phrase1 = "hello"
    phrase2 = "hello"
    distance = levenshtein_distance(phrase1, phrase2)
    assert distance == 0