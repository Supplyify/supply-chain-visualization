# FACILITY DATA

# FACILITY UNIQUE ID
# FACILITY ADDRESS
# FACILITY ZIPCODE
# FACILITY STATE
# NUMBER OF TESTS
# NUMBER POSITIVE
# NUMBER NEGATIVE
# FACILITY HUB – the company that owns/supplies the facility

# TEST DATA

# TEST DATE GIVEN
# TEST DATE COMPLETED
# FACILITY
# TEST RECIPIENT NAME
# TEST TURNAROUND TIME

import argparse
import csv
import datetime
import faker
from random_address import real_random_address
import random

fake = faker.Faker()

# cli integration
parser = argparse.ArgumentParser(description='Generate Covid Supply Chain Data')
parser.add_argument('num_facilities', help='number of facilities to generate', type=int)
parser.add_argument('num_tests', help='number of tests to generate', type=int)
args = parser.parse_args()


# generate facility data
with open("facility-data.csv", 'w', newline='') as f:
    w = csv.writer(f)
    # write the columns
    w.writerow([
        "ID",
        "Address",
        "Zipcode",
        "State",
        "Number of Tests",
        "Number Positive",
        "Number Negative",
        "Facility Hub",
    ])
    for i in range(args.num_facilities):
        location = real_random_address()
        positive = random.randint(0, args.num_tests)
        negative = random.randint(0, args.num_tests)
        w.writerow([
            i,
            location["address1"],
            location["postalCode"],
            location["state"],
            positive + negative,
            positive,
            negative,
            fake.bs().title(),
        ])

# generate covid test data
with open("test-data.csv", 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow([
        "Test Date Given",
        "Test Date Completed",
        "Facility",
        "Recipient Name",
        "Turnaround Time",
    ])
    for i in range(args.num_tests):
        date_given = fake.date_this_year()
        date_completed = fake.date_between(date_given, date_given + datetime.timedelta(30))
        w.writerow([
            date_given,
            date_completed,
            random.randint(0, args.num_facilities),
            fake.name(),
            (date_completed - date_given).days,
        ])
