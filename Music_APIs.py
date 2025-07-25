import requests
import json
import time

# Spotify API Credentials
SPOTIFY_CLIENT_ID = '34538d455b4f41e998add25d5d8f9b89'
SPOTIFY_CLIENT_SECRET = 'b8cae2aae1544246b419844b47c73fd4'

# Authenticate with Spotify API
def authenticate_spotify():
    url = "https://accounts.spotify.com/api/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": SPOTIFY_CLIENT_ID,
        "client_secret": SPOTIFY_CLIENT_SECRET
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("[Spotify] Authentication successful.")
        return token
    else:
        print(f"[Spotify] Authentication failed: {response.status_code} - {response.text}")
        return None

# Fetch genres for an artist from Spotify
def fetch_spotify_artist_genre(artist_id, token, retries=3):
    """
    Fetch genres for a given artist using Spotify API.
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}"
    headers = {"Authorization": f"Bearer {token}"}
    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                genres = response.json().get("genres", [])
                return genres
            elif response.status_code == 429: 
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"[Spotify] Rate limit hit. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"[Spotify] Failed to fetch genres for artist '{artist_id}': {response.status_code}")
                return ["Unknown Genre"]
        except requests.exceptions.RequestException as e:
            print(f"[Spotify] Error fetching genres: {e}. Retrying...")
            time.sleep(2 ** attempt)
    return ["Unknown Genre"]

# Fetch genres for an artist from MusicBrainz
def fetch_musicbrainz_artist_genres(artist_name):
    """
    Fetch genres for a given artist using MusicBrainz.
    """
    base_url = "https://musicbrainz.org/ws/2/artist"
    params = {
        "query": artist_name,
        "fmt": "json",
        "limit": 1
    }
    try:
        response = requests.get(base_url, params=params)
        if response.status_code == 200:
            artists = response.json().get("artists", [])
            if artists and "tags" in artists[0]:
                return ", ".join([tag["name"] for tag in artists[0].get("tags", [])])
        else:
            print(f"[MusicBrainz] Error fetching genres for artist '{artist_name}': {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"[MusicBrainz] Error fetching genres for artist '{artist_name}': {e}")
    return "Unknown Genre"

# Fetch songs from Spotify by year
def fetch_spotify_by_year(year, token, limit=50):
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": f"year:{year}", "type": "track", "limit": 50}
    all_songs = []
    for offset in range(0, limit, 50):
        params["offset"] = offset
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                tracks = response.json().get("tracks", {}).get("items", [])
                for track in tracks:
                    artist_id = track["artists"][0]["id"] if track["artists"] else None
                    genres = fetch_spotify_artist_genre(artist_id, token) if artist_id else ["Unknown Genre"]

                    all_songs.append({
                        "song_name": track["name"],
                        "artist_name": ", ".join([artist["name"] for artist in track["artists"]]),
                        "album_name": track["album"]["name"],
                        "release_year": year,
                        "duration": track["duration_ms"] / 1000.0,
                        "genre": ", ".join(genres),
                        "source": "Spotify"
                    })

                    if len(all_songs) >= limit:
                        break
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"[Spotify] Rate limit hit. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"[Spotify] Error fetching songs for year {year}: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"[Spotify] Error fetching songs: {e}. Retrying...")
            time.sleep(2)
        time.sleep(0.2) 
    print(f"[Spotify] Fetched {len(all_songs)} songs for year {year}.")
    return all_songs

# Fetch songs from MusicBrainz by year
def fetch_musicbrainz_by_year(year, limit=50):
    base_url = "https://musicbrainz.org/ws/2/recording"
    all_songs = []
    for offset in range(0, limit, 100):
        params = {
            "query": f"date:[{year} TO {year}]",
            "limit": 100,
            "offset": offset,
            "fmt": "json"
        }
        try:
            response = requests.get(base_url, params=params)
            if response.status_code == 200:
                recordings = response.json().get("recordings", [])
                for song in recordings:
                    if "title" not in song or "artist-credit" not in song:
                        continue

                    artist_name = ", ".join([artist["name"] for artist in song["artist-credit"]])
                    genre = fetch_musicbrainz_artist_genres(artist_name) 

                    all_songs.append({
                        "song_name": song["title"],
                        "artist_name": artist_name,
                        "album_name": song.get("releases", [{}])[0].get("title", "Unknown Album"),
                        "release_year": year,
                        "duration": song.get("length", 0) / 1000.0,
                        "genre": genre,
                        "source": "MusicBrainz"
                    })
                    if len(all_songs) >= limit:
                        break
            elif response.status_code == 429:
                print("[MusicBrainz] Rate limit hit. Retrying...")
                time.sleep(1)
            else:
                print(f"[MusicBrainz] Error fetching songs for year {year}: {response.status_code}")
                break
        except requests.exceptions.RequestException as e:
            print(f"[MusicBrainz] Error fetching songs for year {year}: {e}")
            time.sleep(2)
        time.sleep(1) 
    print(f"[MusicBrainz] Fetched {len(all_songs)} songs for year {year}.")
    return all_songs

# Save combined data to JSON
def save_combined_data_to_json(data, output_file="songs_DB.json"):
    try:
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
        print(f"[Combined] Data saved to {output_file}. Total entries: {len(data)}")
    except IOError as e:
        print(f"[Combined] Error saving data: {e}")

def main():
    token = authenticate_spotify()
    if not token:
        print("Spotify authentication failed. Exiting.")
        return

    combined_data = []
    for year in range(2000, 2025):
        print(f"[Processing] Year {year}...")
        spotify_data = fetch_spotify_by_year(year, token, limit=50)
        musicbrainz_data = fetch_musicbrainz_by_year(year, limit=50)
        combined_data.extend(spotify_data + musicbrainz_data)
        print(f"[Progress] Combined {len(combined_data)} songs so far.")

    save_combined_data_to_json(combined_data, output_file="songs_DB.json")

if __name__ == "__main__":
    main()
