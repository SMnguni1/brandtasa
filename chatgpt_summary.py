import openai
from dotenv import load_dotenv
import os
from queries import QUERIES
from utils import summarize_response, append_to_sheet
from datetime import datetime

load_dotenv()
openai.api_key = os.getenv('OPENAI_API_KEY')

def query_chatgpt(question):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful tax advisor tasked with providing detailed information about tax consulting services in South Africa. Mention specific firms where relevant."},
            {"role": "user", "content": question}
        ],
        max_tokens=1000
    )
    return response.choices[0].message.content

results = []
for query in QUERIES:
    try:
        full_response = query_chatgpt(query)
        summary = summarize_response(full_response, query)
        results.append([
            datetime.now().isoformat(),
            query,
            summary
        ])
    except Exception as e:
        print(f"Error for {query}: {e}")
        results.append([datetime.now().isoformat(), query, f"Error: {str(e)}"])

if results:
    append_to_sheet(results, 'Summaries')
print("ChatGPT summary tracking complete.")