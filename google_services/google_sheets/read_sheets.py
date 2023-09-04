from googleapiclient.discovery import build
from google_services.authorization.get_oauth_creds import get_creds
import pandas as pd
from config import settings

def read_google_sheet(spreadsheet_id, sheet_name):
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)

    response = service.spreadsheets().values().get(
        spreadsheetId = spreadsheet_id,
        majorDimension = 'ROWS',
        range = sheet_name
    ).execute()

    values = response["values"]
    return pd.DataFrame(data=values[1:], columns=values[0])

# """
# batch.get method
# """

# value_ranges_body = [
#     'europe!A1:C10',
#     'america!A1:C10',
#     'asia!A1:C10',
#     'africa!A1:C10'
# ]

# response = service.spreadsheets().values().batchGet(
#     spreadsheetId = COUNTRY_SHEET_ID,
#     majorDimension = 'ROWS',
#     ranges = value_ranges_body
# ).execute()

# print(response['valueRanges'])

if __name__ == '__main__':
    values = read_google_sheet(settings.sample_machine_sheet_id, "playlists")
    print('Hello World!')