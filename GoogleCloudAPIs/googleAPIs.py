import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials


gspread_client = gspread.service_account(filename='GoogleCloudAPIs/mythic-delight-416415-96828848270c.json')


def get_last_sno(sheet_name: str, worksheet_name: str) -> int:
    """Get the last serial number from a Google Spreadsheet

    :param sheet_name: Name of the Google Spreadsheet
    :param worksheet_name: Name of the worksheet
    :return: Last serial number
    """
    # Open the Google Spreadsheet
    sheet = gspread_client.open(sheet_name)
    
    # Select the worksheet
    worksheet = sheet.worksheet(worksheet_name)
    
    # Get all the data from the worksheet
    data = worksheet.get_all_records()
    
    # Convert the data to a DataFrame
    df = pd.DataFrame(data)
    
    # Get the last serial number
    if '#' not in df.columns or df.empty:
        return 0
    df['#'] = pd.to_numeric(df['#'], errors='coerce')
    df = df.dropna(subset=['#'])
    last_sno = df['#'].max()
    if pd.isna(int(last_sno)):
        return 0
    
    return last_sno

def append_data_spreadsheet(data: list, sheet_name: str, worksheet_name: str) -> bool:
    """Append data to a Google Spreadsheet

    :param data: Data to append
    :param sheet_name: Name of the Google Spreadsheet
    :param worksheet_name: Name of the worksheet
    :return: True if data was appended, else False
    """
    try:
        # Open the Google Spreadsheet
        sheet = gspread_client.open(sheet_name)
        
        # Select the worksheet
        worksheet = sheet.worksheet(worksheet_name)
        
        last_sno: int = int(get_last_sno(sheet_name, worksheet_name))
        # Append the data
        final_data = [last_sno + 1] + data
        worksheet.append_row(final_data)
        print('Data appended successfully')
        return True
    except Exception as e:
        print(e)
        print('Failed to append data')
        return False


