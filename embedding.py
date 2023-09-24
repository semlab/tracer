import argparse
import os
#import csv
from gensim.models import Word2Vec
from gensim.corpora import WikiCorpus


class TokensLoader:
    """
    Helper iterator to load tokenized sentences from a file
    """
    
    def __init__(self, inputpath, delimiter=None):
        self.inputpath = inputpath
        self.delimiter = delimiter


    def __iter__(self):
        with open(self.inputpath) as tokenfile:
            for line in tokenfile:
                line_tokens = line.split(self.delimiter)
                yield line_tokens


           
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
    parser.add_argument('--vector-size', required=False, type=int,
            help="desired  vectors size default is 100")
    #parser.add_argument('-s', '--sentences', required=False, 
    #        help="file path to intermediary save the corpus sentences")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    #args_dict['sentences'] = args.sentences
    args_dict['vector_size'] = args.vector_size
    return args_dict


if __name__ == "__main__":
    args = getargs()
    tokenfile = args['input']
    outfilepath = args['output']
    vector_size = args['vector_size']
    #sentsfilepath = args['sentences']
    #if True:
    #    wikidumppath = args['input']
    #    outputpath = args['output'] if args['output'] is not None else 'wiki.model'
    #    train_wikipedia(wikidumppath, outputpath, args['sentences'])
    #            #sentences_filepath="./output/wikisentences.txt")
    #else:

    vector_size = 100 if vector_size is None else vector_size
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
