
import re
import sys
import codecs
import json
import time

class SmoothingModel:

    def __init__(self,tmap,emap,sentence_list):
        self.tmap = tmap
        self.emap = emap
        self.list = sentence_list
        self.singtt = {}
        self.singtw = {}
        self.ct = {}
        self.cw = {}
        self.tagDict = {}

    def genSingTT(self):
        for k1 in self.tmap.keys():
            count = 0
            for k2 in self.tmap[k1].keys():
                if self.tmap[k1][k2] == 1:
                    count += 1
            self.singtt[k1] = count

    def genSingTW(self):
        for k1 in self.emap.keys():
            count = 0
            for k2 in self.emap[k1].keys():
                if self.emap[k1][k2] == 1:
                    count += 1
            self.singtw[k1] = count

    def backOff(self):
        for sentence in self.list:
            tokens = sentence.split()
            for i in range(len(tokens)):
                word = tokens[i].rsplit('/',1)[0]
                tag = tokens[i].rsplit('/',1)[1]
                if tag in self.ct:
                    self.ct[tag] += 1
                else:
                    self.ct[tag] = 1
                if word in self.cw:
                    self.cw[word] += 1
                else:
                    self.cw[word] = 1
                if word in self.tagDict:
                    self.tagDict[word][tag] = 1
                else:
                    self.tagDict[word] = {}
                    self.tagDict[word][tag] = 1
        self.ct['END'] = len(self.list)

class HMMModel:

    def __init__(self,sentence_list):
        """

        :rtype: object
        """
        self.list = sentence_list
        self.tmap = {}
        self.emap = {}

    def train(self):
        for sentence in self.list:
            tokens = sentence.split()
            for i in range(len(tokens)-1):
                word = tokens[i].rsplit('/',1)[0]
                curr_tag = tokens[i].rsplit('/',1)[1]
                next_tag = tokens[i+1].rsplit('/',1)[1]

                #filling transition matrix
                if i == 0:
                    if 'START' in self.tmap:
                        if curr_tag in self.tmap['START']:
                            self.tmap['START'][curr_tag] += 1
                        else:
                           self.tmap['START'][curr_tag] = 1
                    else:
                        self.tmap['START'] = {}
                        self.tmap['START'][curr_tag] = 1

                if curr_tag in self.tmap:
                    if next_tag in self.tmap[curr_tag]:
                        self.tmap[curr_tag][next_tag] += 1
                    else:
                        self.tmap[curr_tag][next_tag] = 1
                else:
                    self.tmap[curr_tag] = {}
                    self.tmap[curr_tag][next_tag] = 1

                #filling emmison matrix
                if curr_tag in self.emap:
                    if word in self.emap[curr_tag]:
                        self.emap[curr_tag][word] += 1
                    else:
                        self.emap[curr_tag][word] = 1
                else:
                    self.emap[curr_tag] = {}
                    self.emap[curr_tag][word] = 1

                if i == len(tokens)-2:
                    last_word = tokens[i+1].rsplit('/',1)[0]
                    last_tag = next_tag

                    if last_tag in self.tmap:
                        if 'END' in self.tmap[last_tag]:
                            self.tmap[last_tag]['END'] += 1
                        else:
                            self.tmap[last_tag]['END'] = 1
                    else:
                        self.tmap[last_tag] = {}
                        self.tmap[last_tag]['END'] = 1

                    if last_tag in self.emap:
                        if last_word in self.emap[last_tag]:
                            self.emap[last_tag][last_word] += 1
                        else:
                            self.emap[last_tag][last_word] = 1
                    else:
                        self.emap[last_tag] = {}
                        self.emap[last_tag][last_word] = 1


if __name__=="__main__":
   start = time.clock()
   training_data = sys.argv[1]
   sentence_list = []
   with open(training_data, 'r') as input:
       for line in input:
           sentence_list.append(line)

   model = HMMModel(sentence_list)
   model.train()
   smoothingmodel = SmoothingModel(model.tmap,model.emap,sentence_list)
   smoothingmodel.genSingTT()
   smoothingmodel.genSingTW()
   smoothingmodel.backOff()

   for k1,v1 in model.tmap.items():
        count = 0
        for k2,v2 in v1.items():
            count += v2
        for k2,v2 in v1.items():
            v1[k2] = str(str(v2)+"/"+str(count))

   for k1,v1 in model.emap.items():
        count = 0
        for k2,v2 in v1.items():
            count += v2
        for k2,v2 in v1.items():
            v1[k2] = str(str(v2)+"/"+str(count))


   with open('hmmmodel.txt', 'w') as f:
       f.write(str(model.tmap))
       f.write("\n")
       f.write(str(model.emap))
       f.write("\n")
       f.write(str(smoothingmodel.singtt))
       f.write("\n")
       f.write(str(smoothingmodel.singtw))
       f.write("\n")
       f.write(str(smoothingmodel.ct))
       f.write("\n")
       f.write(str(smoothingmodel.cw))
       f.write("\n")
       f.write(str(smoothingmodel.tagDict))
   f.close()
