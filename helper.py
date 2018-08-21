import csv
import os

# Can be downloaded with 'download_station_data()' function
STATION_DATA_FILE = "stations_data.txt"

# Can be downloaded from link given in the description
TRAIN_DATA_FILE = "Train_details_22122017.csv"

STATES_DATA_FILE = "states.csv"


class Train:
    """
    Simple class to access structured data
    """

    def __init__(self, data):
        self.data = data
        self.number = data[0]
        self.name = data[1]
        self.seq = data[2]  # Station Number from start
        self.station_code = data[3]
        self.station_name = data[4]
        self.arrival_time = data[5]
        self.departure_time = data[6]
        self.distance = data[7]
        self.source_station = data[8]
        self.source_station_name = data[9]
        self.destination_station = data[10]
        self.destination_station_name = data[11]


class FullTrain:
    """
    Train class to include all stations and full details
    """

    def __init__(self):
        self.train_number = None
        self.train_name = None
        self.origin = None
        self.origin_code = None
        self.destination = None
        self.destination_code = None
        self._station_list = []
        self.total_distance = 0

    @property
    def stations(self) -> list:
        return [x.station_code for x in self._station_list]

    @property
    def station_list(self) -> list:
        return self._station_list

    def add_station(self, train: Train):
        if self.origin is None:
            self.origin = train.source_station_name
            self.origin_code = train.source_station
            self.train_name = train.name
            self.train_number = train.number
            self.destination = train.destination_station_name
            self.destination_code = train.destination_station

        self._station_list.append(train)
        self.total_distance = train.distance

    def is_same_train(self, train: Train):
        return train.number == self.train_number

    def get_connection_pairs(self) -> list:
        """
        Returns pairs of possible source and destinations
        """
        all_pairs = []
        for i in range(len(self.stations)):
            while i < len(self.stations):
                for k in range(i, len(self.stations)):
                    if i != k:
                        if [i, k] not in all_pairs:
                            all_pairs.append([i, k])
                i += 1

        return [[self.stations[x], self.stations[y]]
                for [x, y] in all_pairs]


def get_data() -> list:
    """
    Converts CSV file into Train models
    """
    all_trains = []
    with open(TRAIN_DATA_FILE) as f:
        c = csv.reader(f)
        for row in c:
            all_trains.append(Train(row))
    return all_trains


def get_full_trains() -> list:
    """
    Converts CSV file into Train models
    """
    all_trains = []
    with open(TRAIN_DATA_FILE) as f:
        c = csv.reader(f)
        for row in c:
            if len(all_trains) == 0:
                all_trains.append(FullTrain())

            t = Train(row)
            try:
                float(t.distance)
                if all_trains[-1].is_same_train(t):
                    all_trains[-1].add_station(t)
                else:
                    all_trains.append(FullTrain())
                    all_trains[-1].add_station(t)
            except ValueError:
                pass
    return all_trains


def get_station_data() -> dict:
    station_dict = {}
    if os.path.isfile(STATION_DATA_FILE):
        with open(STATION_DATA_FILE) as f:
            for line in f:
                station_dict[line.strip().split(";")[0]] = line.strip().split(
                    ";")
    else:
        raise Exception(
            "You need station file ("
            + STATION_DATA_FILE + ") for this. Use 'download_station_data( "
                                  ")' before using this")

    return station_dict
