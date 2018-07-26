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
excluded_from_map = ["Lakshadweep"]


def plot_india_map(state_dict: dict):
    all_states = []

    for k in state_dict:
        all_states.append({"state": k})

    cmap = matplotlib.cm.get_cmap('copper_r')

    try:
        values = [x / max(state_dict.values()) for x in state_dict.values()]
    except ZeroDivisionError:
        values = [0] * len(all_states)
    colors = [cmap(x) for x in values]

    places = ox.gdf_from_places(all_states)
    places = ox.project_gdf(places)
    ox.plot_shape(places, ec="w", fc=colors)


def plot_most_stations():
    stations = get_station_data()
    data = get_data()
    c = Counter()
    for r in data:
        try:
            c.update({stations[str(r.station_code).strip()][2]})
        except KeyError:
            pass

    all_states = OrderedDict()
    with open(STATES_DATA_FILE) as f:
        for line in f:
            s = line.strip().split(",")
            if s[1] not in excluded_from_map:
                all_states[s[1]] = c[s[2]]

    plot_india_map(all_states)


if __name__ == "__main__":
    plot_most_stations()
