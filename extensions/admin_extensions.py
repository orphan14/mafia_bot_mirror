import lightbulb
import os
import random
import re
from extensions.Graph.Graph import MatchGraph
from extensions.data_classes import UsernameStatus, RegistrationStatus
from extensions.db_functions import check_username_status, check_registration_status, get_user_by_discord_id, query_db, \
    create_string_from_pairings, insert_pairings_matches, generate_queue_objects, generate_matches_from_pairings, \
    get_queue, get_matchups_from_queue, get_user_by_username

import urllib.request

plugin = lightbulb.Plugin("AdminPlugin")

def load(bot):
    bot.add_plugin(plugin)

def unload(bot):
    bot.remove_plugin(plugin)

def load_word_list():
    word_url = "http://svnweb.freebsd.org/csrg/share/dict/words?view=co&content-type=text/plain"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)'}
    req = urllib.request.Request(word_url, headers=headers)
    response = urllib.request.urlopen(req)
    long_txt = response.read().decode()
    words = long_txt.splitlines()
    upper_words = [word for word in words if word[0].isupper()]
    name_words = [word for word in upper_words if not word.isupper()]
    return name_words

@plugin.command()
@lightbulb.option("last_name","Please type in your last name.")
@lightbulb.option("first_name","Please type in your first name.")
@lightbulb.command("admin_register_non_discord_user", "Register user into the system.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_register_non_discord_user(ctx: lightbulb.SlashContext) -> None:

    username = ctx.options.first_name + " " + ctx.options.last_name

    # Check for status of this discord user
    username_status = check_username_status(None, username)
    if UsernameStatus.NAME_AVAILABLE == username_status:
        await ctx.respond(f"Username \"{username}\" available.")
        insert_string = f"INSERT INTO users VALUES(DEFAULT,NULL,NULL,'{username}',true);"
        query_db(insert_string)
        await ctx.respond(f"Added user with username \"{username}\"")
    elif UsernameStatus.NAME_TAKEN_THIS_USER == username_status:
        await ctx.respond(f"WARNING: Already registered under username \"{username}\"")
    elif UsernameStatus.NAME_TAKEN_OTHER_USER == username_status:
        await ctx.respond(f"ERROR: Another user already registered under username \"{username}\"")
        return;
    elif UsernameStatus.NAME_ERROR == username_status:
        await ctx.respond("ERROR: Name  query failed")
        return;



@plugin.command()
@lightbulb.option("last_name","Please type in your last name.")
@lightbulb.option("first_name","Please type in your first name.")
@lightbulb.option("user", "Use @ functionality to add user to queue.")
@lightbulb.command("admin_register_user", "Register non discord user into the system.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_register_user(ctx: lightbulb.SlashContext) -> None:
    discord_id = int(re.sub('[<@>]', '', ctx.options.user))
    discord_username = await ctx.app.rest.fetch_user(discord_id)
    username = ctx.options.first_name + " " + ctx.options.last_name

    # Check for status of this discord user
    username_status = check_username_status(discord_id, username)
    if UsernameStatus.NAME_AVAILABLE == username_status:
        await ctx.respond(f"Username \"{username}\" available.")
    elif UsernameStatus.NAME_TAKEN_THIS_USER == username_status:
        await ctx.respond(f"WARNING: Already registered under username \"{username}\"")
    elif UsernameStatus.NAME_TAKEN_OTHER_USER == username_status:
        await ctx.respond(f"ERROR: Another user already registered under username \"{username}\"")
        return;
    elif UsernameStatus.NAME_ERROR == username_status:
        await ctx.respond("ERROR: Name  query failed")
        return;


    registration_status = check_registration_status(discord_id)
    if RegistrationStatus.UNREGISTERED == registration_status:
        insert_string = f"INSERT INTO users VALUES(DEFAULT,{discord_id},'{discord_username}','{username}',true);"
        query_db(insert_string)
        await ctx.respond(f"Added discord user \"{discord_username}\" under username \"{username}\"")
    elif RegistrationStatus.REGISTERED_INACTIVE == registration_status:
        update_active_string = f"UPDATE users SET active=true, username='{username}' where discord_id={discord_id};"
        query_db(update_active_string)
        await ctx.respond(f"Reactivated user \"{discord_username}\" under username \"{username}\"")
    elif RegistrationStatus.REGISTERED_ACTIVE == registration_status:
        user_object = get_user_by_discord_id(discord_id)
        await ctx.respond(
            f"ERROR: Discord user \"{user_object.mDiscordUsername}\" already registered under username \"{user_object.mUsername}\".")
        if UsernameStatus.NAME_AVAILABLE:
            await ctx.respond("Change name by using the /change_name command.")
        await ctx.respond("User not added.")
    elif RegistrationStatus.REGISTRATION_ERROR == registration_status:
        await ctx.respond(f"Error with query for discord user {discord_username}")
        await ctx.respond("Error adding user.")
    else:
        await ctx.respond(f"Error with query for discord user {discord_username}")
        await ctx.respond("Error adding user.")

@plugin.command()
@lightbulb.command("admin_add_random_user", "add_random_user.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_add_random_user(ctx: lightbulb.SlashContext) -> None:
    name_words = load_word_list()
    if 321132897031421952 == ctx.author.id:
        rand_discord_id = random.randint(0, 10000)
        rand_discord_name = ' '.join([name_words[random.randint(0, len(name_words))] for i in range(1)])
        rand_username = ' '.join([name_words[random.randint(0, len(name_words))] for i in range(1)])
        await ctx.respond(f"Adding user {rand_discord_id} {rand_discord_name} {rand_username}")
        insert_statement = f"INSERT INTO users VALUES(DEFAULT,{rand_discord_id},'{rand_discord_name}','{rand_username}',true,DEFAULT)";
        query_db(insert_statement)
    else:
        await ctx.respond("You do not have permissions.")


@plugin.command()
@lightbulb.option("user_two", "Second user")
@lightbulb.option("user_one", "First user")
@lightbulb.command("admin_add_match", "add match between two users.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_add_match_by_ids(ctx: lightbulb.SlashContext) -> None:
    if 321132897031421952 == ctx.author.id:
        user_one_id = int(re.sub('[<@>]', '', ctx.options.user_one))
        user_two_id = int(re.sub('[<@>]', '', ctx.options.user_two))
        user_one_object = get_user_by_discord_id(user_one_id)
        user_two_object = get_user_by_discord_id(user_two_id)
        if None == user_one_object:
            await ctx.respond(f"ERROR: Could not find user id {user_one_id}")
        elif None == user_two_object:
            await ctx.respond(f"ERROR: Could not find user id {user_two_id}")
        else:
            match_insert = f"INSERT INTO matches VALUES(DEFAULT,'{user_one_object.mDiscordUsername}','{user_two_object.mDiscordUsername}',DEFAULT,NULL);"
            query_db(match_insert)
        await ctx.respond(
            f"Added match between users {user_one_object.mUsername}({user_one_object.mDiscordUsername}) and {user_two_object.mUsername}({user_two_object.mDiscordUsername})")
    else:
        await ctx.respond("You do not have permissions.")


@plugin.command()
@lightbulb.option("table", "Table name.")
@lightbulb.option("password", "Admin password.")
@lightbulb.command("admin_reset_table", "Reset table.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_reset_table(ctx: lightbulb.SlashContext) -> None:
    await ctx.respond("Resetting...")
    if 321132897031421952 == ctx.author.id:
        if "mafia" == ctx.options.password:
            filename = f"sql/{ctx.options.table}.sql"
            if (os.path.isfile(filename)):
                f = open(filename, "r")
                query_db(f.read());
                f = open("sql/functions.sql", "r")
                query_db(f.read());
                await ctx.respond(f"{ctx.options.table} reset.")
            else:
                await ctx.respond("Don't know how to handle this table.")
        else:
            await ctx.respond("Incorrect password.")
    else:
        await ctx.respond("You do not have permissions.")


@plugin.command()
@lightbulb.option("id", "Id in queue.")
@lightbulb.command("admin_remove_from_queue_by_id", "Remove someone from queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def show_queue(ctx: lightbulb.SlashContext) -> None:
    id = ctx.options.id
    select_string = f"SELECT * FROM queue WHERE id={id};"
    select_ret = query_db(select_string)
    objects = generate_queue_objects(select_ret);
    if 1 == len(objects):
        delete_string = f"DELETE FROM queue WHERE id={id};"
        ret = query_db(delete_string)
        await ctx.respond(f"Removed \"{objects[0].mUsername}\" from the queue.")
    else:
        await ctx.respond(f"ERROR : Id {id} is not in the queue.")


@plugin.command()
@lightbulb.option("user", "Use @ functionality to add user to queue.")
@lightbulb.command("admin_remove_from_queue", "Remove someone from queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_remove_from_queue(ctx: lightbulb.SlashContext) -> None:
    discord_id = int(re.sub('[<@>]', '', ctx.options.user))
    user_object = get_user_by_discord_id(discord_id)
    if None == user_object:
        await ctx.respond(
            f"Discord user (id:{discord_id}) not registered. Please register first using the /register command.")
        return
    select_string = f"SELECT * FROM queue WHERE discord_username='{user_object.mDiscordUsername}';"
    select_ret = query_db(select_string)
    objects = generate_queue_objects(select_ret);
    if 1 == len(objects):
        delete_string = f"DELETE FROM queue WHERE discord_username='{user_object.mDiscordUsername}';"
        query_db(delete_string)
        await ctx.respond(f"Removed \"{objects[0].mUsername}\" from the queue.")
    else:
        await ctx.respond(f"ERROR : User {user_object.mUsername} is not in the queue.")


@plugin.command()
@lightbulb.option("user", "Use @ functionality to add user to queue.")
@lightbulb.command("admin_add_to_queue", "Add player to queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_add_to_queue(ctx: lightbulb.SlashContext) -> None:
    discord_id = int(re.sub('[<@>]', '', ctx.options.user))
    user_object = get_user_by_discord_id(discord_id)
    if None == user_object:
        await ctx.respond(
            f"Discord user id({discord_id}) not registered. Please register first using the /register command.")
        return
    select_string = f"SELECT * FROM queue WHERE user_id='{user_object.mUserId}';"
    select_ret = query_db(select_string)
    queue_objects = generate_queue_objects(select_ret);
    if 1 == len(queue_objects):
        await ctx.respond(
            f"User is already in queue with id {queue_objects[0].mId} under username \"{queue_objects[0].mUsername}\".")
    elif 1 < len(queue_objects):
        await ctx.respond(f"ERROR: You are already in queue with id \"{queue_objects[0].mId}\".")
        await ctx.respond(f"ERROR: Multiple queue objects for user.")
    else:
        queue_insert = f"INSERT INTO queue VALUES({user_object.mUserId},'{user_object.mUsername}');"
        query_db(queue_insert)
        await ctx.respond(f"Added user to queue {user_object.mUsername}({user_object.mDiscordUsername})")


@plugin.command()
@lightbulb.option("username", "Username of Player")
@lightbulb.command("admin_add_non_discord_to_queue", "Add non discord player to queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_add_to_queue(ctx: lightbulb.SlashContext) -> None:
    user_object = get_user_by_username(ctx.options.username)
    if None == user_object:
        await ctx.respond(
            f"Username \"{ctx.options.username}\" not registered. Please register first using the /admin_register_non_discord_user command.")
        return
    select_string = f"SELECT * FROM queue WHERE username='{user_object.mUsername}';"
    select_ret = query_db(select_string)
    queue_objects = generate_queue_objects(select_ret);
    if 1 == len(queue_objects):
        await ctx.respond(
            f"User is already in queue with id {queue_objects[0].mUserId} under username \"{queue_objects[0].mUsername}\".")
    elif 1 < len(queue_objects):
        await ctx.respond(f"ERROR: You are already in queue with id \"{queue_objects[0].mUserId}\".")
        await ctx.respond(f"ERROR: Multiple queue objects for user.")
    else:
        queue_insert = f"INSERT INTO queue VALUES({user_object.mUserId},'{user_object.mUsername}');"
        query_db(queue_insert)
        await ctx.respond(f"Added user to queue {user_object.mUsername}({user_object.mDiscordUsername})")



@plugin.command()
@lightbulb.command("admin_pair", "Pair players in queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def admin_matchmake(ctx: lightbulb.SlashContext) -> None:
    queueObjects = get_queue();
    print(f"queueObjects:{queueObjects}")
    if len(queueObjects) > 1:
      if 0 != len(queueObjects) % 2:
          await ctx.respond("WARNING : Uneven amount of players in queue.")
      await ctx.respond("Getting matchups...")
      matchupObjects = get_matchups_from_queue(queueObjects)
      await ctx.respond("Got objects... Generating Graph...")
      match_graph = MatchGraph(queueObjects, matchupObjects)
      await ctx.respond("Graph generated... Now Pairing...")
      pairings = match_graph.brute_force_pair()
      await ctx.respond("Done Pairing!")
      print(pairings)
      pairing_matches = generate_matches_from_pairings(pairings, queueObjects)
      pairings_string = create_string_from_pairings(pairings, queueObjects)
      insert_pairings_matches(pairing_matches)
      print(pairings_string)
      await ctx.respond(pairings_string)
    else:
      await ctx.respond("Not enough players in queue to pair.")
