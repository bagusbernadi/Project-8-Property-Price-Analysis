"""Tahap 1: bersihkan data mentah, simpan tabel ke DuckDB dan CSV hasil."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import *  # noqa: E402
import duckdb

con = duckdb.connect(str(DB_PATH))
sql = (SQL_CLEAN / "01_clean.sql").read_text().format(
    RAW_CSV=RAW_CSV.as_posix(), PPM2_MIN=PPM2_MIN, PPM2_MAX=PPM2_MAX)
con.execute(sql)
con.execute(f"COPY listings TO '{CLEAN_CSV.as_posix()}' (HEADER, DELIMITER ',')")
con.table("cleaning_log").df().to_csv(RES_PREP / "01_cleaning_log.csv", index=False)
print(con.table("cleaning_log").df().to_string(index=False))
con.close()
