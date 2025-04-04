from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/generate-post": {"origins": ["http://localhost:7007"]}})

# Add CORS headers to all responses
@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

TOKENMETRICS_API_KEY = os.getenv('TOKEN_METRICS_API_KEY')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

@app.route('/generate-post', methods=['GET'])
def generate_post():
    try:
        # Get data from TokenMetrics API
        tokenmetrics_url = 'https://api.tokenmetrics.com/v2/sentiments'
        tokenmetrics_params = {
            'limit': 1000,
            'page': 0
        }
        tokenmetrics_headers = {
            'accept': 'application/json',
            'api_key': TOKENMETRICS_API_KEY
        }        
        tokenmetrics_response = requests.get(tokenmetrics_url, params=tokenmetrics_params, headers=tokenmetrics_headers)
        if tokenmetrics_response.status_code != 200:
            return jsonify({
                "error": f"TokenMetrics API returned status {tokenmetrics_response.status_code}",
                "response": tokenmetrics_response.text
            }), tokenmetrics_response.status_code
        
        try:
            tokenmetrics_data = tokenmetrics_response.json()
            print('Data:', tokenmetrics_data)
        except ValueError as e:
            return jsonify({
                "error": f"Failed to parse JSON response: {str(e)}",
                "raw_response": tokenmetrics_response.text
            }), 500
        
        # Prepare prompt for Groq
        prompt = """
            You are tasked with creating an engaging social media post summarizing Akavibe market data, powered by Token Metrics.
            Use the provided JSON data: {tokenmetrics_data}. The numbers from the JSON data are valid and should not be changed.
            DO NOT SAY ANYTHING ELSE OTHER THAN THE SOCIAL MEDIA POST.
            **Formatting & Style Guidelines:**

            1.  **Main Title:**
                * Use an **H1 Markdown heading (`#`)**.
                * The title on the first line *must* be "**Akavibe Market Pulse By Token Metrics**".
                * Keep it concise for mobile readability (e.g., `# Akavibe Market Pulse By Token Metrics`).

            2.  **Overall Sentiment:**
                * Clearly state the overall `MARKET_SENTIMENT_LABEL` and `MARKET_SENTIMENT_GRADE`. Replace the values with the actual values from the JSON data.
                * Use **bold text** for the label and score.
                * Include a relevant emoji reflecting the overall sentiment (e.g., 🤔 for Neutral, 📈 for Positive, 📉 for Negative).
                * Example: `📊 Overall Market Vibe: **Neutral** (Score: **56.78**)`

            3.  **Source Breakdowns (News, Reddit, Twitter):**
                * Use **H3 Markdown headings (`###`)** for each source, including a relevant emoji (e.g., `### 📰 News Highlights`, `### 🔥 Reddit Chatter`, `### 🐦 Twitter Trends`).
                * For each source:
                    * State its sentiment `LABEL` and `GRADE` (e.g., `Sentiment: **Neutral** (**54**)`). Use **bold**.
                    * Provide a **brief, bulleted list** (using `-` or `*`) summarizing the *key takeaways* from the provided `SUMMARY`. **DO NOT CONDENSE THE INFORMATION** for social media.

            4.  **Timestamp:**
                * Include the date/time of the data report. Mention it clearly, perhaps near the end. (e.g., `Data as of: {DATETIME}`).

            5.  **Emojis:**
                * Use emojis strategically throughout the post to add visual appeal and break up text, especially with headings and sentiment labels.

            6.  **Markdown:**
                * Utilize Markdown for structure: `##` for the main title, `###` for sections, `**bold**` for emphasis (sentiment labels, scores), and bullet points (`-` or `*`) for summaries.

            7.  **Tone:**
                * Maintain an informative yet engaging and easily digestible tone suitable for social media platforms like Twitter, Facebook, or LinkedIn.

            8.  **Hashtags:**
                * Conclude the post with relevant and trending cryptocurrency hashtags. Include `#Akavibe` and `#TokenMetrics`. (e.g., `#Crypto #MarketSentiment #Bitcoin #Ethereum #DeFi #Akavibe #TokenMetrics`)

            **Objective:** Transform the raw data into a well-structured, visually appealing, and concise social media update that quickly informs followers about the current crypto market sentiment according to Akavibe/Token Metrics.
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
        
    except requests.exceptions.RequestException as e:
        print('Connection error:', str(e))
        return jsonify({
            "error": f"Connection error: {str(e)}",
            "type": type(e).__name__
        }), 500
    except Exception as e:
        print('Error:', str(e))
        return jsonify({
            "error": str(e),
            "type": type(e).__name__
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')