from bs4 import BeautifulSoup
from htmlextract import getargs, HtmlExtractor



class AsahiExtractor(HtmlExtractor):

    def extract_article(self, filepath):
        article = {
            "title": None,
            "date": None,
            "category": None,
            "text": None,
            "publisher": None,
            "url": None,
        }
        with open(filepath) as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            title_tgs = soup.find_all('div', {'class': 'Title'}) 
            if len(title_tgs) > 0:
                article['title'] = title_tgs[0].find('h1').get_text().strip()
                article['date'] = title_tgs[0].find('p', {'class': 'EnLastUpdated'}).get_text().strip()
            article_tg = soup.find('div', {'class': 'ArticleText'}) 
            if article_tg is not None:
                article['text'] = article_tg.get_text().strip()
            article['publisher'] = 'The Asahi Shimbun'
            article['url'] = 'https://www.asahi.com/ajw/articles/' + filepath.split('/')[-1]
        return article


if __name__ == "__main__":
    args = getargs()
    extractor = AsahiExtractor(args['input'], args['output'])
    extractor.listhtml()
    extractor.extract_articles()