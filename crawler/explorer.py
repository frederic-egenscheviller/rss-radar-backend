import requests
from bs4 import BeautifulSoup
from shared.db import get_session
from shared.models import Rss, Item, Token
from datetime import datetime

class Explorer:

    @staticmethod
    def transformUrl(url):
        return url.split('//')[1].split('/')[0]

    @staticmethod
    def save_link(link):
        try:
            session = get_session()
            session.add(Rss(link, "A implémenter", "A implémenter", datetime.now().isoformat())).commit()
            session.close()
            return 1
        except :
            return 0

    def get_links(self):
        soup = BeautifulSoup(self.response, 'html.parser')
        link_tags = soup.find_all('link')
        links = [link.get('href') for link in link_tags if (link.get('href') and link.get('type') == "application/rss+xml")]
        session = get_session()
        links_in_db = [url[0] for url in session.query(Rss.url).filter(Rss.url.in_(links)).all()]
        print(set(links), set(links_in_db))
        valid_links = set(links) - set(links_in_db)
        session.close()
        if len(valid_links) > 1:
            for link in list(valid_links):
                Explorer.save_link(link)
            return list(valid_links)
        elif len(valid_links) == 1:
            Explorer.save_link(list(valid_links)[0])
            return list(valid_links)[0]
        else:
            return None

    def __init__(self, starturl, targeturl):
        self.starturl = Explorer.transformUrl(starturl)
        self.targeturl = Explorer.transformUrl(targeturl)
        self.next = None
        if self.targeturl != self.starturl:
            self.response = requests.get(targeturl, headers={"User-Agent": "curl/7.64.1"}).text
            self.next = self.get_links()

    def __str__(self):
        return self.next or ""

if __name__ == '__main__':
    # Pas de Rss sur celui ci
    A = Explorer("https://portail.basta.media/spip.php?page=backend", "https://www.ftm.eu/articles/how-brexit-failed-to-help-dying-fishing-industry")

    # Celui ci oui
    B = Explorer("https://portail.basta.media/spip.php?page=backend", "https://www.lemonde.fr/emploi/article/2024/05/29/l-ia-et-les-fantomes_6236120_1698637.html")

    # meme lien
    C = Explorer("https://portail.basta.media/spip.php?page=backend", "https://portail.basta.media/bite")

    # existe dans la db
    D= Explorer("https://portail.basta.media/spip.php?page=backend", "https://www.lemonde.fr/idees/article/2024/05/27/la-france-doit-assumer-une-ambition-industrielle-nationale-et-une-competitivite-intra-europeenne_6235873_3232.html")
    print("A = ", A, "B = ", B, " C = ",C, " D = ", D)
