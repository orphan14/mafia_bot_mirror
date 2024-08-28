CREATE OR REPLACE FUNCTION new_user_add_matchups() RETURNS TRIGGER AS $$
DECLARE r RECORD;
BEGIN
    FOR r IN SELECT * FROM users LOOP
      IF r.user_id != NEW.user_id THEN
        -- TODO think about how we want to initialize games since last played
        INSERT INTO user_matchups VALUES(NEW.user_id,r.user_id,NULL,0,0);
        INSERT INTO user_matchups VALUES(r.user_id,NEW.user_id,NULL,0,0);
      END IF;
    END LOOP;
    RETURN NEW;
END $$ language plpgsql;

--DROP TRIGGER IF EXISTS new_user_add_matchups_trigger ON users;
CREATE OR REPLACE TRIGGER new_user_add_matchups_trigger AFTER INSERT ON users
  FOR EACH ROW EXECUTE PROCEDURE new_user_add_matchups();

CREATE OR REPLACE FUNCTION update_matchups() RETURNS TRIGGER AS $$
DECLARE recordOneExists BOOLEAN;
DECLARE recordTwoExists BOOLEAN;
BEGIN
    --Make sure both are in the matchups
    recordOneExists = EXISTS(SELECT * FROM user_matchups WHERE user_id = NEW.user_id_one and opponent_user_id = NEW.user_id_two);
    recordTwoExists = EXISTS(SELECT * FROM user_matchups WHERE user_id = NEW.user_id_two and opponent_user_id = NEW.user_id_one);
    IF recordOneExists AND recordTwoExists THEN
      -- TODO think about how we want to initialize games since last played
      UPDATE user_matchups SET games_since_last_played=0 WHERE user_id = NEW.user_id_one AND opponent_user_id = NEW.user_id_two;
      UPDATE user_matchups SET games_since_last_played=0 WHERE user_id = NEW.user_id_two AND opponent_user_id = NEW.user_id_one;
      UPDATE user_matchups SET games_since_last_played=(games_since_last_played+1) WHERE user_id = NEW.user_id_one AND opponent_user_id != NEW.user_id_two;
      UPDATE user_matchups SET games_since_last_played=(games_since_last_played+1) WHERE user_id = NEW.user_id_two AND opponent_user_id != NEW.user_id_one;
    END IF;
    RETURN NEW;
END $$ language plpgsql;

--DROP TRIGGER IF EXISTS new_user_add_matchups_trigger ON users;
CREATE OR REPLACE TRIGGER update_matchups_trigger AFTER INSERT ON matches
  FOR EACH ROW EXECUTE PROCEDURE update_matchups();
