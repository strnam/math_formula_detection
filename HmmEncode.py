import re
import enchant
import operator
import string
import sys
from collections import namedtuple
from collections import Sequence


english_dict = enchant.Dict("en_US")
MATH_TOKENS = ['sin', 'cos', 'max', 'min', 'dx', 'dy']

TAGGING_SET = ['MVAR', #Math variable
               'MOP',  #Math operator
               'MSYM', #Math symbol
               'MNUM'  #Math number
               'TEXT', #Normal text
               'NUM',  #Normal number
               'PUNC'] #Normal punctuation

# class HmmToken(object):
#   def __init__(self):
#     self.string = None
#     self.start_id = None
#     self.end_id = None
#     self.alias = None
#     self.tag   = None

HmmToken = namedtuple('HmmToken', ['string', 'start_id', 'end_id', 'alias', 'tag'])


class HmmEncodeText(Sequence):
  def __init__(self, text):
    self.message_text = text
    self.tokens = []
    self.full_tokens = [] # Token include newline character

  def __len__(self):
    return len(self.tokens)

  def __getitem__(self, key):
    return self.tokens[key]

  def __str__(self):
    return "\n".join([str(tok) for tok in self.tokens])

  def add_token(self, hmm_token):
    """
    Add token to message
    Args:
      hmm_token (HmmToken): hmm token

    Returns:

    """
    if hmm_token.alias != '\n':
      self.tokens.append(hmm_token)
    self.full_tokens.append(hmm_token)

  def to_hmm_input(self):
    """
    Args:
      hmm_message (HmmEncodeText):

    Returns:
      str: input text for HMM model
    """
    token_alias = [hmm_tok.alias for hmm_tok in self.full_tokens]
    text = " ".join(token_alias).strip()
    text = re.sub('\n+', '\n', text)
    text = re.sub('\n\s+', '\n', text)
    return text

  def read_hmm_output(self, text_hmm_ouput):
    """
    Parse ouput from hmm model to tokens, matching each token toghether and fill tag infomation.
    Args:
      text_hmm_ouput (str): output text of HMM model,
        "<word1>/<tag1> <word2>/<tag2> "

    Returns:

    """
    raw_tokens = [tok.split('/') for tok in text_hmm_ouput.split()]
    if len(raw_tokens) != len(self.tokens):
      raise Exception('The lenght not match')

    new_tokens = []
    for hmm_token, raw_tokens in zip(self.tokens, raw_tokens):
      if hmm_token.alias != raw_tokens[0]:
        raise Exception('The string not match: %s and %s' % (hmm_token.alias, raw_tokens[0]))

      new_hmm_token = hmm_token._replace(tag=raw_tokens[1])
      new_tokens.append(new_hmm_token)

    self.tokens = new_tokens

  def evaluate(self, hmm_message):
    if len(hmm_message) != len(self.tokens):
      raise Exception('The lenght not match')
    num_match = 0
    for i in range(len(hmm_message)):
      if hmm_message[i].alias != self.tokens[i].alias:
        raise Exception('The string not match: %s and %s' % (hmm_message[i].alias, self.tokens[i].alias))
      if hmm_message[i].tag != self.tokens[i].tag:
        num_match += 1

    accuracy = float(num_match)/len(self.tokens)
    return accuracy



class HmmTokenize(object):
  def __init__(self):
    pass

  @classmethod
  def tokenize(cls, text):
    """
    Tokenize text to HmmMessage

    Args:
      text (str):

    Returns:
      HmmEncodeText:
    """
    hmm_message = HmmEncodeText(text)
    raw_tokens = cls._tokenize(text)
    for string, start_id, end_id in raw_tokens:
      alias_string = cls.decode_token(string)
      hmm_token = HmmToken(string=string,
                           start_id=start_id,
                           end_id=end_id,
                           alias=alias_string,
                           tag=None)
      hmm_message.add_token(hmm_token)

    return hmm_message

  @classmethod
  def _split_by_pattern(cls, text, pattern):
    p = re.compile(pattern)
    list_match = []
    for match in p.finditer(text):
      list_match.append((match.group(), match.start(), match.end()))

    return list_match

  @classmethod
  def _tokenize(cls, text):
    # Tokens must non-overlap with each other
    l_token = []

    # word token
    for string_tok, start_id, end_id in cls._split_by_pattern(text, r'\w+'):
      l_token.append((string_tok, start_id, end_id))

    # punctuation token
    punc_pattern = r'[%s]' % string.punctuation
    for string_tok, start_id, end_id in cls._split_by_pattern(text, punc_pattern):
      l_token.append((string_tok, start_id, end_id))

    # newline token (HMM model care to newline so keep it as token)
    for string_tok, start_id, end_id in cls._split_by_pattern(text, r'\n+'):
      l_token.append((string_tok, start_id, end_id))

    l_token = sorted(l_token, key=lambda tok:tok[1]) # Sort token by start_id
    return l_token


  @classmethod
  def decode_token(cls, str_token):
    """
    Decode token to alias. It help reduce the dictionary size
    Args:
      str_token (str): token string

    Returns:
      str: Token alias

    """
    text = str_token.strip()

    if len(text) == 0:
      if '\n' in str_token:
        return '\n'
      else:
        raise Exception('Do not expected character')

    if text == '/':
      return 'splash'  # splash confuse with syntax of hmm, so make it different alias

    if text.isdigit():
      return 'number'

    if len(text) == 1:
      return text

    if text in MATH_TOKENS:
      return text

    if english_dict.check(text):
      return 'word'

    num_upper = len(re.findall(r'[A-Z]', text))
    num_lowwer = len(re.findall(r'[a-z]', text))
    num_number = len(re.findall(r'[0-9]', text))

    pattern = 'upper{0}_lower{1}'.format(num_upper, num_lowwer)
    if num_number > 0:
      pattern = "%s_number" % (pattern)

    return pattern


def decode_text(text):
  #tokens = re.split(r'(\W)', text)
  #tokens = re.findall('\d+|\w+|\W+', text)
  tokens = re.findall('\w+|\W+', text)
  l_tokens = [tok.split(' ') for tok in tokens]
  tokens = reduce(operator.concat, l_tokens)
  tokens = [tok.strip() for tok in tokens if len(tok.strip()) > 0]

  token_decode = [decode_token(tok) for tok in tokens if tok != '']
  return " ".join(token_decode)


def decode_token(text):
  text = text.strip()

  if text == '/':
    return 'SPLASH' # splash confuse with syntax of hmm, so make it different

  if len(text) == 1:
    return text

  if text in MATH_TOKENS:
    return text

  if english_dict.check(text):
    return 'WORD'

  if text.isdigit():
    return 'NUMBER'

  num_upper = len(re.findall(r'[A-Z]',text))
  num_lowwer = len(re.findall(r'[a-z]',text))
  num_number = len(re.findall(r'[0-9]', text))
  pattern = 'upper{0}lower{1}num{2}'.format(num_upper, num_lowwer, num_number)
  return pattern


if __name__ == "__main__":
  text = '2y(dy/dx) + y^2 + 2xy(dy/dx) = 1+8y(dy/dx)'
  text = """
  sector= ?*r*r*(angle/360)
  OADB=3.14*18*18*(80/360) \ter
  =3.14*324*0.22
  =223.8192cm^2
  OADB=223.8192cm^2
  """
  #print(text.split())
  with open('session_train.txt', 'r') as f:
    text = f.read()

  hmm_message = HmmTokenize.tokenize(text)
  with open('session_train_encode.txt', 'w') as f:
    f.write(HmmTokenize.tokenize(text).to_hmm_input())

  # with open('hmmoutput.txt', 'r') as f:
  #   ouput_text = f.read()
  #
  # hmm_message.read_hmm_output(ouput_text)
  # print(hmm_message)

  # raw_data_path = sys.argv[1]
  # with open(raw_data_path, 'r') as f:
  #   lines_text = f.readlines()
  #
  #
  # lines_text = [decode_text(text) for text in lines_text]
  #
  # with open('message_data.txt', 'w') as f:
  #   f.write('\n'.join(lines_text