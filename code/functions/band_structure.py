"""Functions for band structure calculations."""

import numpy as np
import cmath as cm


def _principal(z):
    """
    Compute the principal branch of a complex number :math:`z`, such that :math:`-\pi<\text{Im}(z)\leq\pi`.

    Parameters
    ----------
    z: complex
        The original complex number.

    Returns
    -------
    z: complex
        The principal value of the complex number.
    """

    re = np.real(z)
    im = np.imag(z)
    if im <= -np.pi:
        z = re + 1j * (np.pi - np.abs((im + np.pi)) % (2 * np.pi))
    elif im > np.pi:
        z = re + 1j * (-np.pi + np.abs((im + np.pi)) % (2 * np.pi))

    return z


def berry_curv(_eigenvectors, _band, _idx_x, _idx_y, _group_size=1, method=1):
    r"""
    Compute the Berry curvature.

    **Method 1 (default):**

    The Berry curvature around a plaquette is computed using the formula from :cite:`Fukui05` (example applications in :cite:`SoluyanovPhD, AidelsburgerPhD`), such that

    .. math::
       \mathcal{B}_{12}(\mathbf{k}_\alpha) \equiv - \text{Im}\;\log\;(\tilde{\mathcal{U}}_1(\mathbf{k}_\alpha)\tilde{\mathcal{U}}_2(\mathbf{k}_\alpha+\hat{\mathbf{e}}_1)\tilde{\mathcal{U}}_1(\mathbf{k}_\alpha+\hat{\mathbf{e}}_2)^{-1}\tilde{\mathcal{U}}_2(\mathbf{k}_\alpha)^{-1}),

    where the normalized link variables are defined as

    .. math::
        \tilde{\mathcal{U}}_\gamma(\mathbf{k}_\alpha) = \frac{\det U_\gamma(\mathbf{k}_\alpha)}{|\det U_\gamma(\mathbf{k}_\alpha)|}, \;\;\; \gamma = \{1, 2\},

    with link matrices

    .. math::
        U_\gamma(\mathbf{k}_\alpha) =
        \begin{pmatrix}
        \braket{u_1(\mathbf{k}_\alpha)|u_1(\mathbf{k}_\alpha+\hat{\mathbf{e}_\gamma})} & \dots & \braket{u_1(\mathbf{k}_\alpha)|u_M(\mathbf{k}_\alpha+\hat{\mathbf{e}_\gamma})} \\
        \vdots & \ddots & \vdots \\
         \braket{u_M(\mathbf{k}_\alpha)|u_1(\mathbf{k}_\alpha+\hat{\mathbf{e}_\gamma})} & \dots & \braket{u_M(\mathbf{k}_\alpha)|u_M(\mathbf{k}_\alpha+\hat{\mathbf{e}_\gamma})}
        \end{pmatrix}.

    Here, :math:`\mathbf{k}_\alpha` is the discretized momentum vector, :math:`\{\hat{\mathbf{e}}_1, \hat{\mathbf{e}}_2\}` are linearly independent unit vectors in the momentum grid, and :math:`\ket{u(\mathbf{k}_\alpha)}` is the eigenvector at momentum :math:`\mathbf{k}_\alpha`. The link variables are constructed for :math:`M` touching bands. The Berry curvature at a point :math:`\mathbf{k}` can then be computed by taking the limit of small plaquette size.

    .. note::
        Input eigenvectors are already normalized from :class:`numpy.linalg.eig`.

    .. note::
        The Berry curvature is defined within the principal branch of the logarithm. For example, the corresponding log sum formula for a single band would be

        .. math::
            \mathcal{B}_{12}(\mathbf{k}_\alpha) = - \text{Im}\;\mathcal{P}\;(\log\tilde{\mathcal{U}}_1(\mathbf{k}_\alpha) +\log\tilde{\mathcal{U}}_2(\mathbf{k}_\alpha+\hat{\mathbf{e}}_1)-\log\tilde{\mathcal{U}}_1(\mathbf{k}_\alpha+\hat{\mathbf{e}}_2)-\log\tilde{\mathcal{U}}_2(\mathbf{k}_\alpha)),

        where :math:`\mathcal{P}` denotes the principal value of the complex number :math:`z`, such that :math:`-\pi<\text{Im}(z)\leq\pi`.

    **Method 2:**

    The Berry curvature around a plaquette is computed from the quantum metric :cite:`Parameswaran13` (example applications in :cite:`Claassen15`), such that

    .. math::
       \mathcal{B}_{12}(\mathbf{k}_\alpha) = - 2 \text{Im}[\mathcal{R}_{12}(\mathbf{k}_\alpha)],

    where the quantum metric tensor is defined as

    .. math::
       \mathcal{R}_{12}(\mathbf{k}_\alpha) = \braket{u(\mathbf{k}_\alpha+\hat{\mathbf{e}}_1)|u(\mathbf{k}_\alpha+\hat{\mathbf{e}}_2)} - \braket{u(\mathbf{k}_\alpha+\hat{\mathbf{e}}_1)|u(\mathbf{k}_\alpha)} \braket{u(\mathbf{k}_\alpha)|u(\mathbf{k}_\alpha+\hat{\mathbf{e}}_2)}.

    .. note::
        This method is only implemented for a single band, and it converges significantly slower than method 1.

    Parameters
    ----------
    _eigenvectors: ndarray
        The array of eigenvectors with dimension (num_bands, num_bands, num_samples, num_samples).
    _band: int
        The band number. If part of a band group, this must refer to the lowest band of the group.
    _idx_x: int
        The x-momentum index, with respect to the discretized grid.
    _idx_y: int
        The y-momentum index, with respect to the discretized grid.
    _group_size: int
        The number of touching bands a.k.a. number of bands in the band group (default=1).
    method: [1, 2]
        1. Compute the Berry curvature using the formula from :cite:`Fukui05` (default).
        2. Compute the Berry curvature using the quantum metric :cite:`Parameswaran13`.

    Returns
    -------
    Berry_curv: float
        The Berry curvature around a square plaquette.
    """

    if method == 1:
        def _U(var_num, __eigenvectors, __band, __idx_x, __idx_y, __group_size):
            """Compute the link variable.

            Parameters
            ----------
            var_num: [1, 2]
                The link variable number.
            __eigenvectors: ndarray
                The array of eigenvectors with dimension (num_bands, num_bands, num_samples, num_samples).
            __band: int
                The band number. If part of a band group, this must refer to the lowest band of the group.
            __idx_x: int
                The x-momentum, with respect to the discretized grid.
            __idx_y: int
                The y-momentum, with respect to the discretized grid.
            __group_size: int
                The number of bands in the band group.

            Returns
            -------
            link_var: complex
                The U(1) link variable.
            """

            link_matrix = np.zeros((__group_size, __group_size), dtype=complex)
            for i in range(__group_size):
                for j in range(__group_size):
                    vec1 = __eigenvectors[:, __band+i, __idx_x, __idx_y]
                    if var_num == 1:
                        vec2 = __eigenvectors[:, __band+j, __idx_x + 1, __idx_y]
                    elif var_num == 2:
                        vec2 = __eigenvectors[:, __band + j, __idx_x, __idx_y + 1]
                    else:
                        raise ValueError("link variable number must be in [1, 2].")
                    link_matrix[i, j] = np.conj(vec1).dot(vec2)
            link_var = np.linalg.det(link_matrix)
            return link_var

        Berry_curv = - np.imag(np.log(_U(1, _eigenvectors, _band, _idx_x, _idx_y, _group_size)
                                      * _U(2, _eigenvectors, _band, _idx_x+1, _idx_y, _group_size)
                                      * _U(1, _eigenvectors, _band, _idx_x, _idx_y+1, _group_size)**-1
                                      * _U(2, _eigenvectors, _band, _idx_x, _idx_y, _group_size)**-1))
    elif method == 2:
        if _group_size == 1:
            vec = _eigenvectors[:, _band, _idx_x, _idx_y]
            vec1 = _eigenvectors[:, _band, _idx_x+1, _idx_y]
            vec2 = _eigenvectors[:, _band, _idx_x, _idx_y+1]
            chi = np.conj(vec1).dot(vec2) - np.conj(vec1).dot(vec) * np.conj(vec).dot(vec2)
            Berry_curv = -2 * np.imag(chi)
        else:
            raise ValueError("method=2 with bands>1 in berry_curv is not yet implemented.")
    else:
        raise ValueError("method parameter in berry_curv is not in [1, 2].")

    return Berry_curv


def geom_tensor(_eigenvectors, _band, _idx_x, _idx_y, _group_size=1):
    r"""
    Compute the quantum geometric tensor.

    The quantum geometric tensor is computed using the formula from :cite:`Parameswaran13` (example applications in :cite:`Claassen15`), such that

    .. math::
       \mathcal{R}_{\mu \nu}(\mathbf{k}_\alpha) = \braket{u(\mathbf{k}_\alpha+\hat{\mathbf{e}}_\mu) | u(\mathbf{k}_\alpha+\hat{\mathbf{e}}_\nu)} - \braket{u(\mathbf{k}_\alpha+\hat{\mathbf{e}}_\mu) | u(\mathbf{k}_\alpha)} \braket{u(\mathbf{k}_\alpha) | u(\mathbf{k}_\alpha+\hat{\mathbf{e}}_\nu)},

    where :math:`\ket{u(\mathbf{k}_\alpha)}` is the eigenvector at momentum :math:`\mathbf{k}_\alpha`. The quantum geometric tensor at the point :math:`\mathbf{k}` can then be computed by taking the limit of small plaquette size.

    .. note::
        This function is currently only implemented for a single band.

    Parameters
    ----------
    _eigenvectors: ndarray
        The array of eigenvectors with dimension (num_bands, num_bands, num_samples, num_samples).
    _band: int
        The band number. If part of a band group, this must refer to the lowest band of the group.
    _idx_x: int
        The x-momentum index, with respect to the discretized grid.
    _idx_y: int
        The y-momentum index, with respect to the discretized grid.
    _group_size: int
        The number of touching bands a.k.a. number of bands in the band group (default=1).

    Returns
    -------
    tensor: ndarray
        The quantum geometric tensor with dimension (2,2).
    """

    if _group_size == 1:
        vec = _eigenvectors[:, _band, _idx_x, _idx_y]
        vec1 = _eigenvectors[:, _band, _idx_x + 1, _idx_y]
        vec2 = _eigenvectors[:, _band, _idx_x, _idx_y + 1]

        tensor = np.zeros((2, 2), dtype=np.complex128)
        tensor[0][0] = np.conj(vec1).dot(vec1) - np.conj(vec1).dot(vec)*np.conj(vec).dot(vec1)
        tensor[0][1] = np.conj(vec1).dot(vec2) - np.conj(vec1).dot(vec)*np.conj(vec).dot(vec2)
        tensor[1][0] = np.conj(vec2).dot(vec1) - np.conj(vec2).dot(vec)*np.conj(vec).dot(vec1)
        tensor[1][1] = np.conj(vec2).dot(vec2) - np.conj(vec2).dot(vec)*np.conj(vec).dot(vec2)
    else:
        raise ValueError("geom_tensor function is currently only implemented for _group_size=1.")

    return tensor