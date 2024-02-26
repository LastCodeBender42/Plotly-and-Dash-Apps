from dash import Dash, callback, html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import networkx as nx
import sys
import pkgutil
import dash
import plotly.graph_objs as go
from scipy.stats import linregress
from dash import dcc, html, Input, Output

class CentralityAnalysis:
    def __init__(self):
        super().__init__()
        # Initialize graph variable
        self.G = None
        
    def generate_graph(self):
        # Read data and create graph
        df = pd.read_csv('./data/1YOK.cif_ringEdges', sep='\t')
        subset_df = df.loc[(df['NodeId1'].str.contains('A:')) & (df['NodeId2'].str.contains('A:'))]
        self.G = nx.from_pandas_edgelist(subset_df, 'NodeId1', 'NodeId2', create_using=nx.Graph())
        
    def generate_eigenVals(self):
        # Check if graph is generated
        if self.G is None:
            raise ValueError("Graph not generated. Call generate_graph() first.")
        
        eigen_centr = nx.eigenvector_centrality_numpy(self.G)
        eigendf = pd.DataFrame(list(eigen_centr.items()), columns=['node', 'value'])
        eigendf['norm_val'] = eigendf['value'] / eigendf['value'].max()
        return eigendf
        
    def generate_closeVals(self):
        if self.G is None:
            raise ValueError("Graph not generated. Call generate_graph() first.")
        
        close_centr = nx.closeness_centrality(self.G)
        closedf = pd.DataFrame(list(close_centr.items()), columns=['node', 'value'])
        closedf['norm_val'] = closedf['value'] / closedf['value'].max()
        return closedf
        
    def generate_degrVals(self):
        if self.G is None:
            raise ValueError("Graph not generated. Call generate_graph() first.")
        
        degr_centr = nx.degree_centrality(self.G)
        degrdf = pd.DataFrame(list(degr_centr.items()), columns=['node', 'value'])
        degrdf['norm_val'] = degrdf['value'] / degrdf['value'].max()
        return degrdf
        
    def generate_betwVals(self):
        if self.G is None:
            raise ValueError("Graph not generated. Call generate_graph() first.")
        
        betw_centr = nx.betweenness_centrality(self.G)
        betwdf = pd.DataFrame(list(betw_centr.items()), columns=['node', 'value'])
        betwdf['norm_val'] = betwdf['value'] / betwdf['value'].max()
        return betwdf
            
    def generate_edgeBetw(self):
        if self.G is None:
            raise ValueError("Graph not generated. Call generate_graph() first.")
        
        edge_betw = nx.edge_betweenness_centrality(self.G)
        edge_betwdf = pd.DataFrame(list(edge_betw.items()), columns=['Pair', 'Edge Value'])
        edge_betwdf[['Node1', 'Node2']] = pd.DataFrame(edge_betwdf['Pair'].tolist(), index=edge_betwdf.index)
        edge_betwdf = edge_betwdf[['Node1', 'Node2', 'Edge Value']]
        edge_betwdf['Norm Value'] = edge_betwdf['Edge Value'] / edge_betwdf['Edge Value'].max()
        return edge_betwdf

# Initialize Dash app
app = dash.Dash(__name__)

# Load data and generate initial graph
newGraph = CentralityAnalysis()
newGraph.generate_graph()

datasets = ['eigenVals', 'betwVals', 'degrVals', 'closeVals']
dataframes = {}

for dataset in datasets:
    df = getattr(newGraph, f'generate_{dataset}')()
    df['node'] = df['node'].str.replace(r'\D', '', regex=True)
    df['node'] = pd.to_numeric(df['node'])
    df = df.sort_values(by='node', ascending=True)
    df = df.drop(df.index[-1])
    dataframes[dataset] = df

# Define your dataframes (assuming dataframes is defined elsewhere)
norm_vals = {
    'Eigenvector centrality values': dataframes['eigenVals']['norm_val'],
    'Betweenness centrality values': dataframes['betwVals']['norm_val'],
    'Degree centrality values': dataframes['degrVals']['norm_val'],
    'Closeness centrality values': dataframes['closeVals']['norm_val']
}

# Create dropdown widgets for y-axis
y1_dropdown = dcc.Dropdown(
    id='x-axis',
    options=[{'label': key, 'value': key} for key in norm_vals.keys()], 
    value='Eigenvector centrality values', 
    style={'width': '300px', 'border-radius': '5px'}  # Adjust width and border-radius here
)
y2_dropdown = dcc.Dropdown(
    id='y-axis',
    options=[{'label': key, 'value': key} for key in norm_vals.keys()], 
    value='Betweenness centrality values', 
    style={'width': '300px', 'border-radius': '5px'}  # Adjust width and border-radius here
)

# Create an output div for the plot
plot_output = html.Div(id='plot-output')

# Define callback to update plot
@app.callback(
    Output('plot-output', 'children'),
    [Input('x-axis', 'value'),
     Input('y-axis', 'value')]
)
def update_plot(x_axis, y_axis):
    # Get the selected data
    y1_data = norm_vals[x_axis]
    y2_data = norm_vals[y_axis]

    # Calculate regression line
    slope, intercept, r_value, p_value, std_err = linregress(y1_data, y2_data)
    regression_line = slope * np.array(y1_data) + intercept

    # Format R and R-squared values
    r_text = f'R: {r_value:.2f}'
    r_squared_text = f'R-squared: {r_value**2:.2f}'

    # Add regression line with R and R-squared values to the legend
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=y1_data, y=y2_data, mode='markers', name='Scatter Plot'))
    fig.add_trace(go.Scatter(x=y1_data, y=regression_line, mode='lines', name=f'Regression Line ({r_text}, {r_squared_text})'))
    fig.update_layout(title='Scatterplot with Regression Analysis', xaxis_title=x_axis, yaxis_title=y_axis, width=800)  # Adjust width here
    fig.update_layout(template='ggplot2')  # Set plot style to ggplot2
    return dcc.Graph(figure=fig)

# Layout of the app
app.layout = html.Div([
    html.H1(children='Comparing Centrality Metrics with Regression Analysis', style={'text-align': 'center'}),
    html.Div([html.Label('X-axis:'), y1_dropdown], style={'margin-bottom': '10px'}),
    html.Div([html.Label('Y-axis:'), y2_dropdown], style={'margin-bottom': '10px'}),
    plot_output
])

if __name__ == '__main__':
    app.run_server(debug=True)
