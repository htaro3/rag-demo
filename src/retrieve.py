"""
【retrieve.py：意味検索＋文書再構成】
-----------------------------------------------------
- ユーザーの質問をGemini APIでEmbedding（意味ベクトル）化
- chromadbから類似チャンクを上位n件取得（rag_docs）
- ヒットしたチャンクのdocument_idに基づき、同一文書の全チャンクを取得
- 結果を整形して次工程（AI回答生成）に渡せる形で表示
"""

import google.generativeai as genai
from config import collection

# 検索設定
SEARCH_TOP_N = 3  # 上位何件まで取得するか

# ユーザーから質問を受け取る
query = input("質問を入力してください：\n> ")

try:
    # 質問をベクトル化（retrieval_query指定）
    result = genai.embed_content(
        model="models/text-embedding-004",
        content=query,
        task_type="retrieval_query"
    )
    query_embedding = result["embedding"]

    # 類似チャンク検索（上位n件）
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=SEARCH_TOP_N,
        include=["documents", "metadatas", "distances"]
    )

    # 検索結果からdocument_idを抽出（重複排除）
    hit_doc_ids = {meta["document_id"] for meta in results["metadatas"][0]}

    # 関連する文書チャンクをすべて取得・再構成
    related_docs = []
    for doc_id in hit_doc_ids:
        response = collection.get(where={"document_id": doc_id})
        related_docs.extend(response["documents"])

    # 表示（次工程に渡す用）
    print("\n【検索結果：関連文書（整形済み）】\n" + "-" * 40)
    for doc in related_docs:
        print(doc.strip())
        print()

except Exception as e:
    print(f"エラーが発生しました: {e}")
