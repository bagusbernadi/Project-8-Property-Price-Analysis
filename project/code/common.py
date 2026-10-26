"""Semua path dan konstanta Project 8. ROOT = folder project/."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW_CSV = ROOT / "data" / "raw" / "jabodetabek_house_price.csv"
CLEAN_CSV = ROOT / "data" / "clean" / "listings_clean.csv"
DB_PATH = ROOT / "project_8.duckdb"
SQL_CLEAN = ROOT / "code" / "1-data-preparation" / "sql"
SQL_ANALYSIS = ROOT / "code" / "2-analysis" / "sql"
RES_PREP = ROOT / "results" / "1-data-preparation"
RES_ANALYSIS = ROOT / "results" / "2-analysis"
DOCS_DIR = ROOT / "docs"

# Batas wajar harga per m2 (Rp). ASUMSI, bukan dari sumber data. Lihat docs/definitions.md.
PPM2_MIN = 1_000_000
PPM2_MAX = 100_000_000
MIN_DISTRICT_N = 10  # kecamatan dengan listing kurang dari ini tidak dibandingkan

for _d in (CLEAN_CSV.parent, RES_PREP, RES_ANALYSIS, DOCS_DIR):
    _d.mkdir(parents=True, exist_ok=True)
