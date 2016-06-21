#!/usr/bin/env python

"""emokitten - simple Emotiv EEG processing.

Usage:
  emokitten -h | --help
  emokitten --version
  emokitten alphastars [options]

Options:
  -h --help                    Show this screen.
  --version                    Show version.
  -v --verbose                 Show more information
  --electrode=<electrode>      Electrode [default: O1]
  --powerfiltercutoff=<Hz>     Cut-off frequency for the power [default: 0.5] 
  --powerfilterorder=order     Cut-off frequency for the power [default: 3] 

Program to do simple processing with the Emotiv EEG system.

The program requires the emotiv.py module 
https://github.com/openyou/emokit/tree/master/python/

"""
