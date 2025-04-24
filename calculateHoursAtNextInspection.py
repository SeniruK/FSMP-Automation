'''
Function to calculate Hours at Next Inspection

Input(s):
- DataFrame 4: Inspection Intervals (ACSN, CP Name)
- Database 5: Hours at Last Inspection (ACSN)

Output(s):
- DataFrame 5: Hours at Next Inspection
'''

def calculateHoursAtNextInspection(df_inspection_intervals, df_inspection_table, df_damagefile, df_iat_trkpt, df_cp_ref, ctrlpt_list, acsn_list):
    import pandas as pd

    col_list = ['ACSN'] + ctrlpt_list
    ctrlpt_dict = {"W15LH": 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    trkpt_list_unique = df_damagefile["TRKPT"].unique()

    df_hrs_at_next_inspection = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for ctrlpt in ctrlpt_list:
            trkpt_id = df_cp_ref.loc[(df_cp_ref["CTRLPT"]==ctrlpt)].iloc[0]["TRKPT ID Number"]
            trkpt = df_iat_trkpt.loc[(df_iat_trkpt["TRKPT ID Number"]==trkpt_id)].iloc[0]["TRKPT"]
            if trkpt not in trkpt_list_unique:
                hrs_at_next_inspection = pd.NA
                df_list.append(hrs_at_next_inspection)
            else:
                inspection_intervals = df_inspection_intervals.loc[df_inspection_intervals["ACSN"]==acsn].iloc[0][ctrlpt]
                hrs_at_last_inspection = df_inspection_table.loc[(df_inspection_table["ACSN"]==acsn) & (df_inspection_table["CTRLPT"]==ctrlpt)].iloc[0]["Hours at Last Inspection"]
                # print(f"LAST Inspection: {hrs_at_last_inspection}")
                if (hrs_at_last_inspection in [0, "0", "?", "", " ", None]) or (pd.isnull(hrs_at_last_inspection)): # LOOK HERE: MAKE THIS LESS SPECIFIC
                    hrs_at_last_inspection = 0
                hrs_at_next_inspection = inspection_intervals + float(hrs_at_last_inspection)
                # print(f"NEXT Inspection: {hrs_at_next_inspection}")
                df_list.append(hrs_at_next_inspection)
        df_hrs_at_next_inspection.loc[len(df_hrs_at_next_inspection)] = df_list

    return df_hrs_at_next_inspection