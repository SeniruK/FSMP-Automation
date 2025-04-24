# Communicate with Access Database

import os
import glob
import pyodbc

cwd = os.getcwd()
DB_PATH = glob.glob(os.path.join(cwd, "*.accdb"))[0]

def connect_db():
    connection_string = (f'DRIVER={{Microsoft Access Driver (*.mdb, *.accdb)}};DBQ={DB_PATH};')
    return pyodbc.connect(connection_string)

def pull_table_names(FSMPyear):
    conn = connect_db()
    cursor = conn.cursor()
    tables = ["Normalized_Scale_Factors", "AC_Status_List"]
    for row in cursor.tables(tableType="TABLE"):
        name = row.table_name
        if ("DAMGEFL" in name) and (str(int(FSMPyear)-1) in name):
            tables.append(name)
        elif ("DAMGEFL" in name) and (str(FSMPyear) in name):
            continue
        elif str(FSMPyear) in name:
            tables.append(name)
    conn.close()
    return {"success": [f"Successfully pulled: {t}" for t in tables], "tables": tables}

def get_table_data(table_name, FSMPyear=None):
    conn = connect_db()
    cursor = conn.cursor()
    if table_name == "Normalized_Scale_Factors" and FSMPyear:
        query = f"SELECT * FROM [{table_name}] WHERE Year = ?"
        cursor.execute(query, (int(FSMPyear) - 1,))
    elif table_name == "AC_Status_List" and FSMPyear:
        query = f"SELECT * FROM [{table_name}] WHERE FILENAME = ?"
        cursor.execute(query, (f"BASICFL{int(FSMPyear) - 1}per2",))
    else:
        query = f"SELECT * FROM [{table_name}]"
        cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows = cursor.fetchall()
    data = [dict(zip(columns, row)) for row in rows]
    conn.close()
    return data