"""
Rohit Suratekar
August 2018

Code used in analysis shown in Indian Railways part II - Old versus New
"""

from collections import Counter, defaultdict

import matplotlib.pylab as plt
import numpy as np
from colour import Color

from helper import *


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


def state_wise_connectivity():
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

    with open("state_array.txt", "w") as f:
        for line in mat:
            print_text = ""
            for k in line:
                print_text += k + ","
            print_text = print_text[:-1]
            print(print_text, file=f)

    fig, ax = plt.subplots()
    heatmap = ax.pcolor(mat, cmap='Purples_r', vmin=0.01)
    heatmap.cmap.set_under('black')
    plt.xticks(np.arange(len(state_list)) + 0.5, state_list, rotation=90, )
    plt.yticks(np.arange(len(state_list)) + 0.5, state_list, rotation=0)
    ax.set(aspect="equal")
    plt.ylabel("Destination State")
    plt.xlabel("Origin State")
    plt.colorbar(heatmap)
    plt.show()


def different_states_connected():
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

    state_connectivity = []
    with open("save.txt") as f:  # File created in state_wise_connectivity()
        mat = []
        for line in f:
            line = [int(x) for x in line.split(",")]
            mat.append(np.asarray(line))
            state_connectivity.append(sum(np.asarray(line) > 0))

    mat = np.asarray(mat)

    hh = {state_list[x]: state_connectivity[x] for x in range(len(mat))}
    d = sorted(hh.items(), key=lambda x: x[1], reverse=True)

    names = []
    values = []

    for k in d:
        names.append(k[0])
        values.append(k[1])

    print(names)
    print(values)

    fig, ax = plt.subplots()

    ind = np.arange(len(names))
    ax.barh(ind, values, color="#e3bc13")
    ax.set_yticks(ind)
    ax.set_xlabel("Number of different states connected")
    ax.set_ylabel("State/Union Territory")
    ax.set_yticklabels([x for x in names])
    plt.show()


def run():
    different_states_connected()
