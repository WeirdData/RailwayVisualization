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

from collections import Counter, defaultdict

import matplotlib.pylab as plt
import numpy as np
import requests
from bs4 import BeautifulSoup
from colour import Color

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


def train_distribution():
    data = get_full_trains()
    c = Counter()
    train_type = ["Special", "Long Distance", "Long Distance",
                  "Kolkata Suburban",
                  "Other Suburban", "Passenger", "MEMU", "DEMU", "reserved",
                  "Mumbai Locals"]
    for r in data:
        try:
            if len(r.train_number) == 5:
                letter = str(r.train_number)[0]
                c.update({train_type[int(letter)]})
        except (TypeError, ValueError) as e:
            pass

    names = []
    values = []
    for k in c:
        names.append(k)
        values.append(c[k])

    cmap = plt.cm.get_cmap('Blues')
    colors = [cmap(x / max(values)) for x in values]

    fig, ax = plt.subplots(figsize=(8, 4), subplot_kw=dict(aspect="equal"))
    wedges, texts = ax.pie(values, wedgeprops=dict(width=0.5), startangle=30,
                           colors=colors)

    bbox_props = dict(boxstyle="square,pad=0.3", fc="w", ec="k", lw=0.72)
    kw = dict(xycoords='data', textcoords='data',
              arrowprops=dict(arrowstyle="<-"),
              bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1) / 2. + p.theta1
        y = np.sin(np.deg2rad(ang))
        x = np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        ax.annotate(names[i], xy=(x, y), xytext=(1.35 * np.sign(x), 1.4 * y),
                    horizontalalignment=horizontalalignment, **kw)

    plt.show()


def zone_wise_distribution():
    data = get_full_trains()
    station_data = get_station_data()

    # Except sububan and passenger trains
    division = ["0", "1", "2", "6", "7"]

    zone_counter = Counter()
    subdata = defaultdict(list)

    for r in data:
        try:
            if len(r.train_number) == 5:
                if r.origin_code in station_data.keys():
                    zone = station_data[r.origin_code][-1]
                    if len(zone.strip()) > 0:
                        zone_counter.update({zone})
                        subdata[zone].append(r)
        except (TypeError, ValueError) as e:
            pass

    names = []
    values = []
    ld = "Long Distance"
    su = "Suburban"
    for v in subdata:
        temp = defaultdict(int)
        for r in subdata[v]:
            letter = str(r.train_number)[0]
            if letter in division:
                temp[ld] = temp[ld] + 1
            else:
                temp[su] = temp[su] + 1

        temp_list = [temp[ld], temp[su]]

        names.append(v)
        values.append(temp_list)

    fig, ax = plt.subplots()

    size = 0.3
    vals = np.array(values)

    ot = np.linspace(0.1, 0.9, len(vals))
    cmap = plt.get_cmap("tab20b")
    outer_colors = [cmap(x) for x in ot]
    inner = []
    decrease = 0.25  # Percent dark
    # Change color of inner pie
    for k in outer_colors:
        r, g, b, a = k
        col2 = Color(
            rgb=(r - (r * decrease), g - (g * decrease), b - (b * decrease)))
        inner = inner + [col2.get_rgb(), (r, g, b, 0.6)]

    inner_colors = [x for x in inner]

    ax.pie(vals.sum(axis=1), radius=1, colors=outer_colors,
           wedgeprops=dict(width=size, edgecolor='w'),
           startangle=90)

    ax.pie(vals.flatten(), radius=1 - size, colors=inner_colors,
           wedgeprops=dict(width=size, edgecolor='w'), startangle=90)
    print(sum(vals.flatten()))
    ax.set(aspect="equal")
    plt.show()


def zonal_connectivity():
    """
    Warning: This function will take long time
    Plots histogram of connectivity between zones
    """
    data = get_full_trains()
    station_data = get_station_data()

    c = Counter()

    for z in station_data:
        c.update({station_data[z][3]})

    zone_list = []
    for k in c:
        if len(k) > 0:
            zone_list.append(k)

    zone_list.sort()
    mat = np.zeros(shape=(len(zone_list), len(zone_list)))

    for r in data:
        if r.origin is not None:
            try:
                k = r.get_connection_pairs()
                if [x in station_data.keys() for x in
                    set(np.asarray(k).flatten())]:
                    for pair in k:

                        origin = zone_list.index(station_data[pair[0]][3])
                        dest = zone_list.index(station_data[pair[1]][3])
                        if origin != dest:
                            mat[origin, dest] = mat[origin, dest] + 1
            except (ValueError, KeyError):
                pass

    fig, ax = plt.subplots()
    heatmap = ax.pcolor(mat)
    plt.xticks(np.arange(len(zone_list)) + 0.5, zone_list, rotation=45, )
    plt.yticks(np.arange(len(zone_list)) + 0.5, zone_list, rotation=45)
    ax.set(aspect="equal")
    plt.colorbar(heatmap)
    plt.show()


def play():
    """
    Warning: This function will take long time
    Plots histogram of connectivity between States
    """
    data = get_full_trains()
    station_data = get_station_data()

    c = Counter()

    reject_words = ["None", "BANG"]

    for z in station_data:
        if not (station_data[z][2] in reject_words):
            c.update({station_data[z][2]})

    state_list = []
    for k in c:
        if len(k) > 0:
            state_list.append(k)

    state_list.sort()
    mat = np.zeros(shape=(len(state_list), len(state_list)))

    for r in data:
        if r.origin is not None:
            try:
                k = r.get_connection_pairs()
                if [x in station_data.keys() for x in
                    set(np.asarray(k).flatten())]:
                    for pair in k:

                        origin = state_list.index(station_data[pair[0]][2])
                        dest = state_list.index(station_data[pair[1]][2])
                        if origin != dest:
                            mat[origin, dest] = mat[origin, dest] + 1
            except (ValueError, KeyError):
                pass

    fig, ax = plt.subplots()
    heatmap = ax.pcolor(mat, cmap='copper')
    plt.xticks(np.arange(len(state_list)) + 0.5, state_list, rotation=45, )
    plt.yticks(np.arange(len(state_list)) + 0.5, state_list, rotation=45)
    ax.set(aspect="equal")
    plt.colorbar(heatmap)
    plt.show()


if __name__ == "__main__":
    play()
