#!/usr/bin/env python

import os
import sys

class Chapter():
  def __init__(self, start, end):
    self.title = ""
    self.start = start
    self.end = end

  def __repr__(self):
    return "<title:" + self.title + " start:" + str(self.start) + " end:" + str(self.end) + ">"

# Count how many of char c begin in s before another char
def charCnt(s, c):
  if s.find(c) == 0:
    return 1 + charCnt(s[1:], c)
  else:
    return 0

# Takes output from ffmpeg infor cmd
# Returns hierarchicial KV parse-tree
def parseInfo(ss):
  lines = ss.splitlines()

  for ii in xrange(len(lines)):
    if lines[ii].find("Input #") == 0:
      print(str(ii) + " " + lines[ii])
      start = ii
    if lines[ii].find("Output #") == 0:
      print(str(ii) + " " + lines[ii])
      end = ii
  lines = lines[start+1:end]

  rv = {}
  rv["metadata"] = {}
  rv["general"] = {}
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

###################
# BEGIN EXECUTION #
###################

fh = open('derp.txt', 'r')
info = fh.read()
fh.close()

parseInfo(info)

#print(repr(parseInfo(info)))












