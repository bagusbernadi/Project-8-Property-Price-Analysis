-- Membersihkan listing mentah. Parameter PPM2_MIN/PPM2_MAX diisi dari common.py.
CREATE OR REPLACE TABLE raw AS SELECT row_number() OVER () AS rid, * FROM read_csv_auto('{RAW_CSV}', header=true);

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

-- Log per listing: satu baris per baris mentah yang dibuang atau diberi catatan
CREATE OR REPLACE TABLE listing_log AS
SELECT r.rid, r.url, r.ads_id, r.city, r.district, r.price_in_rp, r.building_size_m2,
  CASE WHEN r.rid NOT IN (SELECT rid FROM s1) THEN 'dibuang: duplikat URL'
       ELSE 'dibuang: duplikat ads_id' END AS aksi
FROM raw r WHERE r.rid NOT IN (SELECT rid FROM s2)
UNION ALL
SELECT l.rid, l.url, l.ads_id, l.city, l.district, l.price_in_rp, l.building_size_m2,
  concat_ws('; ',
    CASE WHEN l.year_built > 2026 THEN 'year_built diubah NULL' END,
    CASE WHEN l.flag_ppm2_out = 1 AND l.building_size_m2 IS NOT NULL THEN 'diberi flag: price per m2 di luar batas' END,
    CASE WHEN l.building_size_m2 IS NULL THEN 'diberi flag: building_size_m2 kosong' END) AS aksi
FROM listings l
WHERE l.year_built > 2026 OR l.flag_ppm2_out = 1 OR l.building_size_m2 IS NULL;
