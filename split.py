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
  return str(subprocess.check_output(s.split(), stderr=subprocess.STDOUT))

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
ap.add_argument(nargs=1, dest='infile', type=str, default=None,
                  help='File to split')
ap.add_argument('-p', '--prefix', default=None, nargs=1, dest='prefix', type=str, required=False,
                  help='Prefix for output files')
ap.add_argument('-b', '--begin', default=0, nargs=1, dest='pause', type=int, required=False,
                  help='Begin with a pause for each slice in seconds')
ap.add_argument('-s', '--slice', default=30, nargs=1, dest='slice', type=int, required=False,
                  help='Size of each slice in minutes')
ap.add_argument('-c', '--chapters', default=False, dest='chapters', action='store_true', required=False,
                  help='Use chapter breaks if present. Overrides -s if present')
ap.add_argument('-d', '--dump', default=False, dest='dump', action='store_true', required=False,
                  help='Dump info on mp3 and exit.')
args = ap.parse_args()

infile = args.infile[0]

# Load the info on the file
info = ff("-i " + infile + " -f null -")

if arg.dump:
  print info
  exit(0)



# Some handy commands
# ffmpeg -i input.ext -c:a copy -ss start_time -t end_time output-ext

