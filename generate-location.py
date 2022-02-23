import argparse
import pandas as pd
from random_address import real_random_address

# use for help with cli interaction
parser = argparse.ArgumentParser(description='Generate Supply Chain Locations')
parser.add_argument('input', help='input supply chain data')
parser.add_argument('output', help='output file')
args = parser.parse_args()

# read in the csv
df = pd.read_csv(args.input)

# remove columns that are no longer needed
df.drop(columns=[
    'SupplierAddress',
    'City',
    'Country',
    'CountryCode',
    'State',
    'CustomerAddress',
    'PostalCode',
], inplace=True)

# helper function to generate locations
def generate_locations():
    locations = real_random_address()
    # remove unnecessary values
    locations.pop('coordinates', None)
    locations.pop('address2', None)
    # join the address into string
    return ' '.join(map(str, locations.values()))


# generate random addresses for the supplier and customer
df = df.assign(
    SupplierAddress=[generate_locations() for _ in range(df.shape[0])],
    CustomerAddress=[generate_locations() for _ in range(df.shape[0])],
)

# output to csv
df.to_csv(args.output)
