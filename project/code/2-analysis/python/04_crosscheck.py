"""Cek silang Q14: median per kota dan kecamatan dari SQL (DuckDB) vs pandas. Excel tidak dipakai (tidak ada di sesi)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import *  # noqa: E402
import duckdb
import pandas as pd

con = duckdb.connect(str(DB_PATH), read_only=True)
sql_c = con.execute("SELECT city, median(price_per_m2) AS m FROM listings WHERE flag_ppm2_out=0 GROUP BY city").df()
sql_d = con.execute("SELECT city, district, median(price_per_m2) AS m FROM listings WHERE flag_ppm2_out=0 GROUP BY city, district HAVING count(*)>=%d" % MIN_DISTRICT_N).df()
v = con.table("listings").df()
v = v[v.flag_ppm2_out == 0]
pd_c = v.groupby("city").price_per_m2.median().reset_index(name="m")
pd_d = v.groupby(["city", "district"]).price_per_m2.agg(["median", "size"]).reset_index()
pd_d = pd_d[pd_d["size"] >= MIN_DISTRICT_N].rename(columns={"median": "m"})[["city", "district", "m"]]
cc = sql_c.merge(pd_c, on="city", suffixes=("_sql", "_pandas"))
cd = sql_d.merge(pd_d, on=["city", "district"], suffixes=("_sql", "_pandas"))
rows = []
for name, df in (("kota", cc), ("kecamatan", cd)):
    diff = (df.m_sql - df.m_pandas).abs()
    rows.append((name, len(df), int((diff < 1e-6).sum()), float(diff.max())))
out = pd.DataFrame(rows, columns=["level", "jumlah_dibandingkan", "sama", "selisih_maks"])
out["status"] = ["PASS" if a == b else "FAIL" for a, b in zip(out.jumlah_dibandingkan, out.sama)]
out.to_csv(RES_ANALYSIS / "04_crosscheck_sql_pandas.csv", index=False)
print(out.to_string(index=False))
con.close()
