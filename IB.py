from ib_insync import *
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

def extract_option_data(option_data_list):
    extracted_data = []
    for option_data in option_data_list:
        contract = option_data.contract
        symbol = contract.symbol
        price = str(option_data.last) if option_data.last else "N/A"  # Convertir el precio a una cadena
        expiry = contract.lastTradeDateOrContractMonth
        data_to_export = [symbol, price, expiry]
        extracted_data.append(data_to_export)
    return extracted_data

def export_to_google_sheets(extracted_data):
    # Resto del código sin cambios...

def main():
    # Create a new IB session
    util.startLoop()
    ib = IB()
    ib.connect('127.0.0.1', 7497, clientId=0)

    # Define the AAPL option contract
    contract = Option('AAPL', exchange='SMART', currency='USD')

    # Request delayed market data for the option
    ib.qualifyContracts(contract)
    ticker = ib.reqMktData(contract, '', False, False)

    print("Waiting for data...")  # Depuración: Verificar que se esté esperando por datos
    # Wait for some time to collect data (adjust as needed)
    ib.sleep(5)

    print("Data received:", ticker)  # Depuración: Verificar los datos recibidos
    # Disconnect from IB
    ib.disconnect()

    # Extract the option data and export to Google Sheets
    extracted_data = extract_option_data(ticker)
    export_to_google_sheets(extracted_data)

if __name__ == "__main__":
    main()
