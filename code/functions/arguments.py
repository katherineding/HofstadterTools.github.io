"""Functions for argument parsing."""

import argparse


def parse_input_arguments(program):
    """
    Parse the input arguments to a given program.

    Each program may be run with a given set of flags. This function parses those command-line arguments and returns them as a dictionary.

    Parameters
    ----------
    program: string
        The name of the program.

    Returns
    -------
    args: dict
        The dictionary of input arguments.
    """

    parser = argparse.ArgumentParser(prog=program)
    models = ["Hofstadter"]
    parser.add_argument("-mod", "--model", type=str, default="Hofstadter", choices=models, help="name of model")
    displays = ["3D", "2D"]
    parser.add_argument("-disp", "--display", type=str, default="3D", choices=displays, help="how to display band structure")
    parser.add_argument("-nphi", nargs=2, type=int, default=[1, 4], help="flux density")
    parser.add_argument("-samp", type=int, default=101, help="number of samples in linear direction")
    parser.add_argument("-bgt", type=float, default=0.01, help="band gap threshold")
    args = vars(parser.parse_args())

    return args