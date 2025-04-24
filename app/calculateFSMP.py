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

def calculateIATModifiedTotalLife(FSMPyear, dataframes):
    import pandas as pd
    
    IATyear = FSMPyear - 1
    df_damagefile = dataframes[f"DAMGEFL{IATyear}per2"]
    df_iat_trkpt = dataframes[f"IAT_TRKPT_{FSMPyear}"]
    df_scale_factors = dataframes["Normalized_Scale_Factors"]
    df_cp_ref = dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]
    
    trkpt_list = dataframes[f"IAT_TRKPT_{FSMPyear}"]["TRKPT"].tolist()
    ctrlpt_list = dataframes[f"CP_Ref_Table5_Special_{FSMPyear}"]["CTRLPT"].tolist()
    acsn_list = dataframes["AC_Status_List"]["ACSN"].tolist()
    ctrlpt_dict = {'W15LH': 'W-15', 'W1LH': 'W-1', 'W15RH': 'W-15', 'W1RH': 'W-1', 'WCT4': 'WCT-4', 'WCT10': 'WCT-10', 'WSAFLH': 'WSA-6 LH', 'WSAFRH': 'WSA-6 RH', 'FIF6': 'FIF-6L', 'AIF9': 'AIF-9', 'AIF12': 'AIF-12', 'AIF51': 'AIF-51', 'HS1LLH': 'HS-1LL', 'HS1ULH': 'HS-1UL', 'HS1LRH': 'HS-1LR', 'HS1URH': 'HS-1UR', 'VS2LH': 'VS-2', 'AF1LH': 'AF-1', 'NAC6LH': 'NAC-6', 'NAC4LH': 'NAC-4', 'NAC6RH': 'NAC-6', 'NAC4RH': 'NAC-4', 'AF1RH': 'AF-1', 'VS2RH': 'VS-2', 'MLG1': 'MLG-01', 'MLG2': 'MLG-02', 'MLG3': 'MLG-03'}
    col_list = ["ACSN"] + trkpt_list
    trkpt_list_unique = df_damagefile["TRKPT"].unique()

    df_iat_modified_total_life = pd.DataFrame(columns=col_list)
    for acsn in acsn_list:
        df_list = [acsn]
        for trkpt in trkpt_list:
            if trkpt not in trkpt_list_unique:
                modified_total_life = pd.NA
                df_list.append(modified_total_life)
            else:
                tlife = df_damagefile.loc[(df_damagefile["TRKPT"]==trkpt) & (df_damagefile["ACSN"]==acsn)].iloc[0]["TLIFE_DT"]
                iat_latest = df_iat_trkpt.loc[(df_iat_trkpt["TRKPT"]==trkpt)].iloc[0]["IAT DT"]
                dt_latest = df_cp_ref.loc[(df_cp_ref["CTRLPT"]==ctrlpt_dict[trkpt])].iloc[0]["Production Life"]
                iat_ratio = dt_latest/iat_latest
                scale_factor = df_scale_factors[(df_scale_factors["Year"]==IATyear) & (df_scale_factors["TRKPT"]==trkpt)].iloc[0]["Factor"]
                modified_total_life = tlife * iat_ratio * scale_factor
                df_list.append(modified_total_life)
        df_iat_modified_total_life.loc[len(df_iat_modified_total_life)] = df_list

    return df_iat_modified_total_life.set_index("ACSN")

