# FSMP Calculation logic

'''
Function to calculate Modified IAT Life

Input(s):
- Database 1: ACSN, IAT TrkPt, DT Total Life, Rpt Per
- Database 2: IAT TrkPt, IAT TrkPt DT Life, TrkPt Identification Number
- Database 3: CP Name (equivalent to IAT TrkPt), Updated CP DT Life, TrkPt Identification Number
- Database 4: ACSN, Active/Inactive, IAT Period

Output(s):
- DataFrame 1: Modified IAT Life
'''

def calculateIATModifiedTotalLife(FSMPyear, db_dataframes, fsmp_dataframes):
    import pandas as pd
    
    IATyear = FSMPyear - 1
    df_damagefile = db_dataframes[f"DAMGEFL{IATyear}per2"].set_index(["ACSN", "TRKPT"])
    df_iat_trkpt = db_dataframes[f"IAT_TRKPT_{FSMPyear}"].set_index("TRKPT")
    df_scale_factors = db_dataframes["Normalized_Scale_Factors"].set_index("TRKPT")
    df_cp_ref = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"].set_index("CTRLPT")
    
    trkpt_list = db_dataframes[f"IAT_TRKPT_{FSMPyear}"]["TRKPT"].tolist()
    ctrlpt_list = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
    acsn_list = db_dataframes["AC_Status_List"]["ACSN"].tolist()
    ctrlpt_dict = {'W15LH': 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    col_list = ["ACSN"] + trkpt_list
    trkpt_list_unique = df_damagefile.index.unique("TRKPT")

    df_iat_modified_total_life = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for trkpt in trkpt_list:
            if trkpt not in trkpt_list_unique:
                modified_total_life = pd.NA
                df_list.append(modified_total_life)
            else:
                tlife = df_damagefile.loc[(acsn, trkpt), "TLIFE_DT"]
                iat_latest = df_iat_trkpt.loc[trkpt, "IAT DT"]
                dt_latest = df_cp_ref.loc[ctrlpt_dict[trkpt], "Production Life"]
                iat_ratio = dt_latest/iat_latest
                scale_factor = df_scale_factors.loc[trkpt, "Factor"]
                modified_total_life = tlife * iat_ratio * scale_factor
                df_list.append(modified_total_life)
        df_iat_modified_total_life.loc[len(df_iat_modified_total_life)] = df_list

    return df_iat_modified_total_life.set_index("ACSN")

'''
Function to calculate CP DT Life

Input(s):
- DataFrame 1: Modified Total Life (ACSN, TrkPt ID Num)
- Database 3: CP DT Life (CP Name, TrkPt ID Num)

Output(s):
- DataFrame 2: CP DT Life
'''

def calculateCPDTLife(FSMPyear, db_dataframes, fsmp_dataframes):
    import pandas as pd
    import numpy as np

    IATyear = FSMPyear - 1
    df_iat_modified_total_life = fsmp_dataframes["iat_modified_total_life"]
    df_damagefile = db_dataframes[f"DAMGEFL{IATyear}per2"].set_index(["ACSN", "TRKPT"])
    df_iat_trkpt = db_dataframes[f"IAT_TRKPT_{FSMPyear}"].set_index("TRKPT")
    df_cp_ref = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"].set_index("CTRLPT")
    
    ctrlpt_list = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
    acsn_list = db_dataframes["AC_Status_List"]["ACSN"].tolist()
    ctrlpt_dict = {'W15LH': 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    col_list = ["ACSN"] + ctrlpt_list
    trkpt_list_unique = df_damagefile.index.unique("TRKPT")

    df_cp_dt_life = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for ctrlpt in ctrlpt_list:
            trkpt_id = df_cp_ref.loc[ctrlpt, "TRKPT ID Number"]
            trkpt = df_iat_trkpt[df_iat_trkpt["TRKPT ID Number"]==trkpt_id].index.values[0]
            if trkpt not in trkpt_list_unique:
                cp_dt_life = pd.NA
                df_list.append(cp_dt_life)
            else:
                dt_latest = df_cp_ref.loc[ctrlpt_dict[trkpt], "Production Life"]
                modified_total_life = df_iat_modified_total_life.loc[acsn, trkpt]
                cp_production_life = df_cp_ref.loc[ctrlpt, "Production Life"]
                cp_dt_life = modified_total_life * cp_production_life / dt_latest
                df_list.append(cp_dt_life)
        df_cp_dt_life.loc[len(df_cp_dt_life)] = df_list

    return df_cp_dt_life.set_index("ACSN")

'''
Function to calculate CP Follow-on Lives

Input(s):
- DataFrame 1: Modified Total Life (ACSN, TrkPt ID Num)
- Database 3: CP DT Life (CP Name, TrkPt ID Num)
- Database 3: CP Follow-on DT Life (CP Name, TrkPt ID Num)

Output(s):
- DataFrame 3: CP Follow-on Life
'''

def calculateCPFollowonLife(FSMPyear, db_dataframes, fsmp_dataframes):
    import pandas as pd
    import numpy as np

    IATyear = FSMPyear - 1
    df_iat_modified_total_life = fsmp_dataframes["iat_modified_total_life"]
    df_cp_dt_life = fsmp_dataframes["cp_dt_life"]
    df_damagefile = db_dataframes[f"DAMGEFL{IATyear}per2"].set_index(["ACSN", "TRKPT"])
    df_iat_trkpt = db_dataframes[f"IAT_TRKPT_{FSMPyear}"].set_index("TRKPT")
    df_cp_ref = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"].set_index("CTRLPT")
    df_special_inspections = db_dataframes[f"Special_Inspections_{FSMPyear}"].set_index("ACSN")
    
    ctrlpt_list = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
    acsn_list = db_dataframes["AC_Status_List"]["ACSN"].tolist()
    ctrlpt_dict = {'W15LH': 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    col_list = ["ACSN"] + ctrlpt_list
    trkpt_list_unique = df_damagefile.index.unique("TRKPT")

    df_cp_followon_life = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for ctrlpt in ctrlpt_list:
            trkpt_id = df_cp_ref.loc[ctrlpt, "TRKPT ID Number"]
            trkpt = df_iat_trkpt[df_iat_trkpt["TRKPT ID Number"]==trkpt_id].index.values[0]
            if trkpt not in trkpt_list_unique:
                cp_followon_life = pd.NA
                df_list.append(cp_followon_life)
            else:
                dt_latest = df_cp_ref.loc[ctrlpt_dict[trkpt], "Production Life"]
                modified_total_life = df_iat_modified_total_life.loc[acsn, trkpt]
                cp_followon_dt = df_cp_ref.loc[ctrlpt, "Follow-on DT Life"]
                if cp_followon_dt == "SPECIAL":
                    cp_followon_dt = df_special_inspections.loc[acsn, ctrlpt]
                cp_followon_life = modified_total_life * float(cp_followon_dt) / dt_latest
                df_list.append(cp_followon_life)
        df_cp_followon_life.loc[len(df_cp_followon_life)] = df_list

    return df_cp_followon_life.set_index("ACSN")

'''
Function to calculate Inspection Intervals

Input(s):
- DataFrame 2: FSMP CP DT Life (ACSN, CP Name)
- Database 3: Inspection Safety Factor (CP Name) or Follow-on Inspection Safety Factor (CP Name)
- Database 5: Hours at Last Inspection (ACSN, CP Name)

Output(s):
- DataFrame 4: Inspection Intervals
'''

def calculateInspectionIntervals(FSMPyear, db_dataframes, fsmp_dataframes):
    import pandas as pd

    IATyear = FSMPyear - 1
    df_cp_dt_life = fsmp_dataframes["cp_dt_life"]
    df_cp_followon_life = fsmp_dataframes["cp_follow_on_life"]
    df_damagefile = db_dataframes[f"DAMGEFL{IATyear}per2"].set_index(["ACSN", "TRKPT"])
    df_iat_trkpt = db_dataframes[f"IAT_TRKPT_{FSMPyear}"].set_index("TRKPT")
    df_cp_ref = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"].set_index("CTRLPT")
    df_inspection_table = db_dataframes[f"Inspection_Table_{FSMPyear}"].set_index(["ACSN", "CTRLPT"])
    
    ctrlpt_list = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
    acsn_list = db_dataframes["AC_Status_List"]["ACSN"].tolist()
    ctrlpt_dict = {'W15LH': 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    col_list = ["ACSN"] + ctrlpt_list
    trkpt_list_unique = df_damagefile.index.unique("TRKPT")

    df_inspection_intervals = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for ctrlpt in ctrlpt_list:
            trkpt_id = df_cp_ref.loc[ctrlpt, "TRKPT ID Number"]
            trkpt = df_iat_trkpt[df_iat_trkpt["TRKPT ID Number"]==trkpt_id].index.values[0]
            if trkpt not in trkpt_list_unique:
                inspection_interval = pd.NA
                df_list.append(inspection_interval)
            else:
                hrs_at_last_inspection = df_inspection_table.loc[(acsn, ctrlpt), "Hours at Last Inspection"]
                if (hrs_at_last_inspection in [0, "0", "?", "", " ", None]) or (pd.isnull(hrs_at_last_inspection)): # LOOK HERE: MAKE THIS LESS SPECIFIC
                    cp_dt_life = df_cp_dt_life.loc[acsn, ctrlpt]
                    sf_initial_inspection = df_cp_ref.loc[ctrlpt, "Safety Factor Initial Inspection"]
                    inspection_interval = cp_dt_life / sf_initial_inspection
                    df_list.append(inspection_interval)
                else:
                    cp_followon_life = df_cp_followon_life.loc[acsn, ctrlpt]
                    sf_followon_inspection = df_cp_ref.loc[ctrlpt, "Safety Factor Follow-on Inspection"]
                    inspection_interval = cp_followon_life / sf_followon_inspection
                    df_list.append(inspection_interval)
        df_inspection_intervals.loc[len(df_inspection_intervals)] = df_list

    return df_inspection_intervals.set_index("ACSN")

'''
Function to calculate Hours at Next Inspection

Input(s):
- DataFrame 4: Inspection Intervals (ACSN, CP Name)
- Database 5: Hours at Last Inspection (ACSN)

Output(s):
- DataFrame 5: Hours at Next Inspection
'''

def calculateHoursAtNextInspection(FSMPyear, db_dataframes, fsmp_dataframes):
    import pandas as pd

    IATyear = FSMPyear - 1
    df_inspection_intervals = fsmp_dataframes["inspection_intervals"]
    df_damagefile = db_dataframes[f"DAMGEFL{IATyear}per2"].set_index(["ACSN", "TRKPT"])
    df_iat_trkpt = db_dataframes[f"IAT_TRKPT_{FSMPyear}"].set_index("TRKPT")
    df_cp_ref = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"].set_index("CTRLPT")
    df_inspection_table = db_dataframes[f"Inspection_Table_{FSMPyear}"].set_index(["ACSN", "CTRLPT"])
    
    ctrlpt_list = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
    acsn_list = db_dataframes["AC_Status_List"]["ACSN"].tolist()
    ctrlpt_dict = {'W15LH': 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    col_list = ["ACSN"] + ctrlpt_list
    trkpt_list_unique = df_damagefile.index.unique("TRKPT")

    df_hrs_at_next_inspection = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for ctrlpt in ctrlpt_list:
            trkpt_id = df_cp_ref.loc[ctrlpt, "TRKPT ID Number"]
            trkpt = df_iat_trkpt[df_iat_trkpt["TRKPT ID Number"]==trkpt_id].index.values[0]
            if trkpt not in trkpt_list_unique:
                hrs_at_next_inspection = pd.NA
                df_list.append(hrs_at_next_inspection)
            else:
                inspection_intervals = df_inspection_intervals.loc[acsn, ctrlpt]
                hrs_at_last_inspection = df_inspection_table.loc[(acsn, ctrlpt), "Hours at Last Inspection"]
                if (hrs_at_last_inspection in [0, "0", "?", "", " ", None]) or (pd.isnull(hrs_at_last_inspection)): # LOOK HERE: MAKE THIS LESS SPECIFIC
                    hrs_at_last_inspection = 0
                hrs_at_next_inspection = inspection_intervals + float(hrs_at_last_inspection)
                df_list.append(hrs_at_next_inspection)
        df_hrs_at_next_inspection.loc[len(df_hrs_at_next_inspection)] = df_list

    return df_hrs_at_next_inspection.set_index("ACSN")

'''
Function to calculate Hours to Next Inspection

Input(s):
- DataFrame 5: Hours at Next Inspection (ACSN, CP Name)
- Database 1: Component Hours (ACSN, TrkPt)

Output(s):
- DataFrame 6: Hours to Next Inspection
'''

def calculateHoursToNextInspection(FSMPyear, db_dataframes, fsmp_dataframes):
    import pandas as pd

    IATyear = FSMPyear - 1
    df_hrs_at_next_inspection = fsmp_dataframes["hours_at_next_inspection"]
    df_damagefile = db_dataframes[f"DAMGEFL{IATyear}per2"].set_index(["ACSN", "TRKPT"])
    df_iat_trkpt = db_dataframes[f"IAT_TRKPT_{FSMPyear}"].set_index("TRKPT")
    df_cp_ref = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"].set_index("CTRLPT")
    
    ctrlpt_list = db_dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
    acsn_list = db_dataframes["AC_Status_List"]["ACSN"].tolist()
    ctrlpt_dict = {'W15LH': 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    col_list = ["ACSN"] + ctrlpt_list
    trkpt_list_unique = df_damagefile.index.unique("TRKPT")

    df_hrs_to_next_inspection = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for ctrlpt in ctrlpt_list:
            trkpt_id = df_cp_ref.loc[ctrlpt, "TRKPT ID Number"]
            trkpt = df_iat_trkpt[df_iat_trkpt["TRKPT ID Number"]==trkpt_id].index.values[0]
            if trkpt not in trkpt_list_unique:
                hrs_to_next_inspection = pd.NA
                df_list.append(hrs_to_next_inspection)
            else:
                hrs_at_last_inspection = df_hrs_at_next_inspection.loc[acsn, ctrlpt]
                component_hours = df_damagefile.loc[(acsn, trkpt), "CMPHRS"]
                hrs_to_next_inspection = hrs_at_last_inspection - component_hours
                df_list.append(hrs_to_next_inspection)
        df_hrs_to_next_inspection.loc[len(df_hrs_to_next_inspection)] = df_list

    return df_hrs_to_next_inspection.set_index("ACSN")