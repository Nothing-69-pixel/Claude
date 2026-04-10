from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({
        "status": "online",
        "message": "Free.ai JSON Proxy is Running"
    })

@app.route('/ask', methods=['GET'])
def ask_ai():
    # ইউজার থেকে প্রশ্ন নেওয়া
    query = request.args.get('q', 'আপনি কি কি পারেন')
    
    url = "https://api.free.ai/v1/chat/"

    # আপনার দেওয়া পেলোড
    payload = {
        "model": "anthropic/claude-sonnet-4",
        "messages": [
            {
                "role": "system",
                "content": "You are Free.ai Coder, an expert AI coding assistant."
            },
            {
                "role": "user",
                "content": query
            }
        ],
        "temperature": 0.2,
        "stream": True,
        "max_tokens": 4096
    }

    # আপনার দেওয়া হেডার
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; M2103K19I Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.7680.166 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'Origin': "https://free.ai",
        'X-Requested-With': "mark.via.gp",
        'Sec-Fetch-Site': "same-site",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Accept-Language': "en-US,en;q=0.9"
    }

    try:
        # রিকোয়েস্ট পাঠানো
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=60)
        
        full_content = ""
        model_name = ""

        # SSE স্ট্রিম প্রসেস করা
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                if decoded_line.startswith('data: '):
                    content_str = decoded_line[6:].strip()
                    
                    if content_str == "[DONE]":
                        break
                    
                    try:
                        chunk_data = json.loads(content_str)
                        # মডেলের নাম সেভ করে রাখা (প্রথম চঙ্ক থেকে)
                        if not model_name:
                            model_name = chunk_data.get("model", "claude-sonnet-4")
                        
                        # কন্টেন্ট অংশটুকু সংগ্রহ করা
                        if "choices" in chunk_data and len(chunk_data["choices"]) > 0:
                            delta = chunk_data["choices"][0].get("delta", {})
                            if "content" in delta:
                                full_content += delta["content"]
                    except:
                        continue

        # সুন্দর JSON ফরম্যাটে আউটপুট দেওয়া
        return jsonify({
            "status": "success",
            "data": {
                "query": query,
                "response": full_content,
                "model": model_name,
                "provider": "Free.ai"
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Vercel এর জন্য
application = app

if __name__ == "__main__":
    app.run(debug=True)
