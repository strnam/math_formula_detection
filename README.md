# Hidden Markov Model part-of-speech tagger for Catalan (using count one smoothing)
<h3> Overview </h3>
    • The training data provided is tokenized and tagged; the test data will be tokenized, and this tagger will add the tags.
<h3> Data - A set of training and development data is included</h3>
	• catalan_corpus_train_tagged.txt - file with tagged training data in the word/TAG format, with words separated by spaces and each sentence on a new line.
	• catalan_corpus_dev_tagged.txt - file with tagged development data in the word/TAG format, with words separated by spaces and each sentence on a new line, to serve as an answer key.	
	• catalan_corpus_dev_raw.txt - A file with untagged development data, with words separated by spaces and each sentence on a new line. 
<h3> Programs</h3>
    • hmmlearn.py will learn a hidden Markov model from the training data, and hmmdecode.py will use the model to tag new data.
	• The learning program will be invoked by calling > python hmmlearn.py /path/to/input
	• The argument is a single file containing the training data; the program will learn a hidden Markov model, and write the model parameters to a file called hmmmodel.txt. 
	• The tagging program will be invoked by calling > python hmmdecode.py /path/to/input
	• The argument is a single file containing the test data; the program will read the parameters of a hidden Markov model from the file hmmmodel.txt, tag each word in the test data, and write the results to a text file called hmmoutput.txt in the same format as the training data.
	