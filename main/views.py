from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
import pandas as pd
import numpy as np
import os
import ast
import nltk
from nltk.stem.porter import PorterStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import wordnet
nltk.download('wordnet')
import requests
import io
from PIL import Image
import PIL
import json

def home(response):
    return render(response, "main/home.html", {})

def movies(response):
    movie_imagepath_dict = {}    
    recommended_movies_list = []     
    if response.method == 'POST':
        print("inside POST method")
        alldata = response.POST
        print(alldata)
        movienames = alldata.getlist('user_movies[]')
        for movie in movienames:
            if movie == '':
                print("ERROR! NULL MOVIE NOT ALLOWED")
        
        model_movies_df = pd.read_csv(r"./main/static/main/database/5000_records_movies.csv",converters={'genres' : list,'overview':list,'keywords':list,'cast':list,'crew':list}) 
        if len(movienames) == 1:
            sorted_movie_list = single_movie_recommendation(model_movies_df,movienames[0],16,'single')           
            for i in sorted_movie_list:
                recommended_movies_list.append(" ".join(model_movies_df[model_movies_df['movie_id']==i[0]].title.tolist()))
            print(recommended_movies_list)            
        else:
            recommended_movies_list = multiple_movie_recommendation(model_movies_df,movienames) 
            print(recommended_movies_list) 
        #get images
        name_image_dict = name_to_image(model_movies_df,recommended_movies_list)
        movie_imagepath_dict = get_image_files(name_image_dict)    
        print(movie_imagepath_dict)
        print(os.getcwd())
        with open("D:\entipwebsite\src\main\static\main\database\movie_imagepath.json", "w") as outfile:
            json.dump(movie_imagepath_dict, outfile)
        'main/images/18.png'
        '''for v in movie_imagepath_dict.values():
            v = v.replace('/','\\')
            v = 'D:\entipwebsite\src\main\static\\'+v
            print('remove file path',v)
            os.remove(v)'''
        
    else:  
        print("refresh")
        file_exists = os.path.exists("D:\entipwebsite\src\main\static\main\database\movie_imagepath.json")
        if file_exists:
            with open("D:\entipwebsite\src\main\static\main\database\movie_imagepath.json",) as json_file:
                movie_imagepath_dict = json.load(json_file)
            if movie_imagepath_dict:
                for v in movie_imagepath_dict.values():
                    v = v.replace('/','\\')
                    v = 'D:\entipwebsite\src\main\static\\'+v
                    print('remove file path',v)
                    os.remove(v)
            movie_imagepath_dict = {}
            with open("D:\entipwebsite\src\main\static\main\database\movie_imagepath.json", "w") as outfile:
                json.dump(movie_imagepath_dict, outfile)
                    
       
    return render(response,"main/movies.html", {"recommendedmovieslist":recommended_movies_list,"movie_imagepath_dict":movie_imagepath_dict})
    
def single_movie_recommendation(model_movies_df,moviename,headnum,flag):
    if flag == 'multiple':
        model_movies_df['tags'] = model_movies_df['genres'] + model_movies_df['keywords']
    if flag == 'single':
        model_movies_df['tags'] = model_movies_df['overview'] + model_movies_df['genres'] + model_movies_df['keywords'] + model_movies_df['cast'] + model_movies_df['crew']
    
    df = model_movies_df[['movie_id','title','tags','vote_average','popularity']]
    
    df['tags'] = df['tags'].apply(lambda x: "".join(x))
    df['tags'] = df['tags'].apply(lambda x: x.lower())    
    df['tags'] = df['tags'].apply(stem)
    cvobj = CountVectorizer(max_features=6000, stop_words='english')
    vectors = cvobj.fit_transform(df['tags']).toarray()    
    similarity = cosine_similarity(vectors)
    movie_index = df[df['title']==moviename].index[0]   
    distances = similarity[movie_index]

    recommendedlist = sorted(list(enumerate(distances)),reverse=True, key=lambda x:x[1])[1:headnum]
    imdbrecommendedlist = []

    for i in recommendedlist: 
        i = list(i)
        i.append(df.iloc[i[0]]['vote_average'])   
        i[0] = df.iloc[i[0]]['movie_id']
        imdbrecommendedlist.append(i)

    roundimdblist = []
    for i in imdbrecommendedlist:
        roundimdblist.append([i[0],round(i[1],2),i[2]])
    return sorted(roundimdblist, reverse = True, key = lambda x: (x[1],x[2]))

def synonym(word):
    synonyms = []
    for syn in wordnet.synsets(word):
        for l in syn.lemmas():
            synonyms.append(l.name())
    return synonyms

def stem(text):
    psobj = PorterStemmer()
    temp = []
    for i in text.split():
      temp.append(psobj.stem(i))
    return " ".join(temp)

def functolist(lst):
  return " ".join(lst)

def multiple_movie_recommendation(df,multiplemovielist):
    print("mulitple movie list",multiplemovielist)
    firstlevellist = []
    for i in multiplemovielist: 
        firstlevellist.extend(single_movie_recommendation(df,i,40,'multiple'))
    movie_id_of_users_input_list = []   
    tag_of_users_input_list = []
    for movie in multiplemovielist:
        idofmovie = df[df['title']==movie]['movie_id'].item()
        movie_id_of_users_input_list.append(idofmovie)
        tag_of_users_input_list.append(stem(" ".join(df[df['movie_id']==idofmovie]['tags'].item())))   
    movie_id_of_firstlevellist_movies = []
    for i in firstlevellist:
        movie_id_of_firstlevellist_movies.append(i[0])
    new_df = df[ df['movie_id'].isin(movie_id_of_firstlevellist_movies)] 
    new_df['tags'] = new_df['tags'].apply(functolist)
    new_df['tags'] = new_df['tags'].apply(stem)

    counterobjlist = []
    newmovielist = []

    for indicer in range(len(new_df)):     
        counters = np.zeros((len(tag_of_users_input_list),1))
        for i in new_df.iloc[indicer]['tags'].split(): 
            for j in range(len(tag_of_users_input_list)):  
                if (stem(i) in tag_of_users_input_list[j].split()) or (stem(" ".join(synonym(i))) in tag_of_users_input_list[j].split()):
                    counters[j]+=1
        if all(x>=1 for x in counters):
            newmovielist.append([new_df.iloc[indicer]['title'], new_df.iloc[indicer]['vote_average']])
            counterobjlist.append(counters)
    if len(newmovielist)>16:
        newmovielist = sorted(newmovielist, reverse=True, key= lambda x: x[1])[:16]
    else:
        newmovielist = sorted(newmovielist, reverse=True, key= lambda x: x[1])
    mylist=[]
    for item in newmovielist:
        mylist.append(item[0])
    return mylist

def name_to_image(df,movienamelist):
    name_image_dict = {}
    for item in movienamelist:        
        someseries = df[df['title']==item]['image info']
        movie_id = df[df['title']==item]['movie_id'].tolist()[0]
        i = someseries.tolist()[0]
        image_dict = eval(i)
        j = 0
        for key in image_dict.keys():
            if key == 'bfp' and image_dict[key] != None: 
                name_image_dict[item] = [image_dict['bfp'],movie_id]
                break
            elif key == 'lfp' and image_dict[key] != None:
                name_image_dict[item] = [image_dict['lfp'],movie_id]
                break
            elif key == 'pfp' and image_dict[key] != None:
                name_image_dict[item] = [image_dict['pfp'],movie_id]
                break
            else:
                name_image_dict[item] = "default.png"
            j=0
    return name_image_dict

def get_image_files(name_image_dict):
    movie_imagepath_dict = {}
    for k,v in name_image_dict.items():        
            print_image_obj = requests.get("https://image.tmdb.org/t/p/original/{}".format(v[0]))
            image_bytes = io.BytesIO(print_image_obj.content)
            image = PIL.Image.open(image_bytes) 
            resize_image = image.resize((500, 400)) 
            #resize_image.show()
            file_name=f"D:\entipwebsite\src\main\static\main\images\{str(v[1])}.png"
            movie_imagepath_dict[k] = f"main/images/{str(v[1])}.png"    # main/images/file.png  # "{% static 'main/images/add_users_btn.png' %}" #r"{% static " +f"'main/images/{str(v[1])}.png'" + r" %}" 
            resize_image.save(file_name, 'PNG')
    return movie_imagepath_dict