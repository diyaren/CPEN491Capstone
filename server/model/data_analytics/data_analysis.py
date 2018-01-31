import os
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt


ORIGINAL_DATASET_PATH = "../../../temp_cpen491_model_setup/training_data/axa_original/"

def main():
    drivers = sorted([int(folderName) for folderName in os.listdir(ORIGINAL_DATASET_PATH)])
    trip_lengths = []
    for idx, driver in enumerate(drivers):
        for trip in list(range(1, 201)):
            driver_trip = np.loadtxt(os.path.join(ORIGINAL_DATASET_PATH, 
                                                  str(driver),
                                                  "{}.csv".format(trip)),
                                     delimiter=',',
                                     skiprows=1)
            trip_lengths.append(driver_trip.shape[0])
        #if idx > 5:
        #    break
        print("done driver {}".format(driver))

    n, bins, patches = plt.hist(trip_lengths, 50, normed=1, facecolor='green', alpha=0.75)

    plt.xlabel('Trip Lengths')
    plt.ylabel('Probability')
    plt.title('Histogram of Trip Lengths (seconds)')
    plt.axis([0, 2000, 0, 0.01])
    plt.grid(True)

    print("Trip lengths ({3} trips): mean:{0}, min: {1}, max: {2}".format(
        np.mean(trip_lengths),
        np.min(trip_lengths),
        np.max(trip_lengths),
        len(trip_lengths)
        ))

    plt.show()

if __name__ == "__main__":
    main()
