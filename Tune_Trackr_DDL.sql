-- Artists Table
CREATE TABLE Artists (
    id SERIAL,
    artist_name VARCHAR(100),
    source VARCHAR(50),
    PRIMARY KEY (id),
    CONSTRAINT unique_artist_name UNIQUE (artist_name)
);

-- Albums Table
CREATE TABLE Albums (
    id SERIAL,
    album_name VARCHAR(255),
    release_year INT CHECK (release_year > 2000 AND release_year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    artist_id INT,
    nb_of_songs INT DEFAULT 0,
    source VARCHAR(50),
    PRIMARY KEY (id),
    FOREIGN KEY (artist_id) REFERENCES Artists(id) ON DELETE CASCADE
);

-- Songs Table
CREATE TABLE Songs (
    id SERIAL,
    song_name VARCHAR(255),
    duration DECIMAL(5, 2) DEFAULT 0.00,
    genre VARCHAR(255),
    release_year INT CHECK (release_year > 2000 AND release_year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    album_id INT,
    artist_id INT,
    source VARCHAR(50),
    is_single BOOLEAN DEFAULT TRUE,
    PRIMARY KEY (id),
    FOREIGN KEY (album_id) REFERENCES Albums(id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES Artists(id) ON DELETE CASCADE
);

-- Collaborations Table
CREATE TABLE Collaborations (
    song_id INT NOT NULL,
    artist_id INT NOT NULL,
    PRIMARY KEY (song_id, artist_id),
    FOREIGN KEY (song_id) REFERENCES Songs(id) ON DELETE CASCADE,
    FOREIGN KEY (artist_id) REFERENCES Artists(id) ON DELETE CASCADE
);

-- Playlists Table
CREATE TABLE Playlists (
    id SERIAL,
    playlist_name VARCHAR(255),
    genre VARCHAR(255),
    year INT CHECK (year > 2000 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    PRIMARY KEY (id),
    UNIQUE (genre, year)
);

-- Playlist_Songs Table (Weak Entity linking Playlists and Songs)
CREATE TABLE Playlist_Songs (
    playlist_id INT,
    song_id INT,
    PRIMARY KEY (playlist_id, song_id),
    FOREIGN KEY (playlist_id) REFERENCES Playlists(id) ON DELETE CASCADE,
    FOREIGN KEY (song_id) REFERENCES Songs(id) ON DELETE CASCADE
);

-- Indexes for Frequently Queried Columns
CREATE INDEX idx_artist_name ON Artists(artist_name);
CREATE INDEX idx_album_name ON Albums(album_name);
CREATE INDEX idx_song_name ON Songs(song_name);
CREATE INDEX idx_playlist_name ON Playlists(playlist_name);
CREATE INDEX idx_playlist_genre_year ON Playlists(genre, year);
