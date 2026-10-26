"""Tahap 2: ringkasan per area, uji lima hipotesis Design, kandidat listing di luar kewajaran."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import *  # noqa: E402
import duckdb
import numpy as np
import pandas as pd

con = duckdb.connect(str(DB_PATH))
con.execute((SQL_ANALYSIS / "02_analysis.sql").read_text().format(MIN_N=MIN_DISTRICT_N))

city = con.table("city_summary").df()
district = con.table("district_summary").df()
ratio = con.table("listing_vs_district").df()
city.round(2).to_csv(RES_ANALYSIS / "02_city_summary.csv", index=False)
district.round(2).to_csv(RES_ANALYSIS / "02_district_summary.csv", index=False)

# Kandidat: rasio < 0.5 atau > 2 terhadap median kecamatan (ambang = ASUMSI, lihat docs)
cand = ratio[(ratio.ratio < 0.5) | (ratio.ratio > 2)].sort_values("ratio")
cand.round(3).to_csv(RES_ANALYSIS / "02_listing_outliers_vs_district.csv", index=False)

valid = con.table("valid").df()
valid["log_ppm2"] = np.log(valid.price_per_m2)

# H1 kota termahal dan termurah
top2 = city.head(2).city.tolist(); bottom2 = city.tail(2).city.tolist()
# H2 lokasi vs jumlah kamar: eta-squared pada log harga per m2
def eta2(g):
    grand = valid.log_ppm2.mean()
    ss_between = (valid.assign(m=valid.groupby(g).log_ppm2.transform("mean")).pipe(lambda d: ((d.m - grand) ** 2).sum()))
    return ss_between / ((valid.log_ppm2 - grand) ** 2).sum()
bed = valid[valid.bedrooms.notna()].copy()
bed["bed_grp"] = bed.bedrooms.clip(upper=6).astype(int).astype(str)
loc_eta = eta2("city")
bed_eta_df = bed.assign(g=bed.bed_grp)
gm = bed_eta_df.log_ppm2.mean()
bed_eta = (bed_eta_df.groupby("g").log_ppm2.transform("mean").sub(gm) ** 2).sum() / ((bed_eta_df.log_ppm2 - gm) ** 2).sum()
# H3 SHM vs HGB pada kecamatan yang punya keduanya (n >= 5 masing-masing)
cert = valid[valid.certificate.str.startswith(("shm", "hgb"))].copy()
cert["c"] = cert.certificate.str[:3]
pv = cert.groupby(["city", "district", "c"]).price_per_m2.agg(["median", "count"]).unstack("c")
pv = pv.dropna()
pv = pv[(pv[("count", "shm")] >= 5) & (pv[("count", "hgb")] >= 5)]
shm_gt = int((pv[("median", "shm")] > pv[("median", "hgb")]).sum())
# H4 luas bangunan vs harga per m2 (Spearman)
rho = valid[["building_size_m2", "price_per_m2"]].corr(method="spearman").iloc[0, 1]
# H5 proporsi listing dengan input yang diragukan
flag_share = con.execute("SELECT avg(flag_ppm2_out) FROM listings").fetchone()[0]
ext_share = len(cand) / len(ratio)

rows = [
    ("H1", "Kota termahal per m2", f"{top2[0]}, {top2[1]} (median tertinggi)", f"{bottom2[0]}, {bottom2[1]} (median terendah)"),
    ("H2", "Eta-squared lokasi (kota)", f"{loc_eta:.3f}", f"Eta-squared jumlah kamar: {bed_eta:.3f}"),
    ("H3", "Kecamatan dengan SHM > HGB (n>=5 kedua jenis)", f"{shm_gt} dari {len(pv)} kecamatan", "-"),
    ("H4", "Spearman luas bangunan vs price per m2", f"{rho:.3f}", "-"),
    ("H5", "Proporsi listing flag (input diragukan)", f"{flag_share:.4f}", f"Rasio ekstrem vs median kecamatan: {ext_share:.3f}"),
]
pd.DataFrame(rows, columns=["hipotesis", "ukuran", "nilai_1", "nilai_2"]).to_csv(RES_ANALYSIS / "02_hypothesis_tests.csv", index=False)

# Sensitivitas batas harga per m2 (asumsi)
sens = []
for lo, hi in [(500_000, 200_000_000), (PPM2_MIN, PPM2_MAX), (2_000_000, 50_000_000)]:
    f = con.execute(f"SELECT count(*) FILTER (WHERE price_per_m2 BETWEEN {lo} AND {hi}) AS valid_n FROM listings").fetchone()[0]
    sens.append((lo, hi, f))
pd.DataFrame(sens, columns=["batas_bawah", "batas_atas", "listing_valid"]).to_csv(RES_ANALYSIS / "02_ppm2_bounds_sensitivity.csv", index=False)

print(city.round(0).to_string(index=False))
print(pd.DataFrame(rows, columns=["h", "ukuran", "a", "b"]).to_string(index=False))
print(f"kandidat rasio ekstrem: {len(cand)}")
con.close()
