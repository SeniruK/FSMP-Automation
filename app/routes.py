# Routes

from flask import Blueprint, render_template, request, jsonify, session, send_file, current_app
import zipfile
import io
import os
import pandas as pd
from .database import pull_table_names, get_table_data
from .calculateFSMP import calculateIATModifiedTotalLife, calculateCPDTLife, calculateCPFollowonLife, calculateInspectionIntervals, calculateHoursAtNextInspection, calculateHoursToNextInspection
from .compare_outputs import run_all_calculations

bp = Blueprint("main", __name__)

calculated_tables = {}

@bp.route("/")
def index():
    return render_template("index.html", years=[2025, 2024, 2023, 2022, 2021, 2020])

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

@bp.route("/run_step/<calculation_step>", methods=["POST"])
def run_step(calculation_step):
    global calculated_tables

    FSMPyear = session.get("FSMPyear")
    table_names = session.get("table_names")
    
    if not FSMPyear or not table_names:
        return jsonify({"error": "Missing year or table data"}), 400
    
    FSMPyear = int(FSMPyear)

    db_dataframes = {}
    for name in table_names:
        data = get_table_data(name, FSMPyear)
        df = pd.DataFrame(data)
        db_dataframes[name] = df
    
    # fsmp_dataframes = {}
    fsmp_functions = {
        "iat_modified_total_life": calculateIATModifiedTotalLife,
        "cp_dt_life": calculateCPDTLife,
        "cp_follow_on_life": calculateCPFollowonLife,
        "inspection_intervals": calculateInspectionIntervals,
        "hours_at_next_inspection": calculateHoursAtNextInspection,
        "hours_to_next_inspection": calculateHoursToNextInspection
    }

    if calculation_step not in fsmp_functions:
        return jsonify({"error": f"Invalid calculation step: {calculation_step}"}), 400
    
    result_df = fsmp_functions[calculation_step](FSMPyear, db_dataframes, calculated_tables)
    calculated_tables[calculation_step] = result_df
    # print(calculated_tables[calculation_step])

    return jsonify({"message": f"'{calculation_step}' complete!"})

@bp.route("/view_table/<table_name>")
def view_table(table_name):
    global calculated_tables

    if table_name not in calculated_tables:
        return jsonify({"error": f"Table '{table_name}' not found."}), 404
    
    df = calculated_tables[table_name].round(0)
    return df.to_html(classes="table table-striped", index=False)

@bp.route("/save_excel", methods=["POST"])
def save_excel():
    global calculated_tables
    FSMPyear = session["FSMPyear"]

    if not calculated_tables:
        return "No FSMP calculated tables found", 400
    
    output_path = os.path.join(current_app.root_path, "downloads\Excel")
    os.makedirs(output_path, exist_ok=True)

    file_path = os.path.join(output_path, f"FSMP_Calculations_{FSMPyear}.xlsx")

    with pd.ExcelWriter(file_path, engine="openpyxl") as writer:
        for name, df in calculated_tables.items():
            safe_name = name[:31].replace("/", "_")
            df.set_index("ACSN").to_excel(writer, sheet_name=safe_name, index=True)
    
    return f"Saved Excel to {file_path}", 200

@bp.route("/save_csv", methods=["POST"])
def save_csv():
    global calculated_tables
    FSMPyear = session["FSMPyear"]

    if not calculated_tables:
        return "No FSMP calculated tables found", 400
    
    output_path = os.path.join(current_app.root_path, "downloads\CSV")
    os.makedirs(output_path, exist_ok=True)

    for name, df in calculated_tables.items():
        safe_name = name[:31].replace("/", "_")
        file_path = os.path.join(output_path, f"{safe_name}_{FSMPyear}.csv")
        df.to_csv(file_path, index=False)
    
    return f"Saved CSVs to {file_path}", 200

@bp.route("/download_comparison_excel", methods=["POST"])
def download_comparison_excel():
    global calculated_tables

    FSMPyear = int(session.get("FSMPyear"))
    prevFSMPyear = FSMPyear - 1
    table_names = session.get("table_names")

    if not FSMPyear or not prevFSMPyear or not table_names:
        return jsonify({"error": "Missing FSMP year or table names"}), 400
    
    current_year_results = run_all_calculations(FSMPyear, table_names)
    previous_year_results = run_all_calculations(prevFSMPyear, table_names)

    df_current = current_year_results.get("hours_at_next_inspection")
    df_previous = previous_year_results.get("hours_at_next_inspection")

    if df_current is None or df_previous is None:
        return jsonify({"error": "Missing calculated data for comparison"}), 500

    downloads_dir = os.path.join(os.get.getcwd(), "downloads/COMPARE")
    os.makedirs(downloads_dir, exist_ok=True)

    filename = f"COMPARE_{FSMPyear}vs{prevFSMPyear}.xlsx"
    filepath = os.path.join(downloads_dir, filename)

    compareOutputs(df_current, df_previous, filename)

    return jsonify({"message": f"Comparison Excel workbook saved to downloads folder as {filename}."})
    