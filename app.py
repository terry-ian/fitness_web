
from flask import Flask, request, jsonify, render_template
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

    # 使用 Google Gemini API 生成答案
    answer = generate_answer(question)

    return jsonify({'answer': answer})


def generate_answer(question):
    # 使用 Google Gemini API 來生成答案
    response = chat.send_message(question)

    # 假設回答中包含程式碼，使用適當的 HTML 包裹代碼塊
    answer_text = response.text.replace('**', '').replace('*', '-')

    # 判斷是否包含程式碼塊標記或常見的程式碼特徵
    if '```' in answer_text or 'def ' in answer_text or 'class ' in answer_text or 'import ' in answer_text:
        answer_text = answer_text.replace('```python', '<pre><code class="python">').replace('```', '</code></pre>')
    elif '    ' in answer_text or '\t' in answer_text:  # 檢查是否有縮排
        answer_text = f'<pre><code>{answer_text}</code></pre>'
    else:
        # 如果沒有明顯的程式碼特徵，但希望統一格式，仍然包裹代碼以防範例外
        answer_text = f'<pre><code>{answer_text}</code></pre>'
    
    return answer_text

if __name__ == '__main__':
    app.run()
