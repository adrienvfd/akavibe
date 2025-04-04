from flask import Flask, jsonify, request
import requests
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)

TOKENMETRICS_API_KEY = os.getenv('TOKEN_METRICS_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

@app.route('/generate-post', methods=['GET'])
def generate_post():
    try:
        # Get data from TokenMetrics API
        tokenmetrics_response = requests.get(tokenmetrics_url, params=tokenmetrics_params, headers=tokenmetrics_headers)
        tokenmetrics_data = tokenmetrics_response.json()
        
        # Prepare prompt for Groq
        prompt = f"""
        Format this information to make it a suitable post for social media. 
        Include emojis and use MARKDOWN format:
        
        {tokenmetrics_data}
        """
        
        # Call Groq API
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile"
        )
        
        # Return the formatted post
        return jsonify({
            "post": chat_completion.choices[0].message.content
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')