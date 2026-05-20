import streamlit as st
import feedparser
import pandas as pd
from datetime import datetime, timezone
import re

st.set_page_config(page_title="通信ニュース × 業務インパクト", page_icon="📰", layout="wide")

# ══════════════════════════════════════════════════════════════════
# 業務インパクト分析ルール
# 「このニュースが来たら、KDDIのDSとして何を調査・対策すべきか」
# ══════════════════════════════════════════════════════════════════
BUSINESS_RULES = [
    {
        "name": "📷 カメラ付き新デバイス・ウェアラブル",
        "triggers": ["カメラ", "AirPods", "スマートグラス", "AR", "VR", "ヘッドセット",
                     "ウェアラブル", "メガネ型", "眼鏡型", "Meta Quest", "Vision Pro"],
        "meaning": "映像を常時送受信する新デバイスが普及すると、**アップリンク（UL）トラフィックが急増**する可能性があります。従来は動画ダウンロード（DL主体）だったトラフィック構造が変化します。",
        "impact_areas": ["UL/DLトラフィック比率の変化", "混雑エリアのPRB使用率上昇", "コアネットワークの上り帯域逼迫"],
        "actions": [
            ("📊 トラフィック予測", "新デバイスの普及曲線を推計し、エリア別のULトラフィック増加量をシミュレーション"),
            ("🔍 現状把握", "現行のULスループット・PRB使用率の余裕度をエリア別に把握"),
            ("📍 影響エリア特定", "都市部・駅周辺・オフィス街など新デバイス利用が集中しそうなエリアを事前特定"),
            ("📈 モデル更新", "トラフィック予測モデルに「新デバイス普及率」変数を追加"),
        ],
        "priority": "🔴 高",
        "color": "#FF6B6B",
    },
    {
        "name": "⏩ 動画の消費パターン変化（倍速・高画質・ショート動画）",
        "triggers": ["倍速", "2倍速", "4K", "8K", "ショート動画", "リール", "TikTok",
                     "YouTube", "Netflix", "動画配信", "ストリーミング", "高画質"],
        "meaning": "**倍速視聴はデータ量そのものは変わらないが、短時間に集中してスループットを消費**します。また4K/8K化はビットレートを大幅に増加させます。視聴パターンの変化がピーク時のネットワーク混雑に直結します。",
        "impact_areas": ["ピーク時間帯のスループット需要増加", "夜間帯（20〜23時）のPRB使用率上昇", "CDNキャッシュ効率の変化"],
        "actions": [
            ("📊 スループット分析", "倍速・高画質視聴が多いと想定されるエリア・時間帯を特定（PRB使用率×スループット分布）"),
            ("🔍 ビットレート調査", "現行のトラフィックデータから動画コンテンツのビットレート分布を調査"),
            ("📍 混雑エリア対策", "夜間帯に混雑しているセルを抽出し、容量増強・パラメータ最適化の優先順位付け"),
            ("📈 予測モデル更新", "トラフィック予測モデルに視聴パターン変数（倍速率・4K比率）を追加"),
        ],
        "priority": "🔴 高",
        "color": "#FF6B6B",
    },
    {
        "name": "🤖 AI・生成AIサービスの普及",
        "triggers": ["AI", "生成AI", "ChatGPT", "Gemini", "Claude", "LLM", "Copilot",
                     "AIエージェント", "画像生成", "音声AI", "AIアシスタント"],
        "meaning": "AI サービスの常時接続・大容量レスポンスにより、**モバイル回線のデータ通信量が増加**します。特に画像・動画生成AIはレスポンスサイズが大きく、レイテンシへの要求も高まります。",
        "impact_areas": ["AIレスポンス通信によるDLトラフィック増加", "低遅延要求の高まり", "ARPUへの影響（大容量プランへの移行促進）"],
        "actions": [
            ("📊 トラフィック分類", "AI関連トラフィックを特定プロトコル・ドメインで分類し、増加傾向を把握"),
            ("🔍 レイテンシ分析", "AI利用が多い時間帯のRTT・遅延分布を確認"),
            ("💡 ARPU分析", "大容量プラン移行率とAIサービス利用の相関を分析"),
            ("📈 需要予測", "AIデバイス普及率を組み込んだ中長期トラフィック予測モデルの更新"),
        ],
        "priority": "🟠 中〜高",
        "color": "#FFA94D",
    },
    {
        "name": "📱 競合他社の料金・サービス変更",
        "triggers": ["ドコモ", "NTT", "ソフトバンク", "楽天", "格安SIM", "MVNO",
                     "料金プラン", "値下げ", "MNP", "乗り換え", "キャンペーン", "新プラン"],
        "meaning": "競合の料金改定やキャンペーンは**MNP転出（チャーン）リスクを高めます**。特に価格感度の高いセグメントでの流出が起きやすくなります。",
        "impact_areas": ["MNP転出率の上昇リスク", "特定セグメント（若年層・低ARPUユーザー）の離脱", "ARPUへの下方圧力"],
        "actions": [
            ("⚠️ チャーンモニタリング", "競合発表後のMNP転出率・解約申請数をリアルタイムモニタリング"),
            ("🔍 リスクセグメント特定", "チャーン予測モデルで影響を受けやすいユーザーセグメントを事前抽出"),
            ("💡 リテンション施策", "リスクスコア上位ユーザーへのターゲット施策（特典付与等）の提案"),
            ("📊 競合分析", "各社の料金・特典を定量比較し、自社プランの競争力をスコアリング"),
        ],
        "priority": "🔴 高",
        "color": "#FF6B6B",
    },
    {
        "name": "🌐 IoT・スマートデバイス普及",
        "triggers": ["IoT", "スマートホーム", "コネクテッド", "センサー", "スマート農業",
                     "工場", "ローカル5G", "自動化", "遠隔", "M2M", "LPWA"],
        "meaning": "IoTデバイスの急増により**接続端末数が爆発的に増加**します。1台あたりのトラフィックは少なくても、mMTC（超多数接続）によってネットワークのシグナリング負荷が高まります。",
        "impact_areas": ["接続端末数の急増（コアへのシグナリング負荷）", "特定エリア（工場・農地）での集中接続", "ARPUへの影響（IoT専用プランの成長）"],
        "actions": [
            ("📊 接続数予測", "エリア別のIoT端末接続数増加予測と、シグナリング負荷シミュレーション"),
            ("🔍 トラフィック分類", "IoTトラフィックをMBBと分離して分析（パケットサイズ・接続頻度の分布確認）"),
            ("📍 エリア特定", "IoT導入が進んでいる工場地帯・農業地域でのネットワーク余裕度を確認"),
            ("💡 ビジネス提案", "ローカル5GやIoT専用SIM需要の高い企業へのアプローチ候補リスト作成"),
        ],
        "priority": "🟠 中〜高",
        "color": "#FFA94D",
    },
    {
        "name": "🚗 自動運転・V2X・モビリティ",
        "triggers": ["自動運転", "V2X", "車載", "コネクテッドカー", "EV", "電気自動車",
                     "ドローン", "モビリティ", "交通", "高速道路", "新幹線"],
        "meaning": "高速移動体との通信は**ハンドオーバー頻度の増加と超低遅延要求**をもたらします。自動運転は人命に関わるため、通信品質の要求水準が従来より格段に高くなります。",
        "impact_areas": ["高速移動時のHO成功率・RLF率", "低遅延（URLLC）の達成可否", "高速道路・鉄道沿線のカバレッジ品質"],
        "actions": [
            ("📊 HO分析", "高速移動エリア（高速道路・新幹線沿線）のハンドオーバー成功率・失敗率を分析"),
            ("🔍 遅延測定", "対象エリアのRTT・遅延分布を測定し、URLLC要件（1ms以下）との乖離を確認"),
            ("📍 カバレッジ調査", "自動運転導入が想定されるルートの電波品質（RSRP・SINR）をマッピング"),
            ("📈 投資計画", "必要な基地局増設・パラメータ最適化の優先エリアを定量化"),
        ],
        "priority": "🟡 中",
        "color": "#FFD43B",
    },
    {
        "name": "📡 5G・ネットワーク技術革新",
        "triggers": ["5G SA", "ネットワークスライシング", "O-RAN", "Open RAN", "vRAN",
                     "MEC", "エッジ", "6G", "衛星通信", "非地上系", "NTN"],
        "meaning": "新しいネットワーク技術の登場は**分析に使えるデータ・KPIの種類が変わる**ことを意味します。O-RANは多様なベンダーのデータが混在し、分析の複雑性が増します。",
        "impact_areas": ["新KPI・ログ形式への対応", "マルチベンダー環境での品質分析", "スライス別のトラフィック分析ニーズ"],
        "actions": [
            ("🔍 データ調査", "新技術導入後に取得できるログ・KPIの仕様を確認し、既存パイプラインへの影響を評価"),
            ("📊 KPI設計", "新技術に対応したKPI（スライス別品質スコア等）の定義と可視化ダッシュボード設計"),
            ("📈 分析基盤更新", "O-RAN/vRAN環境に対応した特徴量エンジニアリングの検討"),
            ("💡 先行調査", "業界論文・標準化動向（3GPP, O-RAN Alliance）をモニタリングし、DS観点で整理"),
        ],
        "priority": "🟡 中",
        "color": "#FFD43B",
    },
    {
        "name": "🏢 大型イベント・インフラ変化",
        "triggers": ["万博", "オリンピック", "コンサート", "スタジアム", "イベント",
                     "災害", "停電", "障害", "工事", "新駅", "再開発"],
        "meaning": "大型イベントや都市開発は**特定エリアへの一時的・恒久的なトラフィック集中**を引き起こします。事前に対策しないとサービス品質の急低下につながります。",
        "impact_areas": ["イベント会場周辺のPRB使用率急上昇", "一時的なユーザー集中による接続失敗", "新エリア開発に伴うカバレッジ拡張ニーズ"],
        "actions": [
            ("📊 過去事例分析", "類似イベント時の基地局ログを分析し、トラフィック増加倍率・パターンを把握"),
            ("📍 対象エリア特定", "イベント会場・周辺エリアの現行キャパシティ（PRB使用率・スループット）を確認"),
            ("🔧 事前対策", "臨時基地局（COW）の配備計画・パラメータ最適化の提案資料作成"),
            ("📈 当日モニタリング", "リアルタイムKPI監視ダッシュボードの準備"),
        ],
        "priority": "🟠 中〜高",
        "color": "#FFA94D",
    },
]

# ══════════════════════════════════════════════════════════════════
# DS関連度キーワード（スコアリング用）
# ══════════════════════════════════════════════════════════════════
DS_KEYWORDS = {
    "高スコア（+2）": ["AI", "機械学習", "5G", "ENDC", "品質", "チャーン", "KPI",
                      "最適化", "IoT", "MEC", "O-RAN", "予測", "異常検知", "トラフィック"],
    "中スコア（+1）": ["ネットワーク", "基地局", "スマートフォン", "KDDI", "au", "4G",
                      "データ", "通信", "サービス", "プラン", "MNP", "加入者"],
}

DS_KEYWORD_MAP = {
    "🤖 AI・機械学習": ["AI", "人工知能", "機械学習", "深層学習", "LLM", "生成AI", "予測モデル"],
    "📡 5G・ネットワーク": ["5G", "6G", "ENDC", "NSA", "NR", "LTE", "基地局", "O-RAN", "MEC"],
    "📊 データ・分析": ["データ分析", "ビッグデータ", "KPI", "品質", "最適化", "自動化", "アナリティクス"],
    "📱 端末・サービス": ["スマートフォン", "iPhone", "Android", "au", "KDDI", "UQ", "MNP"],
    "🌐 IoT・DX": ["IoT", "DX", "スマートシティ", "自動運転", "ローカル5G", "工場"],
    "💼 ビジネス・業界": ["ARPU", "チャーン", "加入者", "料金", "競合", "ドコモ", "ソフトバンク", "楽天"],
}

FEEDS = [
    ("ITmedia Mobile", "https://rss.itmedia.co.jp/rss/2.0/mobile.xml"),
    ("ケータイWatch",  "https://k-tai.watch.impress.co.jp/data/rss/1.0/ktw/feed.rdf"),
    ("ITmedia News",   "https://rss.itmedia.co.jp/rss/2.0/news_bursts.xml"),
    ("Impress Watch",  "https://www.watch.impress.co.jp/data/rss/1.0/iw/feed.rdf"),
]

# ══════════════════════════════════════════════════════════════════
# 関数
# ══════════════════════════════════════════════════════════════════
def match_business_rules(title: str, summary: str) -> list[dict]:
    """ニュースに合致する業務インパクトルールを返す"""
    text = title + " " + summary
    matched = []
    for rule in BUSINESS_RULES:
        if any(kw in text for kw in rule["triggers"]):
            matched.append(rule)
    return matched

def calc_ds_score(title: str, summary: str) -> int:
    text = title + " " + summary
    score = 0
    for kw in DS_KEYWORDS["高スコア（+2）"]:
        if kw in text:
            score += 2
    for kw in DS_KEYWORDS["中スコア（+1）"]:
        if kw in text:
            score += 1
    return min(score, 10)

def get_categories(title: str, summary: str) -> list[str]:
    text = title + " " + summary
    return [cat for cat, kws in DS_KEYWORD_MAP.items() if any(k in text for k in kws)]

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
    return re.sub(r"<[^>]+>", "", text or "")[:250].strip()

@st.cache_data(ttl=1800)
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
                rules   = match_business_rules(title, summary)
                score   = calc_ds_score(title, summary)
                cats    = get_categories(title, summary)
                articles.append({
                    "ソース": name, "タイトル": title, "概要": summary,
                    "URL": link, "公開日時": pub,
                    "業務インパクトルール": rules,
                    "DS関連度スコア": score,
                    "カテゴリ": cats,
                })
        except Exception as e:
            st.warning(f"{name} の取得に失敗: {e}")
    df = pd.DataFrame(articles)
    if not df.empty:
        df = df.sort_values("公開日時", ascending=False).reset_index(drop=True)
    return df

# ══════════════════════════════════════════════════════════════════
# 記事カード描画
# ══════════════════════════════════════════════════════════════════
def render_impact_card(row):
    """業務インパクト付き記事カード"""
    rules    = row["業務インパクトルール"]
    score    = row["DS関連度スコア"]
    pub      = row["公開日時"]
    pub_str  = pub.strftime("%m/%d %H:%M") if pub.year > 2000 else "—"
    cats     = row["カテゴリ"]

    border_color = rules[0]["color"] if rules else "#DEE2E6"

    with st.container(border=True):
        # ヘッダー
        col_title, col_meta = st.columns([5, 1])
        with col_title:
            st.markdown(f"### [{row['タイトル']}]({row['URL']})")
            if row["概要"]:
                st.caption(row["概要"])
            # カテゴリバッジ
            if cats:
                st.markdown(" ".join([f"`{c}`" for c in cats]))
        with col_meta:
            st.markdown(f"**{row['ソース']}**")
            st.caption(f"🕐 {pub_str}")
            st.caption(f"DS関連度: {score}/10")
            st.markdown("🟦" * score + "⬜" * (10 - score))

        # 業務インパクト分析
        if rules:
            for rule in rules:
                st.markdown("---")
                st.markdown(f"#### {rule['priority']} 業務インパクト: {rule['name']}")

                col1, col2 = st.columns([1, 1])
                with col1:
                    st.markdown("**📌 このニュースが意味すること**")
                    st.info(rule["meaning"])
                    st.markdown("**⚠️ KDDIネットワーク・ビジネスへの影響**")
                    for impact in rule["impact_areas"]:
                        st.markdown(f"- {impact}")

                with col2:
                    st.markdown("**✅ DS担当者としての調査・対策アクション**")
                    for action_name, action_desc in rule["actions"]:
                        with st.expander(f"{action_name}"):
                            st.markdown(action_desc)

def render_simple_card(row):
    """シンプルな記事カード（業務インパクトなし）"""
    pub_str = row["公開日時"].strftime("%m/%d %H:%M") if row["公開日時"].year > 2000 else "—"
    with st.container(border=True):
        col1, col2 = st.columns([5, 1])
        with col1:
            st.markdown(f"**[{row['タイトル']}]({row['URL']})**")
            if row["概要"]:
                st.caption(row["概要"])
            if row["カテゴリ"]:
                st.markdown(" ".join([f"`{c}`" for c in row["カテゴリ"]]))
        with col2:
            st.caption(f"**{row['ソース']}**")
            st.caption(f"🕐 {pub_str}")
            st.caption(f"DS: {row['DS関連度スコア']}/10")

# ══════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════
st.title("📰 通信ニュース × DS業務インパクト分析")
st.caption("最新ニュースを自動取得し、「KDDIのデータサイエンティストとして何をすべきか」を自動推定します")

# サイドバー
with st.sidebar:
    st.header("⚙️ フィルター設定")
    selected_feeds = st.multiselect(
        "ニュースソース",
        [name for name, _ in FEEDS],
        default=[name for name, _ in FEEDS],
    )
    st.markdown("---")
    show_impact_only = st.toggle("業務インパクトあり記事のみ表示", value=False)
    min_score = st.slider("DS関連度スコア（最低値）", 0, 10, 0)
    keyword_filter = st.text_input("🔍 キーワード検索", placeholder="例: 倍速, AirPods, 5G...")
    st.markdown("---")
    if st.button("🔄 今すぐ更新", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    st.caption("キャッシュ: 30分ごとに自動更新")

    st.markdown("---")
    st.markdown("**🏷️ 業務インパクトルール一覧**")
    for rule in BUSINESS_RULES:
        st.markdown(f"- {rule['name']}")

# ニュース取得
with st.spinner("ニュースを取得中..."):
    df = fetch_all_news(tuple(selected_feeds))

if df.empty:
    st.error("ニュースを取得できませんでした。")
    st.stop()

# フィルター適用
df_f = df.copy()
if show_impact_only:
    df_f = df_f[df_f["業務インパクトルール"].apply(len) > 0]
if min_score > 0:
    df_f = df_f[df_f["DS関連度スコア"] >= min_score]
if keyword_filter.strip():
    kw = keyword_filter.strip().lower()
    df_f = df_f[
        df_f["タイトル"].str.lower().str.contains(kw, na=False) |
        df_f["概要"].str.lower().str.contains(kw, na=False)
    ]

# メトリクス
st.markdown("---")
impact_count = df["業務インパクトルール"].apply(len).gt(0).sum()
c1, c2, c3, c4 = st.columns(4)
c1.metric("総記事数", f"{len(df)} 件")
c2.metric("表示中", f"{len(df_f)} 件")
c3.metric("🎯 業務インパクトあり", f"{impact_count} 件")
latest = df["公開日時"].max()
c4.metric("最新", latest.strftime("%m/%d %H:%M") if latest.year > 2000 else "—")
st.markdown("---")

# タブ
tab_impact, tab_all, tab_rule = st.tabs(["🎯 業務インパクト分析", "📋 全記事", "📖 インパクトルール一覧"])

# ── Tab1: 業務インパクト ──────────────────────────────────────────
with tab_impact:
    st.subheader("🎯 業務インパクトが検出された記事")
    st.caption("ニュースの内容から「KDDIのDSとして取るべきアクション」を自動推定しています")

    impact_df = df_f[df_f["業務インパクトルール"].apply(len) > 0]

    if impact_df.empty:
        st.info("現在、業務インパクトが検出された記事はありません。フィルターを調整するか、更新ボタンを押してください。")
    else:
        st.success(f"✅ {len(impact_df)} 件の記事で業務インパクトを検出しました")
        for _, row in impact_df.head(15).iterrows():
            render_impact_card(row)

# ── Tab2: 全記事 ─────────────────────────────────────────────────
with tab_all:
    st.subheader(f"全記事（{len(df_f)} 件）")
    for _, row in df_f.head(30).iterrows():
        if len(row["業務インパクトルール"]) > 0:
            render_impact_card(row)
        else:
            render_simple_card(row)

# ── Tab3: ルール一覧 ─────────────────────────────────────────────
with tab_rule:
    st.subheader("📖 業務インパクト自動検出ルール一覧")
    st.caption("以下のパターンに合致するニュースが来たとき、自動的にアクションを提案します")
    for rule in BUSINESS_RULES:
        with st.expander(f"{rule['priority']} {rule['name']}"):
            st.markdown(f"**検出キーワード**: {', '.join(rule['triggers'])}")
            st.markdown("---")
            st.markdown(f"**📌 意味**: {rule['meaning']}")
            st.markdown("**⚠️ 影響領域**:")
            for ia in rule["impact_areas"]:
                st.markdown(f"  - {ia}")
            st.markdown("**✅ 推奨アクション**:")
            for name, desc in rule["actions"]:
                st.markdown(f"  - **{name}**: {desc}")

st.markdown("---")
st.caption("データソース: ITmedia Mobile / ケータイWatch / ITmedia News / Impress Watch | キャッシュ30分 | 🔄ボタンで即時更新")
