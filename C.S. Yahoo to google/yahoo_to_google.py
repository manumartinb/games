import yfinance as yf
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import math
import pandas as pd
import time

def fetch_yahoo_data(ticker, expiry_date):
    opt = yf.Ticker(ticker).option_chain(date=expiry_date)

    opt.calls["lastTradeDate"] = opt.calls["lastTradeDate"].astype(str)
    opt.puts["lastTradeDate"] = opt.puts["lastTradeDate"].astype(str)

    opt.calls["Option Type"] = "CALL"
    opt.puts["Option Type"] = "PUT"

    return {"calls": opt.calls.to_dict(orient="records"), "puts": opt.puts.to_dict(orient="records")}

def send_to_google_sheet(ticker):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("C:/Users/ManuNewPC/Desktop/Script/creds.json", scope)
    client = gspread.authorize(creds)
    spreadsheet = client.open("scraping")

    for ws in spreadsheet.worksheets():
        if ws.title != "control":
            spreadsheet.del_worksheet(ws)

    ticker_obj = yf.Ticker(ticker)
    all_expiry_dates = ticker_obj.options

    for expiry_date in all_expiry_dates:
        formatted_date = pd.to_datetime(expiry_date).strftime('%d%b%y').upper()
        worksheet = spreadsheet.add_worksheet(title=formatted_date, rows="1000", cols="20")
        
        headers = ["ask", "bid", "lastPrice", "volume", "impliedVolatility", "openInterest", "strike", "Option Type"]
        worksheet.append_row(headers)

        data_dict = fetch_yahoo_data(ticker, expiry_date)
        rows = []

        for option_type in ['calls', 'puts']:
            for data in data_dict[option_type]:
                for key, value in data.items():
                    if isinstance(value, float):
                        if math.isnan(value) or math.isinf(value) or value > 1.7e308 or value < -1.7e308:
                            data[key] = 0
                row = [data.get(header, "") for header in headers]
                rows.append(row)

        for i in range(0, len(rows), 20):
            worksheet.append_rows(rows[i:i+20])
            time.sleep(2)

if __name__ == "__main__":
    send_to_google_sheet("AMC")
