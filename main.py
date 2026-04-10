from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

# ইউনিকোড সাপোর্ট
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def home():
    return "Free.ai Claude API is running on Vercel!"

@app.route('/ask', methods=['GET'])
def ask():
    query = request.args.get('q', 'হ্যালো')
    url = "https://api.free.ai/v1/chat/"

    payload = {
        "model": "anthropic/claude-sonnet-4",
        "messages": [
            {"role": "system", "content": "You are a helpful AI assistant. Be concise."},
            {"role": "user", "content": query}
        ],
        "temperature": 0.2,
        "stream": True,
        "max_tokens": 4096
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0",
        'Content-Type': "application/json",
        'Origin': "https://free.ai",
        'Accept': "text/event-stream"
    }

    def generate():
        full_text = ""
        try:
            # SSE স্ট্রিমিং রিকোয়েস্ট
            response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=30)
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        json_str = decoded_line[6:]
                        if json_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(json_str)
                            content = data['choices'][0].get('delta', {}).get('content', '')
                            full_text += content
                        except:
                            continue
            
            # সম্পূর্ণ রেসপন্স JSON আকারে পাঠানো
            return json.dumps({"answer": full_text}, ensure_ascii=False)
        except Exception as e:
            return json.dumps({"error": str(e)}, ensure_ascii=False)

    return Response(generate(), content_type='application/json; charset=utf-8')

# Vercel এর জন্য এটি প্রয়োজন
def handler(event, context):
    return app(event, context)
