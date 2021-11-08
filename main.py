import json
from shutil import copyfile

import requests
from bs4 import BeautifulSoup

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

RECHERCHE = "category=2&text=lamborghini&price=400000-max"
URL = f"https://www.leboncoin.fr/recherche?{RECHERCHE}"

headers = {"User-Agent": "Mozilla/6.0 (X11; Ubuntu; Linux x86_64; rv:88.0) Gecko/20100101 Firefox/88.0"}

response = requests.get(URL, headers=headers)
response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")
json_content = soup.find("script", {"type":"application/json"}).string
datas = json.loads(json_content)

items = datas["props"]["pageProps"]["searchData"]["ads"]

# we write in a file to compare with the old one and see if there is a new post
with open("datas_le_bon_coin.json", mode="w") as f:
    json.dump(datas, f)
message = ''
nbtitre = 1
for item in items:
    if item["url"] in open('old_datas_le_bon_coin.json').read(): #Check if there is a new post
        break
    else:
        print("Titre:", item["subject"])
        print("Lien:", item["url"])
        try:
            print("Prix:", item["price"][0], "€")
        except:
            print('Prix non indiqué')
        #The body of the mail
        message = message + ''.join(item["subject"])
        message = message + '<br>'
        message = message + ''.join(item["url"])
        message = message + '<br>'
        message = message + ''.join(item["price"][0])
        message = message + '-' * 50
        nbtitre = nbtitre + 1 #The numbers of posts

        #The mail addresses and password
        sender_address = 'your.mail@protonmail.com'
        sender_pass = 'thepassword'
        receiver_address = 'your.mail@protonmail.com' 
        #Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = receiver_address
        message['Subject'] = str(nbtitre)+"Leboncoin - My first car"   #The subject line
        #The body and the attachments for the mail
        message.attach(MIMEText(message, 'plain'))
        #Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587) #use gmail with port
        session.starttls() #enable security
        session.login(sender_address, sender_pass) #login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, receiver_address, text)
        session.quit()
copyfile("datas_le_bon_coin.json", "old_datas_le_bon_coin.json")
