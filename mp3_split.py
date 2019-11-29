#!/usr/bin/env python

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
                  help='Begin with a pause for each slice in seconds(not implemented)')
ap.add_argument('-s', '--slice', default=None, nargs=1, dest='slice', type=int, required=False,
                  help='Size of each slice in minutes(not implemented)')
ap.add_argument('-c', '--chapters', default=False, dest='chapters', action='store_true', required=False,
                  help='Use chapter breaks if present. Overrides -s if present')
ap.add_argument('-d', '--dump', default=False, dest='dump', action='store_true', required=False,
                  help='Dump info on mp3 and exit.')
ap.add_argument('-v', '--verbose', default=False, dest='verbose', action='store_true', required=False,
                  help='Verbose output during processing.')
args = ap.parse_args()

if args.pause:
  print("ERROR: -b --begin not yet implemented")
  exit(1)

if args.slice:
  print("ERROR: -s --slice not yet implemented")
  exit(1)

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
# ffmpeg -i in.opus -ss 00:00:30.0 -t 00:03:00 -c copy out.opus
# ffmpeg -loglevel fatal -i test.mp3 -ss 623.907 -to 1187.843 -c:a copy chap3.mp3

if args.chapters and len(info["chapters"]) > 0: # Split by chapters
  if args.verbose:
    print("Splitting by " + str(len(info["chapters"])) + " chapters")
  cnt = 0
  for chap in info["chapters"]:
    cnt += 1
    if args.prefix == None:
      outfile = infile.rsplit(".", 1)[0] + "-" + str(cnt).zfill(3) + ".mp3"
    else:
      outfile = args.prefix[0] + "-" + str(cnt).zfill(3) + ".mp3"

    if args.verbose:
      print("Extracting chapter " + str(cnt) + " to " + outfile + " at " + str(chap.start))
    # This also copies all metadata information into each chapter and sets track number
    ff("-loglevel fatal -i " + infile + " -ss " + str(chap.start) + " -to " + str(chap.end) + \
         " -metadata track=" + str(cnt).zfill(3) + " -c:a copy " + outfile)

else: # Split by slice size
  pass


if args.verbose:
  print("Finished\a\a\a\a")
