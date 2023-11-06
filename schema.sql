DROP TABLE IF EXISTS artworks;
CREATE TABLE artworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    price REAL NOT NULL,
    image_url TEXT NOT NULL,
    listed INTEGER NOT NULL DEFAULT 1
);