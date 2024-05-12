import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
import numpy as np

# Initialize your Dash app and include a Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def categorize_weight(weight):
    if weight < 56:
        return 'Flyweight'
    elif weight < 61:
        return 'Bantamweight'
    elif weight < 66:
        return 'Featherweight'
    elif weight < 71:
        return 'Lightweight'
    elif weight < 77:
        return 'Welterweight'
    elif weight < 84:
        return 'Middleweight'
    elif weight < 93:
        return 'Light Heavyweight'
    else:
        return 'Heavyweight'

# Load and prepare the dataset
data = pd.read_csv('/Users/zainmunawar/Desktop/ufc-fighters-statistics.csv')
data['win_ratio'] = data['wins'] / (data['wins'] + data['losses'] + data['draws'])
data['category'] = data['weight_in_kg'].apply(categorize_weight)
data['stand_up_game_score'] = (data['significant_striking_accuracy'] + data['significant_strike_defence']) / 2
data.loc[data['stand_up_game_score'] == 0, 'stand_up_game_score'] = np.nan

# Dash app initialization with Bootstrap styles
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout using Bootstrap components for better styling and layout
app.layout = dbc.Container([
    dbc.Row(dbc.Col(html.H1("UFC Fighters Dashboard"), className="mb-3")),
    dbc.Row([
        dbc.Col([
            html.P("Filter by Minimum Win Ratio:"),
            dcc.Slider(
                id='win-ratio-slider',
                min=0, max=1, value=0.5, step=0.01,
                marks={str(round(i, 2)): str(round(i, 2)) for i in np.linspace(0, 1, 21)}
            ),
            dcc.Graph(id='height-win-ratio-graph'),
        ], width=12),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Dropdown(
                id='category-dropdown',
                options=[{'label': cat, 'value': cat} for cat in data['category'].unique()],
                value='Lightweight'
            ),
            dcc.Graph(id='takedown-defense-graph'),
        ], width=6),
        dbc.Col([
            dcc.Graph(id='stance-effectiveness-graph'),
        ], width=6),
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id='stand-up-game-scores-graph'),
        ], width=12),
    ])
], fluid=True)

# Callbacks for interactive components
@app.callback(
    Output('height-win-ratio-graph', 'figure'),
    Input('win-ratio-slider', 'value')
)
def update_height_win_ratio(value):
    filtered_data = data[data['win_ratio'] >= value]
    fig = go.Figure(data=[go.Scatter(x=filtered_data['height_cm'], y=filtered_data['win_ratio'], mode='markers', marker=dict(color='blue', opacity=0.5))])
    fig.update_layout(title='Height vs. Win Ratio', xaxis_title='Height (cm)', yaxis_title='Win Ratio')
    return fig

@app.callback(
    Output('takedown-defense-graph', 'figure'),
    Input('category-dropdown', 'value')
)
def update_takedown_defense(selected_category):
    filtered_data = data[data['category'] == selected_category]
    fig = go.Figure(data=[go.Box(x=filtered_data['category'], y=filtered_data['takedown_defense'])])
    fig.update_layout(title='Takedown Defense by Category', xaxis_title='Category', yaxis_title='Takedown Defense (%)')
    return fig

@app.callback(
    Output('stance-effectiveness-graph', 'figure'),
    Input('win-ratio-slider', 'value')
)
def update_stance_effectiveness(value):
    filtered_data = data[data['win_ratio'] >= value]
    stance_stats = filtered_data.groupby('stance')['win_ratio'].mean().reset_index()
    fig = go.Figure(data=[go.Bar(x=stance_stats['stance'], y=stance_stats['win_ratio'])])
    fig.update_layout(title='Effectiveness of Different Stances', xaxis_title='Stance', yaxis_title='Average Win Ratio')
    return fig

@app.callback(
    Output('stand-up-game-scores-graph', 'figure'),
    Input('win-ratio-slider', 'value')
)
def update_stand_up_game_scores(value):
    filtered_data = data[data['win_ratio'] >= value]
    fig = go.Figure(data=[go.Histogram(x=filtered_data['stand_up_game_score'])])
    fig.update_layout(title='Distribution of Stand-Up Game Scores', xaxis_title='Stand-Up Game Score', yaxis_title='Frequency')
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
