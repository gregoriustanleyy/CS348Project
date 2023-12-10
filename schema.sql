DROP TABLE IF EXISTS artworks;
CREATE TABLE artworks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    artist TEXT NOT NULL,
    price REAL NOT NULL,
    image_url TEXT NOT NULL,
    listed INTEGER NOT NULL DEFAULT 1,
    is_locked BOOLEAN NOT NULL DEFAULT 0
);

CREATE INDEX idx_price ON artworks(price);
CREATE INDEX idx_artist ON artworks(artist);
CREATE INDEX idx_listed ON artworks(listed);