from codecs import getdecoder
import json
from textwrap import wrap
import GetDistance
from re import T
from typing import Dict, List
import ProbabilityRatingModel as prm
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import time
import QuickSelect as qs

def getCategories(data:List[dict]):
    """
    Returns top 30 categories to display. based on number of restaurants in category
    not inclusive of 'dining and drinking' and 'restaurant' categories
    Uses quickSelect
    """

    excludes=set(['dining and drinking','restaurant'])
    cat={}
    for d in data:
        if not 'fsq_category_labels' in d:
            continue
        catSet=set()
        for cats in d['fsq_category_labels']:
            for c in cats:
                c = c.lower()
                if c in excludes:
                    continue
                if c not in catSet:
                    catSet.add(c)
                    if not c in cat:
                        cat[c]=1
                    else:
                        cat[c]+=1
    QS=qs.QuickSelect([{'category':c,'count':cat[c]} for c in cat],'count',False)
    return [d['category'] for d in QS.GetNextN(30)]

def getCategoriesDict(data:List[dict]):
    """
    Returns dictionary with key as food category in lowercase
    and value as a list of objects belonging to category
    eg.
    {
        'japanese':[{obj1},{obj2}...]
        'american'
    }
    """

    cat={}
    for d in data:
        if not 'fsq_category_labels' in d:
            continue
        dCats = d['fsq_category_labels']
        catSet=set()
        for dCat in dCats:
            for c in dCat:
                food=c.lower()
                if food not in catSet:
                    catSet.add(food)
                    if not food in cat:
                        cat[food]=[d]
                    else:
                        cat[food].append(d)
    return cat

def simplifyData(data:List[dict],location:List[float], rating_weight,  price_weight,  distance_weight):
    """
    Makes the data leaner
    Adds an additional recommendation_value
    and calculated distance field
    only includes fields:
    id
    categories
    coordinates
    rating
    name
    review_count
    price
    """ 
    output=[]
    for d in data:
        obj={}
        obj['fsq_id']=d['fsq_id']
        obj['name']=d['name']
        obj['fsq_category_labels']=d['fsq_category_labels']
        cat = set()
        for cats in d['fsq_category_labels']:
            for c in cats:
                c=c.lower()
                if c not in cat:
                    cat.add(c)
        obj['category'] = cat
        if 'latitude' not in d:
            continue
        obj['latitude']=float(d['latitude'])
        obj['longitude']=float(d['longitude'])
        rating,price=None,None
        if 'address' in d:
            obj['address'] = d['address']
            if 'address_extended' in d:
                obj['address'] = obj['address'] + ', ' + d['address_extended']
        else:
            obj['address'] = 'NA'
        if 'price' in d:
            price=d['price']
            obj['price'] = price
            obj['display_price']= d['price'] * "$"
        else:
            obj['price'] = 0
            obj['display_price']= 'NA'
        if 'rating' in d:
            obj['rating']=float(d['rating'])
        if "total_tips" in d:
            obj['total_tips']=int(d['total_tips'])
        if "total_photos" in d:
            obj['total_photos']=d['total_photos']
        if 'rating' in d and 'total_tips' in d:
            rating=prm.exponential(obj['total_tips'],obj['rating'])
            obj['ratingAdjusted']=rating
        if location:
            if (obj['latitude'] and obj['longitude']):
                distance=GetDistance.GetDistanceFromCoordinates(location,[obj['latitude'],obj['longitude']])
                obj['distance']= distance
            else:
                obj['distance']=-1
        else:
            obj['distance']=-1
        obj['recommendation']=prm.weighted(rating,rating_weight,price,price_weight,distance,distance_weight)
        output.append(obj)    
    return output

def changeLocation(data:List[Dict],location:List[float]=None):
    for obj in data:
        obj['distance']=GetDistance.GetDistanceFromCoordinates(location,[obj['latitude'],obj['longitude']]) 
def changeWeights(data:List[Dict], rating_weight,  price_weight,  distance_weight):
    for obj in data:
        rating,price,distance=None,None,None
        if 'ratingAdjusted' in obj:
            rating=obj['ratingAdjusted']
        if 'price' in obj:
            price=obj['price']
        if 'distance' in obj:
            distance=obj['distance']
        obj['recommendation']=prm.weighted(rating,rating_weight,price,price_weight,distance,distance_weight)
def filterDataByFieldAndValue(data:List[Dict],field:str,value):
    """
    filters data by field value
    """
    value=str(value).lower()
    field=field.lower()
    output=[]
    for d in data:
        if not field in d:
            continue
        if str(d[field]).lower()==value:
            output.append(d)
    return output

def filterDataByFieldAndValueRange(data:List[Dict],field:str,valueRange):
    """
    filters data by field and value range
    valueRange to be in a List of 2 values, 
    First item being the start of the Range,
    Second value being the End of the range
    """
    field=field.lower()
    output=[]
    for d in data:
        if not field in d:
            continue
        if d[field]>=valueRange[0] and d[field]<=valueRange[1]:
            output.append(d)
    return output    

def getMultipleFoodCategories(data:List[Dict],categories:List[str]):
    """
    Get entries which are part of a desired list of categories
    """
    cats=set(categories)
    output=[]
    for d in data:
        chosen=False
        for c in d['category']:
            if c.lower() in cats:
                chosen=True
        if chosen:
            output.append(d)
    return output
    
def filterVisited(data:List[Dict], visited:List[str]):
    cats=set(visited)
    output=[]
    for d in data:
        if d['name'] not in cats:
            output.append(d)
    return output


def filterDataByFieldsAndValueRanges(data:List[Dict],fields:List[str],valueRanges):
    """
    filters data by field and value range
    valueRange to be in a List of 2 values, 
    First item being the start of the Range,
    Second value being the End of the range
    """
    output=[]
    for d in data:
        toInclude=True
        for i,field in enumerate(fields):
            if not field in d:
                toInclude=False
                break
            field=field.lower()
            if d[field]<valueRanges[i][0] or d[field]>valueRanges[i][1]:
                toInclude=False
        if toInclude:
            output.append(d)
    return output 



def showExample():
    dir="singaporeFnBAll.json"
    f=open(dir,encoding='utf-8')
    data=json.load(f)
    f.close()
    
    #cat=getCategories(data)
    start=time.time()
    sd=simplifyData(data,[1.356007600303024, 103.83149240724738],1,2,3)
    end=time.time()
    print("simplifyData time taken = {0}".format(end-start) )

    start=time.time()
    changeLocation(sd,[1.456007600303024, 103.83149240724738])
    end=time.time()
    print("changeLocation time taken = {0}".format(end-start) )

    start=time.time()
    changeLocation(sd,[1.456007600303024, 106.83149240724738])
    end=time.time()
    print("changeLocation time taken = {0}".format(end-start) )

    start=time.time()
    changeWeights(sd,3,2,1)
    end=time.time()
    print("changeWeights time taken = {0}".format(end-start) )
    start=time.time()
    changeWeights(sd,3,2,1)
    end=time.time()
    print("changeWeights time taken = {0}".format(end-start) )
    # caf=cat['casino']
    #print(filterDataByFieldAndValue(caf,"price","$"))
    # foods = getMultipleFoodCategories(data,categories=['pizza','italian'])
    #[print(f['name'],f['categories']) for f in foods]
    # filtered=filterDataByFieldsAndValueRanges(data,['rating','price'],[[3.0,5.0],[2,3]])
    #[print (f['name'],'price :',f['price'],'rating :',f['rating']) for f in filtered]
    #[print(c['name'],c['price']) for c in filterDataByFieldAndValueRange(caf,"price",[1,3])]
    #[print(c['name'],c['distance']) for c in filterDataByFieldAndValueRange(caf,"distance",[0,2000])]
def CheckCategories():
    dir="singaporeFnBAll.json"
    f=open(dir,encoding='utf-8')
    data=json.load(f)
    data=simplifyData(data,[1.356007600303024, 103.83149240724738],1,2,3)

    f.close()
    print(len(data))
    cat=getCategoriesDict(data)
    
    df=pd.DataFrame([[c.strip(),len(cat[c])] for c in cat],index=cat.keys(),columns=['Name','Count'])
    df=df.sort_values(by=['Count'],ascending=False)
    # print(df)
    # df.plot.bar(x='Name',y='Count',rot=0)
    df=df.drop(['dining and drinking','restaurant'])
    df=df.head(30)
    uniqueSet=set()
    for c in df.index:
        print(c)
        for obj in cat[c]:
            if obj['fsq_id'] not in uniqueSet:
                uniqueSet.add(obj['fsq_id'])
    print(len(uniqueSet))
    print(df.sum())
    top30 =getCategories(data)
    print(top30)
    print(len(top30))
    fig, ax = plt.subplots()
    x=np.arange(len(df['Count']))
    ax.bar(x,df['Count'])
    plt.xticks(x,[name.replace(' ','\n') for name in df['Name']],wrap=True,fontsize=7)
    # plt.show()
#CheckCategories()