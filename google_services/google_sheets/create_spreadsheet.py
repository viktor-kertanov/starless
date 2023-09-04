from googleapiclient.discovery import build
from google_services.authorization.get_oauth_creds import get_creds
from google_services.google_sheets.create_sheet_json import create_spreadsheet

def create_google_spreadsheet(spreadsheet_title: str, sheetnames=['1']):
    creds = get_creds()
    service = build('sheets', 'v4', credentials=creds)

    spreadsheet = create_spreadsheet(spreadsheet_title, sheetnames)

    spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
    print(f"Spreadsheet URL: {spreadsheet['spreadsheetUrl']}")
    
    return spreadsheet['spreadsheetId']


# # The ID and range of a sample spreadsheet.
# SAMPLE_SPREADSHEET_ID = '1z-VmO2k2fW-X5Pk0L2ecBRejvc4kUuWDfdFWK2V5fIY'
# SAMPLE_RANGE_NAME = 'shit!A1:C200'

 # service = build('sheets', 'v4', credentials=creds)

    # # Call the Sheets API
    # sheet = service.spreadsheets()
    # result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
    #                             range=SAMPLE_RANGE_NAME).execute()
    # values = result.get('values', [])

    # if not values:
    #     print('No data found.')
    # else:
    #     for row in values:
    #         # Print columns A and E, which correspond to indices 0 and 4.
    #         for cell in row:
    #             print(cell)

    # result = service.spreadsheets().values().get(
    #     spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME).execute()
    # rows = result.get('values', [])
    # print('{0} rows retrieved.'.format(len(rows)))

# #writing to a google sheet
# rows_to_write = [
#     ['bbb','ddd','cbnc'],
#     [1000,2000,3000],
#     ['latter', 'former', 'barber']
# ]
#
# body = {
#     'values': rows_to_write
# }
#
# result = service.spreadsheets().values().append(
#     spreadsheetId=SAMPLE_SPREADSHEET_ID, range=SAMPLE_RANGE_NAME,
#     valueInputOption=value_input_option, body=body).execute()
# print('{0} cells appended.'.format(result \
#                                        .get('updates') \
#                                        .get('updatedCells')))

if __name__ == '__main__':
    create_google_spreadsheet('16th June 22', [1,2,3,4])