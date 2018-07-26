"""
Rohit Suratekar
July 2018

Ministry of Railways (2015) Indian Railways Train Time Table.
https://data.gov.in/resources/indian-railways-time-table-trains-available
-reservation-01112017. Released Under National Data Sharing and Accessibility
Policy (NDSAP) https://data.gov.in/sites/default/files/NDSAP.pdf

Headers: Train No,Train Name,SEQ,Station Code,Station Name,Arrival time,
Departure Time, Distance,Source Station,Source Station Name,Destination
Station,Destination Station Name


This data file is not included in this repository to avoid redistribution
issues (if any). You can download from above link.
"""

from collections import Counter

import matplotlib.pylab as plt
import numpy as np
import requests
from bs4 import BeautifulSoup

from helper import *

DISTANCE_CUT_OFF = 27.71


def get_statistics() -> None:
    """
    Prints simple statistics about data set
    """
    data = get_data()
    count_train = Counter()
    count_stations = Counter()
    count_source = Counter()
    count_destination = Counter()
    first_train = True
    run = 0
    train_counter = 0
    previous_count = 0
    for r in data:
        count_train.update({r.number})
        count_source.update({r.source_station})
        count_destination.update({r.destination_station})
        # Count both origin and destination stations
        count_stations.update({r.station_code})
        count_stations.update({r.destination_station})

        # Get distance only from last station
        if r.number is str and r.distance is str:
            # Ignores header if any
            pass
        else:
            if first_train:
                train_counter = r.number
                first_train = False

            if train_counter != r.number:
                try:
                    run += int(previous_count)
                except ValueError:
                    # Few Train has NA in this field
                    pass
                train_counter = r.number
            else:
                previous_count = r.distance

    print("Number of entries: %d" % len(data))
    print("Number of Trains: %d" % len(count_train))
    print("Number of Origin Stations: %d" % len(count_source))
    print("Number of Final Destinations: %d" % len(count_destination))
    print("Number of Stations: %d" % len(count_stations))
    print("Total Distance covered: %d" % run)


def stations_with_most_trains() -> None:
    """
    Plots bar plot of stations visited by most number of trains
    :return:
    """
    count = Counter()
    for r in get_data():
        count.update({r.station_name})

    names = []
    values = []
    for c in count.most_common(10):
        names.append(c[0])
        values.append(c[1])

    ind = np.arange(len(names))

    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.barh(ind, values, color="#00b6cb")
    ax.set_yticks(ind)
    ax.set_xlabel("Number of unique train visits")
    ax.set_yticklabels([x.lower() for x in names])
    plt.show()


def train_distance() -> None:
    """
    Plots distribution of train distances
    """
    station_distance = []
    for r in get_full_trains():
        station_distance.append(float(r.total_distance))

    station_distance = np.asanyarray([x for x in station_distance if x < 100])

    plt.hist([x for x in station_distance if x >= DISTANCE_CUT_OFF], 50,
             label="Accepted")
    plt.hist([x for x in station_distance if x < DISTANCE_CUT_OFF], 25,
             label="Rejected", )

    # plt.hist(station_distance, 50)
    plt.ylabel("Number of trains")
    plt.xlabel("Travel Distance (in Km)")
    plt.legend(loc=0)
    plt.show()


def stations_with_cut_off() -> None:
    """
    Plots bar plot of stations visited by most number of trains assuming
    distance cutoff
    """

    count = Counter()
    for r in get_full_trains():
        if float(r.total_distance) > DISTANCE_CUT_OFF:
            count.update({r.origin})

    names = []
    values = []
    for c in count.most_common(10):
        names.append(c[0])
        values.append(c[1])

    ind = np.arange(len(names))

    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.barh(ind, values, color="#95d13c")
    ax.set_yticks(ind)
    ax.set_xlabel("Number of unique long distance train visits")
    ax.set_yticklabels([x.lower() for x in names])
    plt.show()


def stations_with_train_origin() -> None:
    """
    Plots bar plot of station with most number of unique train origins
    """
    count = Counter()
    train_number = 0
    for r in get_data():
        if r.number is not str:
            if r.number != train_number:
                count.update({r.source_station_name})
                train_number = r.number

    names = []
    values = []
    for c in count.most_common(10):
        names.append(c[0])
        values.append(c[1])

    ind = np.arange(len(names))
    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.barh(ind, values, color="#fcaf6d")
    ax.set_yticks(ind)
    ax.set_xlabel("Number of unique train origins")
    ax.set_yticklabels([x.lower() for x in names])
    plt.show()


def stations_pairs() -> None:
    count = Counter()
    train_number = 0
    for r in get_data():
        if r.number is not str:
            if r.number != train_number:
                count.update({
                    r.source_station_name + "--" + r.destination_station_name})
                train_number = r.number

    names = []
    values = []
    for c in count.most_common(20):
        names.append(c[0])
        values.append(c[1])

    ind = np.arange(len(names))
    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.barh(ind, values, color="#e3bc13")
    ax.set_yticks(ind)
    ax.set_xlabel("Number of origin--destinations trains")
    ax.set_yticklabels([x.lower() for x in names])
    plt.show()


def download_station_data() -> None:
    """
    Station data is scrapped from https://irfca.org/apps/station_codes

    Downloads all station name, station and zone

    This code might break if original web page is modified.
    This was working till 22 July 2018

    However lot of stations are hand curated.
    You can use scrip from "fetch_station_data.py" to extract geographical
    information regarding missing stations
    """

    last_page = 41  # There are 41 pages on that website
    base_url = "https://irfca.org/apps/station_codes?page="

    with open(STATION_DATA_FILE, "w") as f:
        for i in range(last_page):
            r = requests.get(base_url + str(i + 1))
            new_soup = BeautifulSoup(r.text, 'html.parser')
            table = new_soup.find("table", {"class": "zebra-striped"})
            table_body = table.find("tbody")
            for row in table_body.find_all("tr"):
                values = []
                for col in row.find_all("td"):
                    values.append(col.text)

                print(";".join(values), file=f)


def get_state_info():
    stations = get_station_data()
    data = get_data()
    c = Counter()
    for r in data:
        try:
            c.update({stations[str(r.station_code).strip()][2]})
        except KeyError:
            pass

    print(c)


def get_additional_info():
    data = get_full_trains()
    c = {}
    for r in data:
        try:
            c[r.train_number] = float(r.total_distance) / len(r.station_list)
        except ZeroDivisionError:
            pass

    print(sorted(c.items(), key=lambda kv: kv[1]))


if __name__ == "__main__":
    get_additional_info()
