from collections import OrderedDict, Counter

import matplotlib
import osmnx as ox

from helper import *

proxy = 'http://proxy.ncbs.res.in:3128'  # Your proxy, if any.
os.environ['https_proxy'] = proxy
os.environ['http_proxy'] = proxy

ox.config(log_console=False, use_cache=True)

# Following places are excluded from plotting because corresponding polygons
# are not on scale and I was unable to make it in shape
excluded_from_map = ["Lakshadweep", "Andaman and Nicobar Islands"]


def get_colors(values, start=0.3):
    val = [x + start for x in values]
    val = [x / max(val) for x in val]
    cmap = matplotlib.cm.get_cmap('Purples')  # Change according to your taste
    colors = [cmap(x) for x in val]
    return colors


def plot_india_map(state_dict: dict):
    all_states = []

    for k in state_dict:
        all_states.append({"state": k})

    try:
        values = [x / max(state_dict.values()) for x in state_dict.values()]
    except ZeroDivisionError:
        values = [0] * len(all_states)

    places = ox.gdf_from_places(all_states)
    places = ox.project_gdf(places)
    ox.plot_shape(places, ec="w", fc=get_colors(values))


def plot_most_stops():
    stations = get_station_data()
    data = get_data()
    c = Counter()
    a = 0
    for r in data:
        try:
            c.update({stations[str(r.station_code).strip()][2]})
            a += 1
        except KeyError:
            pass

    print(c)
    print(a)
    all_states = OrderedDict()
    with open(STATES_DATA_FILE) as f:
        for line in f:
            s = line.strip().split(",")
            if s[1] not in excluded_from_map:
                all_states[s[1]] = c[s[2]]

    plot_india_map(all_states)


def plot_most_stations():
    stations = get_station_data()
    data = get_data()
    stations_codes = Counter()
    a = 0
    for r in data:
        try:
            stations_codes.update({r.station_code})
        except KeyError:
            pass

    states = Counter()
    for r in stations_codes:
        try:
            states.update({stations[str(r).strip()][2]})
            a += 1
        except KeyError:
            pass
    print(states)
    print(a)
    all_states = OrderedDict()
    with open(STATES_DATA_FILE) as f:
        for line in f:
            s = line.strip().split(",")
            if s[1] not in excluded_from_map:
                all_states[s[1]] = states[s[2]]

    plot_india_map(all_states)


def train_origin_data():
    stations = get_station_data()
    data = get_full_trains()

    c = Counter()
    a = 0
    for r in data:
        try:
            c.update({stations[str(r.origin_code).strip()][2]})
            a += 1
        except KeyError:
            pass

    print(c)
    print(a)
    all_states = OrderedDict()
    with open(STATES_DATA_FILE) as f:
        for line in f:
            s = line.strip().split(",")
            if s[1] not in excluded_from_map:
                all_states[s[1]] = c[s[2]]

    plot_india_map(all_states)


def inter_state_trains():
    stations = get_station_data()
    data = get_full_trains()

    c = Counter()
    a = 0
    for r in data:
        try:
            c.update({stations[str(r.origin_code).strip()][2]})
            a += 1
        except KeyError:
            pass

    print(c)
    print(a)
    all_states = OrderedDict()
    with open(STATES_DATA_FILE) as f:
        for line in f:
            s = line.strip().split(",")
            if s[1] not in excluded_from_map:
                all_states[s[1]] = c[s[2]]

    plot_india_map(all_states)


if __name__ == "__main__":
    train_origin_data()
