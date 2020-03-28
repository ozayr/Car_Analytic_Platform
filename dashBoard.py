# from jupyter_plotly_dash import JupyterDash
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.express as px
import pandas as pd
import json
import dash_table
from glob import glob
from datetime import datetime, timedelta

app = dash.Dash()

data_files = glob('json_data_files/*.json')

with open(data_files[0], 'r') as myfile:
    data = myfile.read()
obj = json.loads(data)
dict_of_cars = obj[0]

car_df = pd.DataFrame.from_dict(dict_of_cars, orient='index').reset_index()
car_df['age'] = datetime.now().year - car_df.year

colors = {
    'background': '#111111',
    'text': '#7FDBFF'
}

app.layout = html.Div(style={'backgroundColor': colors['background']}, children=[
    html.H1(children='CAR ANALYTICA', style={'textAlign': 'center', 'color': colors['text']}),

    html.Div(children='Car Analysis Platform', style={'textAlign': 'center', 'color': colors['text']}),
    html.P("", style={'height': '5%'}),

    html.Div(['Make:'], style={'width': '50%', 'color': colors['text'], 'display': 'inline-block'}),
    html.Div(['Model:'], style={'width': '50%', 'color': colors['text'], 'display': 'inline-block'}),

    html.Div(dcc.Dropdown(id='make', options=[{'label': v, 'value': v} for v in list(car_df.make.unique())],
                          value=list(car_df.make.unique())[0]), style={'width': '50%', 'display': 'inline-block'}),
    html.Div(dcc.Dropdown(id='model'), style={'width': '50%', 'display': 'inline-block'}),

    html.Div(['Engine Cap:'], style={'width': '50%', 'color': colors['text']}),
    html.Div(dcc.Dropdown(id='engine'), style={'width': '50%'}),

    #     html.Div([html.H2('All cars info'),html.Table(id='my-table'),html.P(''),], style={'width': '55%', 'float': 'right', 'display': 'inline-block'})

    html.Div(dcc.Graph(id='fig1', style={'color': colors['background']})),

    html.H2(children=['All cars info'], style={'textAlign': 'center', 'color': colors['text']}),
    html.Div(dash_table.DataTable(id='my-table', page_size=10, sort_action='native',
                                  columns=[{"name": i, "id": i} for i in car_df.columns if i not in ['index', 'url']]),
             style={'width': '100%'})

])


# MODELS
@app.callback(dash.dependencies.Output('model', 'options'), [dash.dependencies.Input('make', 'value')])
def callback_populate_models(make):
    return [{'label': v, 'value': v} for v in list(car_df.loc[car_df.make == make].model.unique())]


@app.callback(dash.dependencies.Output('model', 'value'), [dash.dependencies.Input('make', 'value')])
def callback_set_first_model(make):
    return list(car_df.loc[car_df.make == make].model.unique())[0]


# ================================================================================================
# ENGINE
@app.callback(dash.dependencies.Output('engine', 'options'),
              [dash.dependencies.Input('make', 'value'), dash.dependencies.Input('model', 'value')])
def callback_populate_engines(make, model):
    return [{'label': v, 'value': v} for v in
            list(car_df.loc[(car_df.make == make) & (car_df.model == model)].engine.unique())]


@app.callback(dash.dependencies.Output('engine', 'value'),
              [dash.dependencies.Input('make', 'value'), dash.dependencies.Input('model', 'value')])
def callback_set_first_model(make, model):
    return list(car_df.loc[(car_df.make == make) & (car_df.model == model)].engine.unique())[0]


# =================================================================================================


@app.callback(dash.dependencies.Output('fig1', 'figure'),
              [dash.dependencies.Input('engine', 'value'), dash.dependencies.Input('make', 'value'),
               dash.dependencies.Input('model', 'value')])
def callback_populate_graph(engine, make, model):
    return px.scatter(car_df.loc[(car_df.make == make) & (car_df.model == model) & (car_df.engine == engine)],
                      title=f'{make} {model} {engine}', template='plotly_dark', x='mileage', y='price', color='year').update(layout=dict(title=dict(x=0.5)))


@app.callback(dash.dependencies.Output('my-table', 'data'),
              [dash.dependencies.Input('engine', 'value'), dash.dependencies.Input('make', 'value'),
               dash.dependencies.Input('model', 'value')])
def callback_populate_graph(engine, make, model):
    return car_df.loc[(car_df.make == make) & (car_df.model == model) & (car_df.engine == engine)].to_dict('records')


if __name__ == '__main__':
    app.run_server(debug=True)


