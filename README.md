# Music DB and Spotify API

Steps:    
- Run, db_creation.py    
- Run, Tune_Trackr_DDL.sql in pgAdmin    
- Run, populate_DB.py, which will directly fetch from album_nb_songs.json and insert into the Tune_Trackr db    

# additional note
- songs_DB.json is an incomplete DB, missing number of songs per album.  
- album_nb_songs.json, take data from song_db and adds number of songs per album.

# Fetch note
- Run, Music_APIs.py to fetch songs_DB.json
- Run, Album_NB_fetch.py to fetch and add number of songs per album to song_DB.json and save it in new album_nb_songs.json
