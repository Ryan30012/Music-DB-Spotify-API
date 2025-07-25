import requests
import json
import time

# Spotify API Credentials
SPOTIFY_CLIENT_ID = '34538d455b4f41e998add25d5d8f9b89'
SPOTIFY_CLIENT_SECRET = 'b8cae2aae1544246b419844b47c73fd4'

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

# Fetch the number of songs in an album
def fetch_spotify_album_tracks(album_name, token, retries=3):
    """
    Fetch the number of tracks in an album using Spotify API.
    """
    url = "https://api.spotify.com/v1/search"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": album_name, "type": "album", "limit": 1}

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, params=params)
            if response.status_code == 200:
                albums = response.json().get("albums", {}).get("items", [])
                if albums:
                    total_tracks = albums[0].get("total_tracks", "Unknown")
                    return total_tracks
                else:
                    print(f"[Spotify] No albums found for '{album_name}'.")
                    return "Unknown"
            elif response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 1))
                print(f"[Spotify] Rate limit hit. Retrying in {retry_after} seconds...")
                time.sleep(retry_after)
            else:
                print(f"[Spotify] Failed to fetch album '{album_name}': {response.status_code}")
                return "Unknown"
        except requests.exceptions.RequestException as e:
            print(f"[Spotify] Error fetching album '{album_name}': {e}. Retrying...")
            time.sleep(2 ** attempt)
    return "Unknown"

def enrich_albums_with_track_count(input_file, output_file, token):
    """
    Reads the input file, fetches the number of tracks for each album, and saves the enriched data.
    """
    try:
        with open(input_file, "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return

    # Cache to avoid repeated API calls for the same album
    enriched_data = []
    album_track_count_cache = {}  

    for song in data:
        album_name = song.get("album_name", "Unknown Album")
        if album_name in album_track_count_cache:
            total_tracks = album_track_count_cache[album_name]
        else:
            total_tracks = fetch_spotify_album_tracks(album_name, token)
            album_track_count_cache[album_name] = total_tracks

        enriched_data.append({
            **song,
            "nb_of_songs": total_tracks
        })

        if len(enriched_data) % 10 == 0:
            print(f"[Progress] Processed {len(enriched_data)} songs.")

    # Save the data
    try:
        with open(output_file, "w") as f:
            json.dump(enriched_data, f, indent=4)
        print(f"[Output] Enriched data saved to '{output_file}'. Total entries: {len(enriched_data)}")
    except IOError as e:
        print(f"[Error] Could not save enriched data: {e}")

def main():
    token = authenticate_spotify()
    if not token:
        print("Spotify authentication failed. Exiting.")
        return

    input_file = "songs_DB.json"
    output_file = "album_nb_songs.json"

    print("[Start] Enriching albums with track count...")
    enrich_albums_with_track_count(input_file, output_file, token)
    print("[Finish] Enrichment process complete.")

if __name__ == "__main__":
    main()
