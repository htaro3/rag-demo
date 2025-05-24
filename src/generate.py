"""
【generate.py：意味検索済み文書＋質問 → 回答生成】
-----------------------------------------------------
- ユーザーの質問と、retrieve.pyで取得済みの関連文書を用いて
- Gemini APIで自然な回答文を生成する
- 実務で使えるようにプロンプト構成を明示化し、出力も整形済み
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# --------------------------
# 設定
# --------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "models/gemini-1.5-flash"

# --------------------------
# 入力（質問と文書を手動入力 or 前段ファイルから流用も可）
# --------------------------
query = input("質問を再入力してください（またはそのままEnterで再使用）：\n> ").strip()
if not query:
    query = "返品ポリシーはどうなっていますか？"  # デフォルト例（省略可）

print("\n関連文書（内容を貼り付けてください。空行2つで終了）:")
doc_lines = []
while True:
    line = input()
    if line.strip() == "":
        if len(doc_lines) > 0 and doc_lines[-1].strip() == "":
            break
    doc_lines.append(line)
document_context = "\n".join(doc_lines).strip()

# --------------------------
# プロンプト生成（文書＋質問の構成）
# --------------------------
prompt = f"""
以下は社内ナレッジベースの一部抜粋です。内容を踏まえて、ユーザーの質問に答えてください。

【知識ベース抜粋】
{document_context}

【ユーザーからの質問】
{query}

【お願い】
- 必ず知識ベースに基づいて答えてください。
- 答えが明記されていない場合は「その内容は知識ベースには見つかりませんでした」と答えてください。
"""

# --------------------------
# Geminiで回答生成
# --------------------------
try:
    model = genai.GenerativeModel(MODEL_NAME)
    response = model.generate_content(prompt)

    print("\n【生成AIの回答】\n" + "-" * 40)
    print(response.text)

except Exception as e:
    print(f"エラーが発生しました：{e}")
