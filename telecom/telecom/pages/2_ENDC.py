import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="ENDCとは", page_icon="🔗", layout="wide")
st.title("🔗 ENDC とは（E-UTRA NR Dual Connectivity）")
st.markdown("**ENDC** は **4G LTE と 5G NR を同時に使う技術**です。5Gサービス初期（NSA構成）では、4Gの制御機能を使いながら5GのデータチャネルをプラスするためにENDCが使われます。")

# ── 図1: アーキテクチャ図 ────────────────────────────────────────
st.subheader("① ENDCの構成図（NSA Option 3x）")

fig = go.Figure()

# ノード描画
boxes = [
    (0.3, 0.72, 0.7, 0.92, "#D0EBFF", "#228BE6", "📱 UE（スマートフォン）\nLTE + NR 同時接続", 0.5, 0.82),
    (0.0, 0.32, 0.42, 0.58, "#D3F9D8", "#2F9E44", "🗼 eNB（4G LTE基地局）\nMaster Node\n制御プレーン担当",   0.21, 0.45),
    (0.58, 0.32, 1.0, 0.58, "#FFF3BF", "#E67700", "📡 gNB（5G NR基地局）\nSecondary Node\nデータプレーン担当", 0.79, 0.45),
    (0.08, 0.02, 0.52, 0.22, "#FFE3E3", "#C92A2A", "☁️ EPC（4Gコアネットワーク）\nMME / SGW / PGW",       0.30, 0.12),
]
for x0,y0,x1,y1,fc,lc,label,tx,ty in boxes:
    fig.add_shape(type="rect", x0=x0,y0=y0,x1=x1,y1=y1,
                  fillcolor=fc, line=dict(color=lc, width=2.5))
    fig.add_annotation(x=tx, y=ty, text=label.replace("\n","<br>"),
                       showarrow=False, font=dict(size=11))

fig.add_annotation(x=0.75, y=0.12, text="🌐 インターネット", showarrow=False, font=dict(size=13))

# 矢印
arrows = [
    # UE ↔ eNB (LTE)
    (0.38,0.72, 0.22,0.58, "#2F9E44"),
    (0.22,0.58, 0.38,0.72, "#2F9E44"),
    # UE ↔ gNB (NR)
    (0.62,0.72, 0.78,0.58, "#E67700"),
    (0.78,0.58, 0.62,0.72, "#E67700"),
    # eNB ↔ gNB (X2)
    (0.42,0.45, 0.58,0.45, "#888"),
    (0.58,0.45, 0.42,0.45, "#888"),
    # eNB → EPC
    (0.22,0.32, 0.26,0.22, "#C92A2A"),
    # gNB → Internet
    (0.79,0.32, 0.79,0.22, "#E67700"),
]
for x,y,ax,ay,col in arrows:
    fig.add_annotation(x=x,y=y,ax=ax,ay=ay,xref="x",yref="y",axref="x",ayref="y",
                       arrowhead=3,arrowcolor=col,arrowwidth=2.5,text="",showarrow=True)

# ラベル
fig.add_annotation(x=0.29,y=0.65, text="<b>LTE</b> 制御+データ", showarrow=False,
                   font=dict(size=10,color="#2F9E44"))
fig.add_annotation(x=0.72,y=0.65, text="<b>NR</b> データのみ", showarrow=False,
                   font=dict(size=10,color="#E67700"))
fig.add_annotation(x=0.50,y=0.49, text="X2/Xn IF", showarrow=False,
                   font=dict(size=9,color="#888"))
fig.add_annotation(x=0.20,y=0.27, text="S1インターフェース", showarrow=False,
                   font=dict(size=9,color="#C92A2A"))
fig.add_annotation(x=0.84,y=0.27, text="Uプレーン", showarrow=False,
                   font=dict(size=9,color="#E67700"))

fig.update_layout(
    xaxis=dict(visible=False, range=[-0.02,1.02]),
    yaxis=dict(visible=False, range=[-0.02,1.0]),
    plot_bgcolor="white", height=470,
    margin=dict(l=5,r=5,t=10,b=5),
)
st.plotly_chart(fig, use_container_width=True)

# ── NSA Option 種類 ──────────────────────────────────────────────
st.subheader("② NSA Option の種類")
col1, col2 = st.columns(2)
with col1:
    st.dataframe(pd.DataFrame([
        {"Option": "Option 3",    "MN": "eNB(4G)", "SN": "en-gNB(5G)", "コア": "EPC", "特徴": "5GデータがeNB経由でコアへ"},
        {"Option": "Option 3a",   "MN": "eNB(4G)", "SN": "en-gNB(5G)", "コア": "EPC", "特徴": "5GデータがUEから直接コアへ"},
        {"Option": "Option 3x ★", "MN": "eNB(4G)", "SN": "en-gNB(5G)", "コア": "EPC", "特徴": "gNBがデータをスプリット（最多）"},
        {"Option": "Option 7x",   "MN": "ng-eNB",  "SN": "gNB(5G)",    "コア": "5GC", "特徴": "5GコアにLTEアンカー"},
    ]), use_container_width=True, hide_index=True)
with col2:
    st.markdown("""
    **ENDCの動作フロー（Option 3x）**
    ```
    1. UEが4G eNBに接続（通常のLTE）
    2. ネットワークがENDC対応と判断
       └ 5G信号強度・端末能力を確認
    3. eNBがgNBをSNとして追加
       └ RRC Reconfiguration でUEに通知
    4. UEが4G+5Gを同時受信開始
       └ DLスループットが大幅向上
    5. 5G電波が弱まると SN Release
       └ 4Gのみに戻る
    ```
    """)

# ── SA vs NSA ────────────────────────────────────────────────────
st.subheader("③ SA（スタンドアローン）vs NSA（ノンスタンドアローン）")
col3, col4 = st.columns(2)
with col3:
    st.markdown("""
    **NSA — ENDCを使う現行構成**
    - 4Gコア（EPC）を流用
    - eNBが制御の主体（Master Node）
    - ✅ 展開コスト低・既存4G網を活用
    - ❌ 真の5G超低遅延（1ms）は非対応
    - ❌ ネットワークスライシング非対応
    """)
with col4:
    st.markdown("""
    **SA — 純粋な5G**
    - 5Gコア（5GC）を新規構築
    - gNBだけで制御+データ
    - ✅ 超低遅延・スライシング実現
    - ✅ V2X・遠隔手術など高度用途に対応
    - ❌ 5GCへの大規模投資が必要
    """)

# ── スループット比較 ─────────────────────────────────────────────
st.subheader("④ 接続方式別 最大スループット比較")
fig2 = go.Figure()
cats = ["LTEのみ\n(4G単独)", "ENDC\n(4G+5G Sub-6)", "5G SA\n(Sub-6)", "5G SA\n(ミリ波)"]
fig2.add_trace(go.Bar(name="下り(DL)", x=cats, y=[150, 1500, 2000, 20000], marker_color="#228BE6"))
fig2.add_trace(go.Bar(name="上り(UL)", x=cats, y=[50,  150,  400,  2000],  marker_color="#74C0FC"))
fig2.update_layout(barmode="group", yaxis=dict(title="速度 (Mbps)", type="log"),
                   plot_bgcolor="white", height=380)
st.plotly_chart(fig2, use_container_width=True)

st.info("""💡 **DS活用ポイント**
- ログに `rat_type=ENDC` や `dc_mode` フラグがあればENDCセッションを識別できる
- ENDCセッションはLTEより DL スループットが高い → セグメント分析で別扱いが必要
- 5G基地局カバレッジ境界付近でのENDC→LTE切り替え（SN Release）頻発は品質劣化の原因""")
