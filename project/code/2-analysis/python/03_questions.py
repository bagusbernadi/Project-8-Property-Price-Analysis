"""Tahap 2 lanjutan: jawaban Q1-Q13 dari design. Hasil CSV di results/2-analysis/q*.csv."""
import re
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import *  # noqa: E402
import duckdb
import numpy as np
import pandas as pd

con = duckdb.connect(str(DB_PATH), read_only=True)
L = con.table("listings").df()
v = L[L.flag_ppm2_out == 0].copy()
out = RES_ANALYSIS
ASSUME_KM = 50  # ASUMSI batas jarak koordinat dari median kota (Q13)

# Q1: sebaran harga per m2 per kota (median dan IQR)
q1 = v.groupby("city").price_per_m2.describe(percentiles=[.25, .5, .75])[["count", "25%", "50%", "75%"]].reset_index()
q1.round(0).to_csv(out / "q1_city_iqr.csv", index=False)

# Q2: kecamatan termahal dan termurah (n >= MIN)
d = pd.read_csv(out / "02_district_summary.csv")
d.sort_values("median_ppm2", ascending=False).to_csv(out / "q2_district_rank.csv", index=False)

# Q3: harga per m2 bangunan vs tanah (sebaran log)
vt = v[v.land_size_m2 > 0].copy()
vt["ppm2_land"] = vt.price_in_rp / vt.land_size_m2
q3 = pd.DataFrame({
    "dasar": ["per m2 bangunan", "per m2 tanah"],
    "n": [len(vt), len(vt)],
    "median": [vt.price_per_m2.median(), vt.ppm2_land.median()],
    "sd_log": [np.log(vt.price_per_m2).std(), np.log(vt.ppm2_land).std()],
})
q3.round(4).to_csv(out / "q3_basis_compare.csv", index=False)

# Q4: faktor vs log harga per m2 (Spearman untuk numerik, eta-squared untuk kategori)
num = ["land_size_m2", "building_size_m2", "bedrooms", "bathrooms", "carports", "floors", "building_age", "garages"]
rows = []
lv = np.log(v.price_per_m2)
for c in num:
    s = v[[c]].assign(y=lv).dropna()
    rows.append((c, "Spearman rho", round(s[c].corr(s.y, method="spearman"), 3), len(s)))
def eta(cat):
    s = v[[cat]].assign(y=lv).dropna()
    g = s.groupby(cat).y
    ssb = ((g.transform("mean") - s.y.mean()) ** 2).sum()
    return round(ssb / ((s.y - s.y.mean()) ** 2).sum(), 3), len(s)
for c in ["city", "certificate", "property_condition", "furnishing"]:
    e, n = eta(c)
    rows.append((c, "eta-squared", e, n))
pd.DataFrame(rows, columns=["faktor", "ukuran", "nilai", "n"]).to_csv(out / "q4_factor_strength.csv", index=False)

# Q5: selisih SHM vs HGB dalam kecamatan yang sama (n >= 5 masing-masing)
c = v[v.certificate.str.startswith(("shm", "hgb"))].copy()
c["c"] = c.certificate.str[:3]
pv = c.groupby(["city", "district", "c"]).price_per_m2.agg(["median", "count"]).unstack("c").dropna()
pv = pv[(pv[("count", "shm")] >= 5) & (pv[("count", "hgb")] >= 5)]
q5 = pd.DataFrame({"city": pv.index.get_level_values(0), "district": pv.index.get_level_values(1),
                   "median_shm": pv[("median", "shm")].values, "median_hgb": pv[("median", "hgb")].values,
                   "n_shm": pv[("count", "shm")].values, "n_hgb": pv[("count", "hgb")].values})
q5["selisih_pct"] = (q5.median_shm / q5.median_hgb - 1) * 100
q5.round(2).to_csv(out / "q5_cert_pairs.csv", index=False)

# Q6: luas bangunan vs harga per m2
bins = [0, 50, 100, 200, 400, 1e9]
labels = ["<50", "50-99", "100-199", "200-399", ">=400"]
v["bin"] = pd.cut(v.building_size_m2, bins=bins, labels=labels, right=False)
q6 = v.groupby("bin", observed=True).price_per_m2.agg(["count", "median"]).reset_index()
q6.round(0).to_csv(out / "q6_size_bins.csv", index=False)

# Q7: listing undervalued per kota (rasio < 0.5)
r = pd.read_csv(out / "02_listing_outliers_vs_district.csv")
u = r[r.ratio < 0.5]
q7 = u.groupby("city").size().reset_index(name="jumlah_undervalued").merge(
    v.groupby("city").size().reset_index(name="listing_valid"), on="city")
q7["persen"] = q7.jumlah_undervalued / q7.listing_valid * 100
q7.sort_values("persen", ascending=False).round(2).to_csv(out / "q7_undervalued_by_city.csv", index=False)

# Q8: estimasi selisih: harga listing - median harga per m2 kecamatan x luas bangunan (label estimated)
r["estimasi_selisih"] = r.price_in_rp - r.district_median_ppm2 * r.building_size_m2
q8 = pd.DataFrame({
    "kelompok": ["undervalued (rasio < 0.5)", "overvalued (rasio > 2)"],
    "jumlah": [int((r.ratio < 0.5).sum()), int((r.ratio > 2).sum())],
    "total_selisih_rp_estimated": [r.loc[r.ratio < 0.5, "estimasi_selisih"].sum(), r.loc[r.ratio > 2, "estimasi_selisih"].sum()],
    "median_selisih_rp_estimated": [r.loc[r.ratio < 0.5, "estimasi_selisih"].median(), r.loc[r.ratio > 2, "estimasi_selisih"].median()],
})
q8.round(0).to_csv(out / "q8_impact_estimated.csv", index=False)

# Q9: anggaran Rp 1 miliar, luas tanah yang didapat per kecamatan (median harga per m2 tanah)
vt["district_key"] = vt.city + " | " + vt.district
bud = vt.groupby(["city", "district"]).agg(n=("ppm2_land", "size"), med_land=("ppm2_land", "median")).reset_index()
bud = bud[bud.n >= MIN_DISTRICT_N].copy()
bud["luas_tanah_m2_1miliar"] = 1_000_000_000 / bud.med_land
bud.sort_values("luas_tanah_m2_1miliar", ascending=False).round(1).to_csv(out / "q9_budget_land.csv", index=False)

# Q10: segmen harga berdasarkan kuartil median kecamatan
d = d.copy()
q = d.median_ppm2.quantile([.25, .75]).values
d["segmen"] = np.select([d.median_ppm2 >= q[1], d.median_ppm2 <= q[0]], ["mahal", "terjangkau"], default="menengah")
seg_n = v.merge(d[["city", "district", "segmen"]], on=["city", "district"]).groupby("segmen").size()
q10 = d.groupby("segmen").agg(kecamatan=("district", "size"), median_min=("median_ppm2", "min"), median_max=("median_ppm2", "max")).reset_index()
q10["listing"] = q10.segmen.map(seg_n)
q10.round(0).to_csv(out / "q10_segments.csv", index=False)
d.round(0).to_csv(out / "q10_district_segment.csv", index=False)

# Q11: fasilitas vs harga per m2 (median ada vs tidak ada)
v["listrik_va"] = v.electricity.str.extract(r"(\d+)").astype(float)
q11 = pd.DataFrame({
    "fasilitas": ["carport >= 1", "carport = 0", "daya listrik >= 2200 VA", "daya listrik < 2200 VA",
                  "furnished", "unfurnished"],
    "n": [int((v.carports >= 1).sum()), int((v.carports == 0).sum()), int((v.listrik_va >= 2200).sum()),
          int((v.listrik_va < 2200).sum()), int((v.furnishing == "furnished").sum()), int((v.furnishing == "unfurnished").sum())],
    "median_ppm2": [v[v.carports >= 1].price_per_m2.median(), v[v.carports == 0].price_per_m2.median(),
                    v[v.listrik_va >= 2200].price_per_m2.median(), v[v.listrik_va < 2200].price_per_m2.median(),
                    v[v.furnishing == "furnished"].price_per_m2.median(), v[v.furnishing == "unfurnished"].price_per_m2.median()],
})
q11.round(0).to_csv(out / "q11_facilities.csv", index=False)

# Q13: konsistensi koordinat dengan kota (jarak dari median kota) dan nama kecamatan di alamat
L2 = L.dropna(subset=["lat", "long"]).copy()
med = L2.groupby("city")[["lat", "long"]].median()
L2 = L2.join(med, on="city", rsuffix="_med")
L2["km"] = np.sqrt(((L2.lat - L2.lat_med) * 111) ** 2 + ((L2.long - L2.long_med) * 111 * np.cos(np.radians(L2.lat_med))) ** 2)
coord_out = L2[L2.km > ASSUME_KM]
addr_miss = L[[not str(a).lower().find(str(dname).lower()) >= 0 for a, dname in zip(L.address, L.district)]]
q13 = pd.DataFrame({
    "cek": ["koordinat kosong", f"jarak > {ASSUME_KM} km dari median kota", "nama kecamatan tidak ada di alamat", "total listing"],
    "jumlah": [int(L.lat.isna().sum() + L.long.isna().sum()), len(coord_out), len(addr_miss), len(L)],
})
q13.to_csv(out / "q13_geo_consistency.csv", index=False)
coord_out[["ads_id", "city", "district", "address", "lat", "long", "km"]].round(2).to_csv(out / "q13_coord_outliers.csv", index=False)
con.close()
print(q1.round(0).to_string(index=False)); print(q7.round(1).to_string(index=False)); print(q13.to_string(index=False))

# Q12: median per kota sebelum (semua baris dengan luas) vs sesudah pembersihan
raw = pd.read_csv(RAW_CSV)
raw["city"] = raw.city.str.strip()
raw = raw.dropna(subset=["building_size_m2"])
before = (raw.price_in_rp / raw.building_size_m2).groupby(raw.city).median()
con2 = duckdb.connect(str(DB_PATH), read_only=True)
after = con2.execute("SELECT city, median(price_per_m2) AS m FROM listings WHERE flag_ppm2_out = 0 GROUP BY city").df().set_index("city").m
con2.close()
q12 = pd.DataFrame({"city": before.index, "median_sebelum": before.values, "median_sesudah": after.reindex(before.index).values})
q12["selisih_pct"] = (q12.median_sesudah / q12.median_sebelum - 1) * 100
q12.round(2).to_csv(out / "q12_before_after.csv", index=False)
