import json
import csv
import requests
from ratelimit import limits, sleep_and_retry

jwt_token = None
headers = {}
ingame_name = None
WFM_API = "https://api.warframe.market/v1/"

@sleep_and_retry
@limits(calls=3, period=1.2)
def get_request(url):
    """Executes a wfm query"""
    request = requests.get(WFM_API + url, stream=True)
    if request.status_code == 200:
        return request.json()["payload"]
    return None


def filterrelic(input,rarity):
    sell=[]
    buy=[]
    k=0
    for i in input:
#        print(k)
        if i["order_type"]=='sell' and i["platform"]=='pc' and i["subtype"]==rarity and i['user']['status'] == 'ingame':
            sell.append(i)
        elif i["order_type"]=='buy' and i["platform"]=='pc'and i["subtype"]==rarity and i['user']['status'] == 'ingame':
            buy.append(i)
        k=k+1
    return sell,buy

def filter(input):
    sell=[]
    buy=[]
    k=0
    for i in input:
#        print(k)
        if i["order_type"]=='sell' and i["platform"]=='pc' and i['user']['status'] == 'ingame':
            sell.append(i)
        elif i["order_type"]=='buy' and i["platform"]=='pc'and i['user']['status'] == 'ingame':
            buy.append(i)
        k=k+1
    return sell,buy

def pricing(sell,buy):
    sellprice=99999
    for i in sell:
        if i['platinum'] < sellprice:
            sellprice=i['platinum']
        else:
            continue
    buyprice = 0
    for i in buy:
        if i['platinum'] > buyprice:
            buyprice = i['platinum']
        else:
            continue
#    print('Sell price is '+str(sellprice)+' Buy price is '+str(buyprice))
#    profit=sellprice-buyprice
    return sellprice,buyprice

def getitems():
    request= requests.get(WFM_API+'items',stream=True)
    if request.status_code == 200:
        request= request.json()['payload']['items']
        items=[]
        itemname=[]
        for i in request:
            items.append(i['url_name'])
            itemname.append(i['item_name'])
    return items,itemname
        
    

def getdata(url,itemname):
    request = requests.get(WFM_API + url, stream=True)
    writer = csv.writer(f)
    f=open('DATA.csv', 'a', encoding='UTF8', newline='')
#    print(request.json())
    if request.status_code == 200:
        data=request.json()['payload']
        data=data['orders']
        if 'subtype' in data[0]:
            f
        else:
            sell,buy = filter(data)
            profit=pricing(sell,buy)
    elif request.status_code == 503:
        profit=getdata(url)
    elif request.status_code == 429:
        profit=getdata(url)
    else:
        profit='ERROR Status Code: '+str(request.status_code)
    f.close()
    return profit


def main():
    items,itemname=getitems()
    print(items)
    print(itemname)
    i=0
    open('DATA.csv', 'w', encoding='UTF8', newline='')
    while i < len(items):
        url='/items/'+items[i]+'/orders'
        profit=getdata(url,itemname[i])
        print('Profit of '+itemname[i]+' is '+str(profit))
        writer.writerow([itemname[i],profit])
        i=i+1
        print(str(i)+'/'+str(len(items)))
#            print(i)
    return

#main()

def appraiseitem(url):
    request = requests.get(WFM_API + url, stream=True)
#    print(request.json())
    if request.status_code == 200:
        data=request.json()['payload']
        data=data['orders']
        sell,buy = filter(data)
        sellprice,buyprice=pricing(sell,buy)
    elif request.status_code == 503:
        sellprice,buyprice=appraiseitem(url)
    elif request.status_code == 429:
        sellprice,buyprice=appraiseitem(url)
    else:
        sellprice='ERROR Status Code: '+str(request.status_code)
        buyprice='ERROR Status Code: '+str(request.status_code)
    return sellprice,buyprice

def appraiserelic(url,rarity):
    request = requests.get(WFM_API + url, stream=True)
#    print(request.json())
    if request.status_code == 200:
        data=request.json()['payload']
        data=data['orders']
        sell,buy = filterrelic(data,rarity)
        sellprice,buyprice=pricing(sell,buy)
    elif request.status_code == 503:
        sellprice,buyprice=appraiserelic(url,rarity)
    elif request.status_code == 429:
        sellprice,buyprice=appraiserelic(url,rarity)
    else:
        sellprice='ERROR Status Code: '+str(request.status_code)
    return sellprice,buyprice


def relicrun(rewards,items,itemsname,rarity):
    averagesolo=0
    average4b4=0
    rewnames=[]
    for r in rewards:
        rewnames.append(r['itemName'])
    if rarity=='intact':
        for r in rewards:
            if r['itemName']=='Forma Blueprint':
                continue
            elif r['rarity']=='Common':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.689
            elif r['rarity']=='Uncommon':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.372
            elif r['rarity']=='Rare':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.078
    if rarity=='exceptional':
        for r in rewards:
            if r['itemName']=='Forma Blueprint':
                continue
            if r['rarity']=='Common':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.654
            if r['rarity']=='Uncommon':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.427
            if r['rarity']=='Rare':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.151
    if rarity=='flawless':
        for r in rewards:
            if r['itemName']=='Forma Blueprint':
                continue
            if r['rarity']=='Common':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.59
            if r['rarity']=='Uncommon':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.525
            if r['rarity']=='Rare':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.219
    if rarity=='radiant':
        for r in rewards:
            if r['itemName']=='Forma Blueprint':
                continue
            if r['rarity']=='Common':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.518
            if r['rarity']=='Uncommon':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.591
            if r['rarity']=='Rare':
                url= 'items/' + str(items[itemsname.index(r['itemName'])] +'/orders')
                price,buyprice=appraiseitem(url)
                averagesolo=averagesolo+int(price)*int(r['chance'])*0.01
                average4b4=average4b4+price*0.344
    return averagesolo,average4b4,rewnames

        

#DO RELIC APPRAISAL
#RELIC AVG PLAT WORKED OUT, NEED TO WORK OUT RELIC COST






def relicscan():
    f=open('relics_rad.csv', 'w', encoding='UTF8', newline='')
    writer = csv.writer(f)
    writer.writerow(['Tier','Relic','Refinement','Sell price','Buy Price','Solo','4B4','Profit Solo','Profit 4B4','Reward 1','Reward 2','Reward 3','Reward 4','Reward 5','Reward 6'])
    f.close()
    items, itemsname=getitems()
    print("Updating relic database.")
    url = "https://drops.warframestat.us/data/relics.json"
    relic_list = requests.get(url, stream=True)
    if relic_list.status_code != 200:
        return
    relic_list = relic_list.json()["relics"]
    i=0
    relic_rad=[]
    for relic in relic_list:
        if relic['state'].lower() == 'radiant':
            relic_rad.append(relic)
        else:
            continue
    for relic in relic_rad:
        i=i+1
        f=open('relics_rad.csv', 'a', encoding='UTF8', newline='')
        writer = csv.writer(f)
        tier=relic['tier'].lower()
        name=relic['relicName'].lower()
        rarity=relic['state'].lower()
        if rarity=='radiant':
            relicurl = 'items/'+tier+'_'+name+'_relic/orders'
            sell,buy=appraiserelic(relicurl,rarity)
            avgsolo, avg4b4, rewnames =relicrun(relic['rewards'],items,itemsname,rarity)
            writer.writerow([tier,name,rarity,sell,buy,avgsolo,avg4b4,str(avgsolo-sell),str(avg4b4-sell),rewnames[0],rewnames[1],rewnames[2],rewnames[3],rewnames[4],rewnames[5]])
            f.close()
            print('['+str(i)+'/'+str(len(relic_rad))+'] '+tier+' '+name+' '+rarity+' sell buy is '+str(round(sell,3))+' '+str(round(buy,3))+ ' avgsolo avg4b4 is '+str(avgsolo)+' '+str(avg4b4))
        else:
            continue   
relicscan()