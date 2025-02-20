import gspread
from google.oauth2.service_account import Credentials


## Google Sheets Init
scope = ["https://www.googleapis.com/auth/spreadsheets"]
credentials = Credentials.from_service_account_file("credentials.json", scopes=scope)
gc = gspread.service_account(filename='credentials.json')

sheet_id = "1NhU9tel9pk23uAjVNpxBUUyodA7I-fWInC7TqP6I5AA"
sheet = gc.open_by_key(sheet_id)

trooperSheet = sheet.worksheet("Trooper")

## I don't understand this monstrosity anymore...
trooperEventValues = trooperSheet.get_values("E20:E")
trooperEventValues = [int(value[0]) if value else 0 for value in trooperEventValues]

trooperStrikesValues = trooperSheet.get_values("G20:G")
trooperStrikesValues = [int(value[0]) if value else 0 for value in trooperStrikesValues]

## Check for events attended, apply strikes if quota wasn't met
for i, v in enumerate(trooperEventValues, start=20):
    if (v < 3):
        strikeValueOffset = trooperStrikesValues[i-20]
        newStrikeValue = strikeValueOffset + 1
        trooperSheet.update_acell(f"G{i}", newStrikeValue)
        
    trooperSheet.update_acell(f"E{i}", 0)