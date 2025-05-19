import pandas as pd
import glob
import os
import json
from mapping import file_types
import plotly.express as px

#constants
CSV_PATH = r'dqr_csvs'
CLIENT = 'Molina'

def get_dqr_summary(state, refresh_month, lob, feed, stat_file, column):

    files_path = os.path.join(CSV_PATH, CLIENT, refresh_month, state, lob, 'Inputs')

    # If stat_file is 'DAT', set it to 'miscellaneous' for file matching
    # Convert feed name to standardized format from file_types mapping
    if stat_file == 'DAT': stat_file = 'miscellaneous'
    if stat_file == 'Merge_Stats': feed = stat_file
    
    if feed != 'Merge_Stats':
        feed_used = file_types[feed]
    else: feed_used = ''

    print(stat_file)
    print('----------', feed_used)

    pattern = os.path.join(files_path, f"{feed_used.replace(' ', '')}*{stat_file}*.csv")
    
    matching_files = glob.glob(pattern) 

    if len(matching_files) == 0:
        return ''

    full_summary = pd.DataFrame()    

    full_summary = pd.concat([pd.read_csv(file) for file in matching_files], ignore_index=True)
    full_summary.drop_duplicates(inplace=True)

    # print(full_summary)

    # Returning full summary in case of merge stats
    if stat_file == 'Merge_Stats':
        return full_summary
    
    # Calculate fill rate percentage for EDD files only
    if stat_file.lower() == 'edd':
        full_summary['Fillrate'] = (full_summary['count'] / full_summary['count'].max() * 100).round(2).astype(str) + '%'


    col_name = [col for col in full_summary.columns if col.lower().startswith('column')][0]
    column_summary = full_summary[full_summary[col_name] == column]
    column_summary.insert(0, 'File used', feed)
    column_summary.insert(0, 'Market and PT month', state+' '+refresh_month+' '+lob)
    
    return column_summary

# print(get_dqr_summary("AZ", "PT_Dec_2024", "Medicaid", "Non Claims Expenses", "FreqDist", "prod_gl"))

def adhoc_checks(state, refresh_month, lob, checks=[]):
    
    adhoc_path = os.path.join(CSV_PATH, CLIENT, refresh_month, state, lob, 'Inputs', 'adhoc_queries')
    
    matching_files = []
    for check in checks:
        pattern = os.path.join(adhoc_path, f"{check}*.csv")
        matching_files += glob.glob(pattern)

    if len(matching_files) == 0:
        return {}

    full_summary = {
        os.path.basename(path)[:-4] : pd.read_csv(os.path.join(path)) for path in matching_files
    } 

    #additional data to get total medical and pharmacy claims amount to compare with the ineligible/phantom claims
    if(item in checks for item in ['ineligible_claims_rx_claims', 'ineligible_claims_med_claims', 'phantom_claims_rx_claims', 'phantom_claims_med_claims']):
        med_claims = get_dqr_summary(state, refresh_month, lob, "Medical Claims", "EDD", "Paid_Amount")
        med_claims = med_claims['sum']

        rx_claims = get_dqr_summary(state, refresh_month, lob, "Pharmacy Claims", "EDD", "Rx_Paid_Amount")
        rx_claims = rx_claims['sum']

        full_summary['total_med_claims'] = med_claims
        full_summary['total_rx_claims'] = rx_claims
    # print(type(full_summary))
    # full_summary.drop_duplicates(inplace=True)
    return full_summary

# table_data = adhoc_checks("AZ", "PT_Dec_2024", "Medicaid", ["ineligible_claims_rx_claims"])
# print(table_data)
# exit()
# tool_response = {name: df.to_dict(orient="records") for name, df in table_data.items()}

# # Return result as string
# tool_response_str = str(tool_response)

# print('Tool response - ', tool_response_str)

def plot_chart(x_label, x_data, y_label, y_data, chart_type="line", title="Chart"):

    df = pd.DataFrame({x_label: x_data, y_label: y_data})

    try:
        if chart_type == "line":
            fig = px.line(df, x=x_label, y=y_label, title=title, markers=True)
        elif chart_type == "bar":
            fig = px.bar(df, x=x_label, y=y_label, title=title)
        elif chart_type == "scatter":
            fig = px.scatter(df, x=x_label, y=y_label, title=title)
        elif chart_type == "histogram":
            df_hist = pd.DataFrame({y_label: y_data})
            fig = px.histogram(df_hist, x=y_label, title=title)
        else:
            raise ValueError("Unsupported chart type")
    
    except Exception as e:
        return 'Chart could not be generated'

    # Convert the figure to JSON in a way that's compatible with Streamlit
    return {"chart": fig.to_json()}
