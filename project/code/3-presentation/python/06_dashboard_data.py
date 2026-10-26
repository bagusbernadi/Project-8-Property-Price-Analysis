"""Tahap 3: file ringkas untuk dashboard (bisa di-commit: tanpa URL listing, hanya ads_id)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import *  # noqa: E402
import duckdb

con = duckdb.connect(str(DB_PATH), read_only=True)
con.execute(f"""COPY (
  SELECT l.ads_id, l.city, l.district, l.certificate, l.price_in_rp, l.building_size_m2, l.land_size_m2,
         l.bedrooms, l.bathrooms, l.lat, l.long, l.price_per_m2, d.median_ppm2 AS district_median_ppm2
  FROM listings l LEFT JOIN district_summary d USING (city, district)
  WHERE l.flag_ppm2_out = 0 AND NOT (l.lat IS NULL OR l.long IS NULL)
  ORDER BY l.ads_id
) TO '{(RES_PRESENT / 'dash_listings.csv').as_posix()}' (HEADER, DELIMITER ',')""")
con.execute(f"""COPY (SELECT * FROM district_summary ORDER BY city, district)
  TO '{(RES_PRESENT / 'dash_districts.csv').as_posix()}' (HEADER, DELIMITER ',')""")
n = con.execute("SELECT count(*) FROM read_csv_auto('" + (RES_PRESENT / 'dash_listings.csv').as_posix() + "')").fetchone()[0]
print("dash_listings baris:", n)
con.close()
