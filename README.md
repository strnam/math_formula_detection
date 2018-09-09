```python

text = '2y(dy/dx) + y^2 + 2xy(dy/dx) = 1+8y(dy/dx)'
text = """
sector= ?*r*r*(angle/360)
OADB=3.14*18*18*(80/360) \ter
=3.14*324*0.22
=223.8192cm^2
OADB=223.8192cm^2
"""
hmm_message = HmmTokenize.tokenize(text)
```

Ref: HMM implementation from https://github.com/pincha26/NLP_Hidden_Markov_Model
