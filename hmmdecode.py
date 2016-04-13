
import sys
import math
import json
import time


class Model:
      def __init__(self,file):
        self.file = file
        self.tmap = {}
        self.emap = {}
        self.singtt = {}
        self.singtw = {}
        self.ct = {}
        self.cw = {}
        self.ptt = {}
        self.ptw = {}
        self.n = 0
        self.V = 0
        self.pbackoffw = 0


      def retrieveModel(self):
          with open(self.file, 'r') as input:
              list_maps = input.read().split("\n")
              self.tmap = eval(list_maps[0])
              self.emap = eval(list_maps[1])
              self.singtt = eval(list_maps[2])
              self.singtw = eval(list_maps[3])
              self.ct = eval(list_maps[4])
              self.cw = eval(list_maps[5])
              self.tagDict = eval(list_maps[6])

          for v in self.cw.itervalues():
            self.n += v
          self.V = len(self.cw.keys())

          for t in self.ct.keys():
              self.ptt[t] = float(self.ct[t])/float(self.n)
          for w in self.cw.keys():
              self.ptw[w] = float(self.cw[w] + 1)/float(self.n + self.V)


          for k1 in self.tmap.keys():
              for k2 in self.tmap[k1].keys():
                  n,d = self.tmap[k1][k2].split('/')
                  self.tmap[k1][k2] = (float(n)/float(d))
                  #self.tmap[k1][k2] = self.smoothing('T',k1,k2,n,d)

          for k1 in self.emap.keys():
              for k2 in self.emap[k1].keys():
                  n,d = self.emap[k1][k2].split('/')
                  self.emap[k1][k2] = (float(n)+1/float(d))
                  #self.emap[k1][k2] = self.smoothing('E',k1,k2,n,d)
                  #print 2

          self.pbackoffw = float(1)/float(self.n + self.V)


      def smoothing(self,type,k1,k2,num,denom):
          lda = 1
          if type == 'T':
              if k1 in self.singtt:
                  lda += self.singtt[k1]
              val = float(float(num) + lda*self.ptt[k2])/float(float(denom) + lda)

          elif type == 'E':
              if k1 in self.singtw:
                  lda += self.singtw[k1]
              val = float(float(num) + lda*self.ptw[k2])/float(float(denom) + lda)

          elif type == 'MW':
              if k1 in self.singtw:
                  lda += self.singtw[k1]
              val = float(float(num) + lda * self.pbackoffw)/float(float(denom) + lda)

          elif type == 'MT':
              if k1 in self.singtt:
                  lda += self.singtt[k1]
              val = float(float(num) + lda * self.ptt[k2])/float(float(denom) + lda)

          return (val)

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
             if k in self.tmap['START']:
                 self.viterbi[k] = {}
                 self.backpointer[k] = {}
                 if tokens[0] in self.emap[k]:
                     self.viterbi[k][0] = self.tmap['START'][k] * self.emap[k][tokens[0]]
                 else:
                     self.viterbi[k][0] = self.tmap['START'][k] * model.smoothing('MW',k,tokens[0],0,model.ct[k])

                 self.backpointer[k] = {}
                 self.backpointer[k][0] = 'START'

         for i in range(1,len(tokens)):
             if tokens[i] in model.tagDict:
                 self.otagList = model.tagDict[tokens[i]].keys()
             else:
                 self.otagList = self.tmap.keys()
                 self.otagList.remove('START')
             for k1 in self.otagList:

                 maxVal = 0
                 if tokens[i-1] in model.tagDict:
                     self.itagList = model.tagDict[tokens[i-1]].keys()
                 else:
                     self.itagList = self.tmap.keys()
                     self.itagList.remove('START')
                 for k2 in self.itagList:
                     if k1 in self.tmap[k2]:
                        if tokens[i] in self.emap[k1] and k2 in self.viterbi and i-1 in self.viterbi[k2]:
                           maxVal = max(maxVal,self.viterbi[k2][i-1]*self.tmap[k2][k1]*self.emap[k1][tokens[i]])
                        elif k2 in self.viterbi and i-1 in self.viterbi[k2]:
                           maxVal = max(maxVal,self.viterbi[k2][i-1] * self.tmap[k2][k1] * model.smoothing('MW',k1,tokens[i],0,model.ct[k1]))

                     else:
                         if tokens[i] in self.emap[k1] and k2 in self.viterbi and i-1 in self.viterbi[k2]:
                           maxVal = max(maxVal,self.viterbi[k2][i-1]*model.smoothing('MT',k2,k1,0,model.ct[k2])*self.emap[k1][tokens[i]])
                         elif k2 in self.viterbi and i-1 in self.viterbi[k2]:
                           maxVal = max(maxVal,self.viterbi[k2][i-1] * model.smoothing('MT',k2,k1,0,model.ct[k2]) * model.smoothing('MW',k1,tokens[i],0,model.ct[k1]))


                 if k1 in self.viterbi:
                   self.viterbi[k1][i] = maxVal
                 else:
                   self.viterbi[k1] = {}
                   self.viterbi[k1][i] = maxVal


                 maxVal = 0
                 argMax = ''
                 for k2 in self.itagList:
                    if k1 in self.tmap[k2]:
                        if k2 in self.viterbi and i-1 in self.viterbi[k2]:
                           curr_val = self.viterbi[k2][i-1]*self.tmap[k2][k1]
                           if maxVal <= curr_val:
                              maxVal = curr_val
                              argMax = k2
                    else:
                        if k2 in self.viterbi and i-1 in self.viterbi[k2]:
                           curr_val = self.viterbi[k2][i-1]*model.smoothing('MT',k2,k1,0,model.ct[k2])
                           if maxVal <= curr_val:
                              maxVal = curr_val
                              argMax = k2


                 if k1 in self.backpointer:
                    self.backpointer[k1][i] = argMax
                 else:
                    self.backpointer[k1] = {}
                    self.backpointer[k1][i] = argMax


         maxVal = 0
         argMax = ''
         if tokens[len(tokens)-1] in model.tagDict:
             self.otagList = model.tagDict[tokens[len(tokens)-1]].keys()
         else:
             self.otagList = self.tmap.keys()
             self.otagList.remove('START')
         for k1 in self.otagList:
             if 'END' in self.tmap[k1]:
                 curr_val = self.viterbi[k1][len(tokens)-1]*self.tmap[k1]['END']
                 if maxVal <= curr_val:
                      maxVal = curr_val
                      argMax = k1
             else:
                 curr_val = self.viterbi[k1][len(tokens)-1]*model.smoothing('MT',k1,'END',0,model.ct[k1])
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
