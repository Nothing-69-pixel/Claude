from flask import Flask, request, Response # Response ইম্পোর্ট করা হয়েছে
import requests
import json
import re

app = Flask(__name__)

# ইউনিকোড বা কোডিং সমস্যা ঠিক করার ফাংশন
def clean_gemini_response(raw_text):
    try:
        data_blocks = re.findall(r'\["wrb.fr",".*?}\]', raw_text)
        if data_blocks:
            inner_json_str = json.loads(data_blocks[-1])[2]
            inner_data = json.loads(inner_json_str)
            if len(inner_data) > 4 and inner_data[4]:
                return inner_data[4][0][1][0]
            else:
                return inner_data[1][0][0][1]
    except:
        pass
    return raw_text

@app.route('/ask', methods=['GET'])
def ask_ai():
    query = request.args.get('q', '')
    if not query:
        return Response(json.dumps({"error": "No query"}), mimetype='application/json')
    
    url = "https://api.free.ai/v1/chat/"

    payload = {
        "model": "anthropic/claude-sonnet-4",
        "messages": [
            {
                "role": "system",
                "content": "You are Toolsutil ai, an expert AI coding assistant..." # আপনার পুরো সিস্টেম প্রম্পট এখানে থাকবে
            },
            {"role": "user", "content": query}
        ],
        "temperature": 0.2,
        "stream": True
    }

    headers = {
        'Content-Type': "application/json",
        'User-Agent': "Mozilla/5.0...",
        'Origin': "https://free.ai"
    }

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True)
        
        full_text = ""
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                if decoded.startswith('data: '):
                    json_str = decoded[6:].strip()
                    if json_str == "[DONE]": break
                    try:
                        chunk = json.loads(json_str)
                        full_text += chunk["choices"][0].get("delta", {}).get("content", "")
                    except: continue

        # --- এখানে পরিবর্তন করা হয়েছে ---
        result_data = {
            "status": "success",
            "bot_name": "Toolsutil ai",
            "query": query,
            "response": full_text
        }

        # jsonify এর বদলে সরাসরি json.dumps ব্যবহার করে Response পাঠানো হচ্ছে
        # এতে \u003C এর বদলে সরাসরি < দেখা যাবে
        json_output = json.dumps(result_data, ensure_ascii=False, indent=2)
        return Response(json_output, mimetype='application/json')

    except Exception as e:
        return Response(json.dumps({"error": str(e)}), mimetype='application/json')

application = app
