from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENROLLED_FACES_DIR = BACKEND_DIR.parent / "data" / "enrolled_faces"
ENROLLED_FACES_DIR.mkdir(parents=True, exist_ok=True)
