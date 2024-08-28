DROP VIEW IF EXISTS user_matchups_readable;
DROP TABLE IF EXISTS user_matchups;
--CREATE TABLE user_matchups (discord_username TEXT REFERENCES users(discord_username),
--                            opponent TEXT REFERENCES users(discord_username),
--                            games_since_last_played INT,
--                            wins INT ,
--                            losses INT);

CREATE TABLE user_matchups (user_id INT REFERENCES users(user_id),
                            opponent_user_id INT REFERENCES users(user_id),
                            games_since_last_played INT,
                            wins INT ,
                            losses INT);

