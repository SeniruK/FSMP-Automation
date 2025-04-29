# Routes

from flask import Blueprint, render_template, request, jsonify, session
import pandas as pd
from .database import pull_table_names, get_table_data
from .calculateFSMP import calculateIATModifiedTotalLife, calculateCPDTLife, calculateCPFollowonLife, calculateInspectionIntervals, calculateHoursAtNextInspection, calculateHoursToNextInspection

bp = Blueprint("main", __name__)

calculated_tables = {}

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
def show_calculate_page():
    return render_template("calculation.html")

# @bp.route("/run_calculations", methods=["POST"])
# def run_calculations_route():
#     global calculated_tables
#     FSMPyear = int(session.get("FSMPyear"))
#     if not FSMPyear:
#         return "No FSMP year selected", 400

#     table_names = session.get("table_names")
#     if not table_names:
#         return "No tables pulled", 400

#     db_dataframes = {}
#     for name in table_names:
#         data = get_table_data(name, FSMPyear)
#         df = pd.DataFrame(data)
#         db_dataframes[name] = df

        
#     trkpt_list = db_dataframes[f"IAT_TRKPT_{FSMPyear}"]["TRKPT"].tolist()
#     ctrlpt_list = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
#     acsn_list = db_dataframes["AC_Status_List"]["ACSN"].tolist()
    
#     fsmp_dataframes = {}
#     fsmp_dataframes["IAT Modified Total Life"] = calculateIATModifiedTotalLife(FSMPyear, db_dataframes)
#     fsmp_dataframes["CP DT Life"] = calculateCPDTLife(FSMPyear, db_dataframes, fsmp_dataframes)
#     fsmp_dataframes["CP Follow-on Life"] = calculateCPFollowonLife(FSMPyear, db_dataframes, fsmp_dataframes)
#     fsmp_dataframes["Inspection Intervals"] = calculateInspectionIntervals(FSMPyear, db_dataframes, fsmp_dataframes)
#     fsmp_dataframes["Hours at Next Inspection"] = calculateHoursAtNextInspection(FSMPyear, db_dataframes, fsmp_dataframes)
#     fsmp_dataframes["Hours to Next Inspection"] = calculateHoursToNextInspection(FSMPyear, db_dataframes, fsmp_dataframes)

#     # session["fsmp_table_names"] = list(fsmp_dataframes.keys())
#     # session["fsmp_tables"] = {name: df.to_dict(orient="records") for name, df in fsmp_dataframes.items()}
#     calculated_tables = fsmp_dataframes

#     return jsonify({"tables": list(fsmp_dataframes.keys())})

@bp.route("/run_step/<calculation_step>", methods=["POST"])
def run_step(calculation_step):
    global calculated_tables

    FSMPyear = int(session.get("FSMPyear"))
    table_names = session.get("table_names")
    
    if not FSMPyear or not table_names:
        return jsonify({"error": "Missing year or table data"}), 400

    db_dataframes = {}
    for name in table_names:
        data = get_table_data(name, FSMPyear)
        df = pd.DataFrame(data)
        db_dataframes[name] = df
    
    fsmp_dataframes = {}
    fsmp_functions = {
        "IAT Modified Total Life": calculateIATModifiedTotalLife,
        "CP DT Life": calculateCPDTLife,
        "CP Follow-on Life": calculateCPFollowonLife,
        "Inspection Intervals": calculateInspectionIntervals,
        "Hours at Next Inspection": calculateHoursAtNextInspection,
        "Hours to Next Inspection": calculateHoursToNextInspection
    }

    if calculation_step not in fsmp_functions:
        return jsonify({"error": "Invalid calculation step"}), 400
    
    fsmp_dataframes[calculation_step] = fsmp_functions[calculation_step](FSMPyear, db_dataframes, fsmp_dataframes)
    calculated_tables[calculation_step] = fsmp_dataframes[calculation_step]

    return jsonify({"message": f"{calculation_step} complete!"})

@bp.route("/get_calc_table", methods=["POST"])
def get_calc_table():
    global calculated_tables

    table_name = request.json["table_name"]

    fsmp_tables = session.get("fsmp_tables", {})

    df = calculated_tables.get(table_name)
    if df is None:
        return jsonify([])
    
    return jsonify(df.to_dict(orient="records"))