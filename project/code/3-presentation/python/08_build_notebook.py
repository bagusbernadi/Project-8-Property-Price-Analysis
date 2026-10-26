"""Tahap 3: bangun notebook analisis (sel markdown dan kode), lalu jalankan sampai selesai. Output disimpan di results/3-presentation/."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from common import *  # noqa: E402
import nbformat as nbf
from nbclient import NotebookClient

md = lambda s: nbf.v4.new_markdown_cell(s.strip())
code = lambda s: nbf.v4.new_code_cell(s.strip())
cells = [
    md("""# Project 8: Harga Rumah Jabodetabek

Notebook ini membaca file hasil di `results/` dan menampilkan langkah analisis Q1 sampai Q14. Tidak ada angka yang diketik tangan. Sumber data: Kaggle, Versi 1, akses 23 Oktober 2026. Harga adalah harga listing."""),
    code("""import pandas as pd
import matplotlib.pyplot as plt
pd.set_option('display.width', 140)
R = 'results/'
log = pd.read_csv(R + '1-data-preparation/01_cleaning_log.csv')
log"""),
    md("## Harga per m2 per kota (Q1, Q2)"),
    code("""city = pd.read_csv(R + '2-analysis/02_city_summary.csv').sort_values('median_ppm2')
fig, ax = plt.subplots(figsize=(8, 4))
ax.barh(city.city, city.median_ppm2 / 1e6, color='#1A73E8')
ax.set_xlabel('Median harga per m2 (juta Rp)')
for y, v in enumerate(city.median_ppm2 / 1e6):
    ax.text(v + 0.2, y, f'{v:.1f}', va='center')
plt.tight_layout(); plt.show()
city[['city', 'n', 'median_ppm2']].sort_values('median_ppm2', ascending=False)"""),
    md("## Faktor harga per m2 (Q4)"),
    code("""pd.read_csv(R + '2-analysis/q4_factor_strength.csv')"""),
    md("## Uji lima hipotesis Design"),
    code("""pd.read_csv(R + '2-analysis/02_hypothesis_tests.csv')"""),
    md("## Kandidat listing jauh di bawah median kecamatan (Q7)"),
    code("""cand = pd.read_csv(R + '2-analysis/02_listing_outliers_vs_district.csv')
cand[cand.ratio < 0.5].sort_values('ratio').head(10)[['city', 'district', 'address', 'price_in_rp', 'building_size_m2', 'price_per_m2', 'district_median_ppm2', 'ratio']]"""),
    md("## Cek silang (Q14): SQL, pandas, dan spreadsheet"),
    code("""pd.concat({'sql_vs_pandas': pd.read_csv(R + '2-analysis/04_crosscheck_sql_pandas.csv'),
           'sql_vs_spreadsheet': pd.read_csv(R + '2-analysis/05_crosscheck_spreadsheet.csv')}, names=['cek'])"""),
    md("## Catatan\n\nBatas harga per m2, minimal 10 listing per kecamatan, dan ambang rasio adalah asumsi (lihat `docs/definitions.md`). Lisensi dataset belum dicek."),
]
nb = nbf.v4.new_notebook(cells=cells, metadata={"kernelspec": {"name": "python3", "display_name": "Python 3", "language": "python"}})
client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(ROOT)}})
client.execute()
out = RES_PRESENT / "analysis.ipynb"
nbf.write(nb, out)
errs = [c for c in nb.cells if c.cell_type == "code" and any(o.output_type == "error" for o in c.get("outputs", []))]
print("ok", out, "| sel kode dengan error:", len(errs))
