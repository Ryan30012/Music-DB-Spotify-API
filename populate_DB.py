import psycopg2
import json
import random  

# Database connection 
DB_NAME = "tune_trackr"
DB_USER = "postgres"  
DB_PASSWORD = "your_password"  
DB_HOST = "localhost"
DB_PORT = "5432"

# Connect to the database
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cur = conn.cursor()

def get_or_create_artist(artist_name, source):
    """Insert an artist if not exists and return its ID."""
    if not artist_name:  
        return None
    query = """
        INSERT INTO Artists (artist_name, source)
        VALUES (%s, %s)
        ON CONFLICT (artist_name) DO NOTHING
        RETURNING id;
    """
    cur.execute(query, (artist_name, source))
    artist_id = cur.fetchone()
    if not artist_id: 
        cur.execute("SELECT id FROM Artists WHERE artist_name = %s;", (artist_name,))
        artist_id = cur.fetchone()
    return artist_id[0] if artist_id else None

def get_or_create_album(album_name, release_year, artist_id, nb_of_songs, source):
    """Insert an album if not exists and return its ID."""
    if not album_name or not artist_id:  
        return None
    query = """
        INSERT INTO Albums (album_name, release_year, artist_id, nb_of_songs, source)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """
    cur.execute(query, (album_name, release_year, artist_id, nb_of_songs, source))
    album_id = cur.fetchone()
    if not album_id:  
        cur.execute("SELECT id FROM Albums WHERE album_name = %s AND artist_id = %s;", (album_name, artist_id))
        album_id = cur.fetchone()
    return album_id[0] if album_id else None

def insert_song(song_name, duration, genre, release_year, album_id, artist_id, source, is_single=True):
    """Insert a song into the Songs table."""
    if not song_name or not artist_id: 
        return None
    query = """
        INSERT INTO Songs (song_name, duration, genre, release_year, album_id, artist_id, source, is_single)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT DO NOTHING
        RETURNING id;
    """
    cur.execute(query, (song_name, duration, genre, release_year, album_id, artist_id, source, is_single))
    song_id = cur.fetchone()
    return song_id[0] if song_id else None

def insert_collaboration(song_id, artist_id):
    """Insert a collaboration into the Collaborations table."""
    if not song_id or not artist_id: 
        return
    query = """
        INSERT INTO Collaborations (song_id, artist_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """
    cur.execute(query, (song_id, artist_id))

def get_or_create_playlist(playlist_name, genre, year):
    """Insert a playlist if not exists and return its ID."""
    if not playlist_name or not genre or not year:  
        return None
    query = """
        INSERT INTO Playlists (playlist_name, genre, year)
        VALUES (%s, %s, %s)
        ON CONFLICT (genre, year) DO NOTHING
        RETURNING id;
    """
    cur.execute(query, (playlist_name, genre, year))
    playlist_id = cur.fetchone()
    if not playlist_id:  
        cur.execute("SELECT id FROM Playlists WHERE playlist_name = %s;", (playlist_name,))
        playlist_id = cur.fetchone()
    return playlist_id[0] if playlist_id else None

def insert_playlist_song(playlist_id, song_id):
    """Link a song to a playlist."""
    if not playlist_id or not song_id: 
        return
    query = """
        INSERT INTO Playlist_Songs (playlist_id, song_id)
        VALUES (%s, %s)
        ON CONFLICT DO NOTHING;
    """
    cur.execute(query, (playlist_id, song_id))

# Process the JSON file and insert data
def process_and_insert_data(json_file):
    with open(json_file, "r") as f:
        songs = json.load(f)

    for song in songs:
        try:
            song_name = song.get("song_name")
            artist_names = song.get("artist_name", "Unknown Artist").split(", ") 
            main_artist_name = artist_names[0] 
            collab_artists = artist_names[1:] 

            album_name = song.get("album_name")
            release_year = song.get("release_year", 2000)
            duration = round(song.get("duration", 0), 2)  
            genre = None if song.get("genre", "Unknown Genre") == "Unknown Genre" else song.get("genre")
            source = song.get("source")
            nb_of_songs = song.get("nb_of_songs", 1)
            is_single = len(collab_artists) == 0 

            # Insert main artist and get artist ID
            main_artist_id = get_or_create_artist(main_artist_name, source)

            # Insert album and get album ID
            album_id = get_or_create_album(album_name, release_year, main_artist_id, nb_of_songs, source)

            # Insert song and get song ID
            song_id = insert_song(song_name, duration, genre, release_year, album_id, main_artist_id, source, is_single)
            if not song_id:
                print(f"Skipping song '{song_name}' due to missing data.")
                continue

            # Insert collaborations
            for collab_artist_name in collab_artists:
                collab_artist_id = get_or_create_artist(collab_artist_name, source)
                insert_collaboration(song_id, collab_artist_id)

            # Insert song into playlists based on genre and year
            if genre and release_year:
                playlist_name = f"{release_year} {genre.title()} Music"
                playlist_id = get_or_create_playlist(playlist_name, genre, release_year)
                insert_playlist_song(playlist_id, song_id)

            conn.commit()
            print(f"Inserted: {song_name} by {main_artist_name}")

        except Exception as e:
            conn.rollback() 
            print(f"Error inserting {song.get('song_name', 'Unknown Song')}: {e}")

def main():
    process_and_insert_data("album_nb_songs.json")
    print("Data insertion completed.")

if __name__ == "__main__":
    try:
        main()
    finally:
        cur.close()
        conn.close()
