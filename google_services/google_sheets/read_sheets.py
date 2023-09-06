from googleapiclient.discovery import build
from google_services.authorization.get_oauth_creds import get_creds
import pandas as pd
from config import settings
from itertools import zip_longest

def read_google_sheet(spreadsheet_id, sheet_name) -> pd.DataFrame:
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)

    response = service.spreadsheets().values().get(
        spreadsheetId = spreadsheet_id,
        majorDimension = 'ROWS',
        range = sheet_name
    ).execute()

    values = response["values"]
    headers = values[0]
    data = values[1:]

    return pd.DataFrame(data=data, columns=headers)

def read_google_sheet_to_dict(spreadsheet_id, sheet_name) -> list[dict]:
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)

    response = service.spreadsheets().values().get(
        spreadsheetId = spreadsheet_id,
        majorDimension = 'ROWS',
        range = sheet_name
    ).execute()

    values = response["values"]
    headers = values[0]
    data = values[1:]

    data_dict = [dict(zip_longest(headers, row, fillvalue=None)) for row in data]

    return data_dict


if __name__ == '__main__':
    data = read_google_sheet(settings.sample_machine_sheet_id, "playlists")
    dict_format = data.to_dict(orient='records')
    print('Hello World!')