import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime, timezone
import time
import re

st.set_page_config(page_title="通信ニュース", page_icon="📰", layout="wide")

# ── DS業務関連キーワード定義 ────────────────────────────────────────
DS_KEYWORD_MAP = {
    "🤖 AI・機械学習": {
        "keywords": ["AI", "人工知能", "機械学習", "深層学習", "LLM", "生成AI", "ChatGPT",
                     "ニューラル", "予測モデル", "アルゴリズム"],
        "color": "#228BE6",
    },
    "📡 5G・ネットワーク技術": {
        "keywords": ["5G", "6G", "ENDC", "NSA", "SA", "ミリ波", "Sub-6", "NR", "LTE",
                     "基地局", "スモールセル", "O-RAN", "vRAN", "Open RAN", "コアネットワーク",
                     "ネットワークスライシング", "MEC", "エッジコンピューティング"],
        "color": "#2F9E44",
    },
    "📊 データ・分析": {
        "keywords": ["データ分析", "ビッグデータ", "データドリブン", "ダッシュボード",
                     "KPI", "品質改善", "ネットワーク品質", "最適化", "自動化",
                     "アナリティクス", "インサイト", "可視化"],
        "color": "#E67700",
    },
    "📱 端末・サービス": {
        "keywords": ["スマートフォン", "iPhone", "Android", "5Gスマホ", "eSIM",
                     "au", "KDDI", "UQ", "povo", "サブブランド", "MNP", "格安SIM"],
        "color": "#C92A2A",
    },
    "🌐 IoT・DX": {
        "keywords": ["IoT", "DX", "デジタル変革", "スマートシティ", "コネクテッド",
                     "自動運転", "V2X", "遠隔", "ローカル5G", "産業用", "工場"],
        "color": "#6741D9",
    },
    "💼 ビジネス・業界動向": {
        "keywords": ["ARPU", "チャーン", "加入者", "契約数", "MNP", "業績", "決算",
                     "料金プラン", "競合", "ドコモ", "ソフトバンク", "楽天モバイル",
                     "総務省", "電気通信", "認可", "規制"],
        "color": "#0C8599",
    },
}

# DS業務適用スコアリング
DS_HIGH_RELEVANCE = [
    "AI", "機械学習", "データ分析", "ビッグデータ", "KPI", "品質改善",
    "ネットワーク品質", "最適化", "自動化", "ENDC", "5G", "O-RAN",
    "MEC", "エッジ", "スライシング", "チャーン", "ARPU", "ローカル5G",
    "予測", "異常検知", "IoT",
]

# ── RSSフィード一覧 ──────────────────────────────────────────────
FEEDS = [
    ("ITmedia Mobile",    "https://rss.itmedia.co.jp/rss/2.0/mobile.xml"),
    ("ケータイWatch",      "https://k-tai.watch.impress.co.jp/data/rss/1.0/ktw/feed.rdf"),
    ("ITmedia News",      "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml"),
    ("Impress Watch",     "https://www.watch.impress.co.jp/data/rss/1.0/iw/feed.rdf"),
]

# ── ユーティリティ関数 ───────────────────────────────────────────
def classify_article(title: str, summary: str) -> tuple[list[str], int]:
    """カテゴリ分類とDSスコアを返す"""
    text = (title + " " + summary).upper()
    text_ja = title + " " + summary

    matched_categories = []
    ds_score = 0

    for cat, meta in DS_KEYWORD_MAP.items():
        for kw in meta["keywords"]:
            if kw.upper() in text or kw in text_ja:
                if cat not in matched_categories:
                    matched_categories.append(cat)
                if kw in DS_HIGH_RELEVANCE or kw.upper() in [k.upper() for k in DS_HIGH_RELEVANCE]:
                    ds_score += 2
                else:
                    ds_score += 1
                break

    return matched_categories, min(ds_score, 10)

def parse_date(entry) -> datetime:
    for attr in ["published_parsed", "updated_parsed"]:
        t = getattr(entry, attr, None)
        if t:
            try:
                return datetime(*t[:6], tzinfo=timezone.utc)
            except Exception:
                pass
    return datetime(2000, 1, 1, tzinfo=timezone.utc)

def clean_html(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text or "")
    return text[:200].strip()

@st.cache_data(ttl=1800)  # 30分キャッシュ
def fetch_all_news(selected_feeds: tuple) -> pd.DataFrame:
    articles = []
    for name, url in FEEDS:
        if name not in selected_feeds:
            continue
        try:
            d = feedparser.parse(url)
            for entry in d.entries:
                title   = entry.get("title", "")
                summary = clean_html(entry.get("summary", entry.get("description", "")))
                link    = entry.get("link", "")
                pub     = parse_date(entry)
                cats, score = classify_article(title, summary)
                articles.append({
                    "ソース":        name,
                    "タイトル":      title,
                    "概要":          summary,
                    "URL":           link,
                    "公開日時":      pub,
                    "カテゴリ":      cats,
                    "DS関連度スコア": score,
                })
        except Exception as e:
            st.warning(f"{name} の取得に失敗: {e}")

    df = pd.DataFrame(articles)
    if not df.empty:
        df = df.sort_values("公開日時", ascending=False).reset_index(drop=True)
    return df

# ── UI ──────────────────────────────────────────────────────────
st.title("📰 通信ニュース — DS業務への自動適用フィルター")
st.caption("RSSで最新通信ニュースを自動取得し、データサイエンス業務への関連度で分類します")

# サイドバー設定
with st.sidebar:
    st.header("⚙️ フィルター設定")

    selected_feeds = st.multiselect(
        "ニュースソース",
        options=[name for name, _ in FEEDS],
        default=[name for name, _ in FEEDS],
    )

    st.markdown("---")
    min_score = st.slider("DS関連度スコア（最低値）", 0, 10, 0,
                           help="スコアが高いほど DS業務（AI・品質分析・KPI等）への関連度が高い")

    selected_cats = st.multiselect(
        "カテゴリフィルター",
        options=list(DS_KEYWORD_MAP.keys()),
        default=[],
        help="空欄 = 全カテゴリ表示",
    )

    st.markdown("---")
    keyword_filter = st.text_input("🔍 キーワード検索", placeholder="例: ENDC, 5G品質...")

    st.markdown("---")
    if st.button("🔄 ニュースを今すぐ更新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

    st.caption("※ キャッシュは30分ごとに自動更新")

# ニュース取得
with st.spinner("ニュース取得中..."):
    df = fetch_all_news(tuple(selected_feeds))

if df.empty:
    st.error("ニュースを取得できませんでした。ネットワーク接続を確認してください。")
    st.stop()

# フィルター適用
df_filtered = df.copy()

if min_score > 0:
    df_filtered = df_filtered[df_filtered["DS関連度スコア"] >= min_score]

if selected_cats:
    df_filtered = df_filtered[
        df_filtered["カテゴリ"].apply(lambda cats: any(c in cats for c in selected_cats))
    ]

if keyword_filter.strip():
    kw = keyword_filter.strip().lower()
    df_filtered = df_filtered[
        df_filtered["タイトル"].str.lower().str.contains(kw, na=False) |
        df_filtered["概要"].str.lower().str.contains(kw, na=False)
    ]

# ── サマリーメトリクス ─────────────────────────────────────────
st.markdown("---")
c1, c2, c3, c4 = st.columns(4)
c1.metric("総記事数", f"{len(df)} 件")
c2.metric("表示中", f"{len(df_filtered)} 件")
high_rel = (df["DS関連度スコア"] >= 3).sum()
c3.metric("DS高関連記事", f"{high_rel} 件", help="スコア3以上")
latest = df["公開日時"].max()
c4.metric("最新記事", latest.strftime("%m/%d %H:%M") if latest.year > 2000 else "—")
st.markdown("---")

# ── タブ表示 ─────────────────────────────────────────────────
tab_all, tab_ds, tab_cat = st.tabs(["📋 全記事", "⭐ DS高関連ピックアップ", "📂 カテゴリ別"])

# ── 記事カード描画関数 ──────────────────────────────────────────
def render_card(row, show_score=True):
    cats = row["カテゴリ"]
    score = row["DS関連度スコア"]
    pub = row["公開日時"]
    pub_str = pub.strftime("%m/%d %H:%M") if pub.year > 2000 else "—"

    # スコアバー
    bar_filled = "🟦" * score + "⬜" * (10 - score)

    # カテゴリバッジ
    cat_badges = " ".join([
        f"`{c}`" for c in cats
    ]) if cats else "`未分類`"

    # DS適用コメント自動生成
    ds_hint = ""
    if score >= 5:
        hints = []
        title_lower = row["タイトル"].lower() + row["概要"].lower()
        if any(k in title_lower for k in ["ai", "機械学習", "予測", "モデル"]):
            hints.append("ML/AI モデル開発の参考になる可能性")
        if any(k in title_lower for k in ["品質", "kpi", "kqi", "rsrp", "sinr"]):
            hints.append("ネットワーク品質分析・KPI設計への応用可")
        if any(k in title_lower for k in ["チャーン", "arpu", "加入者", "契約"]):
            hints.append("チャーン予測・顧客分析への応用可")
        if any(k in title_lower for k in ["5g", "endc", "oran", "o-ran"]):
            hints.append("5G ネットワークデータ分析の背景知識として有用")
        if any(k in title_lower for k in ["iot", "ローカル5g", "工場", "dx"]):
            hints.append("IoT データ活用・DX案件の参考事例")
        ds_hint = " / ".join(hints) if hints else "DS業務に関連する可能性あり"

    with st.container(border=True):
        col_main, col_meta = st.columns([5, 1])
        with col_main:
            st.markdown(f"### [{row['タイトル']}]({row['URL']})")
            st.markdown(f"{row['概要']}..." if len(row['概要']) > 10 else "")
            st.markdown(cat_badges)
            if ds_hint:
                st.success(f"💡 **DS適用ヒント**: {ds_hint}")
        with col_meta:
            st.markdown(f"**{row['ソース']}**")
            st.markdown(f"🕐 {pub_str}")
            if show_score:
                st.markdown(f"DS関連度: {score}/10")
                st.markdown(bar_filled)

# ── Tab1: 全記事 ─────────────────────────────────────────────────
with tab_all:
    st.subheader(f"全記事一覧（{len(df_filtered)}件）")
    if df_filtered.empty:
        st.info("条件に一致する記事がありません。フィルターを調整してください。")
    else:
        for _, row in df_filtered.head(30).iterrows():
            render_card(row)

# ── Tab2: DS高関連ピックアップ ────────────────────────────────────
with tab_ds:
    st.subheader("⭐ DS業務への適用可能性が高い記事")
    st.caption("DS関連度スコア 3以上の記事を自動ピックアップ")

    ds_articles = df[df["DS関連度スコア"] >= 3].head(20)
    if ds_articles.empty:
        st.info("現在、DS関連度の高い記事は取得できていません。")
    else:
        # スコア上位をハイライト
        top_articles = ds_articles.nlargest(5, "DS関連度スコア")
        st.markdown("#### 🏆 特に注目の記事（スコアTop5）")
        for _, row in top_articles.iterrows():
            render_card(row)

        remaining = ds_articles[~ds_articles["URL"].isin(top_articles["URL"])]
        if not remaining.empty:
            st.markdown("---")
            st.markdown("#### その他のDS関連記事")
            for _, row in remaining.iterrows():
                render_card(row)

# ── Tab3: カテゴリ別 ─────────────────────────────────────────────
with tab_cat:
    st.subheader("📂 カテゴリ別ニュース")

    for cat, meta in DS_KEYWORD_MAP.items():
        cat_articles = df[df["カテゴリ"].apply(lambda cats: cat in cats)]
        if cat_articles.empty:
            continue

        with st.expander(f"{cat} — {len(cat_articles)}件", expanded=False):
            for _, row in cat_articles.head(10).iterrows():
                render_card(row, show_score=False)

# ── フッター ─────────────────────────────────────────────────────
st.markdown("---")
st.caption(
    "データソース: ITmedia Mobile / ケータイWatch / ITmedia News / Impress Watch (RSS) | "
    "キャッシュ: 30分 | 自動更新ボタンで即時取得可能"
)
