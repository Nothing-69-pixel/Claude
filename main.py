from flask import Flask, request, Response
import requests
import json

app = Flask(__name__)

# হোম পেজ মেসেজ
@app.route('/')
def home():
    data = {
        "project": "Toolsutil ai",
        "status": "Online",
        "message": "Welcome to Toolsutil ai API"
    }
    # সুন্দর করে আউটপুট দেখানোর জন্য json.dumps ব্যবহার করা হয়েছে
    return Response(json.dumps(data, indent=2), mimetype='application/json')

@app.route('/ask', methods=['GET'])
def ask_ai():
    # ইউজার থেকে ইনপুট (প্রশ্ন) নেওয়া
    query = request.args.get('q', '')
    if not query:
        return Response(
            json.dumps({"status": "error", "message": "Please provide a query (?q=...)"}, ensure_ascii=False),
            mimetype='application/json',
            status=400
        )
    
    url = "https://api.free.ai/v1/chat/"

    # সিস্টেম প্রম্পট এবং পেলোড সেটআপ
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
        # API তে রিকোয়েস্ট পাঠানো (Streaming on)
        response = requests.post(url, data=json.dumps(payload), headers=headers, stream=True, timeout=120)
        
        full_response_text = ""
        actual_model = ""

        # SSE স্ট্রিম থেকে ডাটা সংগ্রহ করা
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                
                # 'data: ' অংশটুকু ফিল্টার করা
                if decoded_line.startswith('data: '):
                    json_str = decoded_line[6:].strip()
                    
                    if json_str == "[DONE]":
                        break
                    
                    try:
                        chunk = json.loads(json_str)
                        if not actual_model:
                            actual_model = chunk.get("model", "claude-sonnet-4")
                        
                        # কন্টেন্ট অংশটুকু যোগ করা
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            content = chunk["choices"][0].get("delta", {}).get("content", "")
                            full_response_text += content
                    except:
                        continue

        # চূড়ান্ত আউটপুট ডাটা
        result_json = {
            "status": "success",
            "bot_name": "Toolsutil ai",
            "query": query,
            "response": full_response_text,
            "metadata": {
                "model": actual_model,
                "mode": "Expert Coder",
                "safe_mode": "Enabled"
            }
        }

        # --- এখানে সমাধান ---
        # ensure_ascii=False দেওয়ার ফলে <, >, / এবং বাংলা একদম অরিজিনাল থাকবে।
        final_output = json.dumps(result_json, ensure_ascii=False, indent=2)
        
        return Response(final_output, mimetype='application/json')

    except Exception as e:
        error_res = {"status": "error", "message": str(e)}
        return Response(json.dumps(error_res, ensure_ascii=False), mimetype='application/json', status=500)

# Vercel ডিপ্লয়মেন্টের জন্য
application = app

if __name__ == "__main__":
    # লোকাল পিসিতে টেস্ট করার জন্য
    app.run(debug=True)
