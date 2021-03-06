import base64
import datetime
import io

import dash
from dash.dependencies import Input, Output, State
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.express as px

import pandas as pd


external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets,
                suppress_callback_exceptions=True)

app.layout = html.Div([ 
    html.Div(className = 'header',
    children = [html.H1(children = "Taxonomic Classification of Soil Profiles", 
    className = 'title')]
            ),
    
    # this code section taken from Dash docs https://dash.plotly.com/dash-core-components/upload
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow multiple files to be uploaded
        multiple=True
    ),
    html.Div(className = 'plots',
        children = [html.Div(id='output-div'),
        html.Div(id='output-div1'),
        html.Div(id='output-div2'),
        html.Div(id='output-div3')]),
    html.Div(id='output-datatable'),
])


def parse_contents(contents, filename, date):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(
                io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])

    return html.Div([
        html.H5(filename),
        html.H6(datetime.datetime.fromtimestamp(date)),
        # html.P("Inset X axis data"),
        # dcc.Dropdown(id='xaxis-data',
        #              options=[{'label':x, 'value':x} for x in df.columns]),
        # html.P("Inset Y axis data"),
        # dcc.Dropdown(id='yaxis-data',
        #              options=[{'label':x, 'value':x} for x in df.columns]),
        html.Button(id="submit-button", children="Create Graph"),

        # Relevant variables
        dcc.Store(id = 'orden-data', data = df.ORDEN),
        dcc.Store(id = 'altitud-data', data = df.ALTITUD),
        # dcc.Store(id = 'temperatura-data', data = df.REGIMEN_TEMPERATURA),
        # dcc.Store(id = 'humedad-data', data = df.REGIMEN_HUMEDAD),    

        html.Hr(),

        dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns],
            page_size=15
        ),
        dcc.Store(id='stored-data', data=df.to_dict('records')),

        html.Hr(),  # horizontal line

        # For debugging, display the raw contents provided by the web browser
        html.Div('Raw Content'),
        html.Pre(contents[0:200] + '...', style={
            'whiteSpace': 'pre-wrap',
            'wordBreak': 'break-all'
        })
    ])


@app.callback(Output('output-datatable', 'children'),
              Input('upload-data', 'contents'),
              State('upload-data', 'filename'),
              State('upload-data', 'last_modified'))
def update_output(list_of_contents, list_of_names, list_of_dates):
    if list_of_contents is not None:
        children = [
            parse_contents(c, n, d) for c, n, d in
            zip(list_of_contents, list_of_names, list_of_dates)]
        return children


@app.callback(Output('output-div', 'children'),
              Output('output-div1', 'children'),
              Output('output-div2', 'children'),
              Output('output-div3', 'children'),
              Input('submit-button','n_clicks'),
              State('stored-data','data'),
              State('orden-data','data'),
              State('altitud-data', 'data'))
def make_graphs(n, data, orden, altitud):
    
    orden = pd.Series(orden)
    altitud = pd.Series(altitud)

    if n is None:
        return dash.no_update
    else:

        pie_fig = px.pie(data, values=orden.value_counts(), names=orden.value_counts().index)
        box_fig = px.box(data, x = orden, y = altitud)
        text = html.Div(children = [html.H1('70%', style = {'text-align': 'center'}), 
                                    html.H5('accuracy', style = {'text-align': 'center'})])
        heat_map = px.imshow([[1, 20, 30],
                 [20, 1, 60],
                 [30, 60, 1]])

        fig1 = dcc.Graph(figure=pie_fig)
        fig2 = dcc.Graph(figure = box_fig) 
        fig3 = dcc.Graph(figure = heat_map)

        return fig1, fig2, text, fig3



if __name__ == '__main__':
    app.run_server(debug=True)