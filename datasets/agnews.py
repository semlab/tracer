# Intended to simplify the original AGNews file

import csv


def getargs():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dataset', required=True,
        help="AGNews dataset file location")
    parser.add_argument('-o', '--output', required=True,
        help="csv output file")
    args = parser.parse_args()
    args_dict = dict()
    args_dict['dataset'] = args.dataset
    args_dict['output'] = args.output
    return args_dict


def process_article(article_entry):
    article = {}
    article_parts = article_entry.split('\t')
    article['source'] = article_parts[0]
    article['link'] = article_parts[1]
    article['title'] = article_parts[2]
    article['image'] = article_parts[3]
    article['category'] = article_parts[4]
    article['text'] = article_parts[5]
    article['rank'] = article_parts[6]
    article['date'] = article_parts[7]
    article['video'] = None
    return article



if __name__ == "__main__":
    filepath = "../../data/newsSpace"
    articles = []
    with open(filepath, 'r', encoding='latin-1') as datafile:
        content = datafile.read()
        articles = content.split('\\N')
        print(len(articles))
    for idx, entry in enumerate(articles):
        article = process_article(entry)
        print(article['title'])
        if idx >=5:
            break
        