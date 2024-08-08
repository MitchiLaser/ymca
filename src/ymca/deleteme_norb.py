#!/usr/bin/env python3
import multiprocessing as mp
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import osc


# Function to find peaks in the data
def filter(data):
    peaks, properties = find_peaks(data, height=50)
    print(f"Found {len(peaks)} peaks: {properties['peak_heights']}")
    return properties['peak_heights']


# Oscilloscope data generator
def oscilloscope_data_generator():
    Osc = osc.Osc("10.42.0.107")  # IP Address of RP
    while True:
        yield Osc.get_data()[1::2]  # Get data from channel 2]


# Data acquisition process
def data_acquisition(data_queue):
    data_gen = oscilloscope_data_generator()
    for data in data_gen:
        # print("Data acquired")  # Debug print
        data_queue.put(data)


# Data processing process
def data_processing(data_queue, result_queue):
    while True:
        data = data_queue.get()
        peaks = filter(data)
        # print(f"Processed data, found {len(peaks)} peaks")  # Debug print
        result_queue.put(peaks)


# Histogram update process
def histogram_update(result_queue):
    histogram_data = []
    plt.ion()
    fig, ax = plt.subplots()
    while True:
        while not result_queue.empty():
            peaks = result_queue.get()
            # print(f"Updating histogram with {len(peaks)} peaks")  # Debug print
            histogram_data.extend(peaks)
            ax.clear()
            ax.hist(histogram_data, bins=1024)
            plt.xlabel("Channel (ADC count)")
            plt.ylabel("Count (number of entries)")
            # plt.savefig("ymca_run.png")
            plt.draw()
            plt.pause(0.1)


if __name__ == '__main__':
    # Queues for inter-process communication
    data_queue = mp.Queue()
    result_queue = mp.Queue()

    # Start data acquisition process
    data_acquisition_process = mp.Process(target=data_acquisition, args=(data_queue,))
    data_acquisition_process.start()

    # Start data processing processes
    num_processing_processes = 4
    data_processing_processes = []
    for _ in range(num_processing_processes):
        p = mp.Process(target=data_processing, args=(data_queue, result_queue))
        p.start()
        data_processing_processes.append(p)

    # Start histogram update process
    histogram_update_process = mp.Process(target=histogram_update, args=(result_queue,))
    histogram_update_process.start()

    # Ensure all processes are cleaned up on exit
    try:
        data_acquisition_process.join()
        for p in data_processing_processes:
            p.join()
        histogram_update_process.join()
    except KeyboardInterrupt:
        # print("Terminating processes...")
        data_acquisition_process.terminate()
        for p in data_processing_processes:
            p.terminate()
        histogram_update_process.terminate()
        data_acquisition_process.join()
        for p in data_processing_processes:
            p.join()
        histogram_update_process.join()
