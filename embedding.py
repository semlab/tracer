import argparse
import os
import csv
#import spacy
from gensim.models import Word2Vec
from gensim.corpora import WikiCorpus



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
    

def train_wikipedia(inputpath, outputpath, vector_size=300, window=5,
            sentences_filepath=None):
    space = ' '
    sentences = []
    has_loaded = False
    if sentences_filepath is not None and os.path.exists(sentences_filepath):
        # loading from a file
        with open(sentences_filepath) as sentences_file:
            sentences = [line.split(',') for line in sentences_file]
        has_loaded = True
    else: 
        # Processing the wiki corpus
        print("Processing the wiki corpus")
        wiki = WikiCorpus(inputpath, dictionary={})
        sentences = []
        for sentence in wiki.get_texts():
            sentences.append(sentence)
        
        #sentences = [sentence for sentence in wiki.get_texts()]
    if not has_loaded and sentences_filepath is not None:
        # saving to a file
        print("Saving wiki sentences")
        data = '\n'.join([','.join(sentence) for sentence in sentences])
        with open(sentences_filepath, 'w') as sentences_file:
            sentences_file.write(data)

    model = Word2Vec(sentences=sentences,
            vector_size=vector_size, window=window, 
            min_count=1, workers=4)
    model.save(outputpath)



def getargs():
    parser = argparse.ArgumentParser()
    #parser.add_argument('action', help='Action to run')
    parser.add_argument('-i', '--input', required=True, 
            help="input tokens file (prepared by the triplex command)")
    parser.add_argument('-o', '--output', required=False, 
            help="file path to save the vectors")
    parser.add_argument('-s', '--sentences', required=False, 
            help="file path to intermediary save the corpus sentences")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    args_dict['sentences'] = args.sentences
    return args_dict


if __name__ == "__main__":
    args = getargs()
    tokenfile = args['input']
    outfilepath = args['output']
    sentsfilepath = args['sentences']
    if True:
        wikidumppath = args['input']
        outputpath = args['output'] if args['output'] is not None else 'wiki.model'
        train_wikipedia(wikidumppath, outputpath, args['sentences'])
                #sentences_filepath="./output/wikisentences.txt")
    else:
        vector_size = 100
        sents = TokensLoader(tokenfile)
        # TODO add a logging print
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
