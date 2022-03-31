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
    pd.read_csv('facility-data.csv'),
    pd.read_csv('hub-data.csv'),
    left_on='FACILITY UNIQUE ID',
    right_on='HUB UNIQUE ID',
    how='inner'
)

print(df.head())

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

        fig.add_trace(go.Scattermapbox(
            lon=[hub[1], facility[1]],
            lat=[hub[0], facility[0]],
            mode='lines',
            text=f"From Hub {row['HUB UNIQUE ID']} to Facility {row['FACILITY UNIQUE ID']}",
            line=dict(
                width=1,
                color='red',
            ),
        ))
    except KeyboardInterrupt:
        break


fig.add_trace(go.Scattermapbox(
    lon=df['HUB LNG'],
    lat=df['HUB LAT'],
    name=f"{df['HUB UNIQUE ID']}",
    text=df['HUB COMPLETE ADDRESS'],
    mode='markers',
    marker=dict(
        size=5,
        color='rgb(255, 0, 0)',
    )
))

fig.add_trace(go.Scattermapbox(
    lon=df['FACILITY LNG'],
    lat=df['FACILITY LAT'],
    text=df['FACILITY COMPLETE ADDRESS'],
    mode='markers',
    marker=dict(
        size=5,
        color='rgb(0, 255, 0)',
    )
))

fig.update_layout(
    title_text='COVID Supply Chain Visualization',
    showlegend=False,
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

fig.write_html("./export.html")
