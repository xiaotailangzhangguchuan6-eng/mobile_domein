import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="ハンドオーバーの仕組み", page_icon="🔄", layout="wide")
np.random.seed(42)

st.title("🔄 ハンドオーバー（Handover）の仕組み")
st.markdown("**ハンドオーバー（HO）** は、移動中の端末が接続する基地局を切り替える仕組みです。新幹線でも通話・通信が維持されるのはこの技術のおかげです。")

# ── A3イベント ────────────────────────────────────────────────────
st.subheader("① ハンドオーバーのトリガー条件（A3イベント）")
st.markdown("""
LTE/5Gでは、端末が以下の条件を検出したとき基地局に報告し、HOが開始されます。

**A3イベント（最も一般的）**

> **隣接セルの RSRP** ＞ **サービングセルの RSRP** ＋ **オフセット（例: 3dB）**
> この状態が **TTT（Time-to-Trigger）時間（例: 160ms）** 継続したとき

```
隣接セル RSRP > サービングセル RSRP + Offset
└─ TTT (例: 160ms) 持続
    └─ 端末が Measurement Report を送信
        └─ eNB/gNB が Handover Decision
            └─ HO 実行（ターゲットセルへ切替）
```
""")

# ── RSRP 推移グラフ ───────────────────────────────────────────────
st.subheader("② ハンドオーバー時の RSRP 推移")

t = np.linspace(0, 100, 500)
rsrp_a = -75 - 0.3*t + 5*np.sin(0.1*t) + np.random.normal(0, 1, 500)
rsrp_b = -110 + 0.4*t + 5*np.sin(0.1*t+1) + np.random.normal(0, 1, 500)
ho_idx  = int(np.argmax(rsrp_b > rsrp_a + 3))

fig = go.Figure()
fig.add_trace(go.Scatter(x=t, y=rsrp_a, name="サービングセル Cell A",
                          line=dict(color="#228BE6", width=2.5)))
fig.add_trace(go.Scatter(x=t, y=rsrp_b, name="隣接セル Cell B",
                          line=dict(color="#E67700", width=2.5)))
if ho_idx > 0:
    fig.add_vline(x=t[ho_idx], line_dash="dash", line_color="red",
                  annotation_text=f"HO実行点 (t={t[ho_idx]:.0f}s)")
    fig.add_annotation(x=t[ho_idx], y=-78,
                       text="← Cell A 接続  |  Cell B 接続 →",
                       showarrow=False, font=dict(size=11))
fig.add_hline(y=-100, line_dash="dot", line_color="gray",
              annotation_text="不良閾値 -100dBm")
fig.update_layout(title="移動中のRSRP推移（Cell AからCell Bへ切替）",
                  xaxis_title="時間 / 移動距離 (s)",
                  yaxis_title="RSRP (dBm)",
                  plot_bgcolor="white", height=420,
                  legend=dict(x=0.01, y=0.01))
st.plotly_chart(fig, use_container_width=True)

# ── HO 種別 ──────────────────────────────────────────────────────
st.subheader("③ ハンドオーバーの種類")
st.dataframe(pd.DataFrame([
    {"種別": "イントラ周波数 HO",  "説明": "同じ周波数帯のセル間で切替",              "特徴": "最速・中断時間が最短",       "主な用途": "通常移動"},
    {"種別": "インター周波数 HO",  "説明": "異なる周波数帯へ切替（例: n78→Band26）", "特徴": "測定ギャップ必要・やや遅い",  "主な用途": "カバレッジ維持"},
    {"種別": "インターRAT HO",     "説明": "異なる無線方式へ切替（例: 5G→4G）",      "特徴": "最も遅い（異システム間）",    "主な用途": "フォールバック"},
    {"種別": "X2ベース HO",        "説明": "基地局同士がX2 IFで直接調整",            "特徴": "コア経由なし・高速",          "主な用途": "LTE標準的HO"},
    {"種別": "S1ベース HO",        "説明": "コアネットワーク（MME）経由で調整",       "特徴": "X2がない場合に使用",          "主な用途": "異ベンダー間HO"},
    {"種別": "DAPS HO",            "説明": "切替中も両セルの接続を維持",             "特徴": "中断時間ほぼゼロ（5G新機能）", "主な用途": "高速移動・V2X"},
]), use_container_width=True, hide_index=True)

# ── HOF の影響 ────────────────────────────────────────────────────
st.subheader("④ ハンドオーバー失敗（HOF）の影響")
col1, col2 = st.columns(2)
with col1:
    st.markdown("""
    ```
    HOF（Handover Failure）発生
    ├─ RLF（Radio Link Failure）検出
    │   └─ 端末が接続を失う（通話断・切断）
    ├─ RRC 再接続手順
    │   ├─ 成功: ユーザーに瞬断（数秒）として体験
    │   └─ 失敗: 圏外が継続
    └─ ネットワーク側の記録
        └─ HOF率 KPI として管理（目標: <0.5%）
    ```
    """)
with col2:
    st.dataframe(pd.DataFrame({
        "KPI":    ["HO成功率", "HOF率",    "HO回数/端末/時", "RLF率"],
        "目標値": [">99.5%",  "<0.5%",    "設計依存",       "<0.1%"],
        "DS活用": ["品質監視", "原因分析", "パラメータ最適化","障害予兆検知"],
    }), use_container_width=True, hide_index=True)

st.info("""💡 **DS活用ポイント**
- HOFが多い基地局ペア → ハンドオーバーパラメータ（Offset・TTT）の最適化候補
- HO成功率の時系列急落 → ネットワーク障害の予兆として使える
- 新幹線沿線など高速移動エリアはHO頻度が特に高く、専用チューニングが必要""")
