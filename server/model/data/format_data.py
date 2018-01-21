"""
This script creates test data for a selected driver, and appends other random
drivers to create train, test, and validation datasets.

Creates a new dataset with 1 true driver, 5 false drivers (default parameters).
Columns:
driver_label, trip_start, x, y

Usage:
    python format_data.py
"""
import os
import click
import timeit
import time
import pprint
import logging
import multiprocessing

import numpy as np
import pandas as pd
import random


logging.basicConfig(format='%(asctime)5s [%(levelname)s]: %(message)s', filename='log', level=logging.DEBUG)
logger = logging.getLogger(__name__)

TOTAL_NUMBER_DRIVERS = 2736  # not all exist, the value goes up to 3612
DATA_HEADER = ["driver_label", "trip_start", "x", "y"]


def assemble_work_order(work_order):
    # build the dataset
    master_set = np.array([]).reshape(0, len(DATA_HEADER))
    for driver in work_order["job"]:
        # pull in the driver's trip
        trip = pd.read_csv(os.path.join(work_order["input"],
                                        str(driver),
                                        "{}.csv".format(work_order["trip_idx"])),
                           sep=',')
        trip = trip.as_matrix()

        # add a column to denote the start of a trip [1, 0, 0, ..., 0]
        trip_start_column = np.zeros((trip.shape[0], 1), dtype=np.int64)
        trip_start_column[0] = 1
        trip = np.concatenate((trip_start_column, trip), axis=1)

        # add a column to denote when a driver is the truth_driver (1) or another driver (0)
        if str(driver) == str(work_order["truth"]):
            label_column = 1 + np.zeros((trip.shape[0], 1), dtype=np.int64)
        else:
            label_column = np.zeros((trip.shape[0], 1), dtype=np.int64)
        trip = np.concatenate((label_column, trip), axis=1)

        ###############################################################
        # Here is where you would perform additional feature engineering
        # to append to the dataset
        ###############################################################

        # add the trip with new columns to master set
        master_set = np.concatenate((master_set, trip), axis=0)

    logger.info("Created a dataset for driver {1} with other drivers {2}, using trip idx {3}".format(
        id, work_order["truth"], work_order["job"], work_order["trip_idx"]))

    # write to csv
    master_set = pd.DataFrame(master_set)
    work_order["output"].append("{}.csv".format(work_order["trip_idx"]))
    master_set.to_csv(os.path.join(*work_order["output"]), header=DATA_HEADER, index=False)


def worker_function(id, work_queue):
    logger.info("Hello i am worker #{}".format(id))
    work_order = work_queue.get()
    while work_order != 0:
        work_order = work_queue.get()
        logger.info("Worker {0} working on this:".format(id))
        assemble_work_order(work_order)

    logger.info("worker #{} signing off".format(id))


@click.command()
@click.option('--truth_driver', default=1, type=int, help="The driver_id to be set as the ground truth.")
@click.option('--other_drivers', default=5, nargs=1, type=int, help="Number of other drivers to be included with truth driver")
@click.option('--train_split', default=0.8, nargs=1, type=float, help="Percentage (0..1) of data to be set aside for training.  Train + test + validation = 1.0.")
@click.option('--test_split', default=0.1, nargs=1, type=float, help="Percentage (0..1) of data to be set aside for testing.  Train + test + validation = 1.0.")
@click.option('--validation_split', default=0.1, nargs=1, type=float, help="Percentage (0..1) of data to be set aside for validation.  Train + test + validation = 1.0.")
@click.option('--input_dir', default="axa_original", nargs=1, help="Directory to grab data from.")
@click.option('--output_dir', default="formatted_data", nargs=1 , help="Directory to place formatted data.")
@click.option('--processes', default=1, nargs=1, help="Number of parallel tasks to run.")
def format_data(truth_driver, other_drivers, train_split, test_split,
                validation_split, input_dir, output_dir, processes):
    assert abs(1.00 - train_split - test_split - validation_split) <= 0.001
    assert other_drivers < 13
    logging.basicConfig(format='%(asctime)5s [%(levelname)s]: %(message)s', filename='DRIVER_{}_CREATION_LOG'.format(str(truth_driver)), level=logging.DEBUG)

    logger.info("Starting to format data with the ground truth driver as {0}, and {1} other drivers".format(
        truth_driver, other_drivers))
    logger.info("Reading data from: {}".format(input_dir))
    logger.info("Placing formatted data in: {}".format(output_dir))
    start_time = timeit.default_timer()

    # get all the driver id's by parsing the original data directory
    driver_ids = os.listdir(input_dir)
    if '.gitignore' in driver_ids:
        driver_ids.remove('.gitignore')
    random.shuffle(driver_ids)

    # generate work sets
    working_list = []
    target_length = 1 + other_drivers
    for i in list(range(len(driver_ids))):
        list_to_append = driver_ids[i * target_length: i * target_length + target_length]
        if len(list_to_append) == target_length:
            if truth_driver not in list_to_append:
                list_to_append[np.random.choice(np.arange(other_drivers))] = truth_driver
                working_list.append(list_to_append)
            else:
                break

    # randomize the 200 driving trips and partition to fit the desired train, test, val ratios
    trips = list(range(200)) + np.ones((200), int)
    random.shuffle(trips)

    train_idx = train_split * len(trips) 
    test_idx = train_idx + test_split * len(trips) 
    val_idx = test_idx + validation_split * len(trips) 

    # ensure directories exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, 0o777)
    if not os.path.exists(os.path.join(output_dir, str(truth_driver))):
        os.makedirs(os.path.join(output_dir, str(truth_driver)), 0o777)
    if not os.path.exists(os.path.join(output_dir, str(truth_driver), "train")):
        os.makedirs(os.path.join(output_dir, str(truth_driver), "train"), 0o777)
    if not os.path.exists(os.path.join(output_dir, str(truth_driver), "test")):
        os.makedirs(os.path.join(output_dir, str(truth_driver), "test"), 0o777)
    if not os.path.exists(os.path.join(output_dir, str(truth_driver), "val")):
        os.makedirs(os.path.join(output_dir, str(truth_driver), "val"), 0o777)

    workload = []
    # assuming will have way more working lists than trips (not too many extra drivers 5~12)
    for idx, drive_trip in enumerate(trips):
        work_order = {
            "truth": str(truth_driver),
            "job": working_list[idx],
            "trip_idx": drive_trip,
            "input": os.path.join(input_dir)
        }
        if idx < train_idx:
            # put it in the training folder
            work_order["output"] = [os.curdir, output_dir, str(truth_driver), "train"]
        elif idx < test_idx:
            # put it in the test folder
            work_order["output"] = [os.curdir, output_dir, str(truth_driver), "test"]
        else:
            # put it in the validation folder
            work_order["output"] = [os.curdir, output_dir, str(truth_driver), "val"]

        workload.append(work_order)

    '''
    # spawn processes to handle the workload
    workers = []
    work_queue = multiprocessing.Queue()
    for idx, process in enumerate(list(range(processes))):
        worker = multiprocessing.Process(target=worker_function, args=(idx, work_queue,))
        worker.start()
        workers.append(worker)
    
    # fill the queue with work
    for work_order in workload:
        work_queue.put(work_order)

    # send out terminates and wait for all to finish
    for worker in workers:
        work_queue.put(0)

    # wait for finish
    for worker in workers:
        worker.join()
    ''' 

    # fill the queue with work
    for work_order in workload:
        assemble_work_order(work_order)


    logger.info("Finished.  Time elapsed: {:.2f}s".format(timeit.default_timer() - start_time))

if __name__ == "__main__":
    format_data()
