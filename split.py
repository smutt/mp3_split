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


###########
# CLASSES #
###########
class Chapter():
  def __init__(self, start, end):
    self.title = ""
    self.start = start
    self.end = end

  def __repr__(self):
    return "<title:" + self.title + " start:" + str(self.start) + " end:" + str(self.end) + ">"


#############
# FUNCTIONS #
#############
# Count how many of char c begin in s before another char
# deprecated
def charCnt(s, c):
  if s.find(c) == 0:
    return 1 + charCnt(s[1:], c)
  else:
    return 0

# Takes output from ffmpeg info cmd
# Returns parsed info
def parseInfo(ss):
  lines = ss.splitlines()

  for ii in xrange(len(lines)):
    if lines[ii].find("Input #") == 0:
      start = ii
    if lines[ii].find("Output #") == 0:
      end = ii
  lines = lines[start+1:end]

  rv = {}
  rv["general"] = {}
  rv["metadata"] = {}
  rv["chapters"] = []
  active = ""

  for ll in lines:
    if ll.find("  Metadata:") == 0:
      active = "metadata"
      continue

    elif ll.find("  Duration:") == 0:
        vals = ll.strip().split(",")
        rv["general"]["duration"] = vals[0].split("Duration: ")[1]
        rv["general"]["start"] = float(vals[1].split("start: ")[1].strip())
        rv["general"]["bitrate"] = int(vals[2].strip().split(" ")[1])
        continue

    elif ll.find("    Chapter #") == 0:
      active = "chapters"
      vals = ll.split(",")
      start = float(vals[0].split("start ")[1].strip())
      end = float(vals[1].split("end ")[1].strip())
      rv["chapters"].append(Chapter(start, end))
      continue

    if active == "metadata":
      vals = ll.strip().split(":", 1)
      rv["metadata"][vals[0].strip()] = vals[1].strip()

    elif active == "chapters":
      if ll.strip().find("title") == 0:
        rv["chapters"][-1].title = ll.split(":", 1)[1].strip()

  return rv


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

# Capture info on our file
info = parseInfo(ff("-i " + infile + " -f null -"))

if args.dump:
  print("__general__")
  for k,v in info["general"].iteritems():
    print(k + " : " + str(v))

  print("__metadata__")
  for k,v in info["metadata"].iteritems():
    print(k + " : " + str(v))

  print("__chapters__")
  for chap in info["chapters"]:
    print(repr(chap))
  exit(0)


# Some handy commands
# ffmpeg -i input.ext -c:a copy -ss start_time -t end_time output-ext

