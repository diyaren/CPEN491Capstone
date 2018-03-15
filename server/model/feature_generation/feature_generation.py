import os
import numpy as np

from preprocessing import *


ORIGINAL_DATASET_PATH = "../../../../temp_cpen491_model_setup/training_data/axa_original/"


def features_from_trip(trip, plotting=False):
    """
    Extracts features of a trip dataframe.
    OUTPUT:
    np.array including features
    list of angles between points in deg
    """

    # 1. duration
    duration = len(trip)    

    # 2. speed: euclidean distance between adjacent points
    speed = np.sum(np.diff(trip,axis=0)**2,axis=1)**0.5
    energy = np.abs(np.diff(speed**2, axis=0))
    energy_total = sum(energy)

    ### 2.1. smooth GPS data (by convolution) ####    
    smooth_speed =  movingaverage(speed,10) 
    #smooth_speed[np.where(smooth_speed>65)[0]] = smooth_speed[np.where(smooth_speed>65)[0]-1]

    # head changes
    head = np.diff(trip,axis=0)
    head_x,head_y = head[:,0],head[:,1]

    head_quantiles_x = ss.mstats.mquantiles(head_x,np.linspace(0.02,0.99,10))
    head_quantiles_y = ss.mstats.mquantiles(head_y,np.linspace(0.02,0.99,10))

    # compute speed statistics    
    std_speed = smooth_speed.std()
    mean_speed = smooth_speed.mean()
    var_speed = np.var(smooth_speed)
    max_speed = max(smooth_speed)
    # 3. acceleration
    smooth_accel = np.diff(smooth_speed)    

    # 3.1 get all negative acceleration values
    accel_s = np.array(smooth_accel)    
    neg_accel = accel_s[accel_s<0]
    pos_accel = accel_s[accel_s>0]

    # 3.3 average braking strength
    std_braking =  neg_accel.std()
    mean_braking = neg_accel.mean()
    var_braking = np.var(neg_accel)
    std_acceleration = pos_accel.std()
    mean_acceleration = pos_accel.mean() 
    var_acceleration = np.var(pos_accel)

    # summary statistics
    mean_acceleration = pos_accel.mean()

    # 4. total distance traveled    
    total_dist = np.sum(smooth_speed,axis=0)               

    # 5. energy
    energy_per_distance = energy_total / total_dist
    energy_per_time = energy_total / duration

    #### DRIVING STYLE REALTED FEATURES ####
    # 1. acceleration from stop

    # 1.1 get end of stops: where is speed near zero
    end_stops = stops(smooth_speed)        
    n_stops = len(end_stops) # how many stops

    # 1.2 how does the driver accelerate from stop?

    end_stops = end_stops.astype(int)[:-1,1]

    # following interval
    interval = 7 # 7 seconds following end of stop

    # only those which dont exceed indices of trip
    end_stops = end_stops[end_stops+interval<len(smooth_speed)-1]    
    n_stops = len(end_stops) 

    if n_stops>1:
        anfahren = np.zeros(shape=(1,n_stops)) # initialize array

        for i in range(n_stops):
            # slope at acceleration    
            start = end_stops[i]

            anfahren[0,i] =  np.diff([smooth_speed[start],smooth_speed[start+interval]])
       
    else:
        anfahren = np.array([0])

    # compute statistics
    mean_anfahren = anfahren.mean()
    max_anfahren = anfahren.max()
    std_anfahren = anfahren.std()

    # end cell
    last_cell = rounddown(normalize(trip[-2:,:]),30)[-1]

    # speed quantiles
    speed_quantiles = ss.mstats.mquantiles(smooth_speed,np.linspace(0.02,0.99,25)) 

    # acceleration quantiles
    accel_quantiles = ss.mstats.mquantiles(smooth_accel,np.linspace(0.02,0.99,25))

    ################# PLOTS #################
    if plotting:
        figure()        
        x = range(1,len(trip)) # x values for plotting
        #plot(x,total_dist,label='velocity') #speed 
        hold('on')
        #plot(x,accel,color='red',alpha=0.6,label='acceleration') #acceleration 
        grid('on')
        xlabel('time')

        # plot smoothed speed data
        plot(smooth_speed,color='k',label='Spline Interpol')
        # plot smoothed accelerationd data
        plot(smooth_accel,'red',label='Acceleration')
        legend(loc='best')


    #legend()
    ######################################
    return np.concatenate((speed_quantiles,
        accel_quantiles,
        head_quantiles_x,
        head_quantiles_y,
        np.array([energy_total,
            energy_per_distance,
            energy_per_time,
            std_speed,
            mean_speed,
            var_speed,
            std_braking,
            mean_braking,
            var_braking,
            std_acceleration,
            mean_acceleration,
            var_acceleration,
            std_anfahren,
            mean_anfahren,
            max_anfahren])
    ))


def generate_from_dataset():
    """Generates a binary *.npy file containing the features extracted from
    drivers in the original AXA dataset.
    """
    drivers = sorted([int(folderName) for folderName in os.listdir(ORIGINAL_DATASET_PATH)])

    for idx, driver in enumerate(drivers):
        driver_features = []

        # generate feature matrix for all trips for this driver
        for trip in list(range(1,201)):
            driver_trip = np.loadtxt(os.path.join(ORIGINAL_DATASET_PATH, 
                    str(driver),
                    "{}.csv".format(trip)),
                delimiter=',',
                skiprows=1)
            driver_features.append(features_from_trip(driver_trip))

        # append the feature matrix for this driver to the master array
        if idx == 0:
            feature_matrix = driver_features
        else:
            feature_matrix = np.vstack((feature_matrix, driver_features))

        print("Done driver {}".format(driver))
        if idx > 90:
            print("processed {} drivers, exitting".format(idx + 1))
            break


    np.save(os.path.join('myfeatures.npy'), feature_matrix)
    


if __name__ == "__main__":
    # if executing this file, probably trying to generate features.npy
    generate_from_dataset()
