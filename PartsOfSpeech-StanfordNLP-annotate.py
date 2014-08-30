#!/usr/bin/python -W ignore
#
# This script provides parts-of-speech analysis using the POS-tagger from Stanford NLP.
# 
# Each line is tokenized into sentences -- a few lines are not correctly split into sentences by cc-segment-stories.
#
# http://www-nlp.stanford.edu/software/tagger.shtml
#
#       Format TBA 20140720230042.157|20140720230050.866|POS_02|HOLLYWOOD/NNP|IS/VBZ|MOURNING/VBG|THE/DT|LOSS/NNP|OF/IN|A/NNP|LEGEND/NNP
#       Start time|End time|Primary tag(|Word/parts-of-speech tag)*
#
# The stanford-postagger uses the Penn Treebank II tag set, see http://www.clips.ua.ac.be/pages/mbsp-tags
#
# Written by FFS, 2014-08-09
#
# Changelog:
#
#       2014-08-13 Set #!/usr/bin/python -W ignore to turn off Unicode warnings
#       2014-08-09 Forked from PartsOfSpeech-aptagger-01.py
#
# -----------------------------------------------------------------------------------------------------------------

# User input
import sys, os.path
scriptname = os.path.basename(sys.argv[0])
filename = sys.argv[1]

# Help screen
if filename == "-h" :  
   print "".join([ "\n","\t","This is a test script for parts-of-speech analysis -- issue:","\n" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg > $FIL.pos or" ])
   print "".join([ "\t","\t",scriptname," $FIL.seg | sponge $FIL.seg" ])
   print "".join([ "\n","\t","or use the seg-PartsOfSpeech-stanford bash script for bulk processing." ])
   print "".join([ "\n","\t","See also seg-PartsOfSpeech-MBSP.","\n" ])
   quit()

# Libraries
import datetime, re

# Define the taggers (see PartsOfSpeech-StanfordNLP-01.py for nltk client)
# Currently configured -sentenceDelimiter newline -tokenize false
import ner
Mix = ner.SocketNER(host='localhost', port=9020, output_format='slashTags')
UPP = ner.SocketNER(host='localhost', port=9021, output_format='slashTags') 

# Pattern for making sure sentences are split
# http://www.clips.ua.ac.be/pages/pattern-en
from pattern.en import tokenize

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
         credit=["POS_02|",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),"|Source_Program=stanford-postagger 3.4, ",scriptname,"|Source_Person=Kristina Toutanova, FFS|Codebook=Treebank II"]
         print  "".join(credit)
         n=1

# E. Segment tags and other non-caption tags
      if field[2] == "SEG":
         print line,
         continue
      elif len(field[2]) != 3:
         print line,
         continue

# F. Get the text, clean leading chevrons -- if BOM, strip non-ascii, otherwise remove individually
      try:
          text = re.sub('^[>,\ ]{0,6}','', field[3])
          if re.search("(\xef\xbf\xbd)", text): text = ''.join([x for x in text if ord(x) < 128])
          text = str(text).replace('\x00 ','').replace('\xef\xbf\xbd','')
          text = str(text).replace('\xf7','').replace('\xc3\xba','').replace('\xb6','').replace('\xa9','').replace('\xe2\x99\xaa','')
          text = str(text).replace('\xc3\xaf','').replace('\x5c','').replace('\xf1','').replace('\xe1','').replace('\xe7','').replace('\xfa','')
          text = str(text).replace('\xf3','').replace('\xed','').replace('\xe9','').replace('\xe0','').replace('\xae','').replace('\xc2','')
          text = str(text).replace('\xc3','').replace('\xa2','').replace('\xbf','')
#         print text
      except IndexError:
          print line
          continue

# G. Remove clearly wrong unicode characters -- BOM, NULL (only utf8 hex works)
      line = str(line).replace('\x00 ','').replace('\xef\xbf\xbd','')
      print line,

# H. Removed: do not split the text -- assume this is done correctly
      # Ensure the text is split into sentences
      # tokenize(string, punctuation=".,;:!?()[]{}`''\"@#$^&*+-|=~_", replace={})
      # for sentence in tokenize(text):
      sentence = text

# I. Select the parser
      if sentence.isupper() or sentence.islower(): st = UPP
      else: st = Mix

# J. Parts of speech with stanford-postagger via pyner
      try:
             pos = st.tag_text(sentence)
             # AVO_NNP :_: Waves_NNS do_VBP n't_RB care_VB what_WP age_NN you_PRP are_VBP ._.
             pos = str(pos).replace(' ','|').replace('_','/')
             print "".join([field[0],"|",field[1],"|POS_02|",pos])
      except (UnicodeDecodeError, UnicodeEncodeError, IndexError, AssertionError):
             print "".join([field[0],"|",field[1],"|POS_02","|NA"])
             continue

# EOF
