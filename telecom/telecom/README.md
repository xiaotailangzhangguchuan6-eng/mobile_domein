# 📡 通信ドメイン基礎知識学習アプリ

KDDIデータサイエンティスト向け — 通信の基礎知識を図解で学び、最新ニュースをDS業務に活かすStreamlitアプリ。

## 機能一覧

| ページ | 内容 |
|---|---|
| 🔢 周波数帯域 | バンドごとの特性・カバレッジ・建屋内浸透率を図解 |
| 🔗 ENDC | 4G+5G同時接続技術をアーキテクチャ図で解説 |
| 🏗️ ネットワーク構成 | RAN・コアネットワークの構成とノード解説 |
| 📶 電波品質指標 | RSRP・SINR・CQIなどの指標とパスロスモデル |
| 🔄 ハンドオーバー | HO仕組み・A3イベント・HOF分析 |
| 📰 通信ニュース × 業務インパクト | RSSニュース自動取得＋DS業務アクション自動推定 |

## セットアップ

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## デプロイ（Streamlit Community Cloud）

1. このリポジトリをGitLab/GitHubにpush
2. [share.streamlit.io](https://share.streamlit.io) でリポジトリを連携
3. Main file: `Home.py` を指定してDeploy
