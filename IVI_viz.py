import pandas as pd
from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import plotly.graph_objects as go
import dash_daq as daq
import numpy as np

# Load data
df = pd.read_parquet('./CKW_open_data/processed_data.parquet')
# Force value_kwh to be float
df['value_kwh'] = df['value_kwh'].astype(float)

# Create Dash app
app = Dash(__name__)

# Define min and max date
min_date = df['timestamp'].min()
max_date = df['timestamp'].max()

# Define app layout
app.layout = html.Div([
    html.H1(children='A look at smart meters',
            style={'textAlign': 'center', 'font-size': '40px', 'font-family': 'sans-serif'}),
    html.H2(children='Select a smart meters:',
            style={'textAlign': 'center', 'font-size': '30px', 'font-family': 'sans-serif'}),
    html.Div([
        html.Div([
            html.Label('Date range:', style={'width': '90%', 'margin': 'auto', 'font-size': '20px', 'font-family': 'sans-serif'}),
            dcc.DatePickerRange(id='date-picker',
                                min_date_allowed=min_date,
                                max_date_allowed=max_date,
                                start_date=min_date,
                                end_date=min_date+pd.Timedelta(days=14),
                                style={'width': '90%', 'margin': 'auto', 'font-size': '20px', 'font-family': 'sans-serif', 'display': 'block'}),
        ], style={'width': '30%', 'margin': 'auto', 'display': 'inline-block'}),
        html.Div([
            html.Label('Meter IDs:', style={'width': '90%', 'margin': 'auto', 'font-size': '20px', 'font-family': 'sans-serif'}),
            dcc.Dropdown(options=[{'label': meter_id, 'value': meter_id} for meter_id in range(1, df['id'].max()+1)],
                         id='meter-dropdown',
                         multi=True,
                         value=[1],
                         style={'width': '90%', 'margin': 'auto', 'font-size': '20px', 'font-family': 'sans-serif', 'display': 'block'}),
        ], style={'width': '30%', 'margin': 'auto', 'display': 'inline-block'}),
        html.Div([
            html.Label('Addons:', style={'width': '90%', 'margin': 'auto', 'font-size': '20px', 'font-family': 'sans-serif'}),
            dcc.Dropdown(options=[{'label': 'Display Avg Line', 'value': 'avg-line'}],
                         id='addon-dropdown',
                         multi=True,
                         value=[],
                         style={'width': '90%', 'margin': 'auto', 'font-size': '20px', 'font-family': 'sans-serif', 'display': 'block'}),
        ], style={'width': '30%', 'margin': 'auto', 'display': 'inline-block'})
    ], style={'margin-top': '20px', 'margin-bottom': '20px', 'width': '95%', 'text-align': 'center', 'display': 'block', 'margin': 'auto'}),
    dcc.Graph(id='meter-graph',
              style={'width': '100%', 'margin': 'auto', 'display': 'block', 'margin-top': '25px'})
])

# Set up callbacks
@app.callback(Output('meter-graph', 'figure'),
              [Input('meter-dropdown', 'value'),
               Input('date-picker', 'start_date'),
               Input('date-picker', 'end_date'),
               Input('addon-dropdown', 'value')])

# Define graph update function
def update_graph(selected_meters, start_date, end_date, addons):
    fig = px.line()
    for i, meter_id in enumerate(selected_meters):
        df_meter = df[df['id'] == meter_id]
        df_meter = df_meter[(df_meter['timestamp'] >= start_date) & (df_meter['timestamp'] <= end_date)]
        df_meter = df_meter.sort_values('timestamp')
        
        main_trace = go.Scatter(x=df_meter['timestamp'], y=df_meter['value_kwh'], mode='lines', name=f'Meter {i+1}')
        fig.add_trace(main_trace)

        # Removed confidence interval for now as in the final product, there would only be one line (the new simulated data) that uses it
    
    fig.update_layout(title=f'Energy consumption for selected meters from {start_date[:10]} to {end_date[:10]}')
    fig.update_xaxes(title='Time')
    fig.update_yaxes(title='Energy consumption (kWh)')
    
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)