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
# Create your views here.
def home(response):
    return render(response, "main/home.html", {})

def movies(response):    
    print(response.POST)   
    if response.method == 'POST':
        print('inside post') 
        print(response.POST)
        formset = EnterMoviesFormset(response.POST) 
        #form = EnterMoviesForm(response.POST)
        if formset.is_valid():
            print('inside if case')
            movienames = []
            for form in formset: 
                if form.is_valid():
                    print('inside for loop') 
                    print('form',form)
                    print("form's cleaned data",form.cleaned_data)
                    if(form.cleaned_data=={}):
                        print('enter a movie name')
                    else:
                        user_movie_name = form.cleaned_data['moviename']
                        #print("current movie name is:",user_movie_name)
                        #print(type(user_movie_name))
                        movienames.append(user_movie_name)
                    
                #single_movie_recommendation(user_movie_name,20,'single')
        print("movienames: ",movienames)
        return HttpResponseRedirect('/movies/') 
        
    else:  
        formset = EnterMoviesFormset()      
        print("refresh")
        #return HttpResponseRedirect('/movies/') 

    return render(response, "main/movies.html", {"formset":formset})
    #return render('main/movies.html', {}
    
def single_movie_recommendation(moviename,headnum,flag):
    print("inside single_movie_recommendation")
    print("current directory:",os.getcwd())
    model_movies_df = pd.read_csv("./main/static/main/database/model_ready_movies_db.csv") 
    model_movies_df['genres'] = model_movies_df['genres'].apply(ast.literal_eval)
    model_movies_df['overview'] = model_movies_df['overview'].apply(ast.literal_eval)
    model_movies_df['keywords'] = model_movies_df['keywords'].apply(ast.literal_eval)
    model_movies_df['cast'] = model_movies_df['cast'].apply(ast.literal_eval)
    model_movies_df['crew'] = model_movies_df['crew'].apply(ast.literal_eval)
    
    print(model_movies_df.head())
    
    if flag == 'multiple':
        model_movies_df['tags'] = model_movies_df['genres'] + model_movies_df['keywords']
    if flag == 'single':
        model_movies_df['tags'] = model_movies_df['overview'] + model_movies_df['genres'] + model_movies_df['keywords'] + model_movies_df['cast'] + model_movies_df['crew']
    
    df = model_movies_df[['movie_id','title','tags','vote_average','popularity']]
       
    df['tags'] = df['tags'].apply(lambda x: " ".join(x))
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
    for i in sortedimdblist:
        print("Title:", " ".join(model_movies_df[model_movies_df['movie_id']==i[0]].title.tolist()), "\nIMDb Rating:", i[2],"\nSimilarity", i[1])