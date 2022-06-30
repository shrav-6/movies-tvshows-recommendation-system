from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from . forms import EnterMoviesForm, EnterMoviesFormset
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
# Create your views here.
def home(response):
    return render(response, "main/home.html", {})

def movies(response):    
    #print(response.POST)  
    recommended_movies_list = [] 
    if response.method == 'POST':
        print('inside post') 
        #print(response.POST)
        formset = EnterMoviesFormset(response.POST) 
        #form = EnterMoviesForm(response.POST)
        if formset.is_valid():
            #print('inside if case')
            movienames = []
            for form in formset: 
                if form.is_valid():
                    #print('inside for loop') 
                    #print('form',form)
                    #print("form's cleaned data",form.cleaned_data)
                    if(form.cleaned_data=={}):
                        print('enter a movie name')
                    else:
                        user_movie_name = form.cleaned_data['moviename']
                        #print("current movie name is:",user_movie_name)
                        #print(type(user_movie_name))
                        movienames.append(user_movie_name)
            model_movies_df = pd.read_csv(r"./main/static/main/database/5000_records_movies.csv",converters={'genres' : list,'overview':list,'keywords':list,'cast':list,'crew':list}) 
            if len(movienames) == 1:
                sorted_movie_list = single_movie_recommendation(model_movies_df,movienames[0],16,'single')
                #print(single_recommended_movies)
                
                for i in sorted_movie_list:
                    recommended_movies_list.append(" ".join(model_movies_df[model_movies_df['movie_id']==i[0]].title.tolist()))
                print(recommended_movies_list)
            else:
                recommended_movies_list = rec(model_movies_df,movienames) 
                print(recommended_movies_list)
        #print("movienames: ",movienames)
        #return HttpResponseRedirect('/movies/') 
        
    else:  
        formset = EnterMoviesFormset()      
        print("refresh")
        #return HttpResponseRedirect('/movies/') 

        '''    mydict={}
    for i in range(len(recommended_movies_list)):
        mydict[i]=recommended_movies_list[i]'''
        
    return render(response,"main/movies.html", {"formset":formset, "recommendedmovieslist":recommended_movies_list})
    #return render('main/movies.html', {}
    
def single_movie_recommendation(model_movies_df,moviename,headnum,flag):
    print("inside single_movie_recommendation")    
    if flag == 'multiple':
        model_movies_df['tags'] = model_movies_df['genres'] + model_movies_df['keywords']
    if flag == 'single':
        model_movies_df['tags'] = model_movies_df['overview'] + model_movies_df['genres'] + model_movies_df['keywords'] + model_movies_df['cast'] + model_movies_df['crew']
    
    df = model_movies_df[['movie_id','title','tags','vote_average','popularity']]
    #print(df.head())
    
    df['tags'] = df['tags'].apply(lambda x: "".join(x))
    df['tags'] = df['tags'].apply(lambda x: x.lower())

    psobj = PorterStemmer()
    def stem(text):
        temp = []
        for i in text.split():
            temp.append(psobj.stem(i))
        return " ".join(temp)

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
    sortedimdblist = []
    for i in imdbrecommendedlist:
        roundimdblist.append([i[0],round(i[1],2),i[2]])
    sortedimdblist = sorted(roundimdblist, reverse = True, key = lambda x: (x[1],x[2]))
    if flag=='single':
        #print(sortedimdblist)
        #for i in sortedimdblist:
            #single_recommended_movies = model_movies_df[model_movies_df['movie_id']==i[0]].title.tolist()
        return sortedimdblist
    else:
        return sortedimdblist

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

def rec(df,multiplemovielist):
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
    #print(len(newmovielist))
    mylist=[]
    for item in newmovielist:
        mylist.append(item[0])
    #print(mylist)
    return mylist