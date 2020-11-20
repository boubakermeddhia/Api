import os
from flask import render_template, url_for, flash, redirect, request, abort,jsonify
from scrape import app,db
from scrape.forms import ScrapeForm
from scrape.models import data
import requests
from bs4 import BeautifulSoup

domains=''

def tohtml(x):
    return "<html>\n<head></head>\n<body>\n"+str(x)+"</html>"

@app.route("/getjobs",methods=['GET', 'POST'])
def home():
    if request.method=="GET":
        json_data = request.args
        page=int(json_data['page'])
        domain=str(json_data['domain'])
        if len(domain)!=0:
            posts = data.query.filter(data.domain==domain).paginate(page=page, per_page=5)
        else:   
            posts = data.query.order_by(data.id.desc()).paginate(page=page, per_page=5)
        l=[]
        for post in posts.items:
            l.append({'sys':post.id,'post_name': post.post_name.replace('\n',''),'href_company': post.href_company.replace('\n',''),
            'name_company':post.name_company.replace('\n',''),'location':post.location.replace('\n',''),'salary':post.salary.replace('\n',''),
            'href_post':post.href_post.replace('\n','')})
        return jsonify(l)


@app.route("/", methods=['GET', 'POST'])
@app.route("/scrape", methods=['GET', 'POST'])
def save():
    form = ScrapeForm()
    s=0
    if request.method=="POST":
        global domains
        domains=form.domain.data
        for i in range(0,5):
            if i==0:
                r = requests.get('https://www.indeed.com/jobs?q='+str(domains))
            else:
                r = requests.get('https://www.indeed.com/jobs?q='+str(domains)+'&start='+str(i*10))
                
            soup = BeautifulSoup(r.text,'html.parser')
            x=soup.find_all("div", class_="jobsearch-SerpJobCard unifiedRow row result")
            if len(x)==0:
                flash('Please verify your entry', 'warning')
                return redirect(url_for('save'))
            if 1==1 :
                for j in x:
                   y=BeautifulSoup(tohtml(j), 'html.parser')
                if y.find("h2", class_="title") is not None :
                   a=y.find("h2", class_="title").get_text()#name_post
                else:
                   a=''
                if y.find("a", class_="turnstileLink") is not None :
                   v="https://www.indeed.com"+y.find_all("a",class_="turnstileLink")[0]['href']#href_post
                   z=requests.get(v)
                   if (z.status_code==200):
                      if BeautifulSoup(z.text, 'html.parser').find("a") is not None:
                        if len(BeautifulSoup(z.text, 'html.parser').find_all("a", class_="icl-Button--block"))!=0:
                            b=BeautifulSoup(z.text, 'html.parser').find_all("a", class_="icl-Button--block")[0]['href']
                        else:
                            b=''
                      else:
                         b=''
                   else:
                         b=''
                else:
                    b=''
                if BeautifulSoup(tohtml(y.find("span", class_="company")), 'html.parser').find("a") is not None :
                    c=BeautifulSoup(tohtml(y.find("span", class_="company")), 'html.parser').find("a").get_text()#name_company
                else:
                    c=''
                if BeautifulSoup(tohtml(y.find("span", class_="company")), 'html.parser').find("a") is not None:
                    n=requests.get("https://www.indeed.com"+BeautifulSoup(tohtml(y.find("span", class_="company")), 'html.parser').find("a")['href'])#href_company
                    if (n.status_code==200):
                      if BeautifulSoup(n.text, 'html.parser').find("a") is not None:   
                        if len(BeautifulSoup(n.text, 'html.parser').find_all("a", class_="cmp-CompanyLink"))!=0 :
                         m=BeautifulSoup(n.text, 'html.parser').find_all("a", class_="cmp-CompanyLink")[0]['href']
                        else:
                         m=''
                      else:
                         m=''
                    else:
                         m=''
                else:
                    m=''
                if y.find("span", class_="location") is not None :
                    e=y.find_all("span", class_="location")[0].get_text()#location
                else:
                    e=''
                if y.find("span", class_="salary") is not None:
                    f=y.find_all("span", class_="salary")[0].get_text()#salary
                else:
                    f=''
                    
                try:
                    donnee=data(domain=str(domains),post_name=str(a),href_post=str(b),name_company=str(c),href_company=str(m),location=str(e),salary=str(f),verif=str(v))
                    db.session.add(donnee)
                    db.session.commit()
                    s=s+1
                except:
                    pass
                   
        flash('Scrape is finished '+str(s)+' new added in '+str(domains)+' feed', 'success')
        return redirect(url_for('home',page=1,domain=domains))
    return render_template('scrape.html', form=form)


@app.route("/deljob/<int:n>", methods=['GET', 'POST'])
def deljob(n):
    posts = data.query.filter(data.id==n).delete()
    db.session.commit()
    return redirect(url_for('home',page=1,domain=domains))


