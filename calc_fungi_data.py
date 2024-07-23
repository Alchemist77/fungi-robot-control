import pandas as pd
import numpy as np
from scipy.signal import find_peaks, savgol_filter, peak_widths
import matplotlib.pyplot as plt
from PIL import Image
import os
import time
import csv


class SignalPreProcessing:
    def __init__(self):
        self.crop_cnt = 0
        self.crop_interval = 300  # 5 minute intervals
        self.peaks_data = []
        self.neg_peaks_data = []
        self.p_properties = []
        self.n_properties = []
        self.p_width = []
        self.n_width = []
        self.pos_prominence = 10
        self.neg_prominence = 10
        self.rel_height = 0.3
        self.x_axis_data = []
        self.negative_x_axis_data = []
        self.width_pixel = 640
        self.height_pixel = 480
        self.max_data = 0
        self.min_data = 0
        self.fre_pos_sig = []
        self.fre_neg_sig = []
        self.box_tune = 0.2
        self.baseline = 120
        self.length = 300

    def load_data(self, file, col):
        """
        Load and preprocess data from a CSV file.
        """
        data_f = []
        with open(file) as f:
            csv_f = csv.reader(f)
            # print("File:", file)
            for row in csv_f:
                if row[col]:
                    data_f.append(float(row[col]))

        data_f = np.array(data_f[1:1000])
        target_sig = savgol_filter(data_f, 11, 3)  # Smoothing filter
        plt.plot(target_sig)
        plt.xlabel('Sampling Number')
        plt.ylabel('Action potential uV')
        target_sig = target_sig[~np.isnan(target_sig)]
        self.max_data = np.max(target_sig)
        self.min_data = np.min(target_sig)
        plt.show()
        return target_sig

    def calc_peaks(self, crop_figure):
        """
        Calculate the positive and negative peaks in the signal.
        """
        partial_peaks, partial_properties = find_peaks(crop_figure, prominence=self.pos_prominence)
        partial_negative_peaks, partial_negative_properties = find_peaks(-crop_figure, prominence=self.neg_prominence)

        total_peaks = np.append(partial_peaks, partial_negative_peaks)
        total_prominences = np.append(partial_properties["prominences"], -partial_negative_properties["prominences"])
        sort_peak_index = np.argsort(total_peaks)

        peak_data = [0] + [total_prominences[idx] for idx in sort_peak_index] + [0]

        self.fre_pos_sig.append(partial_peaks.shape)
        self.fre_neg_sig.append(partial_negative_peaks.shape)

        self.peaks_data.extend(partial_peaks)
        self.neg_peaks_data.extend(partial_negative_peaks)
        self.p_properties = partial_properties
        self.n_properties = partial_negative_properties

        return self.peaks_data, self.neg_peaks_data, self.p_properties, self.n_properties, peak_data

    def calc_width(self, crop_figure, pos_p, neg_p):
        """
        Calculate the width of peaks in the signal.
        """
        width_half = peak_widths(crop_figure, pos_p, rel_height=self.rel_height)
        negative_width_half = peak_widths(-crop_figure, neg_p, rel_height=self.rel_height)

        total_width_a = np.append(width_half[0], negative_width_half[0])
        total_width_c = np.append(width_half[2], negative_width_half[2])
        total_width_d = np.append(width_half[3], negative_width_half[3])
        sort_index = np.argsort(total_width_c)
        total_with_data = [total_width_a[sort_index], total_width_c[sort_index], total_width_d[sort_index]]

        width_data = [total_with_data[1][0]] + [total_with_data[0][0]]
        for x in range(len(total_with_data[0]) - 1):
            diff_width = total_with_data[1][x + 1] - total_with_data[2][x]
            width_data.append(diff_width)
            width_data.append(total_with_data[0][x + 1])
        width_data.append(self.length - total_with_data[2][-1])

        int_width_2 = width_half[2].astype(int)
        int_width_3 = width_half[3].astype(int)
        int_negative_width_2 = negative_width_half[2].astype(int)
        int_negative_width_3 = negative_width_half[3].astype(int)

        for i in range(len(int_width_2)):
            x_data = np.linspace(int_width_2[i], int_width_3[i], int_width_3[i] - int_width_2[i])
            self.x_axis_data.append(x_data.astype(int))

        for i in range(len(int_negative_width_2)):
            x_data = np.linspace(int_negative_width_2[i], int_negative_width_3[i], int_negative_width_3[i] - int_negative_width_2[i])
            self.negative_x_axis_data.append(x_data.astype(int))

        self.p_width = width_half
        self.n_width = negative_width_half

        return self.p_width, self.n_width, self.x_axis_data, self.negative_x_axis_data, width_data

    def save_signal_img(self, crop_figure, count):
        """
        Save a plot of the signal with peaks to an image file.
        """
        fig, ax = plt.subplots()
        plt.plot(crop_figure, linewidth=0.5)

        contour_heights = crop_figure[self.peaks_data] - self.pos_prominence
        plt.plot(self.peaks_data, crop_figure[self.peaks_data], "x")
        plt.vlines(x=self.peaks_data, ymin=contour_heights, ymax=crop_figure[self.peaks_data])

        neg_contour_heights = crop_figure[self.neg_peaks_data] + self.neg_prominence
        plt.plot(self.neg_peaks_data, crop_figure[self.neg_peaks_data], "o")
        plt.vlines(x=self.neg_peaks_data, ymin=neg_contour_heights, ymax=crop_figure[self.neg_peaks_data])

        plt.xlabel('Sampling Time')
        plt.ylabel('Amplitude (mV)')
        plt.savefig(f'signal_imgs/{count}.png', transparent=True)

        # Convert image to remove alpha channel
        png = Image.open(f'signal_imgs/{count}.png')
        background = Image.new("RGB", png.size, (255, 255, 255))
        background.paste(png, mask=png.split()[3])  # 3 is the alpha channel
        background.save(f'signal_imgs/{count}.png', quality=100)

        return fig, ax, crop_figure

    def save_peak_img(self, crop_figure, ax, count):
        """
        Save a plot highlighting the peaks in the signal to an image file.
        """
        for x_data in self.x_axis_data:
            ax.fill(x_data, crop_figure[x_data], "green")
        for x_data in self.negative_x_axis_data:
            ax.fill(x_data, crop_figure[x_data], "r")

        plt.savefig(f'signal_peak_imgs/{count}.png')

    def calc_peak_distant(self, crop_figure):
        """
        Calculate the distance between peaks in the signal.
        """
        total_spike = len(self.peaks_data) + len(self.neg_peaks_data)
        total_v1 = np.concatenate((crop_figure[self.peaks_data], crop_figure[self.neg_peaks_data]), axis=None)
        total_t = (self.peaks_data + self.neg_peaks_data) * 0.1

        return total_spike, total_v1, total_t

def main():
    sig_pp = SignalPreProcessing()
    count = 1
    col = 1  # CSV file column data


    while count <= 1:
        file_path = 'B1_D1.csv'
        while not os.path.exists(file_path):
            time.sleep(1)

        signal_data = sig_pp.load_data(file_path, col)
        crop_figure = signal_data

        pos_p, neg_p, pos_prop, neg_prop, total_peaks = sig_pp.calc_peaks(crop_figure)
        pos_w, neg_w, pos_x_w, neg_x_w, total_widths = sig_pp.calc_width(crop_figure, pos_p, neg_p)

        fig, ax, crop_figure_new = sig_pp.save_signal_img(crop_figure, count)
        sig_pp.save_peak_img(crop_figure_new, ax, count)

        np.savetxt(f"fungi_ardu_comm/total_p{count}.txt", total_peaks, delimiter=',')
        np.savetxt(f"fungi_ardu_comm/total_w{count}.txt", total_widths, delimiter=',')

        count += 1

if __name__ == "__main__":
    main()
