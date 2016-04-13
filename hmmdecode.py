import sys
import math
import json
import time

# reload(sys)
# sys.setdefaultencoding('utf-8')

class Model:
      def __init__(self,file):
        self.file = file
        self.tmap = {}
        self.emap = {}
        self.ct = {}
        self.cw = {}
        self.lenT = {}
        self.lenE = {}

      def retrieveModel(self):
          with open(self.file, 'r') as input:
              list_maps = input.read().split("\n")
              self.tmap = eval(list_maps[0])
              self.emap = eval(list_maps[1])
              self.ct = eval(list_maps[2])
              self.cw = eval(list_maps[3])
              self.tagDict = eval(list_maps[4])


          for k1 in self.tmap.keys():
              if k1 in self.lenT:
                  self.lenT[k1] += float(self.tmap[k1][self.tmap[k1].keys()[0]].split('/')[1])
              else:
                  self.lenT[k1] = float(self.tmap[k1][self.tmap[k1].keys()[0]].split('/')[1])

          for k1 in self.emap.keys():
              if k1 in self.lenE:
                  self.lenE[k1] += float(self.emap[k1][self.emap[k1].keys()[0]].split('/')[1])
              else:
                  self.lenE[k1] = float(self.emap[k1][self.emap[k1].keys()[0]].split('/')[1])

          for k1 in self.tmap.keys():
              for k2 in self.tmap[k1].keys():
                  n,d = self.tmap[k1][k2].split('/')
                  self.tmap[k1][k2] = (float(n))


          for k1 in self.emap.keys():
              for k2 in self.emap[k1].keys():
                  n,d = self.emap[k1][k2].split('/')
                  self.emap[k1][k2] = (float(n))



class Decoder:

     def __init__(self,sentence,model):
        self.sentence = sentence
        self.tmap = model.tmap
        self.emap = model.emap
        self.viterbi = {}
        self.backpointer = {}
        self.otagList = []
        self.itagList = []
        self.tags = []
        self.postag = ''
        self.model = model


     def decode(self):
         tokens = self.sentence.split()
         if tokens[0] in model.tagDict:
             self.otagList = model.tagDict[tokens[0]].keys()
         else:
             self.otagList = self.tmap.keys()
             self.otagList.remove('START')
         for k in self.otagList:
                 self.viterbi[k] = {}
                 self.backpointer[k] = {}
                 if tokens[0] in self.emap[k]:
                     if self.tmap['START'][k] != 0:
                        self.viterbi[k][0] = float(self.tmap['START'][k])/float(model.lenT['START']) * \
                                          float(self.emap[k][tokens[0]])/float(model.lenE[k])
                     else:
                         self.viterbi[k][0] = 0.00004 * float(self.emap[k][tokens[0]])/float(model.lenE[k])
                 else:
                     if self.tmap['START'][k] != 0:
                        self.viterbi[k][0] = float(self.tmap['START'][k])/float(model.lenT['START'])
                     else:
                        self.viterbi[k][0] = 0.00004

                 self.backpointer[k] = {}
                 self.backpointer[k][0] = 'START'

         for i in range(1,len(tokens)):
             if tokens[i] in model.tagDict:
                 self.otagList = model.tagDict[tokens[i]].keys()
             else:
                 self.otagList = self.tmap.keys()
                 self.otagList.remove('START')

             for k1 in self.otagList:
                 maxVal = 0.0
                 if tokens[i-1] in model.tagDict:
                     self.itagList = model.tagDict[tokens[i-1]].keys()
                 else:
                     self.itagList = self.tmap.keys()
                     self.itagList.remove('START')
                 for k2 in self.itagList:
                        if tokens[i] in self.emap[k1]:
                            if self.tmap[k2][k1] != 0:
                               curr_val = self.viterbi[k2][i-1] * \
                                          float(self.tmap[k2][k1])/float(model.lenT[k2])* \
                                          float(self.emap[k1][tokens[i]])/float(model.lenE[k1])
                            else:
                                curr_val = self.viterbi[k2][i-1] * \
                                           0.00004 *\
                                           float(self.emap[k1][tokens[i]])/float(model.lenE[k1])

                            if curr_val >= maxVal:
                               maxVal = curr_val

                        else:
                            if self.tmap[k2][k1] != 0:
                               curr_val = self.viterbi[k2][i-1] * \
                                            float(self.tmap[k2][k1])/float(model.lenT[k2])
                            else:
                               curr_val = self.viterbi[k2][i-1] * \
                                            0.00004
                            if curr_val >= maxVal:
                               maxVal = curr_val


                 if k1 in self.viterbi:
                   self.viterbi[k1][i] = maxVal

                 else:
                   self.viterbi[k1] = {}
                   self.viterbi[k1][i] = maxVal

                 if self.viterbi[k1][i] == 0.0:
                       self.viterbi[k1][i] = 0.1

                 maxVal = 0.0
                 argMax = ''
                 for k2 in self.itagList:
                           if self.tmap[k2][k1] != 0:
                               curr_val = self.viterbi[k2][i-1] * \
                                          float(self.tmap[k2][k1])/float(model.lenT[k2])
                           else:
                               curr_val = self.viterbi[k2][i-1] * \
                                          0.00004
                           if maxVal <= curr_val:
                              maxVal = curr_val
                              argMax = k2

                 if k1 in self.backpointer:
                    self.backpointer[k1][i] = argMax
                 else:
                    self.backpointer[k1] = {}
                    self.backpointer[k1][i] = argMax


         maxVal = 0.0
         argMax = ''
         if tokens[len(tokens)-1] in model.tagDict:
             self.otagList = model.tagDict[tokens[len(tokens)-1]].keys()
         else:
             self.otagList = self.tmap.keys()
             self.otagList.remove('START')
         for k1 in self.otagList:
                 if self.tmap[k1]['END'] !=0 :
                     curr_val = self.viterbi[k1][len(tokens)-1] * \
                                 float(self.tmap[k1]['END'])/float(model.lenT[k1])
                                #self.tmap[k1]['END']
                 else:
                     curr_val = self.viterbi[k1][len(tokens)-1] * \
                                 0.00004
                 if maxVal <= curr_val:
                      maxVal = curr_val
                      argMax = k1


         self.viterbi['END'] = {}
         self.backpointer['END'] = {}
         self.viterbi['END'][len(tokens)-1] = maxVal
         self.backpointer['END'][len(tokens)-1] = argMax


     def backtrack(self):
         tokens = self.sentence.split()
         tag = (self.backpointer['END'][len(tokens)-1])
         self.tags.append(tag)

         prevTag = tag
         for i in range(len(tokens)-1, -1, -1):
            currTag = self.backpointer[prevTag][i]
            self.tags.append(currTag)
            prevTag = currTag

         self.tags.reverse()

     def POSTag(self):

         tokens = self.sentence.split()
         for i in range(len(tokens)):
             self.postag = self.postag + tokens[i] +'/'+ self.tags[i+1] + ' '


if __name__=="__main__":
   start = time.clock()
   model_data = 'hmmmodel.txt'
   model = Model(model_data)
   model.retrieveModel()

   result = []
  # print sys.argv[1]

   with open(sys.argv[1], 'r') as input:
       for line in input:
        decoder = Decoder(line,model)
        decoder.decode()
        decoder.backtrack()
        decoder.POSTag()
        result.append(decoder.postag)

   with open('hmmoutput.txt','w') as f:
       for r in result:
           f.write(r+"\n")
   f.close()
   print time.clock()-start
