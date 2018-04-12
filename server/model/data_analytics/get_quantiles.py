import os
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


features = np.load("../research/myfeatures.npy")

feature_labels = [
    "Speed Quantiles 1",    # 0
    "Speed Quantiles 2",
    "Speed Quantiles 3",
    "Speed Quantiles 4",
    "Speed Quantiles 5",
    "Speed Quantiles 6",
    "Speed Quantiles 7",
    "Speed Quantiles 8",
    "Speed Quantiles 9",
    "Speed Quantiles 10",
    "Speed Quantiles 11",
    "Speed Quantiles 12",
    "Speed Quantiles 13",
    "Speed Quantiles 14",
    "Speed Quantiles 15",
    "Speed Quantiles 16",
    "Speed Quantiles 17",
    "Speed Quantiles 18",
    "Speed Quantiles 19",
    "Speed Quantiles 20",
    "Speed Quantiles 21",
    "Speed Quantiles 22",
    "Speed Quantiles 23",
    "Speed Quantiles 24",
    "Speed Quantiles 25",
    "Acceleration Quantiles 1", # 25
    "Acceleration Quantiles 2",
    "Acceleration Quantiles 3",
    "Acceleration Quantiles 4",
    "Acceleration Quantiles 5",
    "Acceleration Quantiles 6",
    "Acceleration Quantiles 7",
    "Acceleration Quantiles 8",
    "Acceleration Quantiles 9",
    "Acceleration Quantiles 10",
    "Acceleration Quantiles 11",
    "Acceleration Quantiles 12",
    "Acceleration Quantiles 13",
    "Acceleration Quantiles 14",
    "Acceleration Quantiles 15",
    "Acceleration Quantiles 16",
    "Acceleration Quantiles 17",
    "Acceleration Quantiles 18",
    "Acceleration Quantiles 19",
    "Acceleration Quantiles 20",
    "Acceleration Quantiles 21",
    "Acceleration Quantiles 22",
    "Acceleration Quantiles 23",
    "Acceleration Quantiles 24",
    "Acceleration Quantiles 25",
    "Head Quantiles X 1",   # 50
    "Head Quantiles X 2",
    "Head Quantiles X 3",
    "Head Quantiles X 4",
    "Head Quantiles X 5",
    "Head Quantiles X 6",
    "Head Quantiles X 7",
    "Head Quantiles X 8",
    "Head Quantiles X 9",
    "Head Quantiles X 10",  # 60
    "Head Quantiles Y 1",
    "Head Quantiles Y 2",
    "Head Quantiles Y 3",
    "Head Quantiles Y 4",
    "Head Quantiles Y 5",
    "Head Quantiles Y 6",
    "Head Quantiles Y 7",
    "Head Quantiles Y 8",
    "Head Quantiles Y 9",
    "Head Quantiles Y 10",
]


def get_drivers_feature(driver_idx, trip_idx, feature_idx):
    return features[200 * driver_idx + trip_idx][feature_idx]

def plot_features(axis_title, driver_idxs, feature_idxs, driver_colors):
    """
    """
    all_y = []
    all_x = []
    for driver_idx in driver_idxs:
        driver_y = []
        driver_x = []
        for i in list(range(200)):
            y = []
            for feature in feature_idxs:
                trip = i
                y.append(get_drivers_feature(driver_idx, trip, feature))
            driver_y.append(y)
            driver_x.append(np.linspace(0.02, 0.99, len(feature_idxs)))
        all_y.append(driver_y)
        all_x.append(driver_x)

    plt.scatter(all_x, all_y, c=driver_colors)
    plt.xlabel("Percentiles", fontsize=26)
    plt.ylabel(axis_title, fontsize=26)
    plt.title("Drivers {}".format(str(driver_idxs)), fontsize=26)
    plt.tick_params(axis="both", labelsize=20)
    plt.show()

if __name__ == "__main__":
    #plot_features("Speed Quantiles", 32, list(range(25)), "C1")
    #plot_features("Speed Quantiles", 33, list(range(25)), "C2")
    #plot_features("Heading Y Quantiles", [12, 47], list(range(50, 60)), ["C3", "C4"])

    plot_features("Speed Quantiles", [34], list(range(25)), ["C1"])
    plot_features("Speed Quantiles", [12], list(range(25)), ["C2"])
    plot_features("Speed Quantiles", [22], list(range(25)), ["C3"])
    plot_features("Speed Quantiles", [82], list(range(25)), ["C4"])
    plot_features("Speed Quantiles", [11], list(range(25)), ["C5"])
    #plot_features("Speed Quantiles", [38, 39], list(range(25)), ["C1", "C2"])
    #plot_features("Speed Quantiles", [40, 31], list(range(25)), ["C2", "C6"])
    #plot_features("Acceleration Quantiles", 33, list(range(25, 49)), "C4")
    #plot_features("Heading Quantiles X", 32, list(range(50, 60)), "C5")
    #plot_features("Heading Quantiles X", 33, list(range(50, 60)), "C6")
