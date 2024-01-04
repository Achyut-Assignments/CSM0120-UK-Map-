from UKMap import UKMap

lat_lon_file = "latlon.csv"
users_file = "users.csv"


class LatLon:
    """
    LatLon class

    Attributes:
        town_name (str): name of the town
        latitude (float): latitude of the town
        longitude (float): longitude of the town
    """
    def __init__(self, town_name, latitude, longitude):
        self.town_name = town_name
        self.latitude = latitude
        self.longitude = longitude

    def __str__(self):
        return f"{self.town_name} : [{self.latitude}, {self.longitude}]"


def plot_specific_towns():
    # Read in the towns data (from latlon.csv)
    towns = []
    with open(lat_lon_file, "r") as f:
        for line in f:
            town_name, latitude, longitude = line.strip().split(",")
            towns.append(LatLon(town_name, float(latitude), float(longitude)))

    # Initialise the UKMap object
    uk_map = UKMap()
    for town in towns:
        """
        Plotting the towns to be easily found on the map.
        Marker used: o
        Marker size: 6
        Color: green
        
        
        Plotting the towns that fulfil any of the following criteria:
        • The town name starts with A, B, C, L or M.
        • The town name ends with “bury” or “ampton”.
        
        Marker used: .
        Marker size: 1
        Color: red
        """
        if town.town_name in ["Aberystwyth", "Birmingham", "Cardiff", "London"]:
            uk_map.plot(town.longitude, town.latitude, marker="o", markersize=6, color="green")
        elif town.town_name[0] in ["A", "B", "C", "L", "M"] or town.town_name[-4:] in ["bury", "ampton"]:
            uk_map.plot(town.longitude, town.latitude, markersize=1, color="red")
    uk_map.show()


if __name__ == "__main__":
    plot_specific_towns()
