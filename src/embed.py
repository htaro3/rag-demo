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

# チャンク分割関数（文単位・最大400文字・50字オーバーラップ）
def split_into_chunks(text, max_len=400, overlap=50):
    sentences = re.split('(?<=。)', text)  # 「。」で文を区切る
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_len:
            current_chunk += sentence
        else:
            chunks.append(current_chunk.strip())
            # 最後のoverlap文字分だけ残して次へ
            current_chunk = current_chunk[-overlap:] + sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


# .envからAPIキー取得
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# docs.txt読み込み＆全体を1つの文字列として結合
doc_path = os.path.join(os.path.dirname(__file__), '../data/docs.txt')
with open(doc_path, encoding='utf-8') as f:
     raw_text = f.read()

# チャンク化
chunks = split_into_chunks(raw_text)

# 各チャンクをベクトル化（gemini用）
embeddings = []
for chunk in chunks:
    result = genai.embed_content(
        model="models/text-embedding-004",    # 最新モデル
        content=chunk,
        task_type="retrieval_document"        # 文書検索向けEmbedding
    )
    embeddings.append(result["embedding"])    # 数値ベクトルを保存

# chromadb に保存（コレクション名: rag_docs）
db_path = os.path.join(os.path.dirname(__file__), '../data/chroma_db')
client = chromadb.PersistentClient(path=db_path, settings=Settings(anonymized_telemetry=False))
collection = client.get_or_create_collection("rag_docs")

# 各チャンク・ベクトルを1件ずつ登録
for idx, (chunk, vector) in enumerate(zip(chunks, embeddings)):
    collection.add(
        documents=[chunk],
        ids=[f"chunk_{idx}"],
        embeddings=[vector]
    )

# 処理完了メッセージ
print("知識ベースのEmbedding（意味ベクトル）をベクトルDB（rag_docsコレクション）に登録しました！")
print(f"登録件数: {len(docs)} 件")
print("✅ 分割方式：文単位・最大400文字・50文字オーバーラップ")