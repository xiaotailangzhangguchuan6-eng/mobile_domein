import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="電波伝搬と品質指標", page_icon="📶", layout="wide")
st.title("📶 電波伝搬と受信品質指標")

# ── 主要指標 ─────────────────────────────────────────────────────
st.subheader("① 主要な受信品質指標")
st.dataframe(pd.DataFrame([
    {"指標": "RSRP", "正式名称": "Reference Signal Received Power",
     "単位": "dBm", "良好/不良": ">-80 / <-100 dBm", "説明": "基地局からの受信電力（電波の強さ）"},
    {"指標": "RSRQ", "正式名称": "Reference Signal Received Quality",
     "単位": "dB",  "良好/不良": ">-10 / <-15 dB",   "説明": "受信品質（信号 vs 干渉+ノイズの比率）"},
    {"指標": "SINR", "正式名称": "Signal to Interference plus Noise Ratio",
     "単位": "dB",  "良好/不良": ">20 / <0 dB",       "説明": "信号対干渉雑音比（値が大きいほど良い）"},
    {"指標": "CQI",  "正式名称": "Channel Quality Indicator",
     "単位": "0〜15","良好/不良": "15 / 0",            "説明": "端末が基地局に報告するチャネル品質（変調方式選択に使用）"},
    {"指標": "RSSI", "正式名称": "Received Signal Strength Indicator",
     "単位": "dBm", "良好/不良": "—",                  "説明": "信号+干渉+ノイズの合計受信電力"},
]), use_container_width=True, hide_index=True)

# ── RSRP 品質ゾーン ───────────────────────────────────────────────
st.subheader("② RSRP 品質ゾーン")
col1, col2 = st.columns([1,1])

with col1:
    np.random.seed(7)
    rsrp_vals = np.random.normal(-85, 15, 1000)
    fig1 = go.Figure(go.Histogram(
        x=rsrp_vals, nbinsx=40,
        marker=dict(
            color=rsrp_vals,
            colorscale=[[0,"#C92A2A"],[0.35,"#E67700"],[0.65,"#FAB005"],[1,"#2F9E44"]],
            cmin=-120, cmax=-60,
        ),
    ))
    fig1.add_vline(x=-80,  line_dash="dash", line_color="#2F9E44", annotation_text="良好閾値 -80dBm")
    fig1.add_vline(x=-100, line_dash="dash", line_color="#C92A2A", annotation_text="不良閾値 -100dBm")
    fig1.update_layout(title="RSRP 分布（シミュレーション）",
                       xaxis_title="RSRP (dBm)", yaxis_title="頻度",
                       plot_bgcolor="white", height=350)
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.markdown("""
    | RSRP | 品質 | ユーザー体験 |
    |---|---|---|
    | > -80 dBm | 🟢 優良 | 4K動画・高速通信 |
    | -80〜-90  | 🟡 良好 | HD動画・通常ブラウジング |
    | -90〜-100 | 🟠 普通 | SD動画・若干遅延 |
    | -100〜-110| 🔴 不良 | 通信不安定・切断リスク |
    | < -110    | ⛔ 圏外寸前 | ほぼ接続不可 |

    **なぜ dBm（デシベルミリワット）？**

    電波強度は 10⁻¹²W〜10⁻³W の超広いレンジのため対数スケールで表現。
    - **+3dB** = 電力が約**2倍**
    - **+10dB** = 電力が**10倍**
    """)

# ── パスロスモデル ────────────────────────────────────────────────
st.subheader("③ 電波の減衰（パスロス）— 周波数別比較")
st.markdown("電波は距離が離れるにつれて弱まります。これを **パスロス（Path Loss）** といいます。")

distances = np.logspace(1, np.log10(20000), 200)

def fspl(d_m, f_mhz):
    return 20*np.log10(d_m) + 20*np.log10(f_mhz) + 20*np.log10(4*np.pi/3e8*1e6)

fig2 = go.Figure()
for f, name, color in [
    (700,   "700MHz  (Band26)",    "#1971C2"),
    (2100,  "2.1GHz  (Band1)",    "#2F9E44"),
    (3500,  "3.5GHz  (n78)",      "#E67700"),
    (28000, "28GHz   (n257 ミリ波)","#C92A2A"),
]:
    fig2.add_trace(go.Scatter(x=distances/1000, y=fspl(distances, f),
                               name=name, line=dict(color=color, width=2.5)))

fig2.update_layout(
    title="周波数帯別 自由空間パスロス（同じ距離でも高い周波数ほど減衰が大きい）",
    xaxis=dict(title="距離 (km)", type="log"),
    yaxis=dict(title="パスロス (dB)", range=[60,140]),
    plot_bgcolor="white", height=400,
    legend=dict(x=0.01, y=0.99),
)
st.plotly_chart(fig2, use_container_width=True)

st.info("""💡 **DS活用ポイント**
- RSRP・SINR は通信品質予測モデルの重要な特徴量
- 「RSRP が高いのに遅い」→ 干渉（SINR が低い）が疑われる。RSRP と SINR を両方確認する
- 地図上の RSRP ヒートマップ → カバレッジホール特定・基地局増設判断に活用""")
