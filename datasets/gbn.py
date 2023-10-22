from bs4 import BeautifulSoup
from htmlextract import getargs, HtmlExtractor



class GBNExtractor(HtmlExtractor):

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
            try:
                soup = BeautifulSoup(fp, 'html.parser')
            except UnicodeDecodeError:
                print(f'Could not read {filepath}')
                return None
            article_tg = soup.find('article')
            if article_tg is None:
                return None
            title_tg = article_tg.find('div', {'class': 'post-header-title'})
            if title_tg is not None:
                try:
                    article['category'] = title_tg.find('a').get_text().strip()
                    article['title'] = title_tg.find('h1').get_text().strip()
                    article['date'] = title_tg.find('time').b.get_text().strip()
                except AttributeError:
                    print(f'Malform title for {filepath} ')
            article_text_tg = article_tg.find('div', {'class': 'entry-content clearfix single-post-content'})
            if article_text_tg is None:
                return None
            article['text'] = article_text_tg.get_text().strip()
            article['publisher'] = 'Ghana Business News'
            filepath_sp = filepath.split('/')
            if len(filepath_sp) > 5:
                article['url'] = '/'.join(filepath_sp[-6:-1])
        return article




if __name__ == "__main__":
    args = getargs()
    extractor = GBNExtractor(args['input'], args['output'])
    extractor.listhtml(recurse=True)
    extractor.extract_articles()