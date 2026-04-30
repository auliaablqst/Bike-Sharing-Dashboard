import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from matplotlib.patches import Patch
import os

st.set_page_config(
    page_title="🚲 Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    BASE = os.path.dirname(__file__)
    day_df  = pd.read_csv(os.path.join(BASE, 'main_data.csv'))
    hour_df = pd.read_csv(os.path.join(BASE, 'main_data_hour.csv'))

    day_df['dteday']  = pd.to_datetime(day_df['dteday'])
    hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])

    season_map  = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
    weather_map = {1:'Clear', 2:'Mist/Cloudy', 3:'Light Snow/Rain', 4:'Heavy Rain/Snow'}
    weekday_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}

    for df in [day_df, hour_df]:
        df['season']     = df['season'].map(season_map)
        df['weathersit'] = df['weathersit'].map(weather_map)
        df['weekday']    = df['weekday'].map(weekday_map)

    return day_df, hour_df

day_df, hour_df = load_data()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚲 Bike Sharing")
    st.markdown("**Dashboard Analisis Data**")
    st.markdown("---")

    min_date = day_df['dteday'].min().date()
    max_date = day_df['dteday'].max().date()
    date_range = st.date_input(
        "📅 Rentang Tanggal",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    if len(date_range) == 2:
        start_date = pd.Timestamp(date_range[0])
        end_date   = pd.Timestamp(date_range[1])
    else:
        start_date = pd.Timestamp(min_date)
        end_date   = pd.Timestamp(max_date)

    all_seasons = ['Spring', 'Summer', 'Fall', 'Winter']
    selected_seasons = st.multiselect(
        "🌿 Musim", all_seasons, default=all_seasons
    )

    all_weathers = ['Clear', 'Mist/Cloudy', 'Light Snow/Rain']
    selected_weathers = st.multiselect(
        "🌤️ Kondisi Cuaca", all_weathers, default=all_weathers
    )

    st.markdown("---")
    st.caption("Sumber: Bike Sharing Dataset (Kaggle) · 2011–2012")

# ── Filter Data ───────────────────────────────────────────────────────────────
filtered_day = day_df[
    (day_df['dteday'] >= start_date) &
    (day_df['dteday'] <= end_date) &
    (day_df['season'].isin(selected_seasons)) &
    (day_df['weathersit'].isin(selected_weathers))
]

filtered_hour = hour_df[
    (hour_df['dteday'] >= start_date) &
    (hour_df['dteday'] <= end_date)
]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚲 Bike Sharing Dashboard")
st.markdown("Analisis data peminjaman sepeda tahun **2011–2012**.")
st.markdown("---")

# ── Metrics ───────────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
col1.metric("🔢 Total Peminjaman",   f"{int(filtered_day['cnt'].sum()):,}" if len(filtered_day) > 0 else "0")
col2.metric("📊 Rata-rata Harian",   f"{int(filtered_day['cnt'].mean()):,}" if len(filtered_day) > 0 else "0")
col3.metric("👤 Pengguna Terdaftar", f"{int(filtered_day['registered'].sum()):,}" if len(filtered_day) > 0 else "0")
col4.metric("🚶 Pengguna Kasual",    f"{int(filtered_day['casual'].sum()):,}" if len(filtered_day) > 0 else "0")
st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 1
# ══════════════════════════════════════════════════════════════════════════════
st.header("❓ Pertanyaan 1")
st.markdown(
    "> *Bagaimana pengaruh musim dan kondisi cuaca terhadap rata-rata "
    "peminjaman sepeda harian sepanjang 2011–2012?*"
)

tab1, tab2, tab3 = st.tabs(["📊 Per Musim", "🌤️ Per Cuaca", "🗓️ Tren Bulanan"])

SEASON_ORDER  = ['Spring', 'Summer', 'Fall', 'Winter']
WEATHER_ORDER = ['Clear', 'Mist/Cloudy', 'Light Snow/Rain']
PALETTE_S     = ['#A8D8A8', '#FFD700', '#FF8C00', '#87CEEB']
PALETTE_W     = ['#4FC3F7', '#B0BEC5', '#78909C']

with tab1:
    if filtered_day.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        avail = [s for s in SEASON_ORDER if s in filtered_day['season'].unique()]
        season_data = filtered_day.groupby('season')['cnt'].mean().reindex(avail)
        fig, ax = plt.subplots(figsize=(8, 5))
        colors = [PALETTE_S[SEASON_ORDER.index(s)] for s in avail]
        bars = ax.bar(avail, season_data.values, color=colors,
                      edgecolor='white', linewidth=1.2)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 50,
                    f'{bar.get_height():,.0f}',
                    ha='center', fontsize=10, fontweight='bold')
        ax.set_title('Rata-rata Peminjaman per Musim', fontsize=13, fontweight='bold')
        ax.set_xlabel('Musim')
        ax.set_ylabel('Rata-rata Peminjaman Harian')
        ax.set_ylim(0, season_data.max() * 1.25)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        ax.grid(axis='y', alpha=0.4)
        ax.set_axisbelow(True)
        sns.despine()
        st.pyplot(fig)
        plt.close()
        st.markdown("**Insight:** Musim Fall memiliki rata-rata peminjaman tertinggi, Spring terendah.")

with tab2:
    if filtered_day.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        avail_w = [w for w in WEATHER_ORDER if w in filtered_day['weathersit'].unique()]
        weather_data = filtered_day.groupby('weathersit')['cnt'].mean().reindex(avail_w)
        fig, ax = plt.subplots(figsize=(8, 5))
        colors_w = [PALETTE_W[WEATHER_ORDER.index(w)] for w in avail_w]
        bars = ax.bar(avail_w, weather_data.values, color=colors_w,
                      edgecolor='white', linewidth=1.2)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2,
                    bar.get_height() + 50,
                    f'{bar.get_height():,.0f}',
                    ha='center', fontsize=10, fontweight='bold')
        ax.set_title('Rata-rata Peminjaman per Kondisi Cuaca', fontsize=13, fontweight='bold')
        ax.set_xlabel('Kondisi Cuaca')
        ax.set_ylabel('Rata-rata Peminjaman Harian')
        ax.set_ylim(0, weather_data.max() * 1.25)
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        ax.grid(axis='y', alpha=0.4)
        ax.set_axisbelow(True)
        sns.despine()
        st.pyplot(fig)
        plt.close()
        st.markdown("**Insight:** Cuaca Clear menghasilkan peminjaman ~63% lebih tinggi dibanding Light Snow/Rain.")

with tab3:
    if filtered_day.empty:
        st.warning("Tidak ada data untuk filter yang dipilih.")
    else:
        monthly = (
            filtered_day.groupby(filtered_day['dteday'].dt.to_period('M'))['cnt']
            .mean().reset_index()
        )
        monthly.columns = ['bulan', 'rata_rata']
        monthly['bulan_str'] = monthly['bulan'].astype(str)
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.plot(range(len(monthly)), monthly['rata_rata'],
                color='#2196F3', linewidth=2.5, marker='o', markersize=5)
        ax.fill_between(range(len(monthly)), monthly['rata_rata'],
                        alpha=0.12, color='#2196F3')
        step = max(1, len(monthly) // 8)
        ax.set_xticks(range(0, len(monthly), step))
        ax.set_xticklabels(monthly['bulan_str'].iloc[::step],
                           rotation=45, ha='right', fontsize=9)
        ax.set_title('Tren Rata-rata Peminjaman Bulanan (2011–2012)',
                     fontsize=13, fontweight='bold')
        ax.set_xlabel('Bulan')
        ax.set_ylabel('Rata-rata Peminjaman Harian')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
        ax.grid(alpha=0.4)
        ax.set_axisbelow(True)
        sns.despine()
        st.pyplot(fig)
        plt.close()
        st.markdown("**Insight:** Tren peminjaman meningkat konsisten dari 2011 ke 2012.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# PERTANYAAN 2
# ══════════════════════════════════════════════════════════════════════════════
st.header("❓ Pertanyaan 2")
st.markdown(
    "> *Pada jam berapa puncak peminjaman terjadi untuk pengguna registered "
    "vs casual pada hari kerja vs akhir pekan/libur?*"
)

tab_kerja, tab_libur = st.tabs(["📅 Hari Kerja", "🎉 Akhir Pekan / Libur"])
COLORS = {'registered': '#E63946', 'casual': '#457B9D'}

for tab, (day_type, label) in zip(
    [tab_kerja, tab_libur],
    [(1, 'Hari Kerja'), (0, 'Akhir Pekan / Libur')]
):
    with tab:
        subset = filtered_hour[filtered_hour['workingday'] == day_type]
        if subset.empty:
            st.warning("Tidak ada data.")
        else:
            hourly = subset.groupby('hr')[['registered', 'casual']].mean()
            fig, ax = plt.subplots(figsize=(12, 5))
            ax.plot(hourly.index, hourly['registered'],
                    color=COLORS['registered'], linewidth=2.5,
                    marker='o', markersize=4, label='Registered')
            ax.plot(hourly.index, hourly['casual'],
                    color=COLORS['casual'], linewidth=2.5,
                    marker='s', markersize=4, label='Casual')
            if day_type == 1:
                ax.axvspan(7, 9, alpha=0.1, color='orange', label='Rush Hour')
                ax.axvspan(16, 19, alpha=0.1, color='orange')
            for col, c in [('registered', COLORS['registered']),
                            ('casual', COLORS['casual'])]:
                peak_h = hourly[col].idxmax()
                ax.annotate(
                    f'Puncak\n{int(peak_h):02d}.00',
                    xy=(peak_h, hourly.loc[peak_h, col]),
                    xytext=(peak_h + 1.5, hourly.loc[peak_h, col] + 15),
                    fontsize=8, color=c,
                    arrowprops=dict(arrowstyle='->', color=c, lw=1)
                )
            ax.set_title(f'Pola Peminjaman Per Jam – {label}',
                         fontsize=13, fontweight='bold')
            ax.set_xlabel('Jam')
            ax.set_ylabel('Rata-rata Peminjaman')
            ax.set_xticks(range(0, 24, 2))
            ax.set_xticklabels([f'{h:02d}.00' for h in range(0, 24, 2)],
                               rotation=45, fontsize=9)
            ax.legend(fontsize=10)
            ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
            ax.grid(alpha=0.4)
            ax.set_axisbelow(True)
            sns.despine()
            st.pyplot(fig)
            plt.close()
            if day_type == 1:
                st.markdown("**Insight:** Registered: pola bimodal komuter (08.00 & 17.00–18.00). Casual: merata di siang hari.")
            else:
                st.markdown("**Insight:** Keduanya puncak di siang hari (12.00–14.00) — penggunaan rekreasional.")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# ANALISIS LANJUTAN
# ══════════════════════════════════════════════════════════════════════════════
st.header("🔍 Analisis Lanjutan: Clustering Intensitas Per Jam")
st.markdown(
    "Mengelompokkan 24 jam ke dalam 4 kluster intensitas berdasarkan "
    "rata-rata peminjaman (**metode: binning kuantil**)."
)

hourly_total = filtered_hour.groupby('hr')['cnt'].mean().reset_index()
hourly_total.columns = ['hr', 'avg_cnt']

if not hourly_total.empty:
    q25 = hourly_total['avg_cnt'].quantile(0.25)
    q50 = hourly_total['avg_cnt'].quantile(0.50)
    q75 = hourly_total['avg_cnt'].quantile(0.75)

    def label_cluster(cnt):
        if cnt < q25:   return 'Low (Sepi)'
        elif cnt < q50: return 'Medium'
        elif cnt < q75: return 'High'
        else:           return 'Peak (Puncak)'

    hourly_total['cluster'] = hourly_total['avg_cnt'].apply(label_cluster)

    CLUSTER_COLORS = {
        'Low (Sepi)':    '#AED6F1',
        'Medium':        '#52BE80',
        'High':          '#F39C12',
        'Peak (Puncak)': '#E74C3C'
    }

    fig, ax = plt.subplots(figsize=(14, 5))
    colors = [CLUSTER_COLORS[c] for c in hourly_total['cluster']]
    ax.bar(hourly_total['hr'], hourly_total['avg_cnt'],
           color=colors, edgecolor='white', linewidth=0.8)
    legend_elements = [Patch(facecolor=v, label=k)
                       for k, v in CLUSTER_COLORS.items()]
    ax.legend(handles=legend_elements, loc='upper left',
              fontsize=10, title='Kluster')
    ax.set_title('Kluster Intensitas Penggunaan Sepeda per Jam',
                 fontsize=13, fontweight='bold')
    ax.set_xlabel('Jam')
    ax.set_ylabel('Rata-rata Peminjaman')
    ax.set_xticks(range(24))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
    ax.grid(axis='y', alpha=0.4)
    ax.set_axisbelow(True)
    sns.despine()
    st.pyplot(fig)
    plt.close()

    summary = (
        hourly_total.groupby('cluster')
        .agg(
            Jumlah_Jam=('hr', 'count'),
            Rata_rata=('avg_cnt', 'mean'),
            Jam=('hr', lambda x: ', '.join(f'{h:02d}.00' for h in sorted(x)))
        )
        .reset_index()
        .rename(columns={'cluster': 'Kluster', 'Rata_rata': 'Rata-rata Peminjaman'})
    )
    summary['Rata-rata Peminjaman'] = summary['Rata-rata Peminjaman'].map('{:,.0f}'.format)
    st.dataframe(summary, use_container_width=True, hide_index=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════════════════
# KESIMPULAN
# ══════════════════════════════════════════════════════════════════════════════
st.header("📝 Kesimpulan & Rekomendasi")

col_a, col_b = st.columns(2)
with col_a:
    st.subheader("Kesimpulan")
    st.markdown("""
    1. **Fall + Clear** = kondisi paling produktif. Cuaca buruk menurunkan 
       permintaan hingga **~63%**.
    2. Pengguna **registered** mendominasi hari kerja dengan pola rush hour 
       pagi & sore. Pengguna **casual** & akhir pekan: puncak di siang hari 
       (rekreasional).
    """)

with col_b:
    st.subheader("Rekomendasi")
    st.markdown("""
    1. 🚲 Tambah armada **30–40%** saat musim Fall & cuaca cerah.
    2. 🕗 Isi ulang stasiun perkantoran sebelum jam **08.00 & 16.30** 
       di hari kerja.
    3. 🌳 Pindahkan armada ke area wisata saat **siang hari akhir pekan**.
    4. 🔧 Manfaatkan jam **01.00–05.00** untuk perawatan & rebalancing armada.
    """)

st.caption("Dashboard dibuat dengan Streamlit · Bike Sharing Dataset (Kaggle) · 2011–2012")