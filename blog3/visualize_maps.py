import datetime
from collections import OrderedDict, Counter, defaultdict

import matplotlib
import matplotlib.pylab  as plt
import numpy as np
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
    cmap = matplotlib.cm.get_cmap('YlGn')  # Change according to your taste
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
            if len(r.train_number) == 5:
                letter = str(r.train_number)[0]
                if letter in ["0", "1", "2", "6", "7"]:
                    c.update({stations[str(r.origin_code).strip()][2]})
                    a += 1
        except (TypeError, ValueError):
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


class TimeHolder:
    def __init__(self, time, value):
        datetime_object = datetime.datetime.strptime(time, '%H:%M:%S')
        self.time = datetime_object
        self.value = value
        self.name = datetime_object.strftime('%I:%M %p')

    def check_slot(self):
        for i in range(24):
            if self.time.time() < datetime.time(hour=i):
                return i
        return 24


def convert_slot(hour: int):
    if hour != 24:
        d = datetime.time(hour=hour)
        d2 = datetime.time(hour=(hour - 1))
        return d2.strftime('%H:%M') + " - " + d.strftime('%H:%M')
    else:
        return "23:00 - 00:00"


def train_departure_time():
    data = get_full_trains()
    c = Counter()
    # for r in data:
    #     try:
    #         c.update(
    #             {r.station_list[0].departure_time})  # First station departure
    #     # c.update({r.station_list[-1].arrival_time})  # Last station arrival
    #     except IndexError:
    #         pass

    # After removing local and suburbans
    for r in data:
        try:
            if len(r.train_number) == 5:
                letter = str(r.train_number)[0]
                if letter in ["0", "1", "2", "6", "7"]:
                    c.update(
                        {r.station_list[
                             0].departure_time})  # First station departure
        #   c.update({r.station_list[-1].arrival_time})  # Last station arrival
        except (IndexError, TypeError):
            pass

    object_holder = []
    for k in c.most_common():
        object_holder.append(TimeHolder(k[0], k[1]))

    new_list = defaultdict(int)

    for o in object_holder:
        new_list[o.check_slot()] += o.value

    print(new_list)
    f = []
    for k in new_list.keys():
        f.append((k, new_list[k]))

    f.sort(key=lambda x: x[0], reverse=True)
    names = []
    values = []
    colors = []

    for t in f:
        names.append(convert_slot(t[0]))
        values.append(t[1])
        if t[0] < 13:
            colors.append("#f87eac")
        else:
            colors.append("#00baa1")

    ind = np.arange(len(names))
    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.barh(ind, values, color=colors)
    ax.set_yticks(ind)
    ax.set_xlabel("Frequency")
    ax.set_yticklabels([str(x) for x in names])
    plt.show()


def common_timings():
    data = get_full_trains()
    c = Counter()
    for r in data:
        try:
            if len(r.train_number) == 5:
                letter = str(r.train_number)[0]
                if letter in ["0", "1", "2", "6", "7"]:
                    # c.update(
                    #     {r.station_list[
                    #          0].departure_time})  # First station departure
                    c.update({r.station_list[-1].arrival_time})  # Last station arrival
        except (IndexError, TypeError):
            pass

    object_holder = []
    for k in c.most_common(10):
        object_holder.append(TimeHolder(k[0], k[1]))

    object_holder.sort(key=lambda x: x.time, reverse=True)
    names = []
    values = []

    for o in object_holder:
        names.append(o.name)
        values.append(o.value)

    ind = np.arange(len(names))
    figure = plt.figure()
    ax = figure.add_subplot(111)
    ax.barh(ind, values, color="#00baa1")
    ax.set_yticks(ind)
    ax.set_xlabel("Frequency")
    ax.set_yticklabels([str(x) for x in names])
    plt.show()


if __name__ == "__main__":
    common_timings()
