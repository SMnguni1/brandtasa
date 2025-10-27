import os
from datetime import datetime
from dotenv import load_dotenv
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

def analyze_response(response_text, brand="Tax Consulting South Africa"):
    lower_resp = response_text.lower()
    lower_brand = brand.lower()
    mention = "Yes" if lower_brand in lower_resp else "No"
    score = 0
    if mention == "Yes":
        pos = lower_resp.find(lower_brand)
        if pos < 100:
            score = 10
        elif "recommend" in lower_resp or "top" in lower_resp:
            score = 7
        else:
            score = 5
    excerpt = response_text[:200] + "..." if mention == "Yes" else "No mention found"
    return mention, score, excerpt

def summarize_response(response_text, query, brand="Tax Consulting South Africa"):
    lower_resp = response_text.lower()
    lower_brand = brand.lower()
    summary = f"Regarding the query '{query[:50]}...', the response "
    if lower_brand in lower_resp:
        snippet = response_text[max(0, lower_resp.find(lower_brand) - 50):lower_resp.find(lower_brand) + 100]
        summary += f"mentions {brand}. The mention occurs in the context: '{snippet}...'. "
        if "recommend" in lower_resp or "top" in lower_resp:
            summary += f"This suggests {brand} is viewed positively, possibly as a recommended or leading firm. "
        else:
            summary += f"The mention is neutral, part of a broader discussion on tax services. "
        summary += "This visibility could be leveraged for marketing."
    else:
        summary += f"does not mention {brand}. It focuses on general tax services or other firms in South Africa. "
        summary += "This indicates a potential gap in brand visibility for this query. "
        summary += "Consider optimizing content to increase mentions in such contexts."
    return summary

def append_to_sheet(data_list, sheet_name):
    scopes = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file('credentials/service_account.json', scopes=scopes)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.getenv('SHEET_ID')).worksheet(sheet_name)
    sheet.append_rows(data_list)

def read_from_sheet(sheet_name):
    scopes = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    creds = Credentials.from_service_account_file('credentials/service_account.json', scopes=scopes)
    client = gspread.authorize(creds)
    try:
        sheet = client.open_by_key(os.getenv('SHEET_ID')).worksheet(sheet_name)
        data = sheet.get_all_records()  # Reads as list of dicts
        import pandas as pd
        df = pd.DataFrame(data)
        return df
    except Exception as e:
        print(f"Error reading {sheet_name}: {e}")
        return pd.DataFrame()  # Empty DataFrame on error
    