import streamlit as st

st.set_page_config(page_title="通信ドメイン基礎知識", page_icon="📡", layout="wide")

st.title("📡 通信ドメイン基礎知識")
st.caption("KDDIデータサイエンティスト向け — 図解で学ぶ通信の基本")
st.markdown("---")

col1, col2 = st.columns(2)
with col1:
    st.page_link("pages/1_周波数帯域.py",      label="🔢 周波数帯域（バンド）の特徴", icon="📶")
    st.page_link("pages/2_ENDC.py",            label="🔗 ENDC とは",               icon="🔗")
    st.page_link("pages/3_ネットワーク構成.py", label="🏗️ セルラーネットワーク構成",  icon="🏗️")
with col2:
    st.page_link("pages/4_電波品質指標.py",    label="📶 電波伝搬と品質指標",        icon="📶")
    st.page_link("pages/5_ハンドオーバー.py",  label="🔄 ハンドオーバーの仕組み",    icon="🔄")
    st.page_link("pages/6_通信ニュース.py",    label="📰 通信ニュース（DS関連フィルター）", icon="📰")

st.markdown("---")
st.info("左のサイドバーからもページを切り替えられます。")
