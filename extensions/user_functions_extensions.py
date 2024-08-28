import lightbulb
from extensions.db_functions import query_db, generate_user_objects, generate_queue_objects, get_user_by_discord_id

plugin = lightbulb.Plugin("UserExtension")


@plugin.command()
@lightbulb.command("show_users", "Show user list.")
@lightbulb.implements(lightbulb.SlashCommand)
async def show_users(ctx: lightbulb.SlashContext) -> None:
    # todo pull this from database.
    select_string = "SELECT * from users where active=true ORDER BY user_id;"
    ret = query_db(select_string)
    users_string = "Username - UserId\n"
    if len(ret):
        users = generate_user_objects(ret)
        for user in users:
            users_string += f"{user.mUserId} : {user.mUsername} - {user.mUserId}\n"
    else:
        await ctx.respond("No active users.")
        return;
    await ctx.respond(users_string)


@plugin.command()
@lightbulb.command("queue", "Join queue for weekly pairings.")
@lightbulb.implements(lightbulb.SlashCommand)
async def change_name(ctx: lightbulb.SlashContext) -> None:
    discord_id = ctx.author.id
    discord_username = ctx.author.username
    user_object = get_user_by_discord_id(discord_id)
    select_string = f"SELECT * FROM queue WHERE user_id='{user_object.mUserId}';"
    select_ret = query_db(select_string)
    queue_objects = generate_queue_objects(select_ret);
    if None == user_object:
        await ctx.respond(
            f"Discord user \"{discord_username}\" not registered. Please register first using the /register command.")
    elif 1 == len(queue_objects):
        await ctx.respond(
            f"You are already in queue with id {queue_objects[0].mUserId} under username \"{queue_objects[0].mUsername}\".")
    elif 1 < len(queue_objects):
        await ctx.respond(f"ERROR: You are already in queue with id \"{queue_objects[0].mUserId}\"")
        await ctx.respond(f"ERROR: Multiple queue objects for user.")
    else:
        queue_insert = f"INSERT INTO queue VALUES({user_object.mUserId},'{user_object.mUsername}');"
        query_db(queue_insert)
        await ctx.respond(f"Added user to queue {user_object.mUsername}({discord_username})")


@plugin.command()
@lightbulb.command("show_queue", "Show queue.")
@lightbulb.implements(lightbulb.SlashCommand)
async def show_queue(ctx: lightbulb.SlashContext) -> None:
    select_string = "SELECT * from queue;"
    ret = query_db(select_string)
    queue_objects = generate_queue_objects(ret)
    users_string = "Id - Username\n"
    if len(queue_objects):
        for object in queue_objects:
            users_string += f"{object.mUserId} : {object.mUsername} \n"
    else:
        await ctx.respond("No players in queue.")
        return;
    await ctx.respond(users_string)


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
