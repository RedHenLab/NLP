#!/usr/bin/python
#
# This script provides parts of speech analysis using the MBPS parser from the CLiPS project.
#
# Each line is tokenized into sentences -- a few lines are not correctly split into sentences by cc-segment-stories.
# Note that MBSP now skips lines with utf8 errors -- they are fairly common, though most are likely musical notes and copyright symbols.
#
#       20140710235922.257|20140710235926.928|POS_01|DUDE/NNP/I-NP/O|,/,/O/O|WE/PRP/I-NP/O|HAVE/VBP/I-VP/O|THE/DT/I-NP/O|MUNCHIES/NNS/I-NP/O|!/./O/O
#       Start time|End time|Primary tag(|Word parts of speech tags)*
#
# Memory-Based Shallow Parser (MBSP)
# http://www.clips.ua.ac.be/pages/MBSP
#
# MBSP uses the Penn Treebank II tag set, see http://www.clips.ua.ac.be/pages/mbsp-tags
#
# MBSP starts four data servers that require quite a bit of memory 
# (CHUNK: 80MB, LEMMA: 10MB, RELATION: 160MB, PREPOSITION: 210MB). 
# Only the CHUNK server (which gives you the part-of-speech tags) 
# is mandatory. The optional servers can be disabled in config.py 
# to reduce the memory usage, for example:
#
#         servers = ['chunk', 'lemma']
#
# Note python/MBSP runs on ports 607x and src/MBSP on 606x, to increase capacity.
#
# Written by FFS, 2014-07-28
#
# Changelog:
#
#       2014-08-09 Add lemma (lowercase first), clean NULL as octal (freezes MBSP)
#       2014-08-08 Add port argument
#       2014-08-04 Renamed from to MBSP-pos.py PartsOfSpeech-MBSP-01.py
#       2014-07-31 Each line is tokenized into sentences
#       2014-07-28 Forked from SentiWordNet-03.py
#
# ------------------------------------------------

# User input
import sys, os.path
scriptname = os.path.basename(sys.argv[0])
port = sys.argv[1]

# Help screen
if port == "-h" :  
   print "".join([ "\n","\t","This is a production script for parts-of-speech analysis with the MBSP tagger." ])
   print "".join([ "\n","\t","MBSP ports on roma and cartago include 6040, 6050, 6060, 6070, 6080, and 6090.","\n" ])
   print "".join([ "\t","\t",scriptname," $PORT $FIL.seg > $FIL.pos or" ])
   print "".join([ "\t","\t",scriptname," 6050 2013-01-02_2000_US_CNN_Newsroom.seg | sponge 2013-01-02_2000_US_CNN_Newsroom.seg" ])
   print "".join([ "\n","\t","or use seg-PartsOfSpeech-MBSP for bulk processing.","\n" ])
   quit()

# Libraries
import datetime, re

# Select the MBSP port
MODULE = "".join(["/tvspare/software/python/MBSP-",str(port)])
if MODULE not in sys.path: sys.path.append(MODULE)
try:
   import MBSP
except ImportError:
   print "".join([ "\n","\t","MBSP failed to load on port ",port," -- see '",scriptname," -h' for available ports.","\n" ])
   quit()

# Debug
# print MBSP.parse('I ate pizza with a friend.')

# Filename
filename = sys.argv[2]

# Counter
n = 0

# A. Get the lines from the file
with open(filename) as fp:
   for line in fp:

# B. Split each line into fields
      field = line.split("|")

#    Pretty debug
#     print('\n'.join('{}: {}'.format(*k) for k in enumerate(field)))

# C. Header and footer
      if len(field[0]) != 18:
         print line,
         continue

# D. Program credit
      if n == 0:
         credit=["POS_01|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=MBSP 1.4, ",scriptname,"|Source_Person=Walter Daelemans, FFS|Codebook=Treebank II"]
         print  "".join(credit)
         n=1

# E. Segment tags and other non-caption tags
      if field[2] == "SEG":
         print line,
         continue
      elif len(field[2]) != 3:
         print line,
         continue

# F. Get the text, clean leading chevrons -- if BOM, strip non-ascii, otherwise remove individually; lowercase text
      try:
          text = re.sub('^[>,\ ]{0,6}','', field[3])
          if re.search("(\xef\xbf\xbd)", text): text = ''.join([x for x in text if ord(x) < 128])
          text = str(text).replace('\x00 ','').replace('\xef\xbf\xbd','')
          text = str(text).replace('\xf7','').replace('\xc3\xba','').replace('\xb6','').replace('\xa9','').replace('\xe2\x99\xaa','')
          text = str(text).replace('\xc3\xaf','').replace('\x5c','').replace('\xf1','').replace('\xe1','').replace('\xe7','').replace('\xfa','')
          text = str(text).replace('\xf3','').replace('\xed','').replace('\xe9','').replace('\xe0','').replace('\xae','').replace('\xc2','')
          text = str(text).replace('\xc3','').replace('\xa2','').replace('\xbf','')
          if text.isupper(): text = text.lower()
#         print text
      except IndexError:
          print line
          continue

# G. Remove clearly wrong unicode characters -- BOM, NULL (only utf8 hex works)
      line = str(line).replace('\x00 ','').replace('\xef\xbf\xbd','')
      print line,

# H. Parts of speech with MBSP -- resplit the text if needed
      try:
         pos = MBSP.chunk(text, tokenize=True, lemmata=True)
         for pos in pos.splitlines():
             pos = str(pos).replace(' ','|')
             print "".join([field[0],"|",field[1],"|POS_01","|",pos])
      except (UnicodeDecodeError, UnicodeEncodeError, IndexError, AssertionError):
         # Tag failed UTF-8 lines NA to enable repair
         print "".join([field[0],"|",field[1],"|POS_01","|NA"])
         continue

# I. Close the file
fp.close()

# EOF
