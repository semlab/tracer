import os
#import json
import argparse
import csv
from tqdm import tqdm
from bs4 import BeautifulSoup



def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, 
            help="Path to the folder of the downloaded html")
    parser.add_argument('-o', '--output', required=True, 
            help="Output file path")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['input'] = args.input
    args_dict['output'] = args.output
    return args_dict
    



class HtmlExtractor:

    def __init__(self, inputpath, outputpath):
        self.filepaths = []
        self.inputpath = inputpath
        self.outputpath = outputpath


    def listhtml(self, startdir=None, recurse=False):
        indir = startdir if startdir is not None else self.inputpath
        filepaths = []
        if recurse: 
            for root, dirs, filenames in os.walk(indir):
                for filename in filenames:
                    if filename.endswith('.html'):
                        filepath = os.path.join(root, filename)
                        filepaths.append(filepath)
        else: 
            filepaths = [os.path.join(indir, path) for path in os.listdir(indir) if path.endswith('.html')]
        self.filepaths = filepaths
        return filepaths


    def extract_article(self, filepath):
        """
        how to parse an html page and return the format
        article = {
            "title": None,
            "date": None,
            "category": None,
            "text": None,
            "publisher": None,
        }
        """
        raise NotImplementedError()

    def extract_articles(self):
        with open(self.outputpath, "w") as csvfile:
            article_writer = csv.writer(csvfile)
            for filepath in tqdm(self.filepaths, desc="articles"):
                article = self.extract_article(filepath)
                if article is None: continue
                article_writer.writerow([
                    article['text'],
                    article['title'],
                    article['date'],
                    article['category'],
                    article['publisher'],
                    article['url'],
                ])


r = "/home/gr0259sh/Projects/data/abidjan.net/news.abidjan.net/articles"

    
if __name__ == "__main__":
    print(f"Input dir: {r}")
    filepaths = listhtml(r)
    print(f"no of filepaths: {len(filepaths)}")
    print(f"First filepath: {filepaths[0]}")
    #with open("abidjan.net.json", "w") as outfile:
    with open("abidjan.net.csv", "w") as csvfile:
        article_writer = csv.writer(csvfile)
        for filepath in tqdm(filepaths, desc="articles"):
            article = extract_article(filepath)
            article_writer.writerow([
                article['text'],
                article['title'],
                article['date'],
                article['category'],
                article['publisher'],
            ])
            #json_data = json.dumps(article)
            #csvfile.write(json_data)

    






