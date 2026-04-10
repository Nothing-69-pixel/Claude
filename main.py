from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

@app.route('/')
def home():
    return "Free.ai SSE Proxy is Running!"

@app.route('/ask', methods=['GET'])
def ask_ai():
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
        "stream": True, # স্ট্রিম অন রাখা হয়েছে
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
        # রিকোয়েস্ট পাঠানো (stream=True জরুরি)
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=60)
        
        full_response = ""
        
        # SSE ডাটা প্রসেস করা
        for line in response.iter_lines():
            if line:
                # লাইনটি ডিকোড করা (bytes to string)
                decoded_line = line.decode('utf-8')
                
                # SSE লাইনের শুরুতে সাধারণত 'data: ' থাকে
                if decoded_line.startswith('data: '):
                    json_str = decoded_line[6:] # 'data: ' অংশটুকু বাদ দেওয়া
                    
                    # যদি স্ট্রিম শেষ হয় [DONE] আসে
                    if json_str.strip() == "[DONE]":
                        break
                    
                    try:
                        data = json.loads(json_str)
                        # content অংশটুকু খুঁজে বের করে জোড়া লাগানো
                        if "choices" in data and len(data["choices"]) > 0:
                            content = data["choices"][0].get("delta", {}).get("content", "")
                            full_response += content
                    except json.JSONDecodeError:
                        continue

        # সম্পূর্ণ জোড়া লাগানো উত্তরটি পাঠানো
        return full_response if full_response else "No response from AI."

    except Exception as e:
        return f"Error: {str(e)}", 500

# Vercel-এর জন্য
application = app

if __name__ == "__main__":
    app.run(debug=True)
