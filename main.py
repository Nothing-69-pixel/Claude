from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

# ইউনিকোড বা বাংলা ফন্ট ঠিকভাবে দেখানোর জন্য
app.config['JSON_AS_ASCII'] = False

@app.route('/')
def home():
    return "Free.ai SSE API Proxy is Running!"

@app.route('/ask', methods=['GET'])
def ask():
    query = request.args.get('q')
    if not query:
        return Response(json.dumps({"error": "Please provide a query 'q'"}, ensure_ascii=False), content_type='application/json')

    url = "https://api.free.ai/v1/chat/"

    payload = {
        "model": "anthropic/claude-sonnet-4",
        "messages": [
            {
                "role": "system", 
                "content": "You are a helpful AI assistant. Answer accurately and concisely."
            },
            {
                "role": "user", 
                "content": query
            }
        ],
        "temperature": 0.2,
        "stream": True,
        "max_tokens": 10000000000
    }

    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0",
        'Content-Type': "application/json",
        'Origin': "https://free.ai",
        'Accept': "text/event-stream"
    }

    try:
        # stream=True ব্যবহার করা হয়েছে কারণ API-টি SSE ডাটা পাঠায়
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=30)
        
        full_text = ""
        
        # SSE ডাটা থেকে content খুঁজে বের করার লজিক
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data: '):
                    json_str = decoded_line[6:] # 'data: ' অংশটুকু ফেলে দেওয়া
                    
                    if json_str.strip() == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(json_str)
                        # JSON থেকে শুধু content টুকু নেওয়া
                        if 'choices' in data and len(data['choices']) > 0:
                            content = data['choices'][0].get('delta', {}).get('content', '')
                            full_text += content
                    except:
                        continue
        
        # সম্পূর্ণ উত্তরটি JSON আকারে পাঠানো
        final_json = json.dumps({"answer": full_text.strip()}, ensure_ascii=False)
        return Response(final_json, content_type='application/json; charset=utf-8')

    except Exception as e:
        error_json = json.dumps({"error": str(e)}, ensure_ascii=False)
        return Response(error_json, content_type='application/json', status=500)

# Vercel-এর জন্য মেইন এন্ট্রি পয়েন্ট
if __name__ == "__main__":
    app.run(debug=True)
