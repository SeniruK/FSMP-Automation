'''
Function to calculate CP DT Life

Input(s):
- DataFrame 1: Modified Total Life (ACSN, TrkPt ID Num)
- Database 3: CP DT Life (CP Name, TrkPt ID Num)

Output(s):
- DataFrame 2: CP DT Life
'''

def calculateCPDTLife(df_iat_modified_total_life, df_damagefile, df_iat_trkpt, df_cp_ref, ctrlpt_list, acsn_list):
    import pandas as pd
    import numpy as np

    col_list = ['ACSN'] + ctrlpt_list
    ctrlpt_dict = {"W15LH": 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    trkpt_list_unique = df_damagefile["TRKPT"].unique()

    df_cp_dt_life = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for ctrlpt in ctrlpt_list:
            trkpt_id = df_cp_ref.loc[(df_cp_ref["CTRLPT"]==ctrlpt)].iloc[0]["TRKPT ID Number"]
            trkpt = df_iat_trkpt.loc[(df_iat_trkpt["TRKPT ID Number"]==trkpt_id)].iloc[0]["TRKPT"]
            if trkpt not in trkpt_list_unique:
                cp_dt_life = pd.NA
                df_list.append(cp_dt_life)
            else:
                # trkpt_id = df_cp_ref.loc[(df_cp_ref["CTRLPT"]==ctrlpt)].iloc[0]["TRKPT ID Number"]
                # trkpt = df_iat_trkpt.loc[(df_iat_trkpt["TRKPT ID Number"]==trkpt_id)].iloc[0]["TRKPT"]
                dt_latest = df_cp_ref.loc[(df_cp_ref["CTRLPT"]==ctrlpt_dict[trkpt])].iloc[0]["Production Life"]
                modified_total_life = df_iat_modified_total_life.loc[(df_iat_modified_total_life["ACSN"]==acsn)].iloc[0][trkpt]
                cp_production_life = df_cp_ref.loc[(df_cp_ref["CTRLPT"]==ctrlpt)].iloc[0]["Production Life"]
                cp_dt_life = modified_total_life * cp_production_life / dt_latest
                df_list.append(cp_dt_life)
        df_cp_dt_life.loc[len(df_cp_dt_life)] = df_list

    return df_cp_dt_life