import pyfirmata
import time
from pyfirmata.util import Iterator
import numpy as np
import os.path
import csv

def load_data(file):
    """
    Load and preprocess data from a CSV file.
    """
    fungi_data = []
    with open(file) as f:
        csv_f = csv.reader(f)
        for row in csv_f:
            if row[0]:
                fungi_data.append(float(row[0]))

    fungi_data = np.array(fungi_data)
    print("Data shape:", fungi_data.shape)
    return fungi_data

# Initialize the Arduino board
board = pyfirmata.Arduino('COM6', baudrate=4800)

# Start an iterator thread to avoid buffer overflow
ite = Iterator(board)
ite.start()

# Define the motor pin
motor11 = board.get_pin('d:2:o')  # Digital pin 2, Output mode

count = 1
stop_flag = False

while True:
    print("Start")
    file_path_p = f'fungi_ardu_comm/total_p{count}.txt'
    file_path_w = f'fungi_ardu_comm/total_w{count}.txt'
    print("File paths:", file_path_p, file_path_w)
    time.sleep(0.01)

    # Wait for the data files to exist
    while not os.path.exists(file_path_p):
        time.sleep(1)
        motor11.write(0)

    if os.path.isfile(file_path_p):
        print("Received fungi data")
        total_data_p = load_data(file_path_p)
        total_data_w = load_data(file_path_w)
        print("Total data peaks:", total_data_p)
        print("Total data widths:", total_data_w)

        if total_data_p.any():
            print("Peaks exist")
            for i in range(total_data_w.shape[0]):
                if total_data_p[i] > 0:
                    if total_data_p[i] > 200:
                        print("UV positive direction motor running")
                        for j in range(50):
                            print(f"UV artificial valve motion: {j}")
                            motor11.write(1)
                            time.sleep(0.5)
                            motor11.write(0)
                            time.sleep(0.8)
                            stop_flag = True
                    else:
                        motor11.write(1)
                        print("Positive direction motor running")
                        width = min(total_data_w[i], 30)
                        if total_data_w[i] > 30:
                            print("Width data bigger than 30, capped at 30")
                        time.sleep(width * 0.1)

                elif total_data_p[i] < 0:
                    if total_data_p[i] < -200:
                        print("UV negative direction motor running")
                        for j in range(50):
                            print(f"UV artificial valve motion: {j}")
                            motor11.write(1)
                            time.sleep(0.5)
                            motor11.write(0)
                            time.sleep(0.8)
                            stop_flag = True
                    else:
                        motor11.write(1)
                        print("Negative direction motor running")
                        width = min(total_data_w[i], 30)
                        if total_data_w[i] > 30:
                            print("Width data bigger than 30, capped at 30")
                        time.sleep(width * 0.1)

                else:
                    motor11.write(0)
                    if stop_flag:
                        print("Stop flag is true in the loop")
                        break
                    print("No motor running")
                    time.sleep(total_data_w[i] * 0.1)
        else:
            motor11.write(0)
            print("No peaks exist")
        if stop_flag:
            print("Stop flag is true")
            break

    print("Finish")
    count += 1
