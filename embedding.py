import argparse
import os
import csv
import spacy
from gensim.models import Word2Vec



class EntityRetokenizeComponent:
    
    def __init__(self, nlp):
        pass

    def __call__(self, doc):
        with doc.retokenize() as retokenizer:
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "ORGANIZATION", 
                              "LOCATION", "GPE"]:
                    retokenizer.merge(doc[ent.start:ent.end], 
                        attrs={"LEMMA": str(doc[ent.start:ent.end])})
        return doc





class TokensGenerator:

    def __init__(self, inputpath):
        self.inputpath = inputpath


    def __iter__(self):
        nlp = spacy.load("en_core_web_sm")
        # TODO use nlp with nlp.get_instance()
        retokenizer = EntityRetokenizeComponent(nlp)
        nlp.add_pipe(retokenizer, name='merge_phrases', last=True)
        for filename in os.listdir(self.inputpath):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.inputpath, filename)
                print("tokenizing {}".format(filepath))
                with open(filepath) as f:
                    text = f.read()
                    doc = nlp(text)
                    for sent in doc.sents:
                        # TODO Remove punctuation befre tokenizing
                        tokens = [tk.text.lower() for tk in sent 
                                    if not tk.is_stop
                                    #and tk.is_alpha ]
                                    and (len(tk)>1 or tk.is_alpha)]
                        yield tokens


class TokensLoader:
    """
    Helper iterator to load tokenized sentences from a file
    """

    def __init__(self, inputpath):
        self.inputpath = inputpath


    def __iter__(self):
        with open(self.inputpath) as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                yield row 


def tokenize_to_file(inputpath, outputpath):
    with open(outputpath, 'w') as csvfile:
        csvwriter = csv.writer(csvfile, quotechar='"', quoting=csv.QUOTE_ALL)
        for tokens in TokensGenerator(inputpath):
            csvwriter.writerow(tokens)

           
def shorten_num(num):
    billion = 1000000000
    million = 1000000
    thousand = 1000
    if num // billion > 1:
        return str(int(num // billion)) + 'B'
    elif num // million > 1:
        return str(int(num // million)) + 'M'
    elif num // thousand > 1:
        return str(int(num // thousand)) + 'K'
    else:
        return str(num)
    

def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, 
            help="input tokens file (prepared by the triplex command)")
    parser.add_argument('-o', '--output', required=False, 
            help="file path to save the vectors")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    return args_dict


if __name__ == "__main__":
    args = getargs()
    tokenfile = args['input']
    outfilepath = args['output']
    vector_size = 100
    sents = TokensLoader(tokenfile)
    model = Word2Vec(sentences=sents, vector_size=vector_size, window=5, 
        min_count=1, workers=4)
    vocab_len = len(model.wv)
    default_fname = "gensim.{}.{}.bin".format(shorten_num(vocab_len), 
             vector_size)
    if os.path.isdir(outfilepath):
        outfilepath = os.path.join(outfilepath, default_fname)
    elif outfilepath is None:
        outfilepath = default_fname
    model.save(outfilepath)
