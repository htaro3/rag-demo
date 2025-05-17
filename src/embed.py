"""
【embed.pyの役割】
-----------------------------------------------------
- 本ファイルは「RAG（検索拡張生成）型AIアプリ」の"準備"パート。
- 現場業務で使いたい「ナレッジ・マニュアル・FAQ」などの知識ベース（ここではdata/docs.txt）を
- AIが"意味（ニュアンス）で"探せるように、
    ① テキストを小さな単位（チャンク）に分割
    ② GeminiのEmbedding APIで「意味ベクトル」に変換
    ③ ベクトルDB（chromadb）に"索引"として登録
- この処理をやることで、後続の「ユーザー質問 → 意味検索 → 回答生成」が超高精度＆高速に！
- 現状では1ファイル（docs.txt）だけだが、現場運用時は複数ファイル・多形式も同じフローで拡張可能
"""

import os
import google.generativeai as genai
import chromadb
from chromadb.config import Settings
from dotenv import load_dotenv

# .envファイル読み込んで変数に格納
load_dotenv()

# Google APIキー設定
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# ドキュメント読み込み
doc_path = os.path.join(os.path.dirname(__file__), '../data/docs.txt')
with open(doc_path, encoding='utf-8') as f:
    docs = [line.strip() for line in f if line.strip()]

# 各チャンクをベクトル化（gemini用）
embeddings = []
for doc in docs:
    # テキスト（チャンク）をベクトル化
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=doc,
        task_type="retrieval_document"
    )
    # resltの"embedding"キーにベクトルが格納されている
    embeddings.append(result["embedding"])

# ベクトルDBの保存ディレクトリパスを設定
db_path = os.path.join(os.path.dirname(__file__), '../data/chroma_db')

# chromadbの「永続クライアント」を初期化
client = chromadb.PersistentClient(path = db_path, settings = Settings(anonymized_telemetry = False))

# コレクションrag_docsを取得
collection = client.get_or_create_collection("rag_docs")

# 各チャンク・ベクトルを1件ずつ登録
for idx, (doc, vector) in enumerate(zip(docs, embeddings)):
    collection.add(
        documents = [doc],      # 元文書
        ids = [f"doc_{idx}"],   # ユニークID
        embeddings = [vector]   # AIが生成した意味ベクトル
    )

# 処理完了メッセージ
print("知識ベースのEmbedding（意味ベクトル）をベクトルDB（rag_docsコレクション）に登録しました！")
print(f"登録件数: {len(docs)} 件")
print("→ これで意味が似ている知識をAI検索できる下準備が完成です。")
print("rag_docs = あなた専用の知識ベース（意味検索用インデックス）です。")