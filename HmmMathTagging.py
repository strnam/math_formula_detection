from hmmlearn import HMMModel, SmoothingModel
from hmmdecode import Model, Decoder
from HmmEncode import HmmEncodeText, HmmTokenize
import numpy as np
from sklearn.model_selection import train_test_split

MODEL_PATH = 'hmmmodel.txt'


class HmmMathTagging(object):
  def __init__(self):
    self.model = None

  def train(self, list_label_setences):
    model = HMMModel(list_label_setences)
    model.train()
    smoothingmodel = SmoothingModel(model.tmap, model.emap, list_label_setences)
    smoothingmodel.genSingTT()
    smoothingmodel.genSingTW()
    smoothingmodel.backOff()

    for k1, v1 in model.tmap.items():
      count = 0
      for k2, v2 in v1.items():
        count += v2
      for k2, v2 in v1.items():
        v1[k2] = str(str(v2) + "/" + str(count))

    for k1, v1 in model.emap.items():
      count = 0
      for k2, v2 in v1.items():
        count += v2
      for k2, v2 in v1.items():
        v1[k2] = str(str(v2) + "/" + str(count))
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

    #Load Model
    load_model = Model(MODEL_PATH)
    load_model.retrieveModel()
    self.model = load_model

  def test(self, list_label_setences):
    unlabel_data = []
    for sent in list_label_setences:
      unlabel_sent = [tok.split('/')[0] for tok in sent.split()]
      unlabel_data.append(' '.join(unlabel_sent))

    pedicted_data = self.predict(unlabel_data)
    accuracy = self.evaluate(pedicted_data, list_label_setences)
    # print('Accuracy: %s' % accuracy)
    return accuracy

  def predict(self, setences):
    result = []
    for sent in setences:
      decoder = Decoder(sent, self.model)
      decoder.decode()
      decoder.backtrack()
      decoder.POSTag()
      result.append(decoder.postag)

    return result

  def evaluate(self, list_sentence1, list_sentence2):
    num_match = 0.0
    num_token = 0.0
    for sent1, sent2 in zip(list_sentence1, list_sentence2):
      tokens1 = [tok.split('/') for tok in sent1.split()]
      tokens2 = [tok.split('/') for tok in sent2.split()]
      for tok1, tok2 in zip(tokens1, tokens2):
        num_token +=1
        if tok1[0] != tok2[0]:
          raise Exception('Token do not match')

        if tok1[1] == tok2[1]:
          num_match +=1

    accuracy = num_match/num_token
    return accuracy


class MathDetectioin(object):
  def __init__(self, hmm_tagging_model):
    self.hmm_model = hmm_tagging_model

  def detect(self, text):
    hmm_message = HmmTokenize.tokenize(text)
    hmm_input = hmm_message.to_hmm_input()
    hmm_output = self.hmm_model.predict(hmm_input.split('\n'))
    hmm_message.read_hmm_output('\n'.join(hmm_output))
    return hmm_message

  def detect_math_expression(self, text):
    hmm_text = self.detect(text)
    l_math_expression = []
    l_math_token = []
    for tok in hmm_text:
      if tok.tag.startswith('M'):
        print(tok)
        l_math_token.append(tok)
      elif len(l_math_token) > 0:
        math_express = MathExpression(l_math_token)
        l_math_expression.append(math_express)
        l_math_token = []

    if len(l_math_token) > 0:
      math_express = MathExpression(l_math_token)
      l_math_expression.append(math_express)

    return l_math_expression



class MathExpression(object):
  def __init__(self, list_math_token):
    self.math_tokens = list_math_token

  def __len__(self):
    return len(self.math_tokens)

  def to_json(self):
    text = ''
    cur_id = 0
    for tok in self.math_tokens:
      if cur_id == 0:
        text += tok.string
        cur_id = tok.end_id
      else:
        text = text + (tok.start_id - cur_id)*' ' + tok.string
        cur_id = tok.end_id

    result = {'math_expression': text,
              'start_id': self.math_tokens[0].start_id,
              'end_id': self.math_tokens[-1].end_id,
              'length': len(text)}
    return result


if __name__ == "__main__":
  with open('session_train_encode.txt', 'r') as f:
    train_data = f.readlines()

#   model = HmmMathTagging()
#   model.train(train_data)

#   math_detect = MathDetectioin(model)

#   text = """
# The circle (4,-6) will have a radius, say r. We will have a tangent of it which will cut y axis.
# I'm just starting on this problem - it may take a couple of extra minutes. You can use that time to check your notes or your book to look for tips on how to get the problem started.
# Take a few seconds to review the concept. Does that seem familiar?
# Dont worry
# just wait a few minutes :)

# Equation of circle: (x-5)^2 + (y-6)^2 = r^2
 
# diffrentiating:
 
# 2(x-5) dx + 2(y-6) dy = 2r
# dy/dx = 5-x /y-6

# Now that we've started, does that step look familiar?

# tangent to y axis means 
# dx/dy = = 
# so (y-6) / (5-x) = 0
# y = 6
#   """
#   l_math_expression = math_detect.detect_math_expression(text)
#   print len(l_math_expression)
#   for m_expr in l_math_expression:
#     print('='*10)
#     print(m_expr.to_json())



  l_acc = []
  for i in range(5):
    train, test = train_test_split(train_data,  test_size=0.4)
    model = HmmMathTagging()
    model.train(train)
    acc = model.test(test)
    l_acc.append(acc)
    print('Time %s accuracy %s' %(i, acc))
  
  print('Average accuracy %s' % (np.mean(l_acc)))

