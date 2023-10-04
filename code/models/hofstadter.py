"""The Hofstadter model classes."""

import numpy as np
import functions.models as fm


class Hofstadter:
    r"""The Hofstadter model class.

    The Hamiltonian for the Hofstadter model is given as

    .. math::
        H = - \sum_{\braket{ij}_n} t_n e^{i \theta_{ij}} c_i^\dagger c_j + \mathrm{H.c.},

    where :math:`\braket{ij}_n` denotes nth nearest neighbors on a lattice in the xy-plane, :math:`t_n` are the corresponding hopping amplitudes, :math:`\theta_{ij}` are the Peierls phases, and :math:`c^{(\dagger)}` are the particle (creation)annihilation operators.
    """

    def __init__(self, p, q, a0=1, t=None, lat="square"):
        """Constructor for the Hofstadter class.

        Parameters
        ----------
        p: int
            The numerator of the coprime flux density fraction.
        q: int
            The denominator of the coprime flux density fraction.
        a0: float
            The lattice constant (default=1).
        t: list
            The list of hopping amplitudes in order of ascending NN (default=[1]).
        lat: str
            The name of the lattice (default="square")
        """

        if t is None:
            t = [1]
        self.p = p  #: int : The numerator of the coprime flux density fraction.
        self.q = q  #: int : The denominator of the coprime flux density fraction.
        self.a0 = a0  #: float :The lattice constant (default=1).
        self.t = t  #: float : The units of the hopping amplitudes (default=[1]).
        self.lat = lat  #: str : The name of the lattice (default="square").

    def unit_cell(self):
        """The unit cell of the Hofstadter model.

        Returns
        -------
        num_bands_val: int
            The number of sites.
        avec_val: ndarray
            The lattice vectors.
        bvec_val: ndarray
            The reciprocal lattice vectors.
        sym_points_val: ndarray
            The high symmetry points.
        """

        num_bands_val = self.q
        if self.lat == "square":
            # lattice vectors (MUC)
            a1 = self.a0 * np.array([num_bands_val, 0])
            a2 = self.a0 * np.array([0, 1])
            avec_val = np.vstack((a1, a2))
            # reciprocal lattice vectors (MUC)
            b1 = (2. * np.pi) / self.a0 * np.array([1 / num_bands_val, 0])
            b2 = (2. * np.pi) / self.a0 * np.array([0, 1])
            bvec_val = np.vstack((b1, b2))
            # symmetry points
            GA = np.array([0, 0])
            Y = np.array([0, 0.5])
            S = np.array([0.5, 0.5])
            X = np.array([0.5, 0])
            sym_points_val = [GA, Y, S, X]
        elif self.lat == "triangular":
            # lattice vectors (MUC)
            a1 = self.a0 * np.array([num_bands_val, 0])
            a2 = self.a0 * np.array([1/2, np.sqrt(3)/2])
            avec_val = np.vstack((a1, a2))
            # reciprocal lattice vectors (MUC)
            b1 = (2. * np.pi) / self.a0 * np.array([1 / num_bands_val, -num_bands_val/np.sqrt(3)])
            b2 = (2. * np.pi) / self.a0 * np.array([0, 2/np.sqrt(3)])
            bvec_val = np.vstack((b1, b2))
            # symmetry points
            GA = np.array([0, 0])
            Y = np.array([0, 0.5])
            S = np.array([0.5, 0.5])
            X = np.array([0.5, 0])
            sym_points_val = [GA, Y, S, X]

        return num_bands_val, avec_val, bvec_val, sym_points_val

    def hamiltonian(self, k_val):
        """The Hamiltonian of the Hofstadter model.

        Parameters
        ----------
        k_val: ndarray
            The momentum vector.

        Returns
        -------
        Hamiltonian: ndarray
            The Hofstadter Hamiltonian matrix of dimension (num_bands, num_bands).
        """

        # nearest neighbors
        vec_group = fm.nearest_neighbor_finder("square", self.t)
        Hamiltonian = fm.Hamiltonian(self.t, self.p, self.q, vec_group, k_val)

        return Hamiltonian

    # def hamiltonian(self, k_val):
    #     """The Hamiltonian of the Hofstadter model.
    #
    #     Parameters
    #     ----------
    #     k_val: ndarray
    #         The momentum vector.
    #
    #     Returns
    #     -------
    #     Hamiltonian: ndarray
    #         The Hofstadter Hamiltonian matrix of dimension (num_bands, num_bands).
    #     """
    #
    #     # initialize the Hamiltonian
    #     num_bands_val = self.q
    #     Hamiltonian = np.zeros((num_bands_val, num_bands_val), dtype=np.complex128)
    #
    #     # nearest neighbors
    #     delta = np.zeros((2, 2))
    #     delta[0, :] = self.a0 * np.array([1, 0])
    #     delta[1, :] = self.a0 * np.array([0, 1])
    #
    #     nphi = self.p / self.q
    #
    #     def h(k_val_val, m_val):
    #         return 2 * np.cos(2 * np.pi * nphi * m_val + k_val_val[1] * self.a0)
    #
    #     for n in range(self.q):
    #         Hamiltonian[n][n] = -self.t * h(k_val, n)
    #
    #     for n in range(self.q - 1):
    #         Hamiltonian[n][n + 1] = -self.t * np.exp(+1j * k_val[0] * self.a0)
    #         Hamiltonian[n + 1][n] = -self.t * np.exp(-1j * k_val[0] * self.a0)
    #
    #     Hamiltonian[0][self.q - 1] = -self.t * np.exp(-1j * k_val[0] * self.a0)
    #     Hamiltonian[self.q - 1][0] = -self.t * np.exp(+1j * k_val[0] * self.a0)
    #
    #     return Hamiltonian
