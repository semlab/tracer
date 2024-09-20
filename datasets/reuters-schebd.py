import os
import re
import argparse
import csv
from bs4 import BeautifulSoup


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', required=True,
        help="Reuters dataset location")
    parser.add_argument('-o', '--output', required=True,
        help="output folder")
    parser.add_argument('-s', '--split', action='store_true',
        help="save output in different files")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['dataset'] = args.dataset
    args_dict['output'] = args.output
    args_dict['split'] = args.split
    return args_dict


def text_preproc(text):
    txt = text
    #txt = text.replace('\n', ' ')
    # Removing in text title
    title_delim = ' - '
    txtsp = txt.split(title_delim)
    txt = title_delim.join(txtsp[1:])
    # Removing the trailing 'Reuters
    # helps removing one sents article as well
    sent_delim = '.'
    txtsp = txt.split(sent_delim)
    txt = sent_delim.join(txtsp[:-1]) + sent_delim
    #txtsp = text.split('\n')
    #txt = '\n'.join(txtsp[:-2])
    #txt = '\n'.join(txtsp[:-1])
    #txt = text[:-6]
    return txt


def read_sgm(inputpath):
    sgm_lines = []
    with open(inputpath) as sgm_file:
        line_count = 0
        line = None 
        while line != "":
            try:
                line_count += 1
                line = sgm_file.readline()
                sgm_lines.append(line)
            except UnicodeDecodeError:
                print(f"Warning: line {line_count} of file '{inputpath}' cannot be decoded... skipped")
                continue
    sgm = '\n'.join(sgm_lines)
    return sgm



def filtered(article, char_count=None, excluded_topics=[]):
    """
    :param article: dictionary representing an aritcle
    """
    if char_count is not None and len(article['text']) < char_count:
        return False
    for excluded_topic in excluded_topics:
        if article['topic'] is not None and re.match(excluded_topic, article['topic']) is not None:
            return False
    return True


    

if __name__ == "__main__":
    args = getargs()
    filenames = [filename for filename in  sorted(os.listdir(args['dataset']))
        if filename.endswith(".sgm")]
    total_article_count = 0
    articles = []
    for filename in filenames:
        filepath = os.path.join(args['dataset'], filename)
        print(filepath)
        sgm = read_sgm(filepath)
        soup = BeautifulSoup(sgm, features='lxml')
        reuters_tags = soup.find_all('reuters')
        total_article_count += len(reuters_tags)
        for rt_tag in reuters_tags:
            article = {}
            article['id'] = rt_tag['newid']
            article['date'] = None if rt_tag.date is None else rt_tag.date.text
            text_tag = rt_tag.findChild('text')
            article['title'] = None if text_tag.title is None else text_tag.title.text.replace('\n','')
            article['text'] = text_tag.text if text_tag.body is None else text_tag.body.text
            article['topic'] = None if rt_tag.topics is None else rt_tag.topics.string
            article['file'] = filepath
            if not filtered(article, char_count=100, excluded_topics=['earn', 'money-supply']):
                continue #Skipped unfiltered article
            article['text'] = text_preproc(article['text'])
            if len(article['text']) > 50: # in case text is to short after preproc
                articles.append(article)
        # Output
        outputpath = os.path.join(args['output'], filename +'.csv')
        with open(outputpath, 'w')  as csvfile:
            article_writer = csv.writer(csvfile)
            # header
            article_writer.writerow([ 
                'NEWID', 'TEXT', 'TITLE', 'DATE', 'TOPIC', 'EXPLANATION', 'GRAPH'
            ])
            # content
            for article in articles:
                article_writer.writerow([
                    article['id'],
                    article['text'],
                    article['title'],
                    article['date'],
                    article['topic'],
                ])

