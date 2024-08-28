from extensions.db_functions import *

def generate_queue_objects(result):
  queue_objects = []
  for record in result:
    querieddId = record[0]
    queriedDiscordName = record[1]
    queriedUsername = record[2]
    q = Queue(querieddId, queriedDiscordName, queriedUsername);
    queue_objects.append(q)
  return queue_objects;


def generate_user_objects(result):
  users = []
  for record in result:
    queriedDiscordId = record[0]
    queriedDiscordName = record[1]
    queriedUsername = record[2]
    queriedActive = record[3]
    u = User(queriedDiscordId, queriedDiscordName, queriedUsername, queriedActive);
    users.append(u)
  return users;

def get_user_by_discord_id(discord_id):
  discord_id_select = f"SELECT * from users where discord_id={discord_id};"
  discord_id_ret = query_db(discord_id_select)
  if len(discord_id_ret) :
    queriedUserId = discord_id_ret[0][0]
    queriedDiscordId = discord_id_ret[0][1]
    queriedDiscordName = discord_id_ret[0][2]
    queriedUsername = discord_id_ret[0][3]
    queriedActive = discord_id_ret[0][4]
    u = User(queriedUserId,queriedDiscordId,queriedDiscordName,queriedUsername,queriedActive);
    return u;
  return None;

def get_user_by_username(username):
  discord_id_select = f"SELECT * from users where username='{username}';"
  discord_id_ret = query_db(discord_id_select)
  if len(discord_id_ret) :
    queriedUserId = discord_id_ret[0][0]
    queriedDiscordId = discord_id_ret[0][1]
    queriedDiscordName = discord_id_ret[0][2]
    queriedUsername = discord_id_ret[0][3]
    queriedActive = discord_id_ret[0][4]
    u = User(queriedUserId,queriedDiscordId,queriedDiscordName,queriedUsername,queriedActive);
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

def check_username_status(discord_id,username):
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

