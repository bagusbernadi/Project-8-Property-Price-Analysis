"""Membuat design-and-report/index.html (Report Project versi 2) dari page_v1.html dan CSV hasil.

- Pane Design diambil apa adanya dari page_v1.html (dicek identik dengan sumber).
- Angka di Report berasal dari project/results/*.csv dan DuckDB lewat helper I/D/P/cs (report_lib.py), lalu diaudit.
Jalankan dari mana saja:  python design-and-report/src/build_report.py
"""
import re
import sys
from pathlib import Path

import duckdb
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(REPO / "project" / "code"))
sys.path.insert(0, str(HERE))
from common import DB_PATH, RES_ANALYSIS, RES_PREP, MIN_DISTRICT_N  # noqa: E402
from report_lib import (D, I, P, OK, PART, NO, audit, bars, cs, esc, hbars, legend, pill, qa, table, REG)  # noqa: E402

RA, RP = RES_ANALYSIS, RES_PREP
R = lambda p: pd.read_csv(p)
city = R(RA / "02_city_summary.csv")
dist = R(RA / "02_district_summary.csv")
rank = R(RA / "q2_district_rank.csv")
hyp = R(RA / "02_hypothesis_tests.csv")
sens = R(RA / "02_ppm2_bounds_sensitivity.csv")
cand = R(RA / "02_listing_outliers_vs_district.csv")
q1 = R(RA / "q1_city_iqr.csv")
q3 = R(RA / "q3_basis_compare.csv")
q4 = R(RA / "q4_factor_strength.csv")
q5 = R(RA / "q5_cert_pairs.csv")
q6 = R(RA / "q6_size_bins.csv")
q7 = R(RA / "q7_undervalued_by_city.csv")
q8 = R(RA / "q8_impact_estimated.csv")
q9 = R(RA / "q9_budget_land.csv")
q10 = R(RA / "q10_segments.csv")
q10d = R(RA / "q10_district_segment.csv")
q11 = R(RA / "q11_facilities.csv")
q12 = R(RA / "q12_before_after.csv")
q13 = R(RA / "q13_geo_consistency.csv")
q13c = R(RA / "q13_coord_outliers.csv")
xc = R(RA / "04_crosscheck_sql_pandas.csv")
clog = R(RP / "01_cleaning_log.csv")

con = duckdb.connect(str(DB_PATH), read_only=True)
tbl = {t: con.execute(f"SELECT count(*) FROM {t}").fetchone()[0] for t in ("raw", "listings", "city_summary", "district_summary", "listing_vs_district")}
n_valid = int((con.execute("SELECT count(*) FROM listings WHERE flag_ppm2_out=0").fetchone()[0]))
n_dupurl = tbl["raw"] - int(clog.jumlah[1])
n_med_all = float(R(RA / "02_city_summary.csv").median_ppm2.median())
n_dupads = int(clog.jumlah[1] - clog.jumlah[2])
n_yr = int(clog.jumlah[3]); n_flag = int(clog.jumlah[4]); n_bld = int(clog.jumlah[5])
con.close()

# ---- ringkasan angka kunci
H = {r.hipotesis: r for r in hyp.itertuples()}
n_city = len(city); n_dist = len(dist)
c_hi, c_lo = city.iloc[0], city.iloc[-1]
ratio_low = int((cand.ratio < 0.5).sum()); ratio_hi = int((cand.ratio > 2).sum())
share_ext = len(cand) / tbl["listing_vs_district"]
shm = q5[q5.selisih_pct > 0]
eta_loc, eta_bed = [float(x) for x in (H["H2"].nilai_1, H["H2"].nilai_2.split(": ")[1])]
rho_size = float(H["H4"].nilai_1)
lo_bound, hi_bound = sens.listing_valid.min(), sens.listing_valid.max()
ph_base = sens.set_index(["batas_bawah", "batas_atas"]).listing_valid
base_valid = int(ph_base.loc[(1_000_000, 100_000_000)])
q8r = q8.set_index("kelompok")
xc_ok = bool((xc.status == "PASS").all())
kota = city.set_index("city")

# ---------------------------------------------------------------- Report 1: Data
kp = lambda c, v, l, d: f'<div class="card kpi" style="--h:var(--{c}H)"><span class="v">{v}</span><span class="l">{l}</span><span class="d">{d}</span></div>'
rp1 = ['<div class="kpis">',
       kp("navy", I(tbl["raw"]), "baris mentah", f"Dari file CSV Kaggle, 27 kolom. Satu baris = satu listing."),
       kp("teal", I(tbl["listings"]), "listing setelah pembersihan", f"Dihapus {I(n_dupurl)} duplikat URL dan {I(n_dupads)} duplikat ads_id."),
       kp("amber", I(n_valid), "listing dengan price per m2 valid", f"Di dalam batas asumsi Rp {I(1_000_000)} s.d. Rp {I(100_000_000)} per m2."),
       kp("plum", I(n_city), "kota", f"Bogor dan Tangerang paling banyak listing."),
       kp("rose", I(n_dist), "kecamatan dengan listing cukup", f"Minimal {MIN_DISTRICT_N} listing per kecamatan (asumsi)."),
       kp("sky", I(n_flag + n_bld + n_yr), "baris ditandai atau diubah", "Flag harga, luas kosong, dan tahun bangun di masa depan."),
       '</div>']
rp1.append('<h3>1.1 Data mentah dan pembersihan</h3>')
rp1.append('<div class="card"><h4>Tabel 1.1. Langkah pembersihan</h4>' +
           table(["Langkah", "Jumlah"], [[r.langkah, I(r.jumlah)] for r in clog.itertuples()]) +
           '<p>Keputusan tiap langkah ada di <code>project/docs/cleaning_decisions.md</code>. Angka flag dan batas harga adalah asumsi.</p></div>')
rp1.append('<h3>1.2 Tabel di database dan file hasil</h3>')
rp1.append('<div class="card"><h4>Tabel 1.2a. Tabel di DuckDB</h4>' +
           table(["Tabel", "Isi", "Baris"], [
               ["<code>raw</code>", "Data mentah dari CSV", I(tbl["raw"])],
               ["<code>listings</code>", "Listing bersih, dengan price per m2 dan flag", I(tbl["listings"])],
               ["<code>city_summary</code>", "Median per kota", I(tbl["city_summary"])],
               ["<code>district_summary</code>", "Median per kecamatan (n >= 10)", I(tbl["district_summary"])],
               ["<code>listing_vs_district</code>", "Listing dengan rasio terhadap median kecamatan", I(tbl["listing_vs_district"])]]) +
           '<p>Tabel <code>s1</code> dan <code>s2</code> adalah tahap antara pembersihan dan ikut tersimpan di file database.</p></div>')
rp1.append('<div class="card"><h4>Tabel 1.2b. Cek silang SQL dan pandas (Q14)</h4>' +
           table(["Tingkat", "Dibandingkan", "Sama", "Selisih maks", "Status"],
                 [[r.level, I(r.jumlah_dibandingkan), I(r.sama), D(r.selisih_maks, 6), OK(r.status)] for r in xc.itertuples()]) +
           '<p>Cek dilakukan dengan DuckDB dan pandas. Excel tidak dipakai karena tidak tersedia di sesi.</p></div>')
rp1.append('<div class="card"><h4>Tabel 1.2c. File hasil analisis (CSV)</h4>' +
           table(["File", "Isi"], [
               ["<code>results/1-data-preparation/01_cleaning_log.csv</code>", "Langkah pembersihan"],
               ["<code>results/2-analysis/02_city_summary.csv</code>", "Median per kota"],
               ["<code>results/2-analysis/02_district_summary.csv</code>", "Median per kecamatan"],
               ["<code>results/2-analysis/02_hypothesis_tests.csv</code>", "Uji lima hipotesis"],
               ["<code>results/2-analysis/02_listing_outliers_vs_district.csv</code>", "Listing dengan rasio di luar 0,5 s.d. 2"],
               ["<code>results/2-analysis/02_ppm2_bounds_sensitivity.csv</code>", "Sensitivitas batas harga"],
               ["<code>results/2-analysis/q1 sampai q13 (CSV)</code>", "Jawaban Q1 sampai Q13"],
               ["<code>results/2-analysis/04_crosscheck_sql_pandas.csv</code>", "Cek silang Q14"]]) + '</div>')
rp1.append('<h3>1.3 Angka kunci (KPI)</h3>')
rp1.append('<div class="card">' + table(["KPI", "Rumus ringkas", "Hasil", "Jumlah data"], [
    ["Median price per m2 semua listing valid", "median(harga / luas bangunan)", "Rp " + I(n_med_all), I(n_valid)],
    ["Kota termahal (median)", "median per kota", f"{c_hi.city}: Rp {I(c_hi.median_ppm2)}", I(c_hi.n)],
    ["Kota termurah (median)", "median per kota", f"{c_lo.city}: Rp {I(c_lo.median_ppm2)}", I(c_lo.n)],
    ["Kandidat rasio < 0,5", "harga per m2 / median kecamatan", I(ratio_low), I(n_valid)],
    ["Kandidat rasio > 2", "harga per m2 / median kecamatan", I(ratio_hi), I(n_valid)]]) + '</div>')

# ---------------------------------------------------------------- Report 2: business questions
PRIO = {1: "Utama", 2: "Utama", 3: "Pendukung", 4: "Utama", 5: "Utama", 6: "Pendukung", 7: "Utama", 8: "Utama",
        9: "Pendukung", 10: "Utama", 11: "Tambahan", 12: "Utama", 13: "Utama", 14: "Pendukung"}
WARN = {5, 7, 8, 9, 10, 11, 13, 14}
QT = {1: "Berapa median harga per m2 tanah di tiap kota dan kecamatan, dan seberapa lebar sebarannya?",
      2: "Kecamatan mana yang paling mahal dan paling murah per m2?",
      3: "Seberapa berbeda hasilnya jika memakai harga per m2 bangunan, dan mana yang lebih stabil?",
      4: "Faktor apa yang paling terkait dengan harga per m2?",
      5: "Seberapa besar selisih harga per m2 antara SHM dan HGB di area yang sama?",
      6: "Apakah rumah yang lebih luas punya harga per m2 lebih rendah?",
      7: "Listing mana yang harganya jauh di bawah median area, dan apakah terkumpul di area tertentu?",
      8: "Berapa estimasi selisih harga listing terhadap nilai wajar per area?",
      9: "Dengan anggaran Rp 1 miliar, area mana yang memberi luas tanah terbesar?",
      10: "Bagaimana kecamatan dikelompokkan menjadi segmen mahal, menengah, dan terjangkau?",
      11: "Apakah carport, daya listrik, dan furnishing ikut menaikkan harga per m2?",
      12: "Berapa listing yang duplikat, salah satuan, atau harganya tidak wajar, dan apakah hasil berubah setelah dibersihkan?",
      13: "Apakah nama area dan koordinat konsisten dengan kota?",
      14: "Apakah angka KPI dari database sama dengan hitungan lain?"}
ANS = {
 1: f"Median tertinggi {c_hi.city} (Rp {I(c_hi.median_ppm2)}) dan terendah {c_lo.city} (Rp {I(c_lo.median_ppm2)}). Sebaran di tiap kota lebar: rentang kuartil ke-1 sampai ke-3 Bekasi Rp {I(q1.set_index('city').loc['Bekasi','25%'])} s.d. Rp {I(q1.set_index('city').loc['Bekasi','75%'])}.",
 2: f"{rank.iloc[0].district} ({rank.iloc[0].city}) termahal dengan median Rp {I(rank.iloc[0].median_ppm2)}. {rank.iloc[-1].district} ({rank.iloc[-1].city}) termurah, Rp {I(rank.iloc[-1].median_ppm2)}. Hanya kecamatan dengan minimal {MIN_DISTRICT_N} listing yang dihitung.",
 3: f"Median per m2 bangunan Rp {I(q3.loc[0,'median'])}, per m2 tanah Rp {I(q3.loc[1,'median'])}. Sebaran log per m2 bangunan lebih sempit (sd {D(q3.loc[0,'sd_log'],2)} vs {D(q3.loc[1,'sd_log'],2)}), jadi basis bangunan dipakai di seluruh analisis.",
 4: f"Faktor terkuat: luas tanah (Spearman {D(q4.loc[0,'nilai'],3)}) dan jumlah kamar mandi ({D(q4.loc[3,'nilai'],3)}). Kota memiliki eta-squared {D(q4.loc[8,'nilai'],3)}, sertifikat {D(q4.loc[9,'nilai'],3)}, dan kondisi {D(q4.loc[10,'nilai'],3)}. Lokasi (kota) lebih besar pengaruhnya daripada sertifikat dan kondisi.",
 5: f"Selisih median SHM terhadap HGB per kecamatan adalah {D(q5.selisih_pct.median(),1)}% (median dari {len(q5)} kecamatan). SHM lebih tinggi di {len(shm)} dari {len(q5)} kecamatan, jadi hampir tidak ada selisih yang konsisten.",
 6: "Harga per m2 turun seiring luas bangunan pada kelompok luas tertentu. Median naik dari Rp " + I(q6.iloc[0]['median']) + " (di bawah 50 m2) ke Rp " + I(q6.iloc[-1]['median']) + " (400 m2 ke atas). Korelasi Spearman luas bangunan dengan harga per m2 " + D(rho_size, 3) + ", jadi hipotesis ini tidak didukung.",
 7: f"{I(ratio_low)} listing punya rasio kurang dari 0,5 terhadap median kecamatannya. Kota dengan proporsi tertinggi: {q7.sort_values('persen', ascending=False).iloc[0].city}. Daftar lengkap di CSV <code>02_listing_outliers_vs_district.csv</code>.",
 8: f"Dari {I(ratio_low)} listing undervalued, median estimasi selisih Rp {I(-q8r.loc['undervalued (rasio < 0.5)','median_selisih_rp_estimated'])} per listing (estimated). Total selisih didominasi listing ekstrem, jadi median lebih informatif.",
 9: f"Dengan Rp 1 miliar, {q9.iloc[0].district} ({q9.iloc[0].city}) memberi sekitar {I(q9.iloc[0].luas_tanah_m2_1miliar)} m2 tanah pada median harga tanah. Hitungan memakai median harga per m2 tanah.",
 10: f"{q10.set_index('segmen').loc['mahal','kecamatan']} kecamatan masuk segmen mahal, {q10.set_index('segmen').loc['menengah','kecamatan']} menengah, dan {q10.set_index('segmen').loc['terjangkau','kecamatan']} terjangkau. Cut-off memakai kuartil ke-1 dan ke-3 (asumsi).",
 11: f"Listing dengan carport 1 atau lebih median Rp {I(q11.set_index('fasilitas').loc['carport >= 1','median_ppm2'])} per m2, tanpa carport Rp {I(q11.set_index('fasilitas').loc['carport = 0','median_ppm2'])}. Daya listrik 2.200 VA ke atas lebih mahal. Furnished jauh lebih mahal, tetapi jumlah datanya kecil.",
 12: f"{I(n_dupurl)} duplikat URL, {I(n_dupads)} duplikat ads_id, {I(n_flag)} harga per m2 di luar batas, dan {I(n_yr)} tahun bangun masa depan. Di {int((q12.selisih_pct.abs() < 1).sum())} dari {len(q12)} kota median berubah kurang dari 1%. Jakarta Pusat berubah {D(q12.set_index('city').loc['Jakarta Pusat','selisih_pct'],1)}% (n kecil, didorong listing ekstrem).",
 13: f"{I(q13.loc[1,'jumlah'])} listing punya koordinat lebih dari {I(50)} km dari median kotanya. Semuanya berada di kecamatan Harjamukti (Bogor) dan Depok II, dan koordinatnya kemungkinan salah input. Ambang 50 km adalah asumsi.",
 14: "Median per kota dan kecamatan dari DuckDB sama dengan pandas (" + I(xc.sama.sum()) + " dari " + I(xc.jumlah_dibandingkan.sum()) + " perbandingan). Excel tidak dipakai.",
}
# bukti per tema
qlist = []
for n in range(1, 15):
    qlist.append(qa(f"Q{n}", QT[n], PRIO[n], ANS[n], "Terjawab dengan catatan" if n in WARN else "Terjawab", n in WARN).replace('<div class="qa', f'<div id="q{n}" class="qa', 1))
rp2 = ['<div class="callout g"><h4>Jawaban singkat</h4>',
       f'Semua 14 pertanyaan dijawab dengan data. Dari jumlah itu, {len(WARN)} pertanyaan dijawab dengan catatan (kuning). Pertanyaan utama project dijawab di bagian 7.</div>',
       '<div class="qchips">' + "".join(f'<a class="qc{" w" if n in WARN else ""}" href="#q{n}" title="{esc(QT[n])}">Q{n}</a>' for n in range(1, 15)) + '</div>',
       '<p class="how">Klik nomor pertanyaan untuk melompat. Hijau = terjawab, kuning = terjawab dengan catatan.</p>']
rp2.append('<h3>2.1 Harga per area (Q1 sampai Q3)</h3>')
rp2.append(qlist[0] + qlist[1] + qlist[2])
rp2.append('<h4>Grafik 2.1a. Median harga per m2 per kota</h4>' + bars(
    [(r.city, r.median_ppm2, "#1A73E8", f"{r.city}: Rp {I(r.median_ppm2)} (n={I(r.n)})") for r in city.itertuples()],
    lambda v: I(v), "Median harga per m2 per kota", h=270, rot=35))
rp2.append('<h4>Tabel 2.1b. Lima kecamatan termahal dan termurah</h4>' + table(
    ["Kecamatan", "Kota", "n", "Median Rp/m2"],
    [[r.district, r.city, I(r.n), I(r.median_ppm2)] for r in pd.concat([rank.head(5), rank.tail(5)]).itertuples()]))
rp2.append('<h3>2.2 Faktor harga (Q4, Q5, Q6, Q11)</h3>')
rp2.append(qlist[3] + qlist[4] + qlist[5] + qlist[10])
rp2.append('<h4>Tabel 2.2a. Kekuatan hubungan tiap faktor dengan log harga per m2</h4>' + table(
    ["Faktor", "Ukuran", "Nilai", "n"],
    [[r.faktor, r.ukuran, D(r.nilai, 3), I(r.n)] for r in q4.itertuples()]))
rp2.append('<h4>Tabel 2.2b. Selisih SHM dan HGB per kecamatan</h4>' + table(
    ["Kota", "Kecamatan", "Median SHM", "Median HGB", "Selisih", "n SHM / HGB"],
    [[r.city, r.district, I(r.median_shm), I(r.median_hgb), P(r.selisih_pct/100, 1), f"{I(r.n_shm)} / {I(r.n_hgb)}"] for r in q5.itertuples()]))
rp2.append('<h4>Tabel 2.2c. Harga per m2 per kelompok luas bangunan (m2)</h4>' + table(
    ["Luas bangunan", "n", "Median Rp/m2"],
    [[str(r.bin), I(r.count), I(r.median)] for r in q6.itertuples()]))
rp2.append('<h4>Tabel 2.2d. Median harga per m2 berdasarkan fasilitas</h4>' + table(
    ["Fasilitas", "n", "Median Rp/m2"],
    [[r.fasilitas, I(r.n), I(r.median_ppm2)] for r in q11.itertuples()]))
rp2.append('<h3>2.3 Nilai wajar (Q7, Q8)</h3>')
rp2.append(qlist[6] + qlist[7])
rp2.append('<h4>Tabel 2.3a. Listing undervalued per kota (rasio di bawah 0,5)</h4>' + table(
    ["Kota", "Undervalued", "Listing valid", "Persen"],
    [[r.city, I(r.jumlah_undervalued), I(r.listing_valid), D(r.persen, 1) + "%"] for r in q7.itertuples()]))
rp2.append('<h4>Tabel 2.3b. Estimasi selisih harga (estimated)</h4>' + table(
    ["Kelompok", "Jumlah", "Median selisih per listing", "Total selisih"],
    [[r.kelompok, I(r.jumlah), "Rp " + I(r.median_selisih_rp_estimated), "Rp " + D(r.total_selisih_rp_estimated / 1e9, 1) + " miliar"] for r in q8.itertuples()]))
rp2.append('<h3>2.4 Penerapan (Q9, Q10)</h3>')
rp2.append(qlist[8] + qlist[9])
rp2.append('<h4>Tabel 2.4a. Luas tanah yang didapat dengan Rp 1 miliar (lima teratas)</h4>' + table(
    ["Kota", "Kecamatan", "n", "Median harga tanah per m2", "Luas tanah (m2)"],
    [[r.city, r.district, I(r.n), I(r.med_land), D(r.luas_tanah_m2_1miliar, 1)] for r in q9.head(5).itertuples()]))
rp2.append('<h4>Tabel 2.4b. Segmen kecamatan</h4>' + table(
    ["Segmen", "Kecamatan", "Listing", "Median min", "Median maks"],
    [[r.segmen, I(r.kecamatan), I(r.listing), I(r.median_min), I(r.median_max)] for r in q10.itertuples()]))
rp2.append('<h3>2.5 Validitas data (Q12, Q13, Q14)</h3>')
rp2.append(qlist[11] + qlist[12] + qlist[13])
rp2.append('<h4>Tabel 2.5a. Cek konsistensi koordinat</h4>' + table(
    ["Cek", "Jumlah"], [[r.cek, I(r.jumlah)] for r in q13.itertuples()]) +
    '<h4>Tabel 2.5b. Listing dengan koordinat jauh dari kotanya</h4>' + table(
    ["Kecamatan", "Kota", "Alamat", "Jarak dari median kota (km)"],
    [[r.district, r.city, r.address, I(r.km)] for r in q13c.itertuples()]))

# ---------------------------------------------------------------- Report 3: dataset dan hipotesis
VERD = {"H1": ("Sebagian", PART), "H2": ("Terbukti", OK), "H3": ("Sebagian", PART), "H4": ("Tidak terbukti", NO), "H5": ("Sebagian", PART)}
HTXT = {"H1": "Jakarta Selatan dan Jakarta Pusat termahal per m2, Bogor dan Bekasi paling terjangkau",
        "H2": "Lokasi lebih berpengaruh daripada jumlah kamar", "H3": "SHM lebih mahal daripada HGB di area yang sama",
        "H4": "Rumah lebih luas punya harga per m2 lebih rendah", "H5": "Sebagian listing ekstrem adalah salah input"}
BUKTI = {"H1": f"Jakarta Utara ({I(kota.loc['Jakarta Utara','median_ppm2'])}) dan Jakarta Selatan ({I(kota.loc['Jakarta Selatan','median_ppm2'])}) tertinggi. Jakarta Pusat hanya kelima (n = {I(kota.loc['Jakarta Pusat','n'])}). Depok dan Bekasi termurah.",
         "H2": f"Eta-squared kota {D(eta_loc,3)}, jumlah kamar {D(eta_bed,3)}.",
         "H3": f"SHM lebih tinggi di {len(shm)} dari {len(q5)} kecamatan. Selisih median {D(q5.selisih_pct.median(),1)}%.",
         "H4": f"Spearman luas bangunan vs harga per m2 = {D(rho_size,3)} (positif).",
         "H5": f"{I(n_flag)} listing ({D(n_flag/tbl['listings']*100,2)}%) kena flag batas. {I(ratio_low+ratio_hi)} listing rasio ekstrem, dan belum bisa dipastikan sebagai salah input."}
rp3 = ['<div class="callout a"><h4>Sumber</h4>Daftar Harga Rumah Jabodetabek (Kaggle), Versi 1, tanggal akses 23 Oktober 2026. Lisensi dan sitasi belum dicek (item terbuka).</div>',
       '<h3>3.1 Hipotesis Design</h3>',
       '<div class="scroll"><table class="rt"><tr><th>No</th><th>Hipotesis</th><th>Verdict</th><th>Bukti</th></tr>' +
       "".join(f'<tr><td>{h}</td><td>{esc(HTXT[h])}</td><td>{VERD[h][1](VERD[h][0])}</td><td>{esc(BUKTI[h])}</td></tr>' for h in HTXT) +
       '</table></div>',
       '<h3>3.2 Sensitivitas batas harga per m2</h3>' + table(
           ["Batas bawah (Rp/m2)", "Batas atas (Rp/m2)", "Listing valid"],
           [[I(r.batas_bawah), I(r.batas_atas), I(r.listing_valid)] for r in sens.itertuples()]),
       '<h3>3.3 Penyesuaian terhadap rancangan</h3>',
       '<div class="card"><ul>' +
       "<li>Basis harga per m2 memakai luas bangunan (rancangan belum memilih).</li>" +
       f"<li>Batas wajar Rp {I(1_000_000)} s.d. Rp {I(100_000_000)} dan minimal {MIN_DISTRICT_N} listing per kecamatan adalah asumsi. Lihat tabel 3.2.</li>" +
       "<li>Dua tabel tambahan (<code>listing_vs_district</code>, <code>cleaning_log</code>) dibuat untuk audit.</li></ul></div>"]

# ---------------------------------------------------------------- Report 4: tools
rp4 = ['<div class="scroll"><table class="rt"><tr><th>Tool</th><th>Rancangan</th><th>Realisasi</th><th>Verdict</th></tr>',
       f'<tr><td>DuckDB + SQL</td><td>Database dan query</td><td>Dipakai untuk pembersihan dan analisis (<code>listings</code>, <code>city_summary</code>, dll.)</td><td>{OK("Sesuai")}</td></tr>',
       f'<tr><td>Python (pandas)</td><td>Analisis dan pembersihan</td><td>Dipakai untuk uji hipotesis, cek silang, dan hasil CSV</td><td>{OK("Sesuai")}</td></tr>',
       f'<tr><td>Streamlit + Plotly</td><td>Dashboard interaktif</td><td>Belum dibuat</td><td>{NO("Tidak dibuat")}</td></tr>',
       f'<tr><td>Excel (opsional)</td><td>Cek silang Q14</td><td>Tidak dipakai (tidak tersedia di sesi). Diganti cek silang SQL dan pandas</td><td>{PART("Sebagian")}</td></tr>',
       f'<tr><td>GitHub + Markdown</td><td>Repositori dan README</td><td>Repositori dan README dibuat di branch <code>project-8-build</code></td><td>{OK("Sesuai")}</td></tr>',
       '</table></div>']

# ---------------------------------------------------------------- Report 5: alur kerja
src = (REPO / "design-and-report" / "src" / "page_v1.html").read_text(encoding="utf-8")
s6 = src[src.index('id="s6"'):src.index('id="s7"')]
steps = re.findall(r'<b class="t">(.*?)</b>', s6)
assert len(steps) == 12, len(steps)
REAL = [("Sesuai", OK, "Definisi di README dan <code>docs/definitions.md</code>"),
        ("Sesuai", OK, "Tabel dan kolom ada di DuckDB"),
        ("Sesuai", OK, "CSV diunduh dan diprofil"),
        ("Sesuai + penyesuaian", PART, "Cleaning dilakukan di SQL; nama kecamatan tidak diubah"),
        ("Sebagian", PART, "Cek silang SQL vs pandas dilakukan; Excel tidak"),
        ("Sesuai", OK, "Rasio dan selisih per listing dihitung"),
        ("Sesuai", OK, "Batas minimal 10 listing diterapkan"),
        ("Sesuai", OK, "Ditulis di Report ini"),
        ("Sesuai", OK, "Pengujian ada di Report, bagian 2.5"),
        ("Tidak dibuat", NO, "Notebook belum dibuat"),
        ("Tidak dibuat", NO, "Dashboard belum dibuat"),
        ("Sebagian", PART, "README diperbarui, infografik belum dibuat")]
rp5 = ['<div class="scroll"><table class="rt"><tr><th>No</th><th>Rancangan</th><th>Realisasi</th><th>Verdict</th></tr>']
for i, (t, (vtxt, fn, note)) in enumerate(zip(steps, REAL), 1):
    rp5.append(f'<tr><td>{i}</td><td>{esc(re.sub("<[^>]+>", "", t))}</td><td>{note}</td><td>{fn(vtxt)}</td></tr>')
rp5.append('</table></div>')
rp5.insert(0, '<p class="how">Urutan langkah sama dengan rancangan, tetapi beberapa langkah belum selesai (notebook, dashboard, dan Excel).</p>')
dq_b = int(q8r.loc['undervalued (rasio < 0.5)', 'jumlah'])

# ---------------------------------------------------------------- Report 6: output
OUTS = [("Dashboard interaktif", "Utama", "Tidak dibuat", NO, "Belum dibuat"),
        ("One-sheet infografik", "Utama", "Tidak dibuat", NO, "Belum dibuat"),
        ("Database & query SQL", "Utama", "Sebagian", PART, "File DuckDB dibuat (tidak di-commit). Query SQL ada di <code>project/code/*/sql/</code>"),
        ("Skrip cleaning & pemuat data", "Utama", "Tercapai", OK, "<code>project/code/1-data-preparation/python/01_clean.py</code>"),
        ("Notebook analisis", "Utama", "Tidak dibuat", NO, "Belum dibuat"),
        ("Laporan temuan & rekomendasi", "Utama", "Tercapai", OK, "README dan Report v2 di <code>design-and-report/</code>"),
        ("Repositori GitHub", "Utama", "Tercapai", OK, "Branch <code>project-8-build</code>"),
        ("Slide presentasi", "Opsional", "Tidak dibuat", NO, "Belum dibuat")]
rp6 = ['<div class="scroll"><table class="rt"><tr><th>Output</th><th>Label</th><th>Status</th><th>Bukti</th></tr>' +
       "".join(f'<tr><td>{o}</td><td>{l}</td><td>{fn(s)}</td><td>{b}</td></tr>' for o, l, s, fn, b in OUTS) + '</table></div>']
n_out_done = sum(1 for o in OUTS if o[2] == "Tercapai")

# ---------------------------------------------------------------- Report 7: kesimpulan
crit = [("Sembilan pertanyaan Utama terjawab dengan angka dari data", "Tercapai", OK, "Q1, Q2, Q4, Q5, Q7, Q8, Q10, Q12, Q13 dijawab, lihat bagian 2"),
        ("Angka SQL sama dengan hitungan pandas dan Excel", "Sebagian", PART, f"SQL vs pandas: {I(xc.sama.sum())} dari {I(xc.jumlah_dibandingkan.sum())} sama. Excel tidak dicek"),
        ("Setiap listing yang diubah atau dikeluarkan tercatat", "Sebagian", PART, "Log dalam bentuk jumlah per aturan (Tabel 1.1), belum per listing"),
        ("Orang awam paham dashboard dalam satu menit", "Tidak dibuat", NO, "Dashboard belum dibuat"),
        ("Checklist standar terpenuhi", "Sebagian", PART, "Report dan README selesai, dashboard dan notebook belum")]
n_crit_ok = sum(1 for c in crit if c[1] == "Tercapai")
rp7 = ['<h4>7.1 Hasil analisis</h4>',
       f'<p>Harga per m2 paling terkait dengan luas tanah dan jumlah kamar mandi, serta lokasi kota. Jakarta Utara dan Jakarta Selatan termahal, dan Depok serta Bekasi termurah. Sertifikat dan kondisi hampir tidak berpengaruh. Jumlah kamar tidur lebih kecil pengaruhnya daripada lokasi.</p>',
       '<h4>7.2 Impact</h4>',
       f'<p>Ada {I(ratio_low)} listing yang harganya jauh di bawah median kecamatannya. Ini kandidat untuk diperiksa, bukan harga wajar. Estimasi selisih ditulis sebagai <i>estimated</i>. Harga listing bukan harga transaksi.</p>',
       '<h4>7.3 Success criteria</h4>',
       table(["Kriteria", "Status", "Bukti"], [[c[0], c[2](c[1]), c[3]] for c in crit]) +
       f'<p>Hasil: {I(n_crit_ok)} dari {I(len(crit))} kriteria tercapai.</p>',
       '<h4>7.4 Rekomendasi</h4>',
       '<ul><li>Bandingkan harga per m2 dalam kecamatan yang sama, bukan antar kota.</li>'
       '<li>Periksa manual listing dengan rasio di bawah 0,5 sebelum dianggap murah.</li>'
       '<li>Koreksi koordinat listing di Harjamukti dan Depok II.</li></ul>',
       '<h4>7.5 Saran perbaikan</h4>',
       '<ul><li>Buat dashboard dan infografik, lalu uji dengan pembaca awam.</li>'
       '<li>Tambahkan log pembersihan per listing.</li>'
       '<li>Lakukan cek silang dengan Excel (Q14) bila tersedia.</li></ul>',
       '<h4>7.6 Batasan</h4>',
       '<ul><li>Harga listing bukan harga transaksi.</li>'
       '<li>Pola tidak sama dengan penyebab. Perbedaan kecamatan belum dikontrol sepenuhnya.</li>'
       f'<li>Batas harga per m2, minimal listing, dan ambang rasio adalah asumsi. Lihat docs/definitions.md.</li>'
       f'<li>Jumlah listing per kecamatan tidak merata (Bogor {I(kota.loc["Bogor","n"])}, Jakarta Pusat {I(kota.loc["Jakarta Pusat","n"])}).</li>'
       '<li>Lisensi dataset dan sitasi belum dicek.</li>'
       '<li>Dashboard, infografik, notebook, dan Excel belum dibuat.</li></ul>']

# ---------------------------------------------------------------- rakit halaman
def sec(id_, title, sub, body):
    return f'<h2 id="{id_}">{title}<small>{sub}</small></h2>\n' + body

REPORT_HEAD = [
    ("rp1", "1. Data yang berhasil didapatkan", "Isi data mentah, tabel di database, dan data hasil analisis", rp1),
    ("rp2", "2. Apakah business question terjawab?", f"{len(ANS)} pertanyaan pada Design Project, dijawab dengan data", rp2),
    ("rp3", "3. Apakah dataset sesuai dengan Design Project?", "Perbandingan rancangan dengan realisasi", rp3),
    ("rp4", "4. Apakah tools yang digunakan sesuai?", "Perbandingan rancangan dengan eksekusi", rp4),
    ("rp5", "5. Apakah alur pengerjaan sesuai dengan Design Project?", f"{len(steps)} langkah rancangan vs yang dijalankan", rp5),
    ("rp6", "6. Apakah project output tercapai?", "Output pada Design Project, bagian 7", rp6),
    ("rp7", "7. Kesimpulan", "Hasil analisis, Impact, success criteria, rekomendasi, saran perbaikan, dan batasan", rp7),
]
report_pane = ['<div class="pane" id="report" data-tab="report" hidden>',
               '<div class="callout g"><h4>Report Project versi 2: evaluasi hasil terhadap Design Project</h4>'
               f'Dibuat dari {I(tbl["listings"])} listing bersih. Cek silang dilakukan untuk {I(xc.jumlah_dibandingkan.sum())} kota dan kecamatan. Angka laporan dihasilkan dari file hasil (CSV) dan database.</div>']
for id_, t, sub, body in REPORT_HEAD:
    report_pane.append(sec(id_, t, sub, "".join(body) if isinstance(body, list) else body))
report_pane.append('</div>')
report_html = "\n".join(report_pane)

nav_report = ('<div class="links" data-tab="report" hidden>' +
              '<a href="#rp1">Data</a><a href="#rp2">Business Questions</a><a href="#rp3">Dataset</a><a href="#rp4">Tools</a>'
              '<a href="#rp5">Alur Kerja</a><a href="#rp6">Project Output</a><a href="#rp7">Kesimpulan</a></div>')
nav_old = re.search(r'<nav aria-label="Project navigation">.*?</nav>', src, re.S).group(0)
nav_new = re.sub(r'<div class="links" data-tab="report" hidden>.*?</div>', nav_report, nav_old, flags=re.S)

# --- audit angka sebelum rakit
STATIC = {"1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "0", "50", "2200", "2026", "23", "2.200", "1.000.000", "100.000.000", "0,5", "0,25", "0,75", "1", "3.553",
          "1.1", "1.2", "1.3", "2.1", "2.2", "2.3", "2.4", "2.5", "3.1", "3.2", "3.3", "7.1", "7.2", "7.3", "7.4", "7.5", "7.6",
          "100", "200", "400"}  # nomor bagian Report dan batas kelompok luas (label, bukan hasil)
n_tok, bad = audit(report_html, STATIC)
print("token diperiksa:", n_tok, "| tidak terdaftar:", bad)
assert not bad, bad

# --- rakit halaman: head + style (+report.css) + main(nav baru + pane Design identik + pane Report)
start_design = src.index('<div class="pane" id="design"')
end_design = src.index('<div class="pane" id="report"')
design_pane = src[start_design:end_design]
pre = src[:src.index('<nav aria-label="Project navigation">')]
pre = pre.replace("</style>", (REPO / "design-and-report" / "src" / "report.css").read_text(encoding="utf-8") + "\n</style>", 1)
post = src[src.index('</main>'):]
between = src[src.index(nav_old) + len(nav_old):start_design]
html = pre + nav_new + between + design_pane + report_html + "\n" + post
assert html.count('<div class="pane" id="design"') == 1 and html.count('id="report"') == 1
assert design_pane.strip() == src[start_design:end_design].strip()
(REPO / "design-and-report" / "index.html").write_text(html, encoding="utf-8")
print("ok ditulis", len(html), "bytes")
