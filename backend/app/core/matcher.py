import numpy as np

MATCH_THRESHOLD = 0.65


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    a_norm = a / np.linalg.norm(a)
    b_norm = b / np.linalg.norm(b)
    return float(np.dot(a_norm, b_norm))


def is_match(a: np.ndarray, b: np.ndarray) -> tuple[bool, float]:
    score = cosine_similarity(a, b)
    return score >= MATCH_THRESHOLD, score
