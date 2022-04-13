from dis import show_code
import requests
import pandas as pd
import plotly.graph_objects as go
from dotenv import load_dotenv
import os
from tqdm import tqdm

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
MAPBOX_ACCESS_TOKEN = os.getenv('MAPBOX_ACCESS_TOKEN')


def geocode(address_or_zipcode):
    lat, lng = None, None
    api_key = GOOGLE_API_KEY
    base_url = 'https://maps.googleapis.com/maps/api/geocode/json'
    endpoint = f'{base_url}?address={address_or_zipcode}&key={api_key}'
    # see how our endpoint includes our API key? Yes this is yet another reason to restrict the key
    r = requests.get(endpoint)
    if r.status_code not in range(200, 299):
        return None, None
    try:
        '''
        This try block incase any of our inputs are invalid. This is done instead
        of actually writing out handlers for all kinds of responses.
        '''
        results = r.json()['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
    except:
        pass
    return lat, lng


df = pd.merge(
    pd.read_csv('hub-data.csv'),
    pd.read_csv('facility-data.csv'),
    left_on='HUB UNIQUE ID',
    right_on='FACILITY HUB',
    how='inner'
)

tqdm.pandas()

fig = go.Figure()

for index, row in tqdm(df.iterrows(), desc='Generating Map', total=df.shape[0]):
    try:
        for place in ['FACILITY', 'HUB']:
            df.loc[index, f'{place} COMPLETE ADDRESS'] = ' '.join(map(str, [
                row[f'{place} ADDRESS'],
                row[f'{place} STATE'],
                row[f'{place} ZIPCODE'],
            ]))

        facility = geocode(df.loc[index, 'FACILITY COMPLETE ADDRESS'])
        hub = geocode(df.loc[index, 'HUB COMPLETE ADDRESS'])

        df.loc[index, 'FACILITY LAT'], df.loc[index, 'FACILITY LNG'] = facility
        df.loc[index, 'HUB LAT'], df.loc[index, 'HUB LNG'] = hub

        scale = row['CURRENT TEST SURPLUS'] / row['NUMBER OF TESTS PRODUCED']

        fig.add_trace(go.Scattermapbox(
            lon=[hub[1], facility[1]],
            lat=[hub[0], facility[0]],
            mode='lines',
            legendgroup='PATHS',
            legendgrouptitle={
                'text': 'PATHS',
            },
            line=dict(
                width=1,
                color=f'rgb({-255 * scale + 255}, {255 * scale}, 0)',
            ),
        ))
    except KeyboardInterrupt:
        break

fig.add_trace(go.Scattermapbox(
    lon=df['HUB LNG'],
    lat=df['HUB LAT'],
    customdata=df[[
        'HUB COMPLETE ADDRESS',
        'HUB UNIQUE ID',
        'NUMBER OF TESTS PRODUCED',
        'NUMBER OF TESTS DISTRIBUTED',
        'CURRENT TEST SURPLUS'
    ]],
    legendrank=0,
    hovertemplate='<b>%{customdata[0]}</b><br>' +
    'HUB UNIQUE ID: %{customdata[1]}<br>'
    'TESTS PRODUCED: %{customdata[2]}<br>' +
    'TESTS DISTRIBUTED: %{customdata[3]}<br>' +
    'TESTS SURPLUS: %{customdata[4]}',
    mode='markers',
    name='HUBS',
    marker=dict(
        sizemin=5,
        sizeref=1,
        sizemode='area',
        size=df['CURRENT TEST SURPLUS'],
        color=df['NUMBER OF TESTS DISTRIBUTED'] / df['NUMBER OF TESTS PRODUCED'],
        colorscale=[[0, 'rgba(255,0,0,255)'], [1, 'rgba(0,255,0,255)']],
        opacity=0.7
    )
))

fig.add_trace(go.Scattermapbox(
    lon=df['FACILITY LNG'],
    lat=df['FACILITY LAT'],
    mode='markers',
    name='FACILITIES',
    customdata=df[[
        'FACILITY COMPLETE ADDRESS',
        'FACILITY UNIQUE ID',
        'FACILITY HUB',
        'NUMBER OF TESTS',
        'NUMBER POSITIVE',
        'NUMBER NEGATIVE',
    ]],
    legendrank=0,
    hovertemplate='<b>%{customdata[0]}</b><br>' +
    'FACILITY UNIQUE ID: %{customdata[1]}<br>'
    'FACILITY HUB: %{customdata[2]}<br>' +
    'NUMBER OF TESTS: %{customdata[3]}<br>' +
    'NUMBER POSITIVE: %{customdata[4]}<br>' +
    'NUMBER NEGATIVE: %{customdata[5]}',
    marker=dict(
        sizemin=5,
        sizeref=1,
        sizemode='area',
        size=df['NUMBER OF TESTS'],
        color=df['NUMBER NEGATIVE'] / df['NUMBER OF TESTS'],
        colorscale=[[0, 'rgba(0,0,255,255)'], [1, 'rgba(255,255,0,255)']],
    )
))

fig.update_layout(
    title_text='COVID Supply Chain Visualization',
    showlegend=True,
    autosize=True,
    hovermode='closest',
    mapbox={
        'center': {
            'lat': 37.0902,
            'lon': -95.7129,
        },
        'style': 'light',
        'zoom': 4,
        'accesstoken': MAPBOX_ACCESS_TOKEN,
    }
)

fig.show()

fig.write_html("./index.html")
