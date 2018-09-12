#!/usr/bin/env python

import os
import sys
import signal
import subprocess
import argparse

###########
# GLOBALS #
###########

FFMPEG = "/usr/local/bin/ffmpeg"

#############
# FUNCTIONS #
#############

# Call ffmpeg binary and returns output
def ff(cmd):
  s = FFMPEG + " " + cmd
  return str(subprocess.check_output(s.split(), timeout=TIMEOUT, stderr=subprocess.STDOUT))

# Kill ourselves
def euthanize(signal, frame):
  print(str(signal) + " exiting")

  # Close all open files
  # TODO
  
  sys.exit(0)


###################
# BEGIN EXECUTION #
###################

signal.signal(signal.SIGINT, euthanize)
signal.signal(signal.SIGTERM, euthanize)
signal.signal(signal.SIGABRT, euthanize)
signal.signal(signal.SIGALRM, euthanize)
signal.signal(signal.SIGSEGV, euthanize)
signal.signal(signal.SIGHUP, euthanize)

ap = argparse.ArgumentParser(description='Split a large mp3 file into smaller files')
ap.add_argument(nargs=1, metavar='file', dest='infile', type=argparse.FileType('r'), default=None,
                  help='File to split')
ap.add_argument('-p', '--prefix', nargs=1, dest='prefix', type=str, required=True,
                  help='Prefix for output files')
ap.add_argument('-i', '--inter', default=0, nargs=1, dest='pause', type=int, required=False,
                  help='Inter-pause for each slice in seconds')
ap.add_argument('-s', '--slice', default=30, nargs=1, dest='slice', type=int, required=False,
                  help='Size of each slice in minutes')
args = ap.parse_args()
  
# find the total length of the file


# Some handy commands
# ffmpeg -i input.ext -c:a copy -ss start_time -t end_time output-ext
