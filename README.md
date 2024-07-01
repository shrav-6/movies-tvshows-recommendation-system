# Entip

Entertainment Recommendation System<br/>

## Implementation
1. The recommendation engine was implemented using two methods: content-based filtering and collaborative based filtering.<br/>
2. For content-based filtering, count vectorization and cosine similarity were performed on the dataset using tags, these tags were filtered from the dataframe and the bag of words method was used. <br/>
3. Collaborative based filtering was implemented using k-NN (k -Nearest Neighbor) machine learning model where the user’s rating is the key attribute.<br/>
4. For multiple movie/tv shows recommendation, the single recommendation engine was used as an input to an algorithm which compares their similarity with the user’s input to obtain the appropriate suggestions.<br/><br/>
![alt text](image.png) <br/>
Fig. Content based filtering <br/><br/>
![alt text](image-1.png) <br/>
Fig. Multiple user input recommendation system <br/><br/>
![alt text](image-2.png)<br/>
Fig. Collaborative based filtering<br/>
<br/>

## Test cases
<b>Example test case for multi-user recommendation:</b><br/>
User’s Input:<br/>
1. Urban Legend - Genres: Horror, Thriller<br/>
2. Snatch – Genres: Thriller, Crime<br/>
3. LOL - Genres: Drama, Comedy, Romance<br/>
4. Devil – Genres: Horror, Mystery, Thriller<br/>
![alt text](image-3.png)<br/>
Fig. Output<br/>

<b>Example test case for KNN:</b><br/>
User's Input: Iron Man<br/>
![alt text](image-4.png)<br/>
Fig. Output<br/>

## Future Scope/ Enhancement:
1. Completing the development of the web-application and integrating the recommendation engine with it, is of major concern.
2. Broadening the fields of interest to documentaries as well as songs
3. Optimizing the time complexity of the algorithm for faster recommendations.