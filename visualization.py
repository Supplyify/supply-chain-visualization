from ipywidgets.embed import embed_minimal_html
import gmaps
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv
import os

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

fig = go.Figure()

for index, row in df.iterrows():
    print(index)
    try:
        start = geocode(f"{row['FACILITY ADDRESS']} {row['FACILITY STATE']} {row['FACILITY ZIPCODE']}")
        end = geocode(f"{row['HUB ADDRESS']} {row['HUB STATE']} {row['HUB ZIPCODE']}")

        fig.add_trace(
            go.Scattergeo(
                locationmode='USA-states',
                lon=[start[1], end[1]],
                lat=[start[0], end[0]],
                mode='lines',
                line=dict(width=1, color='red'),
            )
        )
    except KeyboardInterrupt:
        break
    except:
        continue

fig.update_layout(
    title_text='COVID Supply Chain Visualization',
    showlegend=False,
    geo=dict(
        scope='north america',
        projection_type='azimuthal equal area',
        showland=True,
        landcolor='rgb(243, 243, 243)',
        countrycolor='rgb(204, 204, 204)',
    ),
)

fig.write_html("./export.html")
