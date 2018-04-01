import os
import numpy as np
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
    "Total Energy",                 # 70
    "Energy Over Distance",         # 71
    "Enery Over Time",              # 72
    "Speed Standard Deviation",     # 73
    "Average Speed (m/s)",          # 74
    "Speed Variance",               # 75
    "Braking Strength Standard Deviation",          # 76
    "Braking Strength Average (m/s^2)",             # 77
    "Braking Strength Variance",                    # 78
    "Acceleration Standard Deviation",              # 79
    "Average Acceleration (m/s^2)",                 # 80
    "Acceleration Variance",                        # 81
    "Acceleration From Stop Standard Deviation",    # 82
    "Average Acceleration From Stop",               # 83
    "Acceleration From Stop Max"                    # 84
]

def get_drivers_feature(driver_idx, trip_idx, feature_idx):
    return features[200 * driver_idx + trip_idx][feature_idx]

def plot_features(driver_idxs, feature_idxs, drivers_color):
    """
    :param driver_idxs: list of driver_idxs to plot for
    :param feature_idx: list of feature_idxs to plot, this must be 2
    """
    feature0 = [] 
    feature1 = [] 
    for driver in driver_idxs:
        driver_feature0 = []
        driver_feature1 = []
        for trip in list(range(200)):  # trips per driver
            driver_feature0.append(get_drivers_feature(driver, trip, feature_idxs[0]))
            driver_feature1.append(get_drivers_feature(driver, trip, feature_idxs[1]))
        feature0.extend(driver_feature0)
        feature1.extend(driver_feature1)

    colors = []
    # each color different driver
    for idx, i in enumerate(driver_idxs):
        # each driver has 200 samples
        for i in list(range(200)):
            colors.append(drivers_color[idx])

    plt.scatter(feature0, feature1, c=colors)
    plt.xlabel(feature_labels[feature_idxs[0]], fontsize=26)
    plt.ylabel(feature_labels[feature_idxs[1]], fontsize=26)
    plt.title("{0} vs {1}".format(feature_labels[feature_idxs[0]], feature_labels[feature_idxs[1]]), fontsize=26)
    plt.tick_params(axis="both", labelsize=20)
    plt.show()

if __name__ == "__main__":
    #print(get_drivers_feature(0, i, 83))
    #plot_features([21,34], [74, 77], ['C4', 'C2'])
    plot_features([21,34], [74, 80], ["C4", "C2"])
    #plot_features([21,34, 5], [70, 80], ["green", "purple", "blue"])
