"""Tahap 3: infografik satu halaman (PNG dan PDF) dari file hasil. Semua angka dibaca dari CSV."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import *  # noqa: E402
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

city = pd.read_csv(RES_ANALYSIS / "02_city_summary.csv").sort_values("median_ppm2")
q4 = pd.read_csv(RES_ANALYSIS / "q4_factor_strength.csv")
cand = pd.read_csv(RES_ANALYSIS / "02_listing_outliers_vs_district.csv")
cand = cand[cand.ratio < 0.5].sort_values("ratio").head(3)
n_valid = int(city.n.sum())

fig = plt.figure(figsize=(11.69, 8.27))  # A4 landscape
fig.suptitle("Harga Rumah Jabodetabek: harga per m2, faktor, dan listing yang perlu dicek", fontsize=17, weight="bold", y=0.985)
fig.text(0.5, 0.935, f"Dataset publik Kaggle, {n_valid:,} listing valid. Harga listing, bukan harga transaksi.".replace(",", "."),
         ha="center", fontsize=11, color="#5F6368")

ax1 = fig.add_axes([0.13, 0.12, 0.38, 0.72])
ax1.barh(city.city, city.median_ppm2 / 1e6, color="#1A73E8")
for y, v in enumerate(city.median_ppm2 / 1e6):
    ax1.text(v + 0.2, y, f"{v:.1f} juta".replace(".", ","), va="center", fontsize=9)
ax1.set_title("Median harga per m2 per kota (juta Rp)", loc="left", fontsize=12)
ax1.set_xlim(0, city.median_ppm2.max() / 1e6 * 1.2)
for s in ("top", "right"):
    ax1.spines[s].set_visible(False)

ax2 = fig.add_axes([0.58, 0.52, 0.36, 0.32])
f = q4.assign(nilai_abs=q4.nilai.abs()).head(8).iloc[::-1]
ax2.barh(f.faktor, f.nilai, color=["#34A853" if v > 0 else "#EA4335" for v in f.nilai])
ax2.set_title("Kekuatan hubungan dengan harga per m2", loc="left", fontsize=12)
ax2.set_xlabel("Spearman rho (faktor numerik)", fontsize=8)
ax2.tick_params(labelsize=8)
for s in ("top", "right"):
    ax2.spines[s].set_visible(False)

ax3 = fig.add_axes([0.58, 0.12, 0.36, 0.30])
ax3.axis("off")
ax3.set_title("Listing jauh di bawah median kecamatan", loc="left", fontsize=12)
rows = [[r.district, r.city.strip(), f"Rp {r.price_per_m2/1e6:.1f} juta/m2".replace(".", ","), f"{r.ratio:.2f}x".replace(".", ",")] for r in cand.itertuples()]
t = ax3.table(cellText=rows, colLabels=["Kecamatan", "Kota", "Harga per m2", "Rasio"], loc="upper left", cellLoc="left",
              colWidths=[0.4, 0.2, 0.28, 0.12])
t.auto_set_font_size(False)
t.set_fontsize(9)
t.scale(1, 1.6)
fig.text(0.06, 0.06, "Aturan: rasio = harga per m2 listing / median kecamatan (minimal 10 listing). Batas wajar Rp 1 juta s.d. 100 juta per m2 adalah asumsi.",
         fontsize=8.5, color="#5F6368")
fig.text(0.06, 0.035, "Daftar lengkap ada di results/2-analysis. Sumber: Kaggle, Versi 1, akses 23 Oktober 2026.",
         fontsize=8.5, color="#5F6368")
out = RES_PRESENT
fig.savefig(out / "infographic.png", dpi=150)
fig.savefig(out / "infographic.pdf")
print("ok", out / "infographic.png")
