import pandas as pd
import numpy as np

import dash
from dash import dcc, html, Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# LOAD & CLEAN DATA

df = pd.read_csv("Car_sale_ads.csv")

EUR_TO_PLN = 4.27

df["Price_PLN"] = np.where(
    df["Currency"] == "EUR",
    df["Price"] * EUR_TO_PLN,
    df["Price"]
)

df["Offer_publication_date"] = pd.to_datetime(
    df["Offer_publication_date"],
    format="%d/%m/%Y",
    errors="coerce"
)

df["First_registration_date"] = pd.to_datetime(
    df["First_registration_date"],
    format="%d/%m/%Y",
    errors="coerce"
)

# Remove extreme outliers for cleaner charts
df = df[(df["Price_PLN"] > 1_000) & (df["Price_PLN"] < 2_000_000)]
df = df[(df["Production_year"] >= 1980) & (df["Production_year"] <= 2022)]
df["Mileage_km"] = df["Mileage_km"].fillna(0)
df["Power_HP"]   = df["Power_HP"].fillna(df["Power_HP"].median())

# DASH APP
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME],
    suppress_callback_exceptions=True
)

server = app.server

# NAVBAR
navbar = dbc.NavbarSimple(
    brand="Used Cars Dashboard",
    brand_href="/",
    color="primary",
    dark=True,
    children=[
        dbc.NavItem(dbc.NavLink("Overview",         href="/",         active="exact")),
        dbc.NavItem(dbc.NavLink("Market Analysis",  href="/market",   active="exact")),
        dbc.NavItem(dbc.NavLink("Price Explorer",   href="/explorer", active="exact")),
    ]
)

# APP LAYOUT
app.layout = dbc.Container([

    dcc.Location(id="url"),
    navbar,
    html.Br(),
    html.Div(id="page-content"),

], fluid=True)


# PAGE 1 — OVERVIEW
def overview_layout():

    median_price   = int(df["Price_PLN"].median())
    median_mileage = int(df["Mileage_km"].median())
    median_hp      = int(df["Power_HP"].median())
    total_listings = len(df)

    # Brand chart
    top_brands  = df["Vehicle_brand"].value_counts().head(15).index.tolist()
    brand_stats = (
        df[df["Vehicle_brand"].isin(top_brands)]
        .groupby("Vehicle_brand")["Price_PLN"]
        .agg(
            median="median",
            q25=lambda x: x.quantile(0.25),
            q75=lambda x: x.quantile(0.75),
        )
        .sort_values("median", ascending=True)
        .reset_index()
    )

    fig_brand = go.Figure()
    fig_brand.add_trace(go.Bar(
        x=brand_stats["median"],
        y=brand_stats["Vehicle_brand"],
        orientation="h",
        marker=dict(
            color=brand_stats["median"],
            colorscale="RdYlGn",
            showscale=False,
        ),
        error_x=dict(
            type="data", symmetric=False,
            array=brand_stats["q75"] - brand_stats["median"],
            arrayminus=brand_stats["median"] - brand_stats["q25"],
            color="rgba(0,0,0,0.3)",
        ),
        hovertemplate="<b>%{y}</b><br>Median: %{x:,.0f} PLN<extra></extra>",
    ))
    fig_brand.add_vline(
        x=df["Price_PLN"].median(),
        line_dash="dash", line_color="#888",
        annotation_text=f"Overall median: {df['Price_PLN'].median():,.0f} PLN",
        annotation_position="top right",
    )
    fig_brand.update_layout(
        title="Median Car Price by Brand (Top 15)",
        xaxis_title="Median Price (PLN)",
        yaxis_title="",
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(gridcolor="#f0f0f0"),
    )

    # Year chart
    year_stats = (
        df.groupby("Production_year")
        .agg(median_price=("Price_PLN", "median"), count=("Price_PLN", "count"))
        .reset_index()
    )
    year_stats = year_stats[year_stats["count"] >= 100].sort_values("Production_year")

    fig_year = make_subplots(specs=[[{"secondary_y": True}]])
    fig_year.add_trace(
        go.Scatter(
            x=year_stats["Production_year"], y=year_stats["median_price"],
            name="Median Price (PLN)", mode="lines+markers",
            line=dict(width=3, color="#3498db"),
            hovertemplate="Year: %{x}<br>%{y:,.0f} PLN<extra></extra>",
        ),
        secondary_y=False,
    )
    fig_year.add_trace(
        go.Bar(
            x=year_stats["Production_year"], y=year_stats["count"],
            name="Listings", opacity=0.3, marker_color="#95a5a6",
            hovertemplate="Year: %{x}<br>%{y:,}<extra></extra>",
        ),
        secondary_y=True,
    )
    fig_year.update_layout(
        title="Median Car Price and Listing Volume by Production Year",
        plot_bgcolor="white", paper_bgcolor="white", height=500,
    )
    fig_year.update_yaxes(title_text="Median Price (PLN)", gridcolor="#f0f0f0", secondary_y=False)
    fig_year.update_yaxes(title_text="Number of Listings", secondary_y=True)

    # Layout
    return dbc.Container([

        html.H1("Used Car Market — Overview", className="fw-bold mb-4"),

        # KPI cards
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.P("Total Listings", className="text-muted mb-1 small"),
                            html.H3(f"{total_listings:,}", className="mb-0 fw-bold"),
                        ]),
                        html.I(className="fa fa-list fa-2x text-primary opacity-75"),
                    ], className="d-flex justify-content-between align-items-center"),
                ])
            ], className="shadow-sm border-0"), width=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.P("Median Price", className="text-muted mb-1 small"),
                            html.H3(f"{median_price:,.0f} PLN", className="mb-0 fw-bold"),
                        ]),
                        html.I(className="fa fa-tag fa-2x text-success opacity-75"),
                    ], className="d-flex justify-content-between align-items-center"),
                ])
            ], className="shadow-sm border-0"), width=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.P("Median Mileage", className="text-muted mb-1 small"),
                            html.H3(f"{median_mileage:,.0f} km", className="mb-0 fw-bold"),
                        ]),
                        html.I(className="fa fa-road fa-2x text-warning opacity-75"),
                    ], className="d-flex justify-content-between align-items-center"),
                ])
            ], className="shadow-sm border-0"), width=3),

            dbc.Col(dbc.Card([
                dbc.CardBody([
                    html.Div([
                        html.Div([
                            html.P("Median Engine Power", className="text-muted mb-1 small"),
                            html.H3(f"{median_hp} HP", className="mb-0 fw-bold"),
                        ]),
                        html.I(className="fa fa-bolt fa-2x text-danger opacity-75"),
                    ], className="d-flex justify-content-between align-items-center"),
                ])
            ], className="shadow-sm border-0"), width=3),

        ], className="mb-4 g-3"),

        # Charts
        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Brand Comparison", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(figure=fig_brand, config={"displayModeBar": False})),
            ], className="shadow-sm border-0"), width=6),

            dbc.Col(dbc.Card([
                dbc.CardHeader("Price Trend by Production Year", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(figure=fig_year, config={"displayModeBar": False})),
            ], className="shadow-sm border-0"), width=6),
        ], className="g-3"),

    ], fluid=True)


# PAGE 2 — MARKET ANALYSIS
def market_layout():

    # Fuel type chart
    fuel_order = ["Electric", "Hybrid", "Gasoline", "Diesel", "Gasoline + LPG", "Gasoline + CNG"]
    fuel_df = (
        df[df["Fuel_type"].isin(fuel_order)]
        .groupby("Fuel_type")
        .agg(median_price=("Price_PLN", "median"), count=("Price_PLN", "count"))
        .reindex(fuel_order)
        .reset_index()
    )

    colors = [
        "#2ecc71" if f in ["Electric", "Hybrid"]
        else "#3498db" if f == "Diesel"
        else "#e67e22" if "LPG" in f or "CNG" in f
        else "#e74c3c"
        for f in fuel_df["Fuel_type"]
    ]

    fig_fuel = make_subplots(specs=[[{"secondary_y": True}]])
    fig_fuel.add_trace(
        go.Bar(x=fuel_df["Fuel_type"], y=fuel_df["median_price"],
               marker_color=colors, name="Median Price",
               hovertemplate="<b>%{x}</b><br>%{y:,.0f} PLN<extra></extra>"),
        secondary_y=False,
    )
    fig_fuel.add_trace(
        go.Scatter(x=fuel_df["Fuel_type"], y=fuel_df["count"],
                   mode="lines+markers", name="Listings",
                   line=dict(color="#2c3e50", width=2),
                   hovertemplate="<b>%{x}</b><br>%{y:,}<extra></extra>"),
        secondary_y=True,
    )
    fig_fuel.update_layout(
        title="Median Price & Market Share by Fuel Type",
        plot_bgcolor="white", paper_bgcolor="white", height=450,
    )
    fig_fuel.update_yaxes(title_text="Median Price (PLN)", tickformat=",",
                           gridcolor="#f0f0f0", secondary_y=False)
    fig_fuel.update_yaxes(title_text="Number of Listings", secondary_y=True)

    # Heatmap
    type_trans = (
        df.groupby(["Type", "Transmission"])["Price_PLN"]
        .median()
        .unstack("Transmission")
        .reindex(["SUV", "coupe", "sedan", "convertible",
                  "station_wagon", "compact", "minivan", "city_cars", "small_cars"])
        .dropna(how="all")
    )

    fig_heat = go.Figure(data=go.Heatmap(
        z=type_trans.values,
        x=type_trans.columns.tolist(),
        y=type_trans.index.tolist(),
        colorscale="RdYlGn",
        text=[[f"{v:,.0f}" if not np.isnan(v) else "" for v in row]
              for row in type_trans.values],
        texttemplate="%{text}", textfont=dict(size=12),
        hovertemplate="<b>%{y}</b> | <b>%{x}</b><br>%{z:,.0f} PLN<extra></extra>",
        colorbar=dict(title="PLN"),
    ))
    fig_heat.update_layout(
        title="Median Price (PLN) — Body Type × Transmission",
        plot_bgcolor="white", paper_bgcolor="white", height=420,
    )

    # Violin plot
    mileage_df = df[
        (df["Mileage_km"] > 0) & (df["Mileage_km"] < 500_000) &
        (df["Condition"] == "Used") &
        (df["Fuel_type"].isin(["Gasoline", "Diesel", "Hybrid", "Electric", "Gasoline + LPG"]))
    ].copy()

    fig_violin = px.violin(
        mileage_df, x="Fuel_type", y="Mileage_km", color="Fuel_type",
        box=True, points=False,
        color_discrete_map={
            "Gasoline": "#e74c3c", "Diesel": "#3498db",
            "Hybrid": "#2ecc71", "Electric": "#9b59b6", "Gasoline + LPG": "#e67e22",
        },
        labels={"Mileage_km": "Mileage (km)", "Fuel_type": "Fuel Type"},
        title="Mileage Distribution by Fuel Type (Used Cars Only)",
    )
    fig_violin.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=450, showlegend=False,
        yaxis=dict(tickformat=",", gridcolor="#f0f0f0"),
    )

    # Layout
    return dbc.Container([

        html.H1("Market Analysis", className="fw-bold mb-4"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Fuel Type — Price & Volume", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(figure=fig_fuel, config={"displayModeBar": False})),
            ], className="shadow-sm border-0"), width=6),

            dbc.Col(dbc.Card([
                dbc.CardHeader("Body Type × Transmission Heatmap", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(figure=fig_heat, config={"displayModeBar": False})),
            ], className="shadow-sm border-0"), width=6),
        ], className="mb-4 g-3"),

        dbc.Row([
            dbc.Col(dbc.Card([
                dbc.CardHeader("Mileage Distribution by Fuel Type", className="fw-semibold"),
                dbc.CardBody(dcc.Graph(figure=fig_violin, config={"displayModeBar": False})),
            ], className="shadow-sm border-0"), width=12),
        ], className="g-3"),

    ], fluid=True)


# PAGE 3 — PRICE EXPLORER  (interactive with callbacks)
def explorer_layout():

    brand_options = [{"label": b, "value": b}
                     for b in sorted(df["Vehicle_brand"].dropna().unique())]
    fuel_options  = [{"label": f, "value": f}
                     for f in sorted(df["Fuel_type"].dropna().unique())]

    return dbc.Container([

        html.H1("Interactive Price Explorer", className="fw-bold mb-4"),

        dbc.Row([

            # Filter sidebar
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Filters", className="fw-semibold"),
                    dbc.CardBody([

                        html.Label("Vehicle Brand", className="fw-semibold small"),
                        dcc.Dropdown(
                            id="brand-dropdown",
                            options=brand_options,
                            multi=True,
                            placeholder="All brands",
                            className="mb-3",
                        ),

                        html.Label("Fuel Type", className="fw-semibold small"),
                        dcc.Dropdown(
                            id="fuel-dropdown",
                            options=fuel_options,
                            multi=True,
                            placeholder="All fuel types",
                            className="mb-3",
                        ),

                        html.Label("Production Year Range", className="fw-semibold small"),
                        dcc.RangeSlider(
                            id="year-slider",
                            min=int(df["Production_year"].min()),
                            max=int(df["Production_year"].max()),
                            value=[2010, 2021],
                            marks={y: str(y) for y in range(
                                int(df["Production_year"].min()),
                                int(df["Production_year"].max()) + 1,
                                5,
                            )},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="mb-4",
                        ),

                        # mileage as Slider
                        html.Label("Maximum Mileage (km)", className="fw-semibold small"),
                        dcc.Slider(
                            id="mileage-slider",
                            min=0,
                            max=400_000,
                            step=10_000,
                            value=200_000,
                            marks={i: f"{i // 1000}k" for i in range(0, 400_001, 100_000)},
                            tooltip={"placement": "bottom", "always_visible": True},
                            className="mb-4",
                        ),

                        # typed input for max price
                        html.Label("Maximum Price (PLN)", className="fw-semibold small"),
                        dbc.Input(
                            id="price-input",
                            type="number",
                            value=300_000,
                            min=0,
                            step=5_000,
                            className="mb-4",
                        ),

                        # explicit Apply button
                        dbc.Button(
                            [html.I(className="fa fa-search me-2"), "Apply Filters"],
                            id="apply-btn",
                            color="primary",
                            className="w-100",
                            n_clicks=0,
                        ),

                    ]),
                ], className="shadow-sm border-0"),
            ], width=3),

            # Chart area
            dbc.Col([
                dbc.Card([
                    dbc.CardHeader("Price vs Engine Power — colored by Fuel Type",
                                   className="fw-semibold"),
                    dbc.CardBody(dcc.Graph(id="scatter-plot",
                                           config={"displayModeBar": False})),
                ], className="shadow-sm border-0 mb-3"),

                dbc.Card([
                    dbc.CardHeader("Price Distribution of Filtered Cars",
                                   className="fw-semibold"),
                    dbc.CardBody(dcc.Graph(id="hist-plot",
                                           config={"displayModeBar": False})),
                ], className="shadow-sm border-0"),

                html.Div(id="result-count", className="text-muted small mt-2 ms-1"),

            ], width=9),

        ], className="g-3"),

    ], fluid=True)


# PAGE ROUTING  (single callback)
@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
)
def display_page(pathname):
    if pathname == "/market":
        return market_layout()
    if pathname == "/explorer":
        return explorer_layout()
    return overview_layout()


# EXPLORER CALLBACKS  (triggered by Button)
@app.callback(
    Output("scatter-plot",  "figure"),
    Output("hist-plot",     "figure"),
    Output("result-count",  "children"),
    Input("apply-btn",      "n_clicks"),   # Button is the primary trigger
    State("brand-dropdown", "value"),
    State("fuel-dropdown",  "value"),
    State("year-slider",    "value"),
    State("mileage-slider", "value"),
    State("price-input",    "value"),
    prevent_initial_call=False,
)
def update_charts(n_clicks, brands, fuels, years, max_mileage, max_price):

    filtered = df.copy()

    if brands:
        filtered = filtered[filtered["Vehicle_brand"].isin(brands)]
    if fuels:
        filtered = filtered[filtered["Fuel_type"].isin(fuels)]

    filtered = filtered[
        (filtered["Production_year"] >= years[0]) &
        (filtered["Production_year"] <= years[1]) &
        (filtered["Mileage_km"]      <= (max_mileage or 400_000)) &
        (filtered["Price_PLN"]       <= (max_price   or 2_000_000))
    ]

    # Sample for scatter performance
    sample = (filtered.sample(3_000, random_state=42)
              if len(filtered) > 3_000 else filtered)

    FUEL_COLORS = {
        "Gasoline": "#e74c3c", "Diesel": "#3498db", "Hybrid": "#2ecc71",
        "Electric": "#9b59b6", "Gasoline + LPG": "#e67e22", "Gasoline + CNG": "#f39c12",
    }

    # Scatter
    scatter_fig = px.scatter(
        sample,
        x="Power_HP", y="Price_PLN", color="Fuel_type",
        color_discrete_map=FUEL_COLORS,
        opacity=0.45,
        labels={"Power_HP": "Engine Power (HP)", "Price_PLN": "Price (PLN)",
                "Fuel_type": "Fuel Type"},
        hover_data={"Production_year": True, "Vehicle_brand": True},
    )
    scatter_fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", height=420,
        yaxis=dict(tickformat=",", gridcolor="#f0f0f0"),
        xaxis=dict(gridcolor="#f0f0f0"),
    )

    # Histogram
    hist_fig = px.histogram(
        filtered, x="Price_PLN", nbins=60,
        color_discrete_sequence=["#3498db"],
        labels={"Price_PLN": "Price (PLN)"},
    )
    hist_fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", height=320,
        xaxis=dict(tickformat=",", gridcolor="#f0f0f0"),
        yaxis=dict(gridcolor="#f0f0f0"),
    )

    count_msg = (f"Showing {len(filtered):,} listings"
                 + (" (scatter sampled to 3,000)" if len(filtered) > 3_000 else ""))

    return scatter_fig, hist_fig, count_msg


if __name__ == "__main__":
    app.run(debug=True)
