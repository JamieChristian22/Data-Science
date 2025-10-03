# DV0101EN-Final-Assign-Part-2-Questions.py
# Automobile Sales Dashboard — Final Assignment (Plotly + Dash)
# Covers:
# - TASK 2.1 Title
# - TASK 2.2 Two dropdowns (report type + year)
# - TASK 2.3 Output container
# - TASK 2.4 Callbacks (enable/disable year; build 2x2 charts)
# - TASK 2.5 Recession Report charts (4)
# - TASK 2.6 Yearly Report charts (4)
#
# Assumes a CSV named 'automobile_sales.csv' with columns:
# Date, Recession, Automobile_Sales, GDP, unemployment_rate, Consumer_Confidence,
# Seasonality_Weight, Price, Advertising_Expenditure, Vehicle_Type, Competition,
# Month (1..12 or text), Year (1980..2013)

import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# ---------- Load data ----------
CSV = "automobile_sales.csv"
if not os.path.exists(CSV):
    raise FileNotFoundError(
        f"Cannot find '{CSV}' in the current folder.\n"
        "Upload it into the same directory as this Python file."
    )

data = pd.read_csv(CSV)

# Keep the assignment year window
data = data[(data["Year"] >= 1980) & (data["Year"] <= 2013)].copy()

# If Month is numeric, optionally create a month label (not mandatory for grader)
if "Month" in data.columns and pd.api.types.is_numeric_dtype(data["Month"]):
    month_map = {
        1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"
    }
    data["MonthLabel"] = data["Month"].map(month_map)
else:
    # Fallback if Month already exists as text, else create a placeholder
    data["MonthLabel"] = data.get("Month", "Jan")

# ---------- Dash app ----------
app = Dash(__name__)
app.title = "Automobile Sales Statistics Dashboard"

year_list = [i for i in range(1980, 2014, 1)]  # 1980–2013 inclusive

# =========================
# TASK 2.1: Title
# =========================
# Replace the placeholder in the skeleton with this exact H1:
title_component = html.H1(
    "Automobile Sales Statistics Dashboard",
    style={'textAlign': 'center', 'color': '#503D36', 'font-size': '24px'}
)

# =========================
# TASK 2.2: Dropdowns
# =========================
report_dropdown = dcc.Dropdown(
    id='dropdown-statistics',
    options=[
        {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
        {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
    ],
    placeholder='Select a report type',
    value=None,  # let user choose
    style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
)

year_dropdown = dcc.Dropdown(
    id='select-year',
    options=[{'label': i, 'value': i} for i in year_list],
    placeholder='Select-year',
    value=None,
    style={'width': '80%', 'padding': '3px', 'font-size': '20px', 'text-align-last': 'center'}
)

# =========================
# TASK 2.3: Output container
# =========================
output_div = html.Div([
    html.Div(id='output-container', className='chart-grid', style={'display': 'flex'})
])

# App layout (title + controls + output)
app.layout = html.Div(
    style={'maxWidth': '1200px', 'margin': '0 auto', 'fontFamily': 'Arial, sans-serif'},
    children=[
        title_component,
        html.Div([
            html.Label("Select Report Type:", style={'fontWeight': 600}),
            report_dropdown
        ], style={'margin': '10px 0'}),
        html.Div([
            html.Label("Select Year:", style={'fontWeight': 600}),
            year_dropdown
        ], style={'margin': '10px 0'}),
        output_div
    ]
)

# =========================
# TASK 2.4: Callbacks
# =========================

# ---- Update Input Container: enable/disable the year dropdown ----
@app.callback(
    Output(component_id='select-year', component_property='disabled'),
    Input(component_id='dropdown-statistics', component_property='value')
)
def update_input_container(selected_statistics):
    # IMPORTANT: 'disabled' is True to disable, False to enable.
    # We ENABLE year for Yearly Statistics → return False.
    if selected_statistics == 'Yearly Statistics':
        return False
    else:
        return True

# ---- Update Output Container: build the 2×2 chart grid based on selection ----
@app.callback(
    Output(component_id='output-container', component_property='children'),
    [Input(component_id='dropdown-statistics', component_property='value'),
     Input(component_id='select-year', component_property='value')]
)
def update_output_container(selected_statistics, input_year):
    # Nothing selected yet
    if not selected_statistics:
        return html.Div("Please select a report type above.", style={'padding': '10px'})

    # ==============================
    # TASK 2.5: Recession Report
    # ==============================
    if selected_statistics == 'Recession Period Statistics':
        recession_data = data[data['Recession'] == 1].copy()

        # Plot 1: Avg Automobile sales over recession years (line)
        yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        R_chart1 = dcc.Graph(figure=px.line(
            yearly_rec, x='Year', y='Automobile_Sales',
            title="Average Automobile Sales During Recession (Year-wise)",
            markers=True, template='plotly_white'
        ))

        # Plot 2: Avg vehicles sold by vehicle type (bar)
        average_sales = (recession_data
                         .groupby('Vehicle_Type')['Automobile_Sales']
                         .mean().reset_index())
        R_chart2 = dcc.Graph(figure=px.bar(
            average_sales, x='Vehicle_Type', y='Automobile_Sales',
            title="Average Vehicles Sold by Vehicle Type (Recession)",
            template='plotly_white'
        ))

        # Plot 3: Total ad expenditure share by vehicle type (pie)
        exp_rec = (recession_data
                   .groupby('Vehicle_Type')['Advertising_Expenditure']
                   .sum().reset_index())
        R_chart3 = dcc.Graph(figure=px.pie(
            exp_rec, values='Advertising_Expenditure', names='Vehicle_Type',
            title="Ad Expenditure Share by Vehicle Type (Recession)",
            template='plotly_white'
        ))

        # Plot 4: Effect of unemployment rate on sales by vehicle type (bar)
        unemp_data = (recession_data
                      .groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales']
                      .mean().reset_index())
        R_chart4 = dcc.Graph(figure=px.bar(
            unemp_data, x='unemployment_rate', y='Automobile_Sales',
            color='Vehicle_Type', barmode='group',
            labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Average Automobile Sales'},
            title='Effect of Unemployment Rate on Vehicle Type and Sales (Recession)',
            template='plotly_white'
        ))

        # Return as 2 rows × 2 columns
        return [
            html.Div(children=[
                html.Div(R_chart1, style={'flex': 1, 'padding': '6px'}),
                html.Div(R_chart2, style={'flex': 1, 'padding': '6px'})
            ], style={'display': 'flex'}),
            html.Div(children=[
                html.Div(R_chart3, style={'flex': 1, 'padding': '6px'}),
                html.Div(R_chart4, style={'flex': 1, 'padding': '6px'})
            ], style={'display': 'flex'})
        ]

    # ==============================
    # TASK 2.6: Yearly Report
    # ==============================
    elif (input_year and selected_statistics == 'Yearly Statistics'):
        yearly_data = data[data['Year'] == input_year].copy()

        # Plot 1: Yearly Automobile sales (whole period, average per year) — line
        yas = data.groupby('Year')['Automobile_Sales'].mean().reset_index()
        Y_chart1 = dcc.Graph(figure=px.line(
            yas, x='Year', y='Automobile_Sales',
            title="Yearly Automobile Sales (Average per Year, 1980–2013)",
            markers=True, template='plotly_white'
        ))

        # Plot 2: Total Monthly Automobile sales for selected year — line
        # (Sum over the months in the selected year)
        mas = (yearly_data.groupby('Month')['Automobile_Sales']
               .sum().reset_index())
        Y_chart2 = dcc.Graph(figure=px.line(
            mas, x='Month', y='Automobile_Sales',
            title='Total Monthly Automobile Sales',
            markers=True, template='plotly_white'
        ))

        # Plot 3: Average vehicles sold by vehicle type (selected year) — bar
        avr_vdata = (yearly_data.groupby('Vehicle_Type')['Automobile_Sales']
                     .mean().reset_index())
        Y_chart3 = dcc.Graph(figure=px.bar(
            avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
            title=f'Average Vehicles Sold by Vehicle Type in the year {input_year}',
            template='plotly_white'
        ))

        # Plot 4: Total Advertisement Expenditure by vehicle type (selected year) — pie
        exp_data = (yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure']
                    .sum().reset_index())
        Y_chart4 = dcc.Graph(figure=px.pie(
            exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
            title='Total Advertisement Expenditure for Each Vehicle',
            template='plotly_white'
        ))

        # Return as 2 rows × 2 columns
        return [
            html.Div(children=[
                html.Div(Y_chart1, style={'flex': 1, 'padding': '6px'}),
                html.Div(Y_chart2, style={'flex': 1, 'padding': '6px'})
            ], style={'display': 'flex'}),
            html.Div(children=[
                html.Div(Y_chart3, style={'flex': 1, 'padding': '6px'}),
                html.Div(Y_chart4, style={'flex': 1, 'padding': '6px'})
            ], style={'display': 'flex'})
        ]

    # If Yearly was chosen but year not set yet
    return html.Div("Select a year to display Yearly Statistics.", style={'padding': '10px'})

# ---------- Run ----------
if __name__ == "__main__":
    try:
        # Dash 3+
        app.run(host="0.0.0.0", port=8050, debug=False)
    except Exception:
        # Fallback for older Dash (2.x)
        app.run_server(host="0.0.0.0", port=8050, debug=False)
