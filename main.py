import streamlit as st
import requests
import xml.etree.ElementTree as et
import sqlitecloud
from datetime import datetime

def trendgetir(ulke="TR"):
    r=requests.get(f'https://trends.google.com/trending/rss?geo={ulke}')
    kod=r.status_code
    if kod==200:
        veri=r.content
        veri=et.fromstring(veri)
        trendler=[]
        for i in veri.findall('channel/item'):
            title=i[0].text
            trafik=int(i[1].text.replace("+",""))
            haberler=[]
            for etiket in i:
                if "news_item" in etiket.tag:
                    newsitem={}
                    newsitem['title']=etiket[0].text
                    newsitem['url']=etiket[2].text
                    newsitem['resim']=etiket[3].text
                    newsitem['kaynak']=etiket[4].text
                    haberler.append(newsitem)
            trend={}
            trend['title']=title
            trend['trafik']=trafik
            trend['haberler']=haberler
            trendler.append(trend)

        return trendler
    else:
        return False

def trendekle(title,trafik):
  conn = sqlitecloud.connect("sqlitecloud://csdz1faahz.g5.sqlite.cloud:8860/chinook.sqlite?apikey=cZNvIFXRt8qCFlOrDDSeJ4L3yi9PCW8badUKIsxo1IA")
  c=conn.cursor()

  c.execute('SELECT rowid * FROM trendler WHERE title=?',(title,))
  say=c.fetchone()
  if len(say)==0:
    simdi=str(datetime.now())
    c.execute('INSERT INTO trendler VALUES(?,?,?)',(title,trafik,simdi))
    id=c.lastrowid
    conn.commit()
    return id
  else:
    trend=c.fetchone()
    return trend[0]

def haberekle(trend,title,url,resim,kaynak):
  conn = sqlitecloud.connect("sqlitecloud://csdz1faahz.g5.sqlite.cloud:8860/chinook.sqlite?apikey=cZNvIFXRt8qCFlOrDDSeJ4L3yi9PCW8badUKIsxo1IA")
  c=conn.cursor()

  c.execute('SELECT * FROM haberler WHERE url=?')


conn = sqlitecloud.connect("sqlitecloud://csdz1faahz.g5.sqlite.cloud:8860/chinook.sqlite?apikey=cZNvIFXRt8qCFlOrDDSeJ4L3yi9PCW8badUKIsxo1IA")
c=conn.cursor()

c.execute('CREATE TABLE IF NOT EXISTS trendler(title TEXT, trafik INTEGER,tarih TEXT)')
conn.commit()

c.execute('CREATE TABLE IF NOT EXISTS haberler(trend INTEGER,title TEXT,url TEXT,resim TEXT,kaynak TEXT,tarih INTEGER)')
conn.commit()

trendler = trendgetir()
for t in trendler:
    id = trendekle(t['title'], t['trafik'])
    haberler = t['haberler']
    for h in haberler:
        haberekle(id, h['title'], h['url'], h['resim'], h['kaynak'])

c.execute('SELECT trend,title,kaynak,tarih haberler LIMIT 100')
sonuc=c.fetchall()()

st.table(sonuc)
