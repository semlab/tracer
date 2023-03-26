import os
import argparse
import csv
from bs4 import BeautifulSoup


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', required=True
        help="Reuters dataset location")
    parser.add_argument('-o', '--output', required=True,
        help="csv output file")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['dataset'] = args.dataset
    args_dict['output'] = args.output
    return args_dict


def text_preproc(text):
    # TODO process text
    return text


if __name__ == "__main__":
    args = getargs()
    filepaths = [filepath in  sorted(os.listdir(args['dataset']))
        if filepath.endswith(".sgm")]
    for filepath in filepaths:
        articles = []
        skipped_count = 0
        try:
            soup = BeautifulSoup(open(filepath), features='lxml')
            reuters_tags = soup.find_all('reuters')
            for reuters_tag in reuters_tags:
                article = {}
                article['date'] = reuters_tag.date.string
                article['title'] = reuters_tag.text.title.string
                article['text'] = reuters_tag.text.body.string
                article['text'] = text_preproc(article['text'])
                article['category'] = reuters_tag.topics.string
                article['file'] = filepath
            articles.append(article)
        except:
            skipped_count += 1
            continue
    with open('outputpath', 'w')  as csvfile:
        article_writer = csv.writer(csvfile)
        for article in articles:
            article_writer.writerow([
                article['text'],
                article['title'],
                article['date'],
                article['category'],
            ])


