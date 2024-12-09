import os
from flask import Flask, request, Response
import google.generativeai as genai

# 設定 API 金鑰
gemini_key = os.getenv('gemini_key')
os.environ["gemini_key"] = gemini_key

# 初始化 Gemini API
genai.configure(api_key=gemini_key)
model = genai.GenerativeModel(model_name="gemini-1.5-flash")
chat = model.start_chat(history=[
    {
        "role": "user",
        "parts": [
            "設定以繁體中文回覆，除非需要翻譯功能時再切換語言。",
        ],
    },
    {
        "role": "model",
        "parts": [
            "好的，我將以繁體中文回覆您的問題，請隨時提問！",
        ],
    },
])

# 建立 Flask 應用
app = Flask(__name__)

@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json()
    question = data.get("question")

    def generate_stream():
        # 使用 Gemini API 的 stream 模式
        for response in chat.send_message(question, stream=True):
            part = response.get("text", "")
            yield f"data: {part}\n\n"  # 確保流式數據格式正確

    return Response(generate_stream(), content_type="text/event-stream")


if __name__ == "__main__":
    app.run()
