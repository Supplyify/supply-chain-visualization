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

print(df.head())

fig = go.Figure()

for index, row in df.iterrows():
    print(index)
    try:
        facility = geocode(f"{row['FACILITY ADDRESS']} {row['FACILITY STATE']} {row['FACILITY ZIPCODE']}")
        hub = geocode(f"{row['HUB ADDRESS']} {row['HUB STATE']} {row['HUB ZIPCODE']}")

        df.loc[index,'FACILITY LAT'], df.loc[index,'FACILITY LNG'] = facility
        df.loc[index,'HUB LAT'], df.loc[index,'HUB LNG'] = hub

        fig.add_trace(go.Scattergeo(
            locationmode='USA-states',
            lon=[facility[1], hub[1]],
            lat=[facility[0], hub[0]],
            mode='lines',
            line=dict(
                width=1,
                 color='red'
            ),
        ))
    except KeyboardInterrupt:
        break
    except:
        continue

fig.add_trace(go.Scattergeo(
    locationmode='USA-states',
    lon=df['FACILITY LNG'],
    lat=df['FACILITY LAT'],
    hoverinfo='text',
    text=df['FACILITY ADDRESS'],
    mode='markers',
    marker=dict(
        size=2,
        color='rgb(255, 0, 0)',
        line=dict(
            width=3,
            color='rgba(68, 68, 68, 0)'
        )
    )
))


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
