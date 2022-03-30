from ipywidgets.embed import embed_minimal_html
import gmaps
import requests
import pandas as pd

GOOGLE_API_KEY = 'AIzaSyCwBUDe6L9azdW7Gomzv-eEpz_c_OSe0sY'

gmaps.configure(api_key=GOOGLE_API_KEY)

fig = gmaps.figure()


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

features = list()

for index, row in df.iterrows():
    print(index)
    try:
        start = geocode(f"{row['FACILITY ADDRESS']} {row['FACILITY STATE']} {row['FACILITY ZIPCODE']}")
        end = geocode(f"{row['HUB ADDRESS']} {row['HUB STATE']} {row['HUB ZIPCODE']}")
        features.append(gmaps.Line(
            start=start,
            end=end,
            stroke_weight=3.0
        ))
        features.append(gmaps.Marker(start))
        features.append(gmaps.Marker(end))
    except KeyboardInterrupt:
        break
    except:
        continue

drawing = gmaps.drawing_layer(features=features)
fig.add_layer(drawing)
embed_minimal_html('export.html', views=[fig])
