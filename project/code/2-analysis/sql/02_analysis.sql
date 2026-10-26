-- Ringkasan per kota dan kecamatan. Hanya baris dengan price per m2 valid (flag = 0).
CREATE OR REPLACE TABLE valid AS SELECT * FROM listings WHERE flag_ppm2_out = 0;

CREATE OR REPLACE TABLE city_summary AS
SELECT city, count(*) AS n, median(price_per_m2) AS median_ppm2, median(building_size_m2) AS median_building_m2
FROM valid GROUP BY city ORDER BY median_ppm2 DESC;

CREATE OR REPLACE TABLE district_summary AS
SELECT city, district, count(*) AS n, median(price_per_m2) AS median_ppm2
FROM valid GROUP BY city, district HAVING count(*) >= {MIN_N} ORDER BY median_ppm2 DESC;

-- Kandidat harga jauh di bawah/atas median kecamatan (indikator, bukan penilaian properti)
CREATE OR REPLACE TABLE listing_vs_district AS
SELECT v.ads_id, v.city, v.district, v.address, v.price_in_rp, v.building_size_m2,
  v.price_per_m2, d.median_ppm2 AS district_median_ppm2, d.n AS district_n,
  v.price_per_m2 / d.median_ppm2 AS ratio
FROM valid v JOIN district_summary d USING (city, district);
