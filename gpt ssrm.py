import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from dash.exceptions import PreventUpdate
from dash_ag_grid import AgGrid, GridOptions

import pandas as pd
from pandas_gbq import read_gbq

# Set up your Google Cloud credentials for BigQuery

# Initialize Dash app
app = dash.Dash(__name__)

# Define your BigQuery SQL query without LIMIT and OFFSET
base_query = """
SELECT *
FROM `your_project_id.your_dataset_id.your_table_id`
"""

# Define pagination parameters
page_size = 50
current_page = 1

# Create GridOptions for AG Grid
grid_options = GridOptions(
    enableSorting=True,
    enableFilter=True,
    enableColResize=True,
    paginationPageSize=page_size,
    domLayout='autoHeight',
    rowModelType='serverSide',
)

# Define the layout of the Dash app
app.layout = html.Div([
    dcc.Interval(id='interval-component', interval=10*1000, n_intervals=0),  # Refresh interval
    
    AgGrid(
        id='ag-grid',
        gridOptions=grid_options,
    ),
])

@app.callback(
    Output('ag-grid', 'rowData'),
    [Input('ag-grid', 'pageLoaded'), Input('ag-grid', 'filterChanged')],
    prevent_initial_call=True
)
def update_ag_grid_data(page_loaded, filter_changed):
    global current_page

    try:
        # Calculate the start row and end row for the query
        start_row = (current_page - 1) * page_size
        end_row = current_page * page_size

        # Get the applied filters
        filters = []
        if filter_changed:
            for col_id, filter_model in filter_changed['api']['filterModel'].items():
                col_filter = f"{col_id} {filter_model['type']} '{filter_model['filter']}'"
                filters.append(col_filter)
            
        # Create the filter part of the query
        filters_query = ' AND '.join(filters)
        if filters_query:
            filters_query = f'WHERE {filters_query}'

        # Construct the final query
        query = f"{base_query} {filters_query} LIMIT {end_row} OFFSET {start_row}"

        # Query BigQuery for the current page
        df = read_gbq(query, project_id='your_project_id', dialect='standard')

        # Increment current page
        current_page += 1

        # Convert DataFrame to AG Grid compatible format
        data = df.to_dict('records')

        return data

    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == '__main__':
    app.run_server(debug=True)
