#!/usr/bin/env python

"""emokitten - simple Emotiv EEG processing.

Usage:
  emokitten -h | --help
  emokitten --version
  emokitten alphastars [options]

Options:
  -h --help                    Show this screen.
  -v --verbose                 Show more information
  --electrode=<electrode>      Electrode [default: O1]
  --powerfiltercutoff=<Hz>     Cut-off frequency for the power [default: 0.5]
  --powerfilterorder=order     Cut-off frequency for the power [default: 3]

Program to do simple processing with the Emotiv EEG system.

The program requires the emotiv.py module
https://github.com/openyou/emokit/tree/master/python/

"""

from __future__ import division, print_function

import logging

import warnings

from emokit import emotiv

import gevent

import numpy as np

import scipy.signal as signal
from scipy.signal.filter_design import BadCoefficients


SAMPLING_RATE = 128.
BRAIN_ELECTRODES = ('F7', 'F8', 'AF3', 'AF4', 'FC5', 'FC6', 'F3',
                    'F4', 'T7', 'T8', 'O1', 'O2', 'P7', 'P8')


def electrode_signal(headset, electrode='O1'):
    """Yield single electrode signal.

    Parameters
    ----------
    headset : emotiv.Emotiv
        Instance of setup emotiv
    electrode : str
        String for electrode name

    Yields
    ------
    signal : numpy.array
        One-element, one-dimensional array with read EEG data

    """
    while True:
        packet = headset.dequeue()
        yield np.array([packet.sensors[electrode]['value']])


def electrode_signals(headset, electrodes=BRAIN_ELECTRODES):
    """Yield multiple electrode signals.

    Parameters
    ----------
    headset : emotiv.Emotiv
        Instance of headset
    electrodes : list of str
        List of strings with electrode names

    Yields
    ------
    electrode_signal : numpy.array
        1-dimensional array with electrode data

    """
    while True:
        packet = headset.dequeue()
        yield np.array([packet.sensors[electrode]['value']
                        for electrode in electrodes])


def iir_filter_coefs(order=3, cutoff=np.array([7.0, 12, 0]),
                     btype='band', nyq=SAMPLING_RATE/2):
    """Compute IIR filter coefficients.

    Parameters
    ----------
    order : int
        Filter order
    cutoff : numpy.array
        Array with filter cutoff frequencies in Hertz
    btype : 'band'
        Filter type
    nyq : float
        Nyquist frequency in Hertz

    Returns
    -------
    b : numpy.array
        Filter coefficients
    a : numpy.array
        Filter coefficients

    """
    with warnings.catch_warnings():
        warnings.filterwarnings("error")
        try:
            b, a = signal.iirfilter(order, cutoff/nyq, btype=btype)
        except BadCoefficients:
            raise
    return b, a


def iir_filter(x, order=3, cutoff=np.array([7.0, 12, 0]),
               btype='band', nyq=SAMPLING_RATE/2):
    """Filter signal with IIR filter.

    Infinite impulse response filter as generator
    alpha filter with a short IIR filter

    Parameters
    ----------
    x : iterator yielding an numpy.array
        Input signal
    order : int
        Filter order
    cutoff : numpy.array
        Array with cutoff-frequencies
    btype : 'band', 'lowpass', ...
        String with filter type
    nyq : float
        Nyquist frequency

    Yields
    ------
    y : numpy.array

    """
    it = iter(x)
    b, a = iir_filter_coefs(order=order, cutoff=cutoff, btype=btype, nyq=nyq)
    # The delay buffer
    xin = it.next()
    v = np.zeros((len(b), len(xin)))
    while True:
        # Direct form II implementation of IIR filter
        v[0] = xin - a[1:].dot(v[1:, :])
        y = b.dot(v)
        # Would a ring buffer be better here?
        v[1:, :] = v[:-1, :]
        yield y
        xin = it.next()


def abser(x):
    """Yield absolut value of input iterator.

    Parameters
    ----------
    x : iterator
        Iterator that delivers an array

    Yields
    ------
    y : numpy.array
        Absolute value of input iterator value

    """
    it = iter(x)
    while True:
        yield np.abs(it.next())


def ratioer(x, y):
    """Yield ratio of input iterators.

    Parameters
    ----------
    x : iterator
        Input array for the numerator
    y : iterator
        Input array for the denominator

    Yields
    ------
    y : numpy.array
        Output array with division result

    """
    it1 = iter(x)
    it2 = iter(y)
    while True:
        yield it1.next() / it2.next()


def alpha_stars(electrode='O1', cutoff=0.5, order=3):
    """Read EEG and print stars.

    Parameters
    ----------
    electrode : str
        String with electrode name
    cutoff : float
        Cutoff-frequency for the lowpass filter
    order : int
        Filter order of the lowpass filter

    """
    logging.info('Opening Emotiv device')
    try:
        headset = emotiv.Emotiv(display_output=False)
    except:
        logging.fatal("Could not open headset")

    try:
        logging.info('Setup of Emotiv device')
        gevent.spawn(headset.setup)
        gevent.sleep(1.5)

        output = iir_filter(
            abser(
                iir_filter(
                    electrode_signal(
                        headset, electrode=electrode))),
            cutoff=cutoff, order=order, btype='lowpass')

        for n, y in enumerate(output):
            if not n % 10:
                value = int(max(0, min(127, 10*y-60)))
                print(electrode + ': ' + ('*' * (value//2)))
            gevent.sleep(0)

    except KeyboardInterrupt:
        headset.close()
    finally:
        headset.close()


def main():
    """Command-line interface."""
    from docopt import docopt

    arguments = docopt(__doc__)

    if arguments['--verbose'] == 1:
        logging.basicConfig(level=logging.INFO)
    if arguments['--verbose'] > 1:
        logging.basicConfig(level=logging.DEBUG)

    electrode = arguments['--electrode']
    cutoff = float(arguments['--powerfiltercutoff'])
    order = int(arguments['--powerfilterorder'])

    if arguments['alphastars']:
        alpha_stars(electrode, cutoff, order)


if __name__ == "__main__":
    main()
