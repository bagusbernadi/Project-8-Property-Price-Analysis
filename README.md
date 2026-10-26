[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 8: Property Price Analysis

**Status: Analisis dan Report v2 selesai di branch `project-8-build`.** Halaman ada di [`design-and-report/`](design-and-report/). Dashboard, infografik, dan notebook belum dibuat.

**Tujuan:** membangun analisis dan dashboard harga rumah di Jabodetabek yang menunjukkan harga per m² setiap area, faktor yang paling terkait dengan harga, dan listing yang jauh di atas atau di bawah nilai wajarnya, sehingga calon pembeli dapat menilai area dan harga dengan pembanding yang adil.

| | |
|---|---|
| Kategori | Properti / ekonomi |
| Tingkat | Mudah |
| Data | Dataset publik Daftar Harga Rumah Jabodetabek (Kaggle) |
| Tools | DuckDB + SQL, Python (pandas), Streamlit + Plotly. Excel opsional |

## 1. Problem

**Pertanyaan utama:** Faktor apa yang paling terkait dengan harga per m² rumah di Jabodetabek, dan area mana yang paling mahal atau paling undervalued?

Rancangan memecahnya menjadi 14 pertanyaan (9 Utama, 4 Pendukung, 1 Tambahan) dalam tema harga per area, faktor harga, nilai wajar, penerapan, dan validitas data. Daftar lengkap ada di bagian 2 halaman rancangan.

## 2. Data

- Sumber data: [here](https://www.kaggle.com/datasets/nafisbarizki/daftar-harga-rumah-jabodetabek) (Versi: 1, Tanggal akses: 23 Oktober 2026)
- Ukuran: 3.553 baris, 27 kolom (sesuai file yang diunduh). Setelah pembersihan: 3.458 listing unik, 3.439 dengan price per m2 valid.
- Harga di dataset adalah harga listing, bukan harga transaksi.
- Tabel di DuckDB: `raw`, `listings` (bersih), `city_summary`, `district_summary`, `listing_vs_district`, `cleaning_log`.
- Lisensi dan sitasi: **belum dicek** di halaman sumber (item terbuka).
- Data mentah tidak di-commit ke repository.

## 3. Analysis

Pembersihan: [`01_cleaning_log.csv`](project/results/1-data-preparation/01_cleaning_log.csv). Ringkasan kota dan uji hipotesis ada di `project/results/2-analysis/`.

Median price per m2 per kota (listing valid):

| Kota | Listing | Median Rp/m2 |
|---|---|---|
| Jakarta Utara | 123 | 26.250.000 |
| Jakarta Selatan | 226 | 22.325.388 |
| Jakarta Barat | 192 | 17.333.333 |
| Tangerang | 836 | 17.133.929 |
| Jakarta Pusat | 31 | 16.470.588 |
| Jakarta Timur | 82 | 15.780.632 |
| Bogor | 854 | 13.158.658 |
| Depok | 515 | 12.487.500 |
| Bekasi | 580 | 11.402.795 |

Hasil uji hipotesis (angka dari `02_hypothesis_tests.csv`):

1. **Sebagian.** Jakarta Utara tertinggi, Jakarta Selatan kedua, Jakarta Pusat hanya kelima (31 listing). Bekasi dan Depok termurah; Bogor ketujuh, bukan termurah.
2. **Terbukti.** Eta-squared lokasi (kota) 0,246, jumlah kamar 0,075.
3. **Sebagian.** SHM lebih tinggi dari HGB di 6 dari 11 kecamatan yang punya keduanya (n >= 5). Jumlah kecamatan kecil.
4. **Tidak terbukti (arah berlawanan).** Spearman luas bangunan vs price per m2 = +0,294. Rumah lebih luas cenderung punya harga per m2 lebih tinggi.
5. **Sebagian.** 0,55% listing dapat flag input (price per m2 di luar batas asumsi). 6,9% listing punya rasio ekstrem vs median kecamatan (`02_listing_outliers_vs_district.csv`). Tidak semua rasio ekstrem terbukti salah input.

## 4. Recommendation

- Bandingkan harga per m2 dalam kecamatan yang sama, bukan antar kota.
- Verifikasi manual listing dengan rasio di bawah 0,5 sebelum dianggap murah (misalnya harga Rp 125 juta untuk 110 m2).

## 5. Impact

Belum dihitung. Estimasi selisih harga per area belum dibuat (item terbuka).

## Batasan yang sudah diketahui

- Harga listing ≠ harga transaksi.
- Pola belum tentu penyebab; perbandingan dilakukan dalam kecamatan yang sama.
- Jumlah listing per kecamatan tidak merata (Bogor 854, Jakarta Pusat 31).
- Batas wajar price per m2 (Rp 1 juta s.d. Rp 100 juta) adalah asumsi. Sensitivitas hanya mengubah sekitar 1% listing valid.
- Lisensi dataset dan sitasi belum dicek.
- Dashboard, infografik, notebook, dan cek Excel (Q14) belum dibuat.

## Struktur repository

```
index.html                       Pengalihan ke design-and-report/ (URL GitHub Pages tetap)
README.md
design-and-report/index.html     Halaman project (tab Design dan Report)
project/
  code/common.py                 Path dan konstanta
  code/1-data-preparation/       python/01_clean.py, sql/01_clean.sql
  code/2-analysis/               python/02_analysis.py, 03_questions.py, 04_crosscheck.py, sql/02_analysis.sql
  results/                       Hasil CSV per tahap
design-and-report/src/           page_v1.html (pane Design), report_lib.py, report.css, build_report.py
  data/README.md                 Sumber dan lisensi data (raw/ tidak di-commit)
  docs/                          definitions.md, cleaning_decisions.md
  requirements.txt
```

## Menjalankan

Dari folder `project/` (data mentah diletakkan di `data/raw/jabodetabek_house_price.csv`):

```
pip install -r requirements.txt
python code/1-data-preparation/python/01_clean.py
python code/2-analysis/python/02_analysis.py
python code/2-analysis/python/03_questions.py
python code/2-analysis/python/04_crosscheck.py
cd .. && python design-and-report/src/build_report.py
```
