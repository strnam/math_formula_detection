```python
  model = HmmMathTagging()
  model.train(train_data)

  math_detect = MathDetectioin(model)

  text = """
The circle (4,-6) will have a radius, say r. We will have a tangent of it which will cut y axis.
I'm just starting on this problem - it may take a couple of extra minutes. You can use that time to check your notes or your book to look for tips on how to get the problem started.
Take a few seconds to review the concept. Does that seem familiar?
Dont worry
just wait a few minutes :)

Equation of circle: (x-5)^2 + (y-6)^2 = r^2
 
diffrentiating:
 
2(x-5) dx + 2(y-6) dy = 2r
dy/dx = 5-x /y-6
  """
  l_math_expression = math_detect.detect_math_expression(text)
```

Ref: HMM implementation from https://github.com/pincha26/NLP_Hidden_Markov_Model
