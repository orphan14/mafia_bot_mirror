DROP TABLE IF EXISTS queue;
CREATE TABLE queue (user_id INT REFERENCES users(user_id) UNIQUE,
                    username TEXT REFERENCES users(username) UNIQUE);