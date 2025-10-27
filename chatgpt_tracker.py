import openai
from dotenv import load_dotenv
import os
from queries import QUERIES
from utils import analyze_response, append_to_sheet
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def query_chatgpt(question):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful tax advisor. Respond naturally about tax services in South Africa."},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

results = []
for query in QUERIES:
    try:
        full_response = query_chatgpt(query)
        mention, score, excerpt = analyze_response(full_response)
        results.append([
            datetime.now().isoformat(),
            query,
            mention,
            score,
            excerpt,
            full_response[:500]  # Truncate
        ])
    except Exception as e:
        print(f"Error for {query}: {e}")
        results.append([datetime.now().isoformat(), query, "Error", 0, str(e), ""])

if results:
    append_to_sheet(results, 'ChatGPT')
print("ChatGPT tracking complete.")