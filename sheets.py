import gspread
import credentials
import config

gc = gspread.service_account_from_dict(credentials.serviceAccountKey)
sheet = gc.open_by_key(config.sheetID)
