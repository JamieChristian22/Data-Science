# spacex-dash-app.py  (v5)
import hashlib, pathlib
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

print(">>> STARTING DASH APP v5 (port 8060)")
print(">>> FILE:", __file__)
print(">>> MD5:", hashlib.md5(pathlib.Path(__file__).read_bytes()).hexdigest())

CSV_PATH = "spacex_launch_dash.csv"
spacex_df = pd.read_csv(CSV_PATH)

COL_SITE = "Launch Site"
COL_CLASS = "class"
COL_PAYLOAD = "Payload Mass (kg)"
COL_BOOSTER = "Booster Version Category"

min_payload = int(spacex_df[COL_PAYLOAD].min())
max_payload = int(spacex_df[COL_PAYLOAD].max())
launch_sites = sorted(spacex_df[COL_SITE].unique().tolist())
print(">>> Sites:", launch_sites)
print(">>> Payload range:", min_payload, "to", max_payload)

app = dash.Dash(__name__)
app.title = "SpaceX Launch Records Dashboard — v5"

app.layout = html.Div(
    [
        html.H1("SpaceX Launch Records Dashboard — v5", style={"textAlign": "center"}),

        # TASK 1: Dropdown
        html.Div(
            dcc.Dropdown(
                id="site-dropdown",
                options=[{"label": "All Sites", "value": "ALL"}]
                + [{"label": s, "value": s} for s in launch_sites],
                value="ALL",
                placeholder="Select a Launch Site here",
                searchable=True,
                clearable=False,
            ),
            style={"width": "60%", "margin": "0 auto"},
        ),

        html.Br(),

        # TASK 2: Pie
        dcc.Graph(id="success-pie-chart"),

        html.Br(),

        # TASK 3: Slider
        html.Div(
            [
                html.Label("Payload range (Kg):"),
                dcc.RangeSlider(
                    id="payload-slider",
                    min=0, max=10000, step=1000,
                    value=[min_payload, max_payload],
                    marks={0: "0", 2500: "2500", 5000: "5000", 7500: "7500", 10000: "10000"},
                ),
            ],
            style={"width": "80%", "margin": "0 auto"},
        ),

        html.Br(),

        # TASK 4: Scatter
        dcc.Graph(id="success-payload-scatter-chart"),
    ],
    style={"fontFamily": "Arial, sans-serif"},
)

# TASK 2 callback
@app.callback(Output("success-pie-chart", "figure"),
              Input("site-dropdown", "value"))
def render_pie(selected_site):
    if selected_site == "ALL":
        agg = (spacex_df.groupby(COL_SITE, as_index=False)[COL_CLASS]
               .sum().sort_values(COL_CLASS, ascending=False))
        fig = px.pie(agg, values=COL_CLASS, names=COL_SITE,
                     title="Total Successful Launches by Site")
    else:
        d = spacex_df[spacex_df[COL_SITE] == selected_site]
        counts = d[COL_CLASS].value_counts().rename_axis("Outcome").reset_index(name="count")
        counts["Outcome"] = counts["Outcome"].map({1: "Success", 0: "Failure"})
        fig = px.pie(counts, values="count", names="Outcome",
                     title=f"Launch Outcomes for {selected_site}")
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(margin=dict(l=40, r=40, t=60, b=20))
    return fig

# TASK 4 callback
@app.callback(Output("success-payload-scatter-chart", "figure"),
              [Input("site-dropdown", "value"),
               Input("payload-slider", "value")])
def render_scatter(selected_site, payload_range):
    low, high = payload_range
    m = (spacex_df[COL_PAYLOAD] >= low) & (spacex_df[COL_PAYLOAD] <= high)
    dff = spacex_df[m] if selected_site == "ALL" else spacex_df[(spacex_df[COL_SITE] == selected_site) & m]
    title = (f"Payload vs Outcome — All Sites ({low}–{high} Kg)"
             if selected_site == "ALL" else
             f"Payload vs Outcome — {selected_site} ({low}–{high} Kg)")
    fig = px.scatter(dff, x=COL_PAYLOAD, y=COL_CLASS, color=COL_BOOSTER,
                     hover_data=[COL_SITE, COL_BOOSTER],
                     labels={COL_CLASS: "Launch Outcome (1=Success, 0=Failure)"},
                     title=title)
    fig.update_layout(margin=dict(l=40, r=40, t=60, b=20),
                      yaxis=dict(tickmode="array", tickvals=[0, 1]))
    return fig

if __name__ == "__main__":
    # Dash v3
    app.run(debug=False, host="0.0.0.0", port=8060)
