"""Central configuration for L&F MATCH."""
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "outputs"

LOST_FILE = DATA_DIR / "lost.csv"
FOUND_FILE = DATA_DIR / "found.csv"

MATCHES_FILE = OUTPUT_DIR / "matches.csv"
NO_MATCH_FILE = OUTPUT_DIR / "no_match.csv"
UNCLAIMED_FILE = OUTPUT_DIR / "unclaimed.csv"
SUMMARY_FILE = OUTPUT_DIR / "summary.txt"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

ALLOWED_ITEMS = {
    "phone", "wallet", "id_card", "bottle", "bag", "earphones",
    "keys", "umbrella", "calculator", "watch", "spectacles", "other"
}
ALLOWED_COLOURS = {
    "black", "white", "red", "blue", "green",
    "yellow", "pink", "brown", "grey", "orange"
}

# The project brief does not provide a fixed campus-place list.
# Edit this list to match the actual campus vocabulary.
CAMPUS_PLACES = {
    "library", "canteen", "classroom", "laboratory", "lab",
    "bus stop", "parking area", "auditorium", "office",
    "playground", "hostel", "corridor", "main gate",
    "sports room", "seminar hall"
}

LIKELY_THRESHOLD = 3
MAX_DATE_GAP_DAYS = 30
