# Retrieval-Augmented Generation (RAG) Demo

このプロジェクトは、検索拡張生成（RAG: Retrieval-Augmented Generation）の最小構成デモです。

## ディレクトリ構成

```
rag-demo/
├── data/                # ドキュメントや知識ベースを格納
│   └── docs.txt
├── src/                 # メインのPythonコード
│   ├── embed.py         # 埋め込み生成・インデックス作成
│   ├── retrieve.py      # 類似検索
│   └── generate.py      # 生成AIによる回答生成
├── test/                # テストコード
│   └── gemini_test.py
├── .env                 # APIキーなどの環境変数
├── requirements.txt     # 必要なPythonパッケージ
└── README.md            # プロジェクト説明
```

## セットアップ

1. 必要なパッケージのインストール
   ```sh
   pip install -r requirements.txt
   ```
2. `.env` ファイルにAPIキーを記載
   ```
   GOOGLE_API_KEY=your_google_api_key
   ```
3. `data/docs.txt` に知識ベースとなるテキストを記載

## 使い方

- `src/embed.py` でドキュメントの埋め込みとインデックス作成
- `src/retrieve.py` で質問に対する類似ドキュメント検索
- `src/generate.py` で検索結果と質問をもとにGeminiで回答生成

---

詳細は各スクリプトのコメントやドキュメントを参照してください。
