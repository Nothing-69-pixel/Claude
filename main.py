from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

# হোম পেজ মেসেজ
@app.route('/')
def home():
    return jsonify({
        "project": "Toolsutil ai",
        "status": "Running",
        "author": "Expert AI Coder"
    })

@app.route('/ask', methods=['GET'])
def ask_ai():
    # ইউজার থেকে ইনপুট নেওয়া
    query = request.args.get('q', '')
    if not query:
        return jsonify({
            "status": "error", 
            "message": "Please provide a query using ?q="
        }), 400
    
    url = "https://api.free.ai/v1/chat/"

    # সিস্টেম প্রম্পটে 'Toolsutil ai' নাম সেট করা হয়েছে
    payload = {
        "model": "anthropic/claude-sonnet-4",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are Toolsutil ai, an expert AI coding assistant. You help users write, debug, refactor, and understand code. "
                    "When proposing file changes, use unified diff format in a code block with the filename. "
                    "When showing terminal commands, use ```bash code blocks. Always explain your changes briefly. "
                    "Be concise and precise. Support all programming languages. Use best practices and modern patterns. "
                    "SAFE MODE is ON: Only propose changes, never execute destructive operations. Show diffs for user approval."
                )
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

    # আপনার দেওয়া নির্দিষ্ট হেডারগুলো
    headers = {
        'User-Agent': "Mozilla/5.0 (Linux; Android 13; M2103K19I Build/TP1A.220624.014) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.7680.166 Mobile Safari/537.36",
        'Content-Type': "application/json",
        'Accept-Encoding': "gzip, deflate, br, zstd",
        'Origin': "https://free.ai",
        'X-Requested-With': "mark.via.gp",
        'Sec-Fetch-Site': "same-site",
        'Sec-Fetch-Mode': "cors",
        'Sec-Fetch-Dest': "empty",
        'Accept-Language': "en-US,en;q=0.9"
    }

    try:
        # API রিকোয়েস্ট পাঠানো (Streaming enabled)
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=120)
        
        full_response_text = ""
        model_used = ""

        # SSE (Server-Sent Events) ডাটা প্রসেস করা
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                # লাইনের শুরু যদি 'data: ' হয়
                if decoded_line.startswith('data: '):
                    json_data_str = decoded_line[6:].strip()
                    
                    # স্ট্রিম শেষ হলে [DONE] আসবে
                    if json_data_str == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(json_data_str)
                        if not model_used:
                            model_used = chunk.get("model", "")
                        
                        # ডেল্টা কন্টেন্ট থেকে টেক্সট অংশটুকু নেওয়া
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            content = chunk["choices"][0].get("delta", {}).get("content", "")
                            full_response_text += content
                    except:
                        continue

        # চূড়ান্ত JSON রেসপন্স
        return jsonify({
            "status": "success",
            "bot_name": "Toolsutil ai",
            "query": query,
            "response": full_response_text,
            "metadata": {
                "model": model_used,
                "mode": "Expert Coder",
                "safe_mode": "Enabled"
            }
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# Vercel ডিপ্লয়মেন্টের জন্য জরুরি
application = app

if __name__ == "__main__":
    app.run(debug=True)
