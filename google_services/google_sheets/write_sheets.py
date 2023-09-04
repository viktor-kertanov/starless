from googleapiclient.discovery import build
from google_services.authorization.get_oauth_creds import get_creds

def write_to_spreadsheet(chart, spreadsheet_id: str, sheet_name: str, dimension='ROWS'):
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)
    # mySpreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
    
    value_range_body = {
    'majorDimension': dimension,
    'values': chart}

    workrange = f'{sheet_name}'

    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        valueInputOption='USER_ENTERED',
        range=workrange,
        body = value_range_body
    ).execute()


def append_to_spreadsheet(chart, spreadsheet_id: str, sheet_name: str, dimension='ROWS'):
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)
    
    value_range_body = {
    'majorDimension': dimension,
    'values': chart}

    workrange = f'{sheet_name}'

    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        valueInputOption='USER_ENTERED',
        range=workrange,
        body = value_range_body
    ).execute()

if __name__ == '__main__':
    values = [['1','viktor','kertanov','testing','script'], ['2','lol','rofl','blah','nah']]
    append_to_spreadsheet(values, '1Y2iZBPrEeS9q31UaSD9dnVntqhB5YqCAf3nXIMn1XyY', 'music insights')
