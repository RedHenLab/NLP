#!/usr/bin/python
#
# Master in /home/csa/Pattern2.6/
#
# This script converts frame-tagged files in json produced by Semafor to the NewsScape format
# 
#       https://github.com/sammthomson/semafor
# 
# Written by FFS, 2014-08-03
#
# Changelog:
#
#       2014-09-07 Forked from FrameNet-05.py
#
# ------------------------------------------------

# User input
import sys, os.path
scriptname = os.path.basename(sys.argv[0])
filename1 = sys.argv[1]

# Help screen
if filename1 == "-h" :
   print "".join([ "\n","\t","Production script for converting json files to the NewsScape format.","\n" ])
   print "".join([ "\t","Syntax:" ])
   print "".join([ "\t","\t",scriptname," <input filename.seg> <input filename.json>" ])
   print "".join([ "\n","\t","Examples:" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg $FIL.json > $FIL.frm" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg $FIL.json | tee -a $FIL.frm" ])
   print "".join([ "\n","\t","The seg-FrameNet script calls this script for bulk processing.","\n" ])
   quit()

# Second file name
filename2 = sys.argv[2]

# Utility libraries
import json, datetime, string, re

# Open the json file
framefile = open(filename2, "r")

# Counter
n=0

# A. Open the seg file
with open(filename1) as fp:

   # Examine a line at a time
   for line in fp:

# B. Strip newline and split into fields
      field = line.split("|")

#    Pretty debug
#      print('\n'.join('{}: {}'.format(*k) for k in enumerate(field)))

# C. Header and footer
      if len(field[0]) != 18:
          print line,
          continue

# D. Program credit
      if n == 0:
          credit=["FRM_01|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=FrameNet 1.5, Semafor 3.0-alpha4, ",scriptname,"|Source_Person=Charles Fillmore, Dipanjan Das, FFS|Codebook=Token|Position|Frame name|Semantic Role Labeling|Token|Position|Frame element"]
          print  "".join(credit)
          n=1

# E. Segment tags and other non-caption tags
      if field[2] == "SEG":
          print line,
          continue
      elif len(field[2]) != 3:
          print line,
          continue

# G. Remove clearly wrong unicode characters -- BOM, NULL (only utf8 hex works)
#      line = str(line).replace('\x00 ','').replace('\xef\xbf\xbd','')
      print line,

# H. Read the next line from the json file
      try:
        jsonline = framefile.readline()

        # Convert from json to dict
        SemaforDict = json.loads(jsonline)

        # Tokens
        tokens = " ".join(SemaforDict.items()[1][1])
#       print tokens

        # List the detected frames for this sentence
        for framedict in SemaforDict.items()[0][1]:

#               print framedict

                # Initialize variables
                fe = ""

                # Frame name and token position
                framenamedict = framedict.items()[0]
                framename = framenamedict[1].items()[0][1]
                start = framenamedict[1].items()[1][1][0].items()[0][1]
                end   = framenamedict[1].items()[1][1][0].items()[1][1]
                token = framenamedict[1].items()[1][1][0].items()[2][1]

                # Frame elements selected by Semantic Role Labeling
                fedict = framedict.items()[1][1][0].items()
#               print fedict
                for element in fedict[0][1]:
                   fename = element.items()[0][1]
                   festart = element.items()[1][1][0].items()[0][1]
                   feend = element.items()[1][1][0].items()[1][1]
                   fetoken = element.items()[1][1][0].items()[2][1]

                   # Skip the annotation if the frame element name is the same as the frame name (redundant)
                   if fename != framename: 
                     fe = "".join([fe,"|SRL|",fetoken,"|",str(festart),"-",str(feend),"|",fename])

#                  print unicode(fe)
                print "".join([field[0],"|",field[1],"|FRM_01|",token,"|",str(start),"-",str(end),"|",framename,fe])

      except (ValueError): continue

# Clean up
fp.close()

# EOF
