import numpy as np
import os
import matplotlib.pyplot as plt
import functions.utility as fu
import functions.plotting as fp


if __name__ == '__main__':

    # load the file
    filename = "butterfly_honeycomb_q_93_t_1_alpha_1_theta_1_3_col_point_avron.npy"
    dir = "../data/" if os.path.isdir('../data') else ""
    file_data = np.load(dir+filename, allow_pickle=True)

    # read/customize the file_data
    model = file_data[0]
    args = file_data[1]
    data = file_data[2]

    # construct the figure(s)
    fp.butterfly(model, args, data)
    plt.show()