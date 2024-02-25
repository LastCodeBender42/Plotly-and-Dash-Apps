import dash
from dash import html, dcc
import pandas as pd
import plotly.graph_objs as go

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def plotly_line_graph():
    # Read CSV file into Pandas DataFrame
    data = pd.read_csv('importFileTest.csv')  # Replace with your CSV file path

    # Create a Plotly figure with an interactive line graph
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['source'], y=data['target'], mode='lines', name='Line Plot', marker=dict(color='#32CD32')))
    fig.update_layout(title='Plotly Line Graph in Dash', xaxis_title='X-axis', yaxis_title='Y-axis')

    return dcc.Graph(figure=fig)


def plotly_freq_hist():
    # Read CSV file into Pandas DataFrame
    data = pd.read_csv('importFileTest.csv')

    # Create a Plotly figure with an interactive histogram
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=data['target'], histnorm='probability density', name='Density Line', marker=dict(color='orange')))
    fig.update_layout(title='Density Histogram with Density Line in Dash', xaxis_title='Y-axis', yaxis_title='Probability', bargap=0.2)

    return dcc.Graph(figure=fig)


def plotly_network():
    edge_list_file = "1yok.txt"  # Replace with your file path

    # Read edge list file and process data
    edges = []
    with open(edge_list_file, "r") as file:
        for line in file:
            source, target, *_ = line.strip().split()  # Assuming at least two columns separated by space or tab
            edges.append({'from': source, 'to': target})

    all_nodes = set()
    for edge in edges:
        all_nodes.add(edge['from'])
        all_nodes.add(edge['to'])

    nodes = []
    node_id_mapping = {}
    for idx, node in enumerate(all_nodes):
        node_id = idx + 1
        nodes.append({'id': node_id, 'label': node, 'title': f'Description for {node}'})
        node_id_mapping[node] = node_id

    for edge in edges:
        edge['from'] = node_id_mapping[edge['from']]
        edge['to'] = node_id_mapping[edge['to']]

    # Generating the HTML content for network visualization
    html_content = f"""
    <div id="network-container" style="width: 100%; height: 90vh; border: 1px solid lightgray;"></div>

    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
    <script type="text/javascript">
        var nodes = new vis.DataSet({nodes});
        var edges = new vis.DataSet({edges});

        var container = document.getElementById('network-container');
        var data = {{ nodes: nodes, edges: edges }};
        var options = {{
            nodes: {{
                color: {{
                    border: '#708090',
                    background: '#04D9FF',
                }},
            }},
        }};
        var network = new vis.Network(container, data, options);
    </script>
    """
    return html_content

def py3dmol_structure():
    import pandas as pd
    import py3Dmol

    df = pd.read_csv("/Users/davidfoutch/Desktop/4pld.txt", sep="\t")

    view = py3Dmol.view(query='pdb:4PLD')
    chA = {'chain':'A'}
    chB = {'chain':'B'}
    view.addSurface(py3Dmol.VDW,{'opacity':0.4,'color':'white'}, chA)
    view.setStyle(chA,{'cartoon': {'color':'white'}})
    view.setStyle(chB,{'': {'color':None}})
    view.setHoverable({},True,'''function(atom,viewer,event,container) {
                       if(!atom.label) {
                        atom.label = viewer.addLabel(atom.resn+":"+atom.atom,{position: atom, backgroundColor: 'mintcream', fontColor:'black'});
                       }}''',
                   '''function(atom,viewer) { 
                       if(atom.label) {
                        viewer.removeLabel(atom.label);
                        delete atom.label;
                       }
                    }''')



    resset = [300,400,401,402,403,404]
    for i in resset:
        view.addStyle({'chain':'A','resi': i},{'cartoon':{'color':'red'}})

    for i in range(723):
        
        view.addCylinder(
            {'start':dict(x=df.iloc[i][2],y=df.iloc[i][3],z=df.iloc[i][4]),
            'end':dict(x=df.iloc[i][5],y=df.iloc[i][6],z=df.iloc[i][7]),
            'radius':0.12,
            'fromCap':1,
            'toCap':1,
            'color':'teal',
            'dashes':False
            }
        ) 
                                                     
    view.render()


app.layout = html.Div([
    html.H1("Partitioned Canvases with Plotly Line Graph"),
    html.Div([
        html.Div([
            html.H2("Plotly Line Graph"),
            plotly_line_graph()
        ], style={'width': '50%', 'display': 'inline-block'}),
        html.Div([
            html.H2("Frequency Histogram"),
            plotly_freq_hist()
        ], style={'width': '50%', 'display': 'inline-block'}),
    ]),
    html.H2("Network and Structure Visualization"),
    html.Div([
        html.Iframe(srcDoc=plotly_network(), style={'width': '100%', 'height': '90vh', 'border': 'none'})
    ])
])

if __name__ == '__main__':
    app.run_server(port=8030)
