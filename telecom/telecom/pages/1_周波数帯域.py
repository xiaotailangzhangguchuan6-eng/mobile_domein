import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="周波数帯域の特徴", page_icon="🔢", layout="wide")
st.title("🔢 周波数帯域（バンド）の特徴")
st.markdown("スマートフォンが電波を使うとき、**周波数帯（バンド）によって特性が大きく異なります**。「低い周波数 = 遠くまで届くが遅い」「高い周波数 = 速いが遠くへ届かない」が基本原則です。")

bands_df = pd.DataFrame([
    {"バンド名": "700MHz帯 (Band28)", "周波数_MHz": 700,   "カバレッジ_km": 10,  "最大速度_Mbps": 75,    "建屋内浸透": 95, "用途": "プラチナバンド・広域カバー"},
    {"バンド名": "900MHz帯 (Band8)",  "周波数_MHz": 900,   "カバレッジ_km": 8,   "最大速度_Mbps": 75,    "建屋内浸透": 90, "用途": "農村・地下"},
    {"バンド名": "1.7GHz帯 (Band3)", "周波数_MHz": 1700,  "カバレッジ_km": 4,   "最大速度_Mbps": 150,   "建屋内浸透": 75, "用途": "都市部メイン"},
    {"バンド名": "2.1GHz帯 (Band1)", "周波数_MHz": 2100,  "カバレッジ_km": 3,   "最大速度_Mbps": 300,   "建屋内浸透": 65, "用途": "都市部容量"},
    {"バンド名": "3.5GHz帯 (n78)",   "周波数_MHz": 3500,  "カバレッジ_km": 1.5, "最大速度_Mbps": 2000,  "建屋内浸透": 40, "用途": "5G Sub-6 主力"},
    {"バンド名": "4.0GHz帯 (n77)",   "周波数_MHz": 4000,  "カバレッジ_km": 1.2, "最大速度_Mbps": 2400,  "建屋内浸透": 35, "用途": "5G Sub-6 KDDI"},
    {"バンド名": "28GHz帯 (n257)",   "周波数_MHz": 28000, "カバレッジ_km": 0.2, "最大速度_Mbps": 20000, "建屋内浸透": 5,  "用途": "5G ミリ波"},
])
colors = ["#1971C2","#1C7ED6","#2F9E44","#40C057","#E67700","#FD7E14","#C92A2A"]

# ── 図1: 特性マップ ──────────────────────────────────────────────
st.subheader("① 周波数 vs カバレッジ（バブルサイズ = 最大速度）")
fig1 = go.Figure()
for i, row in bands_df.iterrows():
    fig1.add_trace(go.Scatter(
        x=[row["周波数_MHz"]], y=[row["カバレッジ_km"]],
        mode="markers+text",
        marker=dict(size=row["最大速度_Mbps"]**0.35, color=colors[i], opacity=0.85,
                    line=dict(color="white", width=2)),
        text=[row["バンド名"]], textposition="top center",
        name=row["バンド名"],
        hovertemplate=(f"<b>{row['バンド名']}</b><br>周波数: {row['周波数_MHz']}MHz<br>"
                       f"カバレッジ: {row['カバレッジ_km']}km<br>最大速度: {row['最大速度_Mbps']}Mbps<br>"
                       f"建屋内浸透: {row['建屋内浸透']}%<extra></extra>"),
    ))
fig1.update_xaxes(type="log", title="周波数 (MHz) — 対数スケール")
fig1.update_yaxes(title="カバレッジ半径 (km)")
fig1.update_layout(plot_bgcolor="white", height=430, showlegend=False,
                   annotations=[
                       dict(x=np.log10(700), y=10.8, text="← 低周波数: 広域・低速",
                            showarrow=False, font=dict(color="#1971C2", size=12)),
                       dict(x=np.log10(28000), y=0.6, text="高周波数: 狭域・超高速 →",
                            showarrow=False, font=dict(color="#C92A2A", size=12)),
                   ])
st.plotly_chart(fig1, use_container_width=True)

# ── 図2: 建屋内浸透率 ────────────────────────────────────────────
st.subheader("② 建屋内浸透率（地下・屋内での受信しやすさ）")
fig2 = go.Figure(go.Bar(
    x=bands_df["バンド名"], y=bands_df["建屋内浸透"],
    marker_color=colors,
    text=bands_df["建屋内浸透"].apply(lambda v: f"{v}%"), textposition="outside",
))
fig2.add_hline(y=70, line_dash="dash", line_color="gray", annotation_text="実用閾値 70%")
fig2.update_layout(yaxis=dict(title="浸透率 (%)", range=[0, 110]),
                   xaxis_title="バンド", plot_bgcolor="white", height=360)
st.plotly_chart(fig2, use_container_width=True)

# ── KDDI 保有バンド ───────────────────────────────────────────────
st.subheader("③ KDDIが保有する主な周波数帯")
st.dataframe(pd.DataFrame([
    {"世代": "4G LTE", "バンド": "Band26 (800MHz)",  "帯域幅": "15MHz",  "役割": "プラチナバンド。全国カバー・地下鉄・建屋内"},
    {"世代": "4G LTE", "バンド": "Band11 (1.5GHz)", "帯域幅": "20MHz",  "役割": "都市部の補完カバー"},
    {"世代": "4G LTE", "バンド": "Band1 (2.1GHz)",  "帯域幅": "20MHz",  "役割": "都市部メイン容量"},
    {"世代": "4G LTE", "バンド": "Band3 (1.7GHz)",  "帯域幅": "20MHz",  "役割": "都市部補完"},
    {"世代": "5G NR",  "バンド": "n77 (3.7GHz)",    "帯域幅": "100MHz", "役割": "5G Sub-6 主力帯域"},
    {"世代": "5G NR",  "バンド": "n77 (4.0GHz)",    "帯域幅": "100MHz", "役割": "5G Sub-6（UQコミュニケーションズ）"},
    {"世代": "5G NR",  "バンド": "n257 (28GHz)",    "帯域幅": "400MHz", "役割": "5G ミリ波。超高速・超大容量（ホットスポット）"},
]), use_container_width=True, hide_index=True)

st.info("""💡 **DS活用ポイント**
- 基地局データの `band` カラム: 低周波数 ≒ 広域カバー用、高周波数 ≒ 容量補完用
- エリア品質分析では「バンド × 時間帯 × PRB使用率」のクロス集計が基本
- ミリ波(28GHz)は接続時間が極端に短く外れ値扱いになりやすいので注意""")
