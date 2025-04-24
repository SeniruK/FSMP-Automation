# Routes

from flask import Blueprint, render_template, request, jsonify, session
import pandas as pd
from .database import pull_table_names, get_table_data
from .calculateFSMP import calculateIATModifiedTotalLife

bp = Blueprint("main", __name__)

@bp.route("/")
def index():
    return render_template("index.html", years=[2024, 2023, 2022, 2021, 2020])

@bp.route("/pull_tables", methods=["POST"])
def pull_tables():
    FSMPyear = request.json["year"]
    pulled_table_names = pull_table_names(FSMPyear)

    session["FSMPyear"] = FSMPyear
    session["table_names"] = pulled_table_names["tables"]
    return jsonify(pulled_table_names)

@bp.route("/get_table", methods=["POST"])
def get_table():
    table_name = request.json["table_name"]
    FSMPyear = request.json.get("FSMPyear")
    data = get_table_data(table_name, FSMPyear)
    return jsonify(data)

@bp.route("/calculate")
def calculate_page():
    FSMPyear = int(session.get("FSMPyear"))
    if not FSMPyear:
        return "No FSMP year selected", 400

    table_names = session.get("table_names")
    if not table_names:
        return "No tables pulled", 400

    dataframes = {}
    for name in table_names:
        data = get_table_data(name, FSMPyear)
        df = pd.DataFrame(data)
        dataframes[name] = df

    trkpt_list = dataframes[f"IAT_TRKPT_{FSMPyear}"]["TRKPT"].tolist()
    ctrlpt_list = dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
    acsn_list = dataframes["AC_Status_List"]["ACSN"].tolist()
    
    dataframes["IAT Modified Total Life"] = calculateIATModifiedTotalLife(FSMPyear, dataframes)

    result = {
        "message": "Calculation complete!",
        "summary": {name: len(df) for name, df in dataframes.items()}
    }

    return render_template("calculation.html", result=result)