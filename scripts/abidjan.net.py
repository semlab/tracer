import os
#import json
import csv
from tqdm import tqdm
from bs4 import BeautifulSoup



def listhtml(startdir):
    filepaths = []
    for root, dirs, filenames in os.walk(startdir):
        for filename in filenames:
            if filename.endswith('.html'):
                filepath = os.path.join(root, filename)
                filepaths.append(filepath)
    return filepaths


def extract_article(filepath):
    article = {
        "title": None,
        "date": None,
        "category": None,
        "text": None,
        "publisher": None,
    }
    with open(filepath) as fp:
        soup = BeautifulSoup(fp, 'html.parser')
        article_tg = soup.find('article')
        # the title
        article["title"] = article_tg.find("h1").get_text().strip()
        # the text
        texts = article_tg.find_all("div", {"class":"txt"})
        text = texts[0].get_text() #text[0].string
        article["text"] = text.strip()
        # pub date
        pubdates = article_tg.find_all("span", {"class": "date"})
        pubdate = pubdates[0].get_text()
        pubdate_sp = pubdate.split('|')
        pdate = pubdate_sp[0].strip()
        pdate = " ".join(pdate.split()[3:]) # removing "Publie le "
        article["date"] = pdate # TODO Convert to ISO date
        if len(pubdate_sp) > 1:
            article["publisher"] = pubdate_sp[1].strip()
        # Categorie
        categories = article_tg.find_all("a", {"class": "cat"})
        article["category"] = categories[0].get_text().strip()
    return article

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

    


