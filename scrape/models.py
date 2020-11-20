from datetime import datetime
from scrape import db


class data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    domain=db.Column(db.String(120))
    post_name = db.Column(db.String(120))
    href_post = db.Column(db.String(120))
    name_company = db.Column(db.String(120))
    href_company = db.Column(db.String(120))
    location=db.Column(db.String(120))
    salary=db.Column(db.String(120))
    verif=db.Column(db.String(120),unique=True)
    

    def __repr__(self):
        return "data('{0}', '{1}', '{2}')".format(self.post_name,self.href_post,self.href_company)


