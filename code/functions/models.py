import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d


def nearest_neighbor_finder(avec, acartvec, abasisvec, t_list, m_init, n_init):

    # --- Create list of NN to consider from t_list
    numb_list = []
    for i, t in enumerate(t_list):
        if t != 0:
            numb_list.append(i+1)

    # --- Create grid of basis vectors from [-t_max, t_max]
    vectors = []
    vectors_unit = []
    for i in range(-numb_list[-1], numb_list[-1]+1):
        for j in range(-numb_list[-1], numb_list[-1]+1):
            r_unit = np.array([i, j])
            vectors_unit.append(r_unit)
            r = np.matmul(r_unit, avec)
            for k in abasisvec:
                vectors.append(r+k)

    # --- Shift the grid of vectors relative to an initial point (m_init, n_init)
    vectors = [np.subtract(i, np.array(m_init * acartvec[0] + n_init * acartvec[1])) for i in vectors]

    # --- Define data array with info on each vector
    data = np.zeros((len(vectors), 10), dtype=object)
    for i, r in enumerate(vectors):
        data[i, 0] = round(np.linalg.norm(r), 10)  # round so that we can use it for comparison
        data[i, 1] = np.angle(r[0]+1j*r[1])
        data[i, 2] = r[0]
        data[i, 3] = r[1]
        data[i, 4] = round(r[0] / acartvec[0][0])
        data[i, 5] = round(r[1] / acartvec[1][1])

    # --- Extract the NN groups (filter data based on radius)
    data = data[data[:, 0].argsort()]  # sort by increasing r
    # delete the first r=0 row
    mask = (data[:, 0] != 0)
    data = data[mask, :]
    radii = np.sort(list(set(data[:, 0])))
    # label the NN group
    for i, row in enumerate(data):
        for j, r in enumerate(radii):
            if row[0] == r:
                data[i, 6] = j+1
                data[i, 7] = m_init
                data[i, 8] = n_init
                data[i, 9] = m_init + data[i, 4]
    select_radii = [radii[i - 1] for i in numb_list]
    # delete rows with other radii
    rows_to_delete = []
    for i, row in enumerate(data):
        if row[0] not in select_radii:
            rows_to_delete.append(i)
    data = np.delete(data, rows_to_delete, axis=0)
    # print("data = ", data)

    return data


def nearest_neighbor_sorter(data_array):

    # --- Delete backtrack vectors
    delete_list = []
    for i, val in enumerate(data_array):
        if val[7] + val[4] == 0 and val[8] + val[5] == 0:  # backtrack
            delete_list.append(i)
    data_array = np.delete(data_array, delete_list, axis=0)
    # print("filter data array = ", data_array)

    # --- Count the independent paths
    numb_paths = 0
    # count double paths
    double = True
    for i, val in enumerate(data_array):
        if val[7] == 0 and val[8] == 0:  # origin
            for j, val2 in enumerate(data_array):
                if val[7] + val[4] == val2[7] and val[8] + val[5] == val2[8]:
                    numb_paths = numb_paths + 1
    # --- Count single paths
    if numb_paths == 0:
        double = False
        for i, val in enumerate(data_array):
            if val[7] == 0 and val[8] == 0:  # origin
                numb_paths = numb_paths + 1
    # print("numb_paths = ", numb_paths)

    # --- Group the independent paths
    paths = np.zeros(numb_paths, dtype=object)
    for i in range(numb_paths):
        paths[i] = []
    counter = 0
    if double:
        for i, val in enumerate(data_array):
            if val[7] == 0 and val[8] == 0:  # origin
                for j, val2 in enumerate(data_array):
                    if val[7] + val[4] == val2[7] and val[8] + val[5] == val2[8]:
                        if np.max([np.abs(val[9]), np.abs(val2[9])]) == np.abs(val2[9]):
                            mtot = val2[9]
                        else:
                            mtot = val[9]
                        paths[counter] = [val, val2, mtot]
                        counter = counter + 1
    else:
        for i, val in enumerate(data_array):
            if val[7] == 0 and val[8] == 0:  # origin
                paths[counter] = [val, val[9]]
                counter = counter + 1
    # print("paths = ", paths)

    # --- Count the number of total m
    m_tot = []
    for i, val in enumerate(paths):
        m_tot.append(val[-1])
    m_tot = np.sort(list(set(m_tot)))
    # print("m_tot = ", m_tot)
    numb_m = len(m_tot)
    # print("numb_m = ", numb_m)

    # --- Group the independent paths by total m
    grouped_paths = np.zeros(numb_m, dtype=object)
    for i in range(numb_m):
        grouped_paths[i] = []

    for i, mval in enumerate(m_tot):
        for j, val in enumerate(paths):
            if val[-1] == mval:
                grouped_paths[i].append(val[:-1])
        grouped_paths[i].append(mval)
    # print("grouped_paths = ", grouped_paths)

    return grouped_paths


def peierls_factor(basis, nphi, vec, m):

    if basis == 1:
        area = 1
    elif basis == 2:
        area = 3
    else:
        raise ValueError("area factor in Peierls phase not implemented")

    phase = 2 * np.pi * nphi * vec[1] * (m + vec[0]/2) / area
    factor = np.exp(1j * phase)

    return factor


def diag_func(basis, t_val, nphi, vec_list, k, m):

    term = 0
    for vec_inf in vec_list:
        for inner_vec_inf in vec_inf:
            NN_group = int(inner_vec_inf[6])
            xy_vector = np.array([inner_vec_inf[2], inner_vec_inf[3]])
            mn_vector = np.array([inner_vec_inf[4], inner_vec_inf[5]])
            term += - t_val[NN_group - 1] * peierls_factor(basis, nphi, mn_vector, m) * np.exp(1j * np.vdot(xy_vector, k))

    return term


def Hamiltonian(basis, t_val, p_val, q_val, acartvec, vec_group_list, k_val):

    Hamiltonian = np.zeros((q_val, q_val), dtype=np.complex128)

    m_values = []
    for term in vec_group_list:
        m_values.append(term[-1])
    # print("m_values = ", m_values)

    if basis == 1:  # single-particle basis

        pos_m_vals = [i for i in m_values if i >= 0]
        # print("pos_m_vals = ", pos_m_vals)

        for idx, i in enumerate(pos_m_vals):
            if i == 0:
                Hamiltonian += np.diag(np.array([diag_func(basis, t_val, p_val / q_val, vec_group_list[len(vec_group_list)//2][:-1], k_val, m) for m in range(q_val)]))
            else:
                # upper_diag_array
                upper_diag_array = np.array([diag_func(basis, t_val, p_val / q_val, vec_group_list[len(vec_group_list)//2+idx][:-1], k_val, (m+i) % q_val) for m in range(q_val)])
                Hamiltonian += np.roll(np.diag(upper_diag_array), i, axis=1)
                # lower_diag_array
                Hamiltonian += np.roll(np.diag(np.conj(upper_diag_array)), i, axis=0)

    else:  # >1 particle basis

        # extract comb m list
        m_values_comb = []
        for i, val in enumerate(vec_group_list):
            m_values_comb.append(val[-1])
        pos_m_vals_comb = [i for i in m_values_comb if i >= 0]
        # print("pos_m_vals_comb = ", pos_m_vals_comb)

        for i in pos_m_vals_comb:

            # upper_diag_array
            def upper_diag_func(basis, nphi, m_val, k_val_val, i_val):
                term = 0
                for idx, val in enumerate(vec_group_list):
                    if val[-1] == i_val:
                        for k, val2 in enumerate(val[:-1]):
                            term += (peierls_factor(basis, nphi, np.array([val2[0][4], val2[0][5]]), (m_val + val2[0][7]) % (q_val+1))
                                     * np.exp(1j * np.vdot(np.array([val2[0][2], val2[0][3]]), k_val_val))
                                     * peierls_factor(basis, nphi, np.array([val2[1][4], val2[1][5]]), (m_val + val2[1][7]) % (q_val+1))
                                     * np.exp(1j * np.vdot(np.array([val2[1][2], val2[1][3]]), k_val_val)))
                return term

            # upper_diag_array
            upper_diag_array = np.array([upper_diag_func(basis, p_val/q_val, (m+i) % q_val, k_val, i) for m in range(q_val)])
            Hamiltonian += np.roll(np.diag(upper_diag_array), i, axis=1)
            # lower_diag_array
            Hamiltonian += np.roll(np.diag(np.conj(upper_diag_array)), i, axis=0)

    return Hamiltonian


if __name__ == '__main__':

    t = [1, 0, -0.25]

    vec_group = nearest_neighbor_finder("square", t)

    print(vec_group)

    ###

    num_bands = 5
    num_samples = 101

    b1 = (2. * np.pi) * np.array([1 / num_bands, 0])
    b2 = (2. * np.pi) * np.array([0, 1])
    bvec = np.vstack((b1, b2))

    eigenvalues = np.zeros((num_bands, num_samples, num_samples))  # real
    eigenvectors = np.zeros((num_bands, num_bands, num_samples, num_samples), dtype=np.complex128)  # complex
    for band in range(num_bands):
        for idx_x in range(num_samples):
            frac_kx = idx_x / (num_samples - 1)
            for idx_y in range(num_samples):
                frac_ky = idx_y / (num_samples - 1)
                k = np.matmul(np.array([frac_kx, frac_ky]), bvec)
                # print("k = ", k)
                eigvals, eigvecs = np.linalg.eigh(Hamiltonian(t, 1, num_bands, vec_group, k))
                idx = np.argsort(eigvals)
                eigenvalues[band, idx_x, idx_y] = eigvals[idx[band]]
                eigenvectors[:, band, idx_x, idx_y] = eigvecs[:, idx[band]]

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    idx_x = np.linspace(0, num_samples - 1, num_samples - 1, dtype=int)
    idx_y = np.linspace(0, num_samples - 1, num_samples - 1, dtype=int)
    kx, ky = np.meshgrid(idx_x, idx_y)
    for i in range(num_bands):
        ax.plot_surface(kx, ky, eigenvalues[i, kx, ky], alpha=0.5)
    ax.set_xlabel('$k_1/|\mathbf{b}_1|$')
    ax.set_ylabel('$k_2/|\mathbf{b}_2|$')
    ax.set_zlabel('$E$')

    def normalize(value, tick_number):
        if value == 0:
            return "$0$"
        elif value == num_samples - 1:
            return "$1$"
        else:
            return f"${value / (num_samples - 1):.1g}$"

    ax.xaxis.set_major_formatter(plt.FuncFormatter(normalize))
    ax.yaxis.set_major_formatter(plt.FuncFormatter(normalize))

    plt.show()
