
from flask import Flask, request, Response, render_template, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# 設定你的 API 金鑰
gemini_key = os.getenv('gemini_key')
os.environ["gemini_key"] = gemini_key

# 初始化 Gemini API 客戶端
genai.configure(api_key=gemini_key)

model = genai.GenerativeModel(model_name="gemini-1.5-flash")
chat = model.start_chat(history=[
    {
      "role": "user",
      "parts": [
        "回復設定繁體中文，除非要翻譯功能時再翻譯成其他語言，然後盡量查詢後再回覆，不要有錯誤資訊和唬爛訊息",
      ],
    },
    {
      "role": "model",
      "parts": [
        "好的，我明白了。我會盡力以繁體中文回覆您的問題，除非您明確要求翻譯成其他語言。我會盡量查詢後再回覆，並避免提供錯誤資訊或虛假訊息。請盡情提問！ \n",
      ],
    },
  ])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    question = data.get('question')

    # 使用流式方法生成回答
    return Response(generate_answer_stream(question), content_type='text/event-stream')

def generate_answer_stream(question):
    # 使用 Gemini API 流式生成答案
    for response in chat.send_message(question, stream=True):
        part = response.get('text', '').replace('**', '').replace('*', '-')

        # 格式化 HTML
        if '```' in part or 'def ' in part or 'class ' in part or 'import ' in part:
            part = part.replace('```python', '<pre><code class="python">').replace('```', '</code></pre>')
        elif '    ' in part or '\t' in part:
            part = f'<pre><code>{part}</code></pre>'
        else:
            part = f'<pre><code>{part}</code></pre>'

        # 使用 Server-Sent Events 傳輸數據
        yield f"data: {part}\n\n"

if __name__ == '__main__':
    app.run(debug=True)
