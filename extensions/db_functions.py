import pg8000.native
from extensions.data_classes import User, Queue, Matchup, PairingsMatch, UsernameStatus, RegistrationStatus


from dotenv import load_dotenv
import os


env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path=env_path)

DB_PASSWORD = os.getenv("DB_PASSWORD")

con = pg8000.native.Connection(database="postgres",
                               user="postgres.lazxdshbgbcdhwfqwtte",
                               password=DB_PASSWORD,
                               host="aws-0-us-west-1.pooler.supabase.com",
                               port=6543)


def query_db(statement):
    result = []
    try:
        result = con.run(statement);
    except Exception as err:
        print(f"Unexpected {err=}, {type(err)=}")
    return result


def generate_queue_objects(result):
    queue_objects = []
    for record in result:
        querieddUserId = record[0]
        queriedUsername = record[1]
        q = Queue(querieddUserId, queriedUsername);
        queue_objects.append(q)
    return queue_objects;


def generate_user_objects(result):
    users = []
    for record in result:
        queriedId = record[0]
        queriedDiscordId = record[1]
        queriedDiscordName = record[2]
        queriedUsername = record[3]
        queriedActive = record[4]
        u = User(queriedId,queriedDiscordId, queriedDiscordName, queriedUsername, queriedActive);
        users.append(u)
    return users;


def generate_matchup_objects(result):
    matchups = []
    for record in result:
        queried_user_id = record[0]
        queried_opponent_user_id = record[1]
        queried_games_since_last = record[2]
        queried_wins = record[3]
        queried_losses = record[4]
        m = Matchup(queried_user_id, queried_opponent_user_id, queried_games_since_last, queried_wins, queried_losses);
        matchups.append(m)
    return matchups;


def get_user_by_discord_id(discord_id):
    discord_id_select = f"SELECT * from users where discord_id={discord_id};"
    discord_id_ret = query_db(discord_id_select)
    if len(discord_id_ret):
        queriedId = discord_id_ret[0][0]
        queriedDiscordId = discord_id_ret[0][1]
        queriedDiscordName = discord_id_ret[0][2]
        queriedUsername = discord_id_ret[0][3]
        queriedActive = discord_id_ret[0][4]
        u = User(queriedId,queriedDiscordId, queriedDiscordName, queriedUsername, queriedActive);
        return u;
    return None;


def get_user_by_username(username):
    discord_id_select = f"SELECT * from users where username='{username}';"
    discord_id_ret = query_db(discord_id_select)
    if len(discord_id_ret):
        queriedId = discord_id_ret[0][0]
        queriedDiscordId = discord_id_ret[0][1]
        queriedDiscordName = discord_id_ret[0][2]
        queriedUsername = discord_id_ret[0][3]
        queriedActive = discord_id_ret[0][4]
        u = User(queriedId,queriedDiscordId, queriedDiscordName, queriedUsername, queriedActive);
        return u;
    return None;


def check_registration_status(discord_id):
    # First check if discord_id is already registered
    user = get_user_by_discord_id(discord_id)
    if None == user:
        return RegistrationStatus.UNREGISTERED
    else:
        if user.mActive:
            return RegistrationStatus.REGISTERED_ACTIVE
        else:
            return RegistrationStatus.REGISTERED_INACTIVE


def check_username_status(discord_id, username):
    # First check if discord_id is already registered
    username_select = "SELECT * from users where username='{}'".format(username)
    users = generate_user_objects(query_db(username_select))
    if 0 == len(users):
        return UsernameStatus.NAME_AVAILABLE
    elif len(users) > 1:
        return UsernameStatus.NAME_ERROR
    else:
        if discord_id == users[0].mDiscordId:
            return UsernameStatus.NAME_TAKEN_THIS_USER
        else:
            return UsernameStatus.NAME_TAKEN_OTHER_USER


def get_queue():
    select_string = "SELECT * FROM queue;"
    ret = query_db(select_string)
    return generate_queue_objects(ret)


def queue_dict_from_objects(objects):
    ret = {}
    for object in objects:
        ret[object.mUserId] = object
    return ret


def get_matchups_from_queue(objects):
    matchup_recs = []
    queriedTuples = []
    for q in objects:
        for iq in objects:
            if ((q.mUserId, iq.mUserId) not in queriedTuples) and (
                    (iq.mUserId, q.mUserId) not in queriedTuples):
                select_string = f"SELECT * FROM user_matchups where (user_id='{q.mUserId}' AND opponent_user_id='{iq.mUserId}') " \
                                f"OR (user_id='{iq.mUserId}' AND opponent_user_id='{q.mUserId}');"
                queriedTuples.append((q.mUserId, iq.mUserId))
                queriedTuples.append((iq.mUserId, q.mUserId))
                ret = query_db(select_string)
                for item in ret:
                    matchup_recs.append(item)
    return generate_matchup_objects(matchup_recs)


def generate_matches_from_pairings(pairing, queue):
    matches = []
    queue_dict = queue_dict_from_objects(queue)
    for item in pairing:
        print(item)
        print(item[0])
        print(item[1])
        player_one = queue_dict[item[0][0]]
        player_two = queue_dict[item[0][1]]
        m = PairingsMatch(player_one.mUserId, player_two.mUserId, item[1])
        matches.append(m)
    return matches


def insert_pairings_matches(pairings_matches):
    for item in pairings_matches:
        insert_string = f"INSERT INTO matches VALUES(DEFAULT,'{item.mUserIdOne}','{item.mUserIdTwo}',{item.mPairingScore},DEFAULT);"
        query_db(insert_string)


def create_string_from_pairings(pairings_matches, queue):
    queue_dict = queue_dict_from_objects(queue)
    out_string = "--------PAIRINGS--------\n"
    out_string += "------------------------\n"
    pairing_player_list = []
    for item in pairings_matches:
        player_one = queue_dict[item[0][0]]
        player_two = queue_dict[item[0][1]]
        pairing_player_list.append((player_one, player_two))
    max_p1_name_length = max([len(x[0].mUsername) for x in pairing_player_list])
    max_p2_name_length = max([len(x[1].mUsername) for x in pairing_player_list])
    for p1, p2 in pairing_player_list:
        out_string += f"{p1.mUsername.ljust(max_p1_name_length)} VS {p2.mUsername.ljust(max_p2_name_length)}\n"
    out_string = f"```\n{out_string}```"
    return out_string
