[← Back to portfolio](https://bagusbernadi.github.io/)

# Project 8: Property Price Analysis

**Status: Design (rancangan).** Halaman rancangan ada di [`index.html`](index.html). Analisis, dashboard, dan angka hasil belum dikerjakan, sehingga bagian Analysis, Recommendation, dan Impact di bawah masih kosong.

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
- Ukuran (perkiraan, **belum diverifikasi**): ±3.553 listing, ±27 kolom.
- Harga di dataset adalah harga listing, bukan harga transaksi.
- Rencana tabel: `listings`, `dim_area`, `listing_features`, `area_summary`.
- Lisensi dan sitasi: dicek di halaman sumber sebelum project dipublikasikan.
- Data mentah tidak di-commit ke repository.

## 3. Analysis

Belum dikerjakan. Rencana langkah (12 langkah, tahap A sampai D) ada di bagian 6 halaman rancangan. Semua angka nanti dihitung dari data dengan SQL dan dicek silang.

Hipotesis yang akan diuji (belum terbukti):
1. Jakarta Selatan dan Jakarta Pusat termahal per m², Bogor dan Bekasi paling terjangkau.
2. Lokasi lebih berpengaruh daripada jumlah kamar.
3. SHM lebih mahal per m² daripada HGB di area yang sama.
4. Rumah lebih luas punya harga per m² lebih rendah.
5. Sebagian listing ekstrem adalah salah input.

## 4. Recommendation

Belum dikerjakan. Output yang direncanakan: area dan tipe properti dengan harga per m² wajar dibanding median area.

## 5. Impact

Belum dikerjakan. Rumus yang akan dipakai (semua hasil diberi label `estimated`):

```
Estimasi selisih = harga listing − median harga per m² area × luas (label estimated)
```

## Batasan yang sudah diketahui

- Harga listing ≠ harga transaksi.
- Pola belum tentu penyebab; perbandingan dilakukan dalam kecamatan yang sama.
- Jumlah listing per kecamatan tidak merata.

## Struktur repository

```
index.html   Halaman rancangan project (bisa dibuka di browser atau lewat GitHub Pages)
README.md    Dokumen ini
```

Folder `docs/`, `data/`, `scripts/`, `sql/`, `notebooks/`, `dashboard/`, dan `outputs/` ditambahkan saat pengerjaan dimulai.
