# --- external imports
import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
from math import gcd
import matplotlib.ticker as ticker
from fractions import Fraction
from matplotlib.ticker import MaxNLocator
# --- internal imports
import functions.arguments as fa
from models.hofstadter import Hofstadter


def hamiltonian(p, M, k_val):

    # initialize the Hamiltonian
    Hamiltonian = np.zeros((M, M), dtype=np.complex128)

    nphi = p / q

    def A(nphi_val, m_val):
        value = 2 * np.cos(4 * np.pi * nphi_val * (m_val - 1/3))
        return value

    def C(nphi_val, m_val):
        value = 2 * np.cos(2 * np.pi * nphi_val * (m_val + 5/3)) * np.exp(- 1j * np.pi * nphi * 0.5 * (4 * m_val + 4))
        return value

    upper_diag_array = np.array([A(nphi, m) for m in range(q)])
    Hamiltonian += np.roll(np.diag(upper_diag_array), 0, axis=1)

    upper_diag_array2 = np.array([C(nphi, m) for m in range(q)])
    Hamiltonian += np.roll(np.diag(upper_diag_array2), 2, axis=1)
    Hamiltonian += np.roll(np.diag(np.conj(upper_diag_array2)), 2, axis=0)

    lmbda = np.real(np.linalg.eigvals(Hamiltonian))
    eenergies = np.zeros(2 * len(lmbda))
    for i in range(len(lmbda)):
        eenergies[i] = +np.sqrt(3 + lmbda[i])
        eenergies[len(lmbda) + i] = -np.sqrt(3 + lmbda[i])

    return eenergies


if __name__ == '__main__':

    # input arguments
    q = 199

    # construct butterfly
    nphi_list, E_list = [], []
    values = []

    for p in range(1, q):

        if gcd(p, q) != 1:  # nphi must be a coprime fraction
            continue

        M = q

        nphi = p / q
        nphi_list = [nphi for i in range(2*M)]
        eham = hamiltonian(p, M, np.array([0, 0]))
        values.append((eham, nphi_list))

    # construct figure
    fig = plt.figure()
    ax = plt.subplot(111)
    ax.set_title(f"$n_\phi = p/{q}$")

    # nphi_list = list(np.concatenate(nphi_list).ravel())
    # E_list = list(np.concatenate(E_list).ravel())
    #
    # ax.scatter(nphi_list, E_list, s=1, marker='.')

    for eigenvalues, alphas in values:
        ax.plot(alphas, eigenvalues, '.', color='r', markersize=0.5)

    ax.set_ylabel('$E$')
    ax.set_xlabel('$n_\phi$')
    plt.show()
