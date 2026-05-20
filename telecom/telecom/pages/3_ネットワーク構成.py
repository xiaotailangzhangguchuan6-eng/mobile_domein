import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="セルラーネットワーク構成", page_icon="🏗️", layout="wide")
st.title("🏗️ セルラーネットワークの構成")
st.markdown("モバイルネットワークは大きく **無線アクセス網（RAN）** と **コアネットワーク（Core）** に分かれます。")

# ── ネットワーク構成 ─────────────────────────────────────────────
st.subheader("① ネットワーク全体構成（4G LTE）")
st.markdown("""
```
┌─────────────────────────────────────────────────────────────────┐
│  RAN（無線アクセス網）                EPC（4Gコアネットワーク）  │
│                                                                  │
│  📱 UE ──[Uu無線]── 🗼 eNB ──[S1-MME]── MME（制御プレーン）     │
│  スマホ              4G基地局   │                               │
│                                └──[S1-U]── SGW ── PGW ──🌐 Net  │
│                                            ↑GW      ↑GW         │
│                                                                  │
│  複数のeNBは [X2インターフェース] で相互接続（ハンドオーバー等）  │
└─────────────────────────────────────────────────────────────────┘
```
""")

# ── ノード解説 ───────────────────────────────────────────────────
st.subheader("② 主要ノード解説")
st.dataframe(pd.DataFrame([
    {"ノード": "UE",  "正式名称": "User Equipment",               "役割": "スマートフォン・IoTデバイス等のエンドユーザー端末"},
    {"ノード": "eNB", "正式名称": "evolved Node B",               "役割": "4G LTE 基地局。無線リソース管理・スケジューリング"},
    {"ノード": "gNB", "正式名称": "next generation Node B",       "役割": "5G NR 基地局。5G無線アクセスを提供"},
    {"ノード": "MME", "正式名称": "Mobility Management Entity",   "役割": "4Gコアの制御装置。認証・位置管理・HO制御"},
    {"ノード": "SGW", "正式名称": "Serving Gateway",              "役割": "ユーザーデータを中継するゲートウェイ（RAN側）"},
    {"ノード": "PGW", "正式名称": "PDN Gateway",                  "役割": "インターネット接続GW。IPアドレス払い出し・課金"},
    {"ノード": "HSS", "正式名称": "Home Subscriber Server",       "役割": "加入者情報DB。認証鍵・プロファイル管理"},
    {"ノード": "AMF", "正式名称": "Access and Mobility Function", "役割": "5GCの制御機能（MMEに相当）"},
    {"ノード": "UPF", "正式名称": "User Plane Function",          "役割": "5GCのデータ転送機能（SGW+PGWに相当）"},
    {"ノード": "SMF", "正式名称": "Session Management Function",  "役割": "5GCのセッション管理。UPFを制御"},
]), use_container_width=True, hide_index=True)

# ── セルの種類 ───────────────────────────────────────────────────
st.subheader("③ セルの種類（カバレッジ階層）")
col1, col2 = st.columns([1, 1])
with col1:
    st.dataframe(pd.DataFrame({
        "種別":       ["マクロセル", "マイクロセル", "ピコセル",   "フェムトセル"],
        "半径":       ["1〜20km",   "200m〜1km",  "100〜200m", "10〜50m"],
        "出力":       ["数十〜数百W", "数W〜数十W", "〜1W",      "mW〜数百mW"],
        "設置場所":   ["山頂・鉄塔", "街路灯・ビル壁面", "駅・SC内", "室内（オフィス）"],
        "目的":       ["広域カバー", "都市部容量補完", "屋内HotSpot", "屋内深部カバー"],
    }), use_container_width=True, hide_index=True)

with col2:
    fig = go.Figure()
    cell_layers = [
        ("マクロセル",  12, "rgba(30,100,200,0.12)",  "#1E64C8"),
        ("マイクロセル", 5, "rgba(46,160,67,0.18)",   "#2EA043"),
        ("ピコセル",     2, "rgba(230,119,0,0.22)",   "#E67700"),
        ("フェムトセル", 0.8,"rgba(201,42,42,0.28)",  "#C92A2A"),
    ]
    theta = np.linspace(0, 2*np.pi, 120)
    for name, r, fill, line_col in cell_layers:
        fig.add_trace(go.Scatter(
            x=r*np.cos(theta), y=r*np.sin(theta),
            fill="toself", fillcolor=fill,
            line=dict(color=line_col, width=2), name=name,
            hovertemplate=f"<b>{name}</b><br>半径: {r}km<extra></extra>",
        ))
    fig.add_trace(go.Scatter(x=[0], y=[0], mode="markers",
                              marker=dict(size=14, color="black", symbol="triangle-up"),
                              name="基地局"))
    fig.update_layout(
        title="セル階層（同心円イメージ）",
        xaxis=dict(title="距離 (km)", range=[-14,14], scaleanchor="y"),
        yaxis=dict(title="距離 (km)", range=[-14,14]),
        plot_bgcolor="white", height=400,
    )
    st.plotly_chart(fig, use_container_width=True)

st.info("""💡 **DS活用ポイント**
- 基地局マスタに `cell_type`（マクロ/スモール）が含まれることが多い
- マクロセルとスモールセルは KPI 分布が大きく異なるため、モデルでは別々に扱うか特徴量にする
- フェムトセル（室内）は接続数が少なくデータが疎になりがち""")
