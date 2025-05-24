"""
【embed.pyの役割】
-----------------------------------------------------
- 本ファイルは「RAG（検索拡張生成）型AIアプリ」の"準備"パート。
- 現場業務で使いたい「ナレッジ・マニュアル・FAQ」などの知識ベースをAIが"意味（ニュアンス）で"探せるように、
    ① テキストを小さな単位（チャンク）に分割
    ② GeminiのEmbedding APIで「意味ベクトル」に変換
    ③ ベクトルDB（chromadb）に"索引"として登録
- この処理をやることで、後続の「ユーザー質問 → 意味検索 → 回答生成」が超高精度＆高速に！
- 現状では1ファイル（docs.txt）だけだが、現場運用時は複数ファイル・多形式も同じフローで拡張可能
"""

import os
import re
import google.generativeai as genai
from config import collection  # ← 初期化済みのcollectionを共通import

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

## チャンク分割設定
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
DATA_DIR = os.path.join(os.path.dirname(__file__), '../data')

# 文単位・オーバーラップ付きチャンク分割関数
def split_into_chunks(text, max_len=CHUNK_SIZE, overlap=CHUNK_OVERLAP):
    sentences = re.split('(?<=。)', text)
    chunks, current = [], ""
    for sentence in sentences:
        if len(current) + len(sentence) <= max_len:
            current += sentence
        else:
            chunks.append(current.strip())
            current = current[-overlap:] + sentence
    if current:
        chunks.append(current.strip())
    return chunks

# dataディレクトリ内の.txtファイル一覧取得
txt_files = [f for f in os.listdir(DATA_DIR) if f.endswith('.txt')]

for file_name in txt_files:
    document_id = file_name.replace('.txt', '')
    file_path = os.path.join(DATA_DIR, file_name)

    try:
        # 重複登録チェック（1チャンクでもあればスキップ）
        check_id = f"{document_id}_chunk_0"
        exists = collection.get(ids=[check_id])
        if exists["ids"]:
            print(f"{document_id} は既に登録済みのためスキップします。")
            continue

        # テキスト読み込み＆チャンク分割
        with open(file_path, encoding='utf-8') as f:
            text = f.read()
        chunks = split_into_chunks(text)

        # 各チャンクをembedding（ベクトル化）
        embeddings = []
        for chunk in chunks:
            result = genai.embed_content(
                model="models/text-embedding-004",
                content=chunk,
                task_type="retrieval_document"
            )
            embeddings.append(result["embedding"])

        # 一括登録（documents / ids / metadatas / embeddings）
        collection.add(
            documents=chunks,
            ids=[f"{document_id}_chunk_{i}" for i in range(len(chunks))],
            metadatas=[{"document_id": document_id}] * len(chunks),
            embeddings=embeddings
        )

        print(f"{file_name} のチャンク数: {len(chunks)} 件 → 登録完了")

    except Exception as e:
        print(f"{file_name} の処理中にエラーが発生しました: {e}")
        continue

print("\n全ファイルの処理が完了しました。")