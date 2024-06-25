from sqlalchemy.orm import Session
from .models import Page, SessionLocal

class Storage:
    def __init__(self):
        self.db = SessionLocal()

    def save_page(self, url, content):
        existing_page = self.get_page_by_url(url)
        if existing_page:
            print(f"URL já existe no banco de dados: {url}")
            return existing_page
        
        page = Page(url=url, content=content, crawled=True)
        self.db.add(page)
        self.db.commit()
        self.db.refresh(page)
        return page

    def get_all_pages(self):
        return self.db.query(Page).all()

    def get_page_by_url(self, url):
        return self.db.query(Page).filter(Page.url == url).first()

    def get_status(self):
        total_pages = self.db.query(Page).count()
        crawled_pages = self.db.query(Page).filter(Page.crawled == True).count()
        return {"total_pages": total_pages, "crawled_pages": crawled_pages}

    def clear_all_pages(self):
        self.db.query(Page).delete()
        self.db.commit()
        