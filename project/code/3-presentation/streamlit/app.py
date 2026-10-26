"""Dashboard Project 8: Harga Rumah Jabodetabek. Jalankan dari folder project/:
    streamlit run code/3-presentation/streamlit/app.py
Membaca file ringkas di results/ (tidak butuh database atau data mentah)."""
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT = Path(__file__).resolve().parents[3]
RES = ROOT / "results"
L = pd.read_csv(RES / "3-presentation" / "dash_listings.csv")
D = pd.read_csv(RES / "3-presentation" / "dash_districts.csv")
COORD_BAD = set(pd.read_csv(RES / "2-analysis" / "q13_coord_outliers.csv").ads_id.str.strip())
CITY_MED = pd.read_csv(RES / "2-analysis" / "02_city_summary.csv")
L["ads_id"] = L.ads_id.astype(str).str.strip()
L["city"] = L.city.str.strip()
L["map_ok"] = ~L.ads_id.isin(COORD_BAD)
L["ratio"] = L.price_per_m2 / L.district_median_ppm2

st.set_page_config(page_title="Harga Rumah Jabodetabek", layout="wide")
st.title("Harga Rumah Jabodetabek")
st.caption("Dataset publik Kaggle (Versi 1, akses 23 Oktober 2026). Harga listing, bukan harga transaksi.")

with st.sidebar:
    st.header("Filter")
    kota = st.multiselect("Kota", sorted(L.city.unique()), default=sorted(L.city.unique()))
    sert = st.multiselect("Sertifikat", sorted(L.certificate.dropna().unique()), default=sorted(L.certificate.dropna().unique()))
    lo, hi = st.slider("Rentang harga (miliar Rp)", 0.0, 20.0, (0.0, 20.0), 0.1)

F = L[L.city.isin(kota) & L.certificate.isin(sert) & L.price_in_rp.between(lo * 1e9, hi * 1e9)]
tab1, tab2, tab3, tab4 = st.tabs(["Ringkasan", "Peta Harga per Area", "Faktor Harga", "Kalkulator Nilai Wajar"])

with tab1:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Listing", f"{len(F):,}".replace(",", "."))
    c2.metric("Median Rp/m2", f"{F.price_per_m2.median():,.0f}".replace(",", "."))
    c3.metric("Kota", F.city.nunique())
    c4.metric("Listing undervalued (rasio < 0,5)", f"{int((F.ratio < 0.5).sum()):,}".replace(",", "."))
    cm = CITY_MED[CITY_MED.city.isin(kota)].sort_values("median_ppm2")
    st.plotly_chart(px.bar(cm, x="median_ppm2", y="city", orientation="h", labels={"median_ppm2": "Median Rp per m2", "city": ""},
                           title="Median harga per m2 per kota"), width="stretch")

with tab2:
    st.caption("Titik listing dengan koordinat di luar Jabodetabek sudah dikeluarkan (lihat q13_coord_outliers.csv).")
    M = F[F.map_ok]
    st.map(M, latitude="lat", longitude="long", size=20)
    st.dataframe(D[D.city.isin(kota)].sort_values("median_ppm2", ascending=False).head(30).rename(columns={
        "median_ppm2": "median Rp/m2", "n": "listing"}), width="stretch", hide_index=True)

with tab3:
    st.write("Hubungan luas tanah dengan harga per m2 (skala log). Setiap titik adalah satu listing.")
    fig = px.scatter(F.dropna(subset=["land_size_m2"]), x="land_size_m2", y="price_per_m2", color="city", log_x=True, log_y=True,
                     labels={"land_size_m2": "Luas tanah (m2)", "price_per_m2": "Harga per m2 bangunan (Rp)"}, opacity=0.5)
    st.plotly_chart(fig, width="stretch")
    st.write("Median harga per m2 menurut sertifikat:")
    st.dataframe(F.groupby("certificate").price_per_m2.agg(["count", "median"]).reset_index(), hide_index=True, width="stretch")

with tab4:
    st.write("Estimasi nilai wajar = median harga per m2 kecamatan x luas bangunan. Hasil ini indikator, bukan penilaian properti.")
    opts = D.sort_values(["city", "district"]).assign(label=lambda x: x.city + " | " + x.district)
    pick = st.selectbox("Kecamatan", opts.label.tolist())
    row = opts[opts.label == pick].iloc[0]
    luas = st.number_input("Luas bangunan (m2)", min_value=10.0, max_value=2000.0, value=100.0, step=5.0)
    harga = st.number_input("Harga listing (Rp)", min_value=0.0, value=float(round(row.median_ppm2 * luas)), step=1e6)
    wajar = row.median_ppm2 * luas
    st.metric("Estimasi nilai wajar (estimated)", f"Rp {wajar:,.0f}".replace(",", "."))
    if harga > 0:
        rasio = harga / wajar
        st.write(f"Rasio harga listing terhadap nilai wajar: {rasio:.2f}. Di bawah 0,5 atau di atas 2 perlu diperiksa.")
    st.caption(f"Dihitung dari {int(row.n)} listing di kecamatan ini.")
