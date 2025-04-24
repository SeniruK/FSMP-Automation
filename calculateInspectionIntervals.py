'''
Function to calculate Inspection Intervals

Input(s):
- DataFrame 2: FSMP CP DT Life (ACSN, CP Name)
- Database 3: Inspection Safety Factor (CP Name) or Follow-on Inspection Safety Factor (CP Name)
- Database 5: Hours at Last Inspection (ACSN, CP Name)

Output(s):
- DataFrame 4: Inspection Intervals
'''

def calculateInspectionIntervals(df_cp_dt_life, df_cp_followon_life, df_inspection_table, df_damagefile, df_iat_trkpt, df_cp_ref, ctrlpt_list, acsn_list):
    import pandas as pd

    col_list = ['ACSN'] + ctrlpt_list
    ctrlpt_dict = {"W15LH": 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    trkpt_list_unique = df_damagefile["TRKPT"].unique()

    df_inspection_intervals = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for ctrlpt in ctrlpt_list:
            trkpt_id = df_cp_ref.loc[(df_cp_ref["CTRLPT"]==ctrlpt)].iloc[0]["TRKPT ID Number"]
            trkpt = df_iat_trkpt.loc[(df_iat_trkpt["TRKPT ID Number"]==trkpt_id)].iloc[0]["TRKPT"]
            if trkpt not in trkpt_list_unique:
                inspection_interval = pd.NA
                df_list.append(inspection_interval)
            else:
                hrs_at_last_inspection = df_inspection_table.loc[(df_inspection_table["ACSN"]==acsn) & (df_inspection_table["CTRLPT"]==ctrlpt)].iloc[0]["Hours at Last Inspection"]
                # print(acsn, ctrlpt, hrs_at_last_inspection)
                if (hrs_at_last_inspection in [0, "0", "?", "", " ", None]) or (pd.isnull(hrs_at_last_inspection)): # LOOK HERE: MAKE THIS LESS SPECIFIC
                    # print("CP DT")
                    cp_dt_life = df_cp_dt_life.loc[(df_cp_dt_life["ACSN"]==acsn)].iloc[0][ctrlpt]
                    sf_initial_inspection = df_cp_ref.loc[df_cp_ref["CTRLPT"]==ctrlpt].iloc[0]["Safety Factor Initial Inspection"]
                    inspection_interval = cp_dt_life / sf_initial_inspection
                    df_list.append(inspection_interval)
                    # print(cp_dt_life, sf_initial_inspection, inspection_interval,"\n")
                else:
                    # print("CP Follow-on")
                    cp_followon_life = df_cp_followon_life.loc[df_cp_followon_life["ACSN"]==acsn].iloc[0][ctrlpt]
                    sf_followon_inspection = df_cp_ref.loc[df_cp_ref["CTRLPT"]==ctrlpt].iloc[0]["Safety Factor Follow-on Inspection"]
                    inspection_interval = cp_followon_life / sf_followon_inspection
                    df_list.append(inspection_interval)
                    # print(cp_followon_life, sf_followon_inspection, inspection_interval,"\n")
        df_inspection_intervals.loc[len(df_inspection_intervals)] = df_list

    return df_inspection_intervals