DROP TABLE IF EXISTS matches;
CREATE TABLE matches (id SERIAL PRIMARY KEY,
                      user_id_one INT REFERENCES users(user_id),
                      user_id_two INT REFERENCES users(user_id),
                      pairing_score INT,
                      date_played DATE NOT NULL DEFAULT CURRENT_DATE,
                      winner INT REFERENCES users(user_id)
                      );
