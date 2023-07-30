#questo è il file che legge il file excel è lo carica su sqlite

import from_excel_to_sqlite

#qui legge il database di sqlite 

import read_db

#il path di excel (quello inserito è di esampio ma per testarlo su un altro computer è da cambiare)

excel_path = r"C:\Users\Giovanni\Desktop\demo\dati.xlsx"

#qui nella funzione devo solo passare il path

from_excel_to_sqlite.create_and_load_db(excel_path)

#in questa funzione non dobbiamo passare nulla in input, ed abbiamo in output il pandas db

df = read_db.read_df()

print(df)