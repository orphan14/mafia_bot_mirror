DROP TABLE IF EXISTS user_elo;
CREATE TABLE user_elo (user_id INT REFERENCES users(user_id),
                       elo INT,
                       wins INT ,
                       losses INT);