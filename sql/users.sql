DROP TABLE IF EXISTS users CASCADE;
CREATE TABLE IF NOT EXISTS users (user_id SERIAL UNIQUE PRIMARY KEY,
                                  discord_id BIGINT UNIQUE,
                                  discord_username TEXT UNIQUE,
                                  username TEXT UNIQUE NOT NULL,
                                  active BOOLEAN NOT NULL,
                                  date_joined DATE NOT NULL DEFAULT CURRENT_DATE);
