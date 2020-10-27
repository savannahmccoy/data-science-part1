#!/usr/bin/env python
# coding: utf-8

# In[ ]:


import json
import csv
import time
import sys
import pandas as pd
import numpy as np
import prettyprinter as pp
import matplotlib.pyplot as plt

# pandas options
pd.options.mode.chained_assignment = None  
pd.options.display.max_columns = None
pd.options.display.max_rows = None

# spotify api
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
import spotipy

# FILL THIS IN WITH YOUR OWN API CREDENTIALS
client_id = "..." 
client_secret = "..."


# In[ ]:


sp = spotipy.Spotify(auth_manager = SpotifyClientCredentials(client_id = client_id,
                                                             client_secret = client_secret))


# #### READING in original dataset

# In[ ]:


df = pd.read_csv ('data.csv')


# #### REMOVING songs before year 1950

# In[ ]:


new_df = df[df['year'] > 1950]


# #### PULLING additional song features

# In[ ]:


def get_song_info(s_ids):
    
    n = 0
    p = 50
    
    print(n)
    print(p)
    
    fields = ['song_id', 'primary_artist_id', 'album_type', 'time_signature']
    
    with open("song_info.csv", 'w') as csvfile:  
    
        csvwriter = csv.writer(csvfile)  
        csvwriter.writerow(fields)  
    
        for i in range(int(len(s_ids)/50)+1):
            print(i)
            print("\n")
            ids = s_ids[n:p]
            n = n + 50
            p = p + 50
            print(n)
            print(p)

            urns = ["spotify:track:" + x for x in ids]
            tracks_analysis = sp.audio_features(urns)
            tracks = sp.tracks(urns)['tracks']
            m = 0
            for track in tracks:
                s_id = track['id'] 
                a_id = track['artists'][0]['id']
                album_type = track['album']['album_type']
                time_signature = tracks_analysis[m]['time_signature']
                m = m + 1
                csvwriter.writerow([s_id, a_id, album_type, time_signature])


    
i = 0  
s_ids = list(new_df['id'])
start = time.time()
get_song_info(s_ids)
end = time.time()
print("time:", str(end - start))


# #### PULLING additional artist info

# In[ ]:


def get_artists_info(a_ids):
    n = 0
    p = 50
    
    print(n)
    print(p)
    
    fields = ['artist_id', 'genres', 'followers', 'popularity']
    
    with open("artist_info.csv", 'w') as csvfile:  
    
        csvwriter = csv.writer(csvfile)  
        csvwriter.writerow(fields)  

        for i in range(int(len(a_ids)/50)+1):
            print(i)
            print("\n")
            ids = a_ids[n:p]
            n = n + 50
            p = p + 50
            print(n)
            print(p)

            urns = ["spotify:artist:" + x for x in ids]
            artists = sp.artists(urns)['artists']
            for artist in artists:
                a_id = artist['id'] 
                followers = artist['followers']['total']
                genres = artist['genres']
                popularity = artist['popularity']
                
                csvwriter.writerow([a_id, genres, followers, popularity])
                
                
start = time.time()
udf = pd.read_csv('song_info.csv')
ua_ids = list(set(udf["primary_artist_id"]))
get_artists_info(ua_ids)
end = time.time()
print("time:", str(end - start))


# #### MERGING pulled data into main df

# In[ ]:


# MERGING SONG DATA
new_df = new_df.rename(columns={"id": "song_id", "popularity": "song_popularity"}, errors="raise")
sdf = pd.read_csv('song_info.csv')
m_df = pd.merge(new_df, sdf, on="song_id")
m_df


# In[ ]:


# MERGING ARTIST INFO
adf = pd.read_csv('artist_info.csv')
adf = adf.rename(columns={"artist_id": "primary_artist_id"}, errors="raise")
t_df = pd.merge(m_df, adf, on="primary_artist_id")
t_df


# In[ ]:


new_df = t_df.rename(columns={"followers": "primary_artist_followers", 
                              "genres":"primary_artist_genres", 
                              "popularity":"primary_artist_popularity"}, errors="raise")


# #### FORMING additional features

# In[ ]:


new_df['isSingle'] = [1 if x == "single" else 0 for x in new_df['album_type']]


# In[ ]:


a_ls = [x.strip('][').split(', ') for x in list(new_df["artists"])]
new_df['hasFeature'] = [1 if len(x) > 1 else 0 for x in a_ls]


# In[ ]:


new_df['isPopular'] = [1 if x >= 80 else 0 for x in new_df["song_popularity"]]


# In[ ]:


new_df.to_csv ('new_data_precleaned.csv', index = True, header = True)


# #### CLEANING feature data types

# In[164]:


def convert_to_list_artists(row):
#     ls = row["artists"].strip('][').split(', ') 
    ls = row["artists"] 
    ls = [x[1:-1] for x in ls]
    return ls

def convert_to_list_genres(row):
#     ls = row["primary_artist_genres"].strip('][').split(', ') 
    ls = row["primary_artist_genres"]
    ls = [x[1:-1] for x in ls]
    return ls

new_df['primary_artist_genres'] = new_df.apply(lambda row: convert_to_list_genres(row), axis=1)
new_df["artists"] = new_df.apply(lambda row: convert_to_list_artists(row), axis=1)


# In[165]:


def get_primary_artist(row):
    return row["artists"][0]

new_df = new_df.rename(columns={"primary_artist": "primary_artist_name"}, errors="raise")
new_df['primary_artist'] = new_df.apply(lambda row: get_primary_artist(row), axis=1)


# #### REMOVING unnecessary columns

# In[ ]:


# del new_df['album_type']

del new_df['no_genre']
del new_df['release_date']
del new_df['primary_artist_id']
del new_df['song_id']
del new_df['no_genre']


# In[166]:


new_df.to_csv('final_new_data.csv', index = True, header = True)

