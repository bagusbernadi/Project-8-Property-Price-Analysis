# Definisi dan asumsi

| Istilah | Definisi | Status |
|---|---|---|
| Price per m2 | `price_in_rp / building_size_m2` (luas bangunan, bukan luas tanah) | Keputusan analisis |
| Batas wajar price per m2 | Rp 1.000.000 s.d. Rp 100.000.000. Di luar batas = flag input diragukan | **Asumsi**, diuji sensitivitas (`02_ppm2_bounds_sensitivity.csv`) |
| Kecamatan dibandingkan | Minimal 10 listing valid | **Asumsi** |
| Kandidat harga jauh di bawah/atas | Rasio price per m2 terhadap median kecamatan < 0,5 atau > 2 | **Asumsi**, indikator, bukan penilaian properti |
| Eta-squared | Proporsi variasi log price per m2 yang dijelaskan satu faktor | Ukuran standar |

Catatan: angka kandidat harga bukan nilai wajar properti. Harga listing belum tentu harga transaksi.
