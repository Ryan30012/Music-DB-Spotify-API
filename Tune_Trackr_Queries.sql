-- Basic select with simple where clause: 

-- Select all tracks released in the year 2020.
SELECT * 
FROM Songs 
WHERE release_year = 2020;



-- Basic select with simple group by clause (with and without having clause). 

-- Count the number of songs per genre
SELECT genre, COUNT(*) AS song_count
FROM Songs
GROUP BY genre;

-- Fetch genres with more than 10 songs
SELECT genre, COUNT(*) AS song_count
FROM Songs
GROUP BY genre
HAVING COUNT(*) > 10;



-- A simple join query as well as its equivalent implementation using cartesian product and where clause. 

-- Fetch all albums along with their artists
-- Simple Join Query:
SELECT DISTINCT Albums.album_name, Artists.artist_name
FROM Albums
JOIN Artists ON Albums.artist_id = Artists.id;

-- Using cartesian Product:
SELECT DISTINCT Albums.album_name, Artists.artist_name
FROM Albums, Artists
WHERE Albums.artist_id = Artists.id;



-- A few queries to demonstrate various join types on the same tables: inner vs. outer (left and right) vs. full join. Use of null values in the database to show the differences is required. 

-- Inner Join
-- Find songs and playlists with matching genres (non-NULL genres only)
SELECT s.song_name, s.genre AS song_genre, p.playlist_name, p.genre AS playlist_genre
FROM Songs s
INNER JOIN Playlists p ON s.genre = p.genre;

-- Outer Join
-- Find all songs and playlists, including those with no matching genres
SELECT s.song_name, s.genre AS song_genre, p.playlist_name, p.genre AS playlist_genre
FROM Songs s
FULL JOIN Playlists p ON s.genre = p.genre;


-- Left Join
-- Find all songs and their matching playlists (include songs without matching genres)
SELECT s.song_name, s.genre AS song_genre, p.playlist_name, p.genre AS playlist_genre
FROM Songs s
LEFT JOIN Playlists p ON s.genre = p.genre;

-- Right Join
-- Find all playlists and their matching songs (include playlists without matching genres)
SELECT s.song_name, s.genre AS song_genre, p.playlist_name, p.genre AS playlist_genre
FROM Songs s
RIGHT JOIN Playlists p ON s.genre = p.genre;



-- A few queries to demonstrate use of Null values for undefined / non-applicable.

-- Find all songs with unidentified genres (“null”)
SELECT song_name as name, s.genre
FROM Songs s
WHERE s.genre IS NULL;

-- For testing Purposes:
INSERT INTO Albums (album_name, release_year, artist_id, nb_of_songs, source)
VALUES ('Test-1', 2024, NULL, 10, 'Test Source');

INSERT INTO Songs (song_name, duration, genre, release_year, album_id, artist_id, source, is_single)
VALUES ('Test-2', 180.00, 'Test Genre', 2023, NULL, 101, 'Test Source', TRUE);

-- Find all albums without an artist id
SELECT album_name as name, a.artist_id
FROM Albums a
WHERE a.artist_id IS NULL;

-- Find all songs without an album id
SELECT song_name as name, s.album_id
FROM Songs s
WHERE s.album_id IS NULL;



-- A couple of examples to demonstrate correlated queries. 

-- Find artists who have only one album.
SELECT A.id AS artist_id, A.artist_name
FROM Artists A
WHERE 1 = (
    SELECT COUNT(*) 
    FROM Albums AL 
    WHERE AL.artist_id = A.id
);

-- Find songs that are shorter than the average duration of all songs
SELECT song_name, duration
FROM Songs s1
WHERE duration < (
    SELECT AVG(s2.duration)
    FROM Songs s2
    WHERE s2.artist_id = s1.artist_id
);



-- One example per set operations: intersect, union, and difference vs. their equivalences without using set operations. 

-- Find genres that are present in both songs and playlists.
-- With Intersect:
SELECT DISTINCT s.genre
FROM Songs s
WHERE s.genre IS NOT NULL
INTERSECT (
SELECT DISTINCT p.genre
FROM Playlists p
);

-- Without intersect:
SELECT DISTINCT s.genre
FROM Songs s
WHERE s.genre IS NOT NULL
  AND s.genre IN (
      SELECT DISTINCT p.genre
      FROM Playlists p
  );

-- Find all distinct genres from both songs and playlists
-- With Union:
SELECT DISTINCT s.genre
FROM Songs s
WHERE s.genre IS NOT NULL
UNION
SELECT DISTINCT p.genre
FROM Playlists p;

-- Without Union:
SELECT DISTINCT genre
FROM (
    SELECT s.genre
    FROM Songs s
    WHERE s.genre IS NOT NULL
    UNION ALL
    SELECT p.genre
    FROM Playlists p
) AS sub;


-- Find all genres in songs that are not present in playlists
-- With Difference:
SELECT DISTINCT s.genre
FROM Songs s
WHERE s.genre IS NOT NULL
EXCEPT
SELECT DISTINCT p.genre
FROM Playlists p;

-- Without Difference:
SELECT DISTINCT s.genre
FROM Songs s
WHERE s.genre IS NOT NULL
  AND s.genre NOT IN (
      SELECT DISTINCT p.genre
      FROM Playlists p
  );



-- An example of a view that has a hard-coded criteria, by which the content of the view may change upon changing the hard-coded value (see L09 slide 24). 

-- A view that only shows tracks longer than 3 minutes 
-- This part must be run individually

-- CREATE VIEW LongSongs AS 
-- (SELECT * FROM Songs WHERE duration > 180)



-- Two queries that demonstrate the overlap and covering constraints. 

-- Find all artists who have created songs and have also contributed to collaborations
SELECT DISTINCT a.artist_name
FROM Artists a
JOIN Songs s ON a.id = s.artist_id
JOIN Collaborations c ON a.id = c.artist_id;

-- Find all artists who are not represented in either Songs or Collaborations

-- For testing Purposes:
INSERT INTO Artists (artist_name, source)
VALUES ('Test Artist', 'Test Insert');

SELECT a.artist_name
FROM Artists a
LEFT JOIN Songs s ON a.id = s.artist_id
LEFT JOIN Collaborations c ON a.id = c.artist_id
WHERE s.artist_id IS NULL AND c.artist_id IS NULL;



-- Two implementations of the division operator using a) a regular nested query using NOT IN and b) a correlated nested query using NOT EXISTS and EXCEPT (See [2])3 .

-- Find artists who doesn’t have Pop tracks.
SELECT a.id, a.artist_name
FROM Artists a
WHERE a.id NOT IN ( SELECT s.artist_id 
FROM Songs s 
WHERE genre = 'Pop');

-- Find all songs where the associated artist has not released any songs in all possible genres.
SELECT s.song_name AS name
FROM Songs s
WHERE NOT EXISTS (
    SELECT DISTINCT g.genre AS genre
    FROM Songs g
    WHERE g.artist_id = s.artist_id
    EXCEPT
    SELECT DISTINCT x.genre
    FROM Songs x
);
