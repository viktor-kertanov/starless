def create_sheets(sheet_names: list[str]):
    sheets_output = []
    sheet_names = [str(sheet) for sheet in sheet_names if sheet]
    
    for sheet in sheet_names:
        row = {
            'properties': {
                'title': sheet
                }
            }
        sheets_output.append(row)
    return sheets_output

def create_spreadsheet(title, sheet_names=['First sheet'], autoRecalc='MINUTE'):
    
    spreadsheet = {
    'properties': {
        'title': title,
        'locale': 'en_US',
        'autoRecalc': autoRecalc
        },
    }
    spreadsheet['sheets'] = create_sheets(sheet_names)

    return spreadsheet

if __name__ == '__main__':
    a = create_spreadsheet('Music', sheet_names=['First sheet', 'Second sheet'])
    print(a)