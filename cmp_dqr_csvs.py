'''
Compares two refreshes DQR utilizing their underlying csvs
'''
import os
import json
import datetime
from pandas import read_csv, merge, DataFrame, concat
from tabulate import tabulate

from get_stats import CSV_PATH
from mapping import file_types

CLIENT = 'Molina'

CLIENTS = {
    'Molina': {
        'Medicaid': ['AZ', 'FL', 'IA', 'ID', 'IL', 'KY', 'MA', 'MI', 'MS', 'NE', 'NM', 'NV', 'NY', 'OH', 'SC', 'TX', 'UT', 'VA', 'WA', 'WI']
        , 'Medicare': ['AZ', 'IL', 'KY', 'MA', 'MI', 'MS', 'NV', 'NY', 'OH', 'SC', 'TX', 'UT', 'VA', 'WA', 'WI']
        , 'Marketplace': ['FL', 'ID', 'IL', 'KY', 'MI', 'MS', 'NM', 'NV', 'OH', 'SC', 'TX', 'UT', 'WA', 'WI']
    }
    , 'BCBSNE': {
        'Commercial': ['NE']
        , 'Medicare Advantage': ['NE']
    }
    # , 'UH': {
    #     'lobs': []
    # }
}

INVERTED_FT = {
    v: k for k, v in file_types.items() if k not in ['HEDIS Measures', 'National Benchmarks', 'State Benchmarks']
}

STAT_FILES = {
    'EDD': 'edd',
    'FreqDist': 'fd',
    'miscellaneous': 'dat',
}

def iterate_inputs_folder(refresh_path: str,
                          refresh: str,
                          map_dqr_csvs
                        ):
    refresh_files = os.listdir(refresh_path)
    for file_name in refresh_files:
        if file_name.endswith('.csv'):
            file_name_split = file_name.split('_')
            prefix = file_name_split[0]
            suffix = file_name_split[-1].replace(".csv", "")
            if prefix in INVERTED_FT.keys():
                map_dqr_csvs[INVERTED_FT[prefix]][STAT_FILES[suffix]][refresh] = os.path.join(refresh_path, file_name)
    
    return map_dqr_csvs

def makedirs(file_path):
    os.makedirs(os.path.dirname(file_path), exist_ok = True)

def save_as_json(data, file_path):
    makedirs(file_path)
    with open(file_path, 'w') as json_file:
        json.dump(data, json_file, indent=4)

def check(refresh1, refresh2):
    if len(refresh1) > 0 and len(refresh2) > 0:
        return True
    return False

def get_dfs(refresh1_file_path, refresh2_file_path):
    df1 = read_csv(refresh1_file_path)
    df2 = read_csv(refresh2_file_path)

    return df1, df2

FILL_RATE_DIFF_THRESHOLD = 0.05
AVG_VALUE_DIFF_THRESHOLD = 0.10

def edd_ops(edd):
    # cols = ['Column', 'Count', 'Unique', 'Sum', 'Min', 'Max', 'Data Type']
    # edd = edd[cols]
    # print(edd.columns)
    row_count = edd['count'].max()
    edd['Fill Rate'] = edd['count']/row_count
    mask = edd['DataType'] != 'datetime64[ns]'
    edd['Average Value'] = 0.0
    edd.loc[mask, 'Average Value'] = edd.loc[mask, 'sum'].astype('float')/edd.loc[mask, 'count']

    edd = edd.rename(columns = {'column': 'Column Name'})
    
    return edd

def cmp_edd(edd1, edd2):
    edd1 = edd_ops(edd1)
    edd2 = edd_ops(edd2)

    # # Using merge
    cols = ['Column Name', 'Fill Rate', 'Average Value']
    for col in ['Column Name']:
        edd1[f'{col}_lowercase'] = edd1[col].map(lambda x: x.lower() if isinstance(x, str) else x)
        edd2[f'{col}_lowercase'] = edd2[col].map(lambda x: x.lower() if isinstance(x, str) else x)
        cols += [f'{col}_lowercase']
    
    # suffixes=('_added', '_deleted')
    merged = merge(edd1[cols], edd2[cols], on='Column Name_lowercase', how='outer', indicator=True)
    # FILTER ROWS WHERE FILL RATE IS ABSENT
    merged = merged.loc[~(merged['Fill Rate_x'].isin(['#DIV/0!'])) & ~(merged['Fill Rate_y'].isin(['#DIV/0!']))]
    
    cols_added = merged.loc[merged['_merge'] == 'left_only', 'Column Name_x']
    cols_deleted = merged.loc[merged['_merge'] == 'right_only', 'Column Name_y']
    cols_common = merged.loc[merged['_merge'] == 'both', 'Column Name_x']
    
    merged['diff_fill_rate'] = merged.loc[merged['_merge'] == 'both', 'Fill Rate_x'] - merged.loc[merged['_merge'] == 'both', 'Fill Rate_y']
    cols_fr_diff = merged.loc[merged['diff_fill_rate'] > FILL_RATE_DIFF_THRESHOLD, 'Column Name_x']
    cols_fr_diff_val = merged.loc[merged['diff_fill_rate'] > FILL_RATE_DIFF_THRESHOLD, 'diff_fill_rate'] * 100
    mask = (merged['_merge'] == 'both') #& (merged['Average Value_y'] != 0)
    merged.loc[mask, 'diff_avg_value'] = abs(merged.loc[mask, 'Average Value_x'] - merged.loc[mask, 'Average Value_y'])
    merged.loc[mask, 'diff_avg_val_%'] = merged.loc[mask, 'diff_avg_value'] / merged.loc[mask, 'Average Value_y'].replace(0, 1)
    
    cols_av_diff = merged.loc[merged['diff_avg_val_%'] > AVG_VALUE_DIFF_THRESHOLD, 'Column Name_x']
    cols_av_diff_val = merged.loc[merged['diff_avg_val_%'] > AVG_VALUE_DIFF_THRESHOLD, 'diff_avg_val_%'] * 100
    
    return {
        'added': DataFrame({'Added': list(cols_added)}),
        # 'common': DataFrame({'Common': list(cols_common)}),
        'deleted': DataFrame({'Deleted': list(cols_deleted)}),
        'fill_rate': DataFrame({f'Fill Rate Diff > {FILL_RATE_DIFF_THRESHOLD * 100}%': list(cols_fr_diff),
                                f'Fill Rate Diff Value': list(cols_fr_diff_val)}),
        'avg_val': DataFrame({f'Average Value Diff > {AVG_VALUE_DIFF_THRESHOLD * 100}%': list(cols_av_diff),
                              f'Average Value Diff % Value': list(cols_av_diff_val),})
    }

def fd_ops(fd):    
    fd = fd.rename(columns = {col:col.replace(" ", "") for col in fd.columns})
    fd[f'% Row_Count'] = fd['Frequency']/fd.groupby(by=['ColumnName'])['Frequency'].transform('sum') * 100
    return fd

def cmp_fd(fd1, fd2, new_cols_added, file_type):
    fd1 = fd_ops(fd1)
    fd2 = fd_ops(fd2)

    cols = ['ColumnName', 'ColumnValue', 'Frequency', f'% Row_Count']
    for col in ['ColumnName', 'ColumnValue']:
        col_lwr = f'{col}_lowercase'
        fd1[col_lwr] = fd1[col].map(lambda x: x.lower() if isinstance(x, str) else x.strftime('%d-%m-%Y') if isinstance(x, datetime.datetime) else x)
        fd2[col_lwr] = fd2[col].map(lambda x: x.lower() if isinstance(x, str) else x.strftime('%d-%m-%Y') if isinstance(x, datetime.datetime) else x)
        cols += [col_lwr]

    suffixes=('_added', '_deleted')
    merged = merge(fd1[cols], fd2[cols], on=['ColumnName_lowercase', 'ColumnValue_lowercase'], how='outer', suffixes=suffixes, indicator=True)

    cmp_mapping = read_csv(os.path.join('mapping', 'cmp_mapping.csv'))
    cmp_mapping_file_type_columns = cmp_mapping.loc[cmp_mapping['FileType'] == file_type,["ColumnName"]].values.tolist()

    # print(merged)
    mask_syssrcname = (merged['ColumnName_lowercase'] == 'syssourcename')
    mask_new_cols = (merged[f'ColumnName{suffixes[0]}'].isin(list(new_cols_added)))
    mask_feqdist_prev_1_curr_1 = (merged[f'ColumnName{suffixes[0]}'].isin(merged[f'ColumnName{suffixes[1]}']))
    mask_exclude_cols = (merged['ColumnName_lowercase'].isin([i[0].lower() for i in cmp_mapping_file_type_columns]))
    
    cols_vals_added_existing_freqdist_1 = merged.loc[~mask_syssrcname & ~mask_new_cols & ~mask_exclude_cols & mask_feqdist_prev_1_curr_1 & (merged['_merge'] == 'left_only'), [f'ColumnName{suffixes[0]}', f'ColumnValue{suffixes[0]}', f'% Row_Count{suffixes[0]}']].reset_index(drop=True)
    cols_vals_added_existing_freqdist_0 = merged.loc[~mask_syssrcname & ~mask_new_cols & ~mask_exclude_cols & ~mask_feqdist_prev_1_curr_1 & (merged['_merge'] == 'left_only'), [f'ColumnName{suffixes[0]}', f'ColumnValue{suffixes[0]}', f'% Row_Count{suffixes[0]}']].reset_index(drop=True)
    cols_vals_added_new = merged.loc[mask_new_cols & (merged['_merge'] == 'left_only'), [f'ColumnName{suffixes[0]}', f'ColumnValue{suffixes[0]}', f'% Row_Count{suffixes[0]}']].reset_index(drop=True)
    cols_vals_deleted = merged.loc[~mask_syssrcname & ~mask_exclude_cols & (merged['_merge'] == 'right_only'), [f'ColumnName{suffixes[1]}', f'ColumnValue{suffixes[1]}']].reset_index(drop=True)

    fd_dfs = [
                cols_vals_added_existing_freqdist_1,
                cols_vals_added_existing_freqdist_0,
                cols_vals_added_new,
                cols_vals_deleted,
             ]

    for df in fd_dfs:
        df.columns = [col_name.replace('_added', '').replace('_deleted', '') for col_name in df.columns]

    return {
        'ex_1': cols_vals_added_existing_freqdist_1,
        'ex_0': cols_vals_added_existing_freqdist_0,
        'new': cols_vals_added_new,
        'del': cols_vals_deleted
    }


def cmp_dqr(lob: str          # LINE OF BUSINESS
            , state: str        # MARKET
            , refresh1:str      # REFRESH MONTH 1
            , refresh2:str      # REFRESH MONTH 2
        ):
    
    client = CLIENT
    if client not in CLIENTS.keys():
        raise ValueError(f'{client} does not exist')
    if lob not in CLIENTS[client].keys():
        raise ValueError(f'{lob} does not exist')
    if state not in CLIENTS[client][lob]:
        raise ValueError(f'{state} does not exist')
    
    refresh1 = refresh1.replace(" ", "_")
    refresh2 = refresh2.replace(" ", "_")
    
    refresh1_path = os.path.join(CSV_PATH, client, refresh1, state, lob, 'Inputs')
    refresh2_path = os.path.join(CSV_PATH, client, refresh2, state, lob, 'Inputs')

    refresh1 = refresh1.replace('_', '')
    refresh2 = refresh2.replace('_', '')

    map_dqr_csvs = {}
    for k, _ in file_types.items():
        map_dqr_csvs[k] = {
            'edd':{
                refresh1: '',
                refresh2: '',
            }, 
            'fd':{
                refresh1: '',
                refresh2: '',
            }, 
            'dat':{
                refresh1: '',
                refresh2: '',
            }
        } 
    
    map_dqr_csvs = iterate_inputs_folder(refresh_path=refresh1_path, refresh=refresh1, map_dqr_csvs=map_dqr_csvs)
    map_dqr_csvs = iterate_inputs_folder(refresh_path=refresh2_path, refresh=refresh2, map_dqr_csvs=map_dqr_csvs)

    save_as_json(map_dqr_csvs, os.path.join('json', client, lob, state, f'{refresh1}_vs_{refresh2}.json'))

    cmp_dfs = {
        'edd' : {
            'added' : [],
            'deleted' : [],
            'fill_rate' : [],
            'avg_val' : [],
        },
        'fd' : {
            'ex_1' : [],
            'ex_0' : [],
            'new' : [],
            'del' : [],
        },
    }

    for file_type, paths in map_dqr_csvs.items():
        if file_type.startswith('Masking') or file_type in ['HEDIS Measures', 'National Benchmarks', 'State Benchmarks']:
            continue

        print(f'[{file_type}]')
        if check(paths['edd'][refresh1], paths['edd'][refresh2]):
            print(f'\t[EDD]')
            edd1, edd2 = get_dfs(map_dqr_csvs[file_type]['edd'][refresh1], map_dqr_csvs[file_type]['edd'][refresh2])
            cmp_edd_res = cmp_edd(edd1, edd2)
            for key, df in cmp_edd_res.items():
                cmp_dfs['edd'][key].append(df.assign(File_Type = file_type))

        if check(paths['edd'][refresh1], paths['edd'][refresh2]) and check(paths['fd'][refresh1], paths['fd'][refresh2]):
            print(f'\t[FD]')
            fd1, fd2 = get_dfs(map_dqr_csvs[file_type]['fd'][refresh1], map_dqr_csvs[file_type]['fd'][refresh2])
            cmp_fd_res = cmp_fd(fd1, fd2, cmp_edd_res['added'], file_type)
            for key, df in cmp_fd_res.items():
                cmp_dfs['fd'][key].append(df.assign(File_Type = file_type))
        
        # for stat_type in ['edd', 'fd']:
        #     if check(*paths[stat_type]):
        #         print(f'\t[{stat_type.upper()}]')
        #         cmp_res = cmp_edd(get_dfs(*map_dqr_csvs[file_type][stat_type]))
        #         for key, df in cmp_res.items():
        #             cmp_dfs[stat_type][key].append(df.assign(File_Type = file_type))

    ## CONCAT DATAFRAME LIST
    for section, _ in cmp_dfs.items():
        for key, df_list in cmp_dfs[section].items():
            cmp_dfs[section][key] = concat(df_list, ignore_index=True)

    return f"""
    Use the below results from the DQR comparator to draw insights and inconsistencies in the data:
    1. Columns added in the new refresh:
    {tabulate(cmp_dfs['edd']['added'], headers='keys', tablefmt='psql')}
    2. Columns deleted in the new refresh:
    {tabulate(cmp_dfs['edd']['deleted'], headers='keys', tablefmt='psql')}
    3. Columns with fill rate difference greater than the threshold
    {tabulate(cmp_dfs['edd']['fill_rate'], headers='keys', tablefmt='psql')}
    4. Columns with average value difference greater than the threshold
    {tabulate(cmp_dfs['edd']['avg_val'], headers='keys', tablefmt='psql')}
    5. New values added in existing columns with freq dist = 1 in the new refresh
    {tabulate(cmp_dfs['fd']['ex_1'], headers='keys', tablefmt='psql')}
    6. New values added in existing columns with freq dist = 0 in the new refresh
    {tabulate(cmp_dfs['fd']['ex_0'], headers='keys', tablefmt='psql')}
    7. Values added in new columns in the new refresh
    {tabulate(cmp_dfs['fd']['new'], headers='keys', tablefmt='psql')}
    8. Deleted values in existing columns in the new refresh
    {tabulate(cmp_dfs['fd']['del'], headers='keys', tablefmt='psql')}
    """
    
    # path_csv_output = os.path.join(os.getcwd(), 'tmp', client, lob, state, f'{refresh1}_vs_{refresh2}')
    # os.makedirs(path_csv_output, exist_ok=True)

    # for section, _ in cmp_dfs.items():
    #     for key, cmp_df in cmp_dfs[section].items():
    #         # # # REARRANGE COLUMNS
    #         col_list = cmp_df.columns.to_list()
    #         col_list = [col_list[-1]] + col_list[:-1]   # LAST COL + REMAINING COLUMNS 
    #         cmp_df = cmp_df[col_list]

    #         # # # SAVE AS CSV
    #         file_path = os.path.join(path_csv_output, f'{section}_{key}.csv')
    #         cmp_df.to_csv(file_path, index=False)


if __name__ == '__main__':
    print(cmp_dqr('Medicaid', 'FL', 'PT Feb 2025', 'PT Jan 2025'))