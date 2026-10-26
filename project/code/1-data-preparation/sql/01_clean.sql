-- Membersihkan listing mentah. Parameter PPM2_MIN/PPM2_MAX diisi dari common.py.
CREATE OR REPLACE TABLE raw AS SELECT * FROM read_csv_auto('{RAW_CSV}', header=true);

-- 1. Duplikat URL persis: simpan baris pertama
CREATE OR REPLACE TABLE s1 AS
SELECT * EXCLUDE (rn) REPLACE (trim(city) AS city) FROM (SELECT *, row_number() OVER (PARTITION BY url ORDER BY ads_id) rn FROM raw) WHERE rn = 1;

-- 2. Listing sama (ads_id sama, hanya beda suffix #qid): simpan satu
CREATE OR REPLACE TABLE s2 AS
SELECT * EXCLUDE (rn) FROM (SELECT *, row_number() OVER (PARTITION BY ads_id ORDER BY url) rn FROM s1) WHERE rn = 1;

-- 3. Tahun bangun di masa depan dianggap salah input
CREATE OR REPLACE TABLE listings AS
SELECT *,
  price_in_rp / building_size_m2 AS price_per_m2,
  CASE WHEN year_built > 2026 THEN NULL ELSE year_built END AS year_built_clean,
  CASE WHEN price_in_rp / building_size_m2 BETWEEN {PPM2_MIN} AND {PPM2_MAX} THEN 0 ELSE 1 END AS flag_ppm2_out
FROM s2;

-- Jumlah per aturan untuk log
CREATE OR REPLACE TABLE cleaning_log AS
SELECT 'baris mentah' AS langkah, (SELECT count(*) FROM raw) AS jumlah
UNION ALL SELECT 'setelah hapus duplikat URL', (SELECT count(*) FROM s1)
UNION ALL SELECT 'setelah hapus duplikat ads_id', (SELECT count(*) FROM s2)
UNION ALL SELECT 'year_built > 2026 jadi NULL', (SELECT count(*) FROM listings WHERE year_built > 2026)
UNION ALL SELECT 'price per m2 di luar batas (flag)', (SELECT count(*) FROM listings WHERE price_per_m2 IS NOT NULL AND flag_ppm2_out = 1)
UNION ALL SELECT 'building_size_m2 kosong', (SELECT count(*) FROM listings WHERE building_size_m2 IS NULL)
UNION ALL SELECT 'city ada spasi di depan (di-trim)', (SELECT count(*) FROM raw WHERE city <> trim(city));
