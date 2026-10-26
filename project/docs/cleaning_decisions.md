# Keputusan pembersihan data

1. Duplikat URL persis (1 pasang): simpan baris pertama.
2. Duplikat `ads_id` (listing sama, beda suffix `#qid`): simpan satu baris. Harga kembar di semua pasangan.
3. `year_built` > 2026 (1 baris): dijadikan NULL.
4. Price per m2 di luar batas asumsi (18 baris): diberi flag dan tidak ikut perbandingan.
5. `building_size_m2` kosong (1 baris): price per m2 NULL, tidak ikut perbandingan.

Hasil per langkah: `results/1-data-preparation/01_cleaning_log.csv`.
6. `city` ada spasi di depan pada semua baris (contoh `' Bekasi'`): di-trim. Tanpa trim, nama kota tidak cocok dengan tabel lain.
