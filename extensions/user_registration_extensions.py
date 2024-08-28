import lightbulb
from extensions.db_functions import query_db, get_user_by_discord_id, UsernameStatus, check_username_status, check_registration_status, \
    RegistrationStatus

plugin = lightbulb.Plugin("UserRegistrationExtension")


@plugin.command()
@lightbulb.option("last_name", "Please type in your last name.")
@lightbulb.option("first_name", "Please type in your first name.")
@lightbulb.command("register", "Register user.")
@lightbulb.implements(lightbulb.SlashCommand)
async def register(ctx: lightbulb.SlashContext) -> None:
    discord_id = ctx.author.id
    discord_username = ctx.author.username
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
@lightbulb.option("last_name", "Please type in your last name.")
@lightbulb.option("first_name", "Please type in your first name.")
@lightbulb.command("change_name", "ChangeName.")
@lightbulb.implements(lightbulb.SlashCommand)
async def change_name(ctx: lightbulb.SlashContext) -> None:
    discord_id = ctx.author.id
    discord_username = ctx.author.username
    registration_status = check_registration_status(discord_id)

    if RegistrationStatus.UNREGISTERED == registration_status:
        await ctx.respond(
            f"Discord user \"{discord_username}\" not registered. Please use the /register command instead.")
    elif RegistrationStatus.REGISTERED_INACTIVE == registration_status:
        await ctx.respond(
            f"WARNING: User \"{discord_username}\" is currently INACTIVE. Please use the /register command if you wish to be active. Name change will still be attempted.")
    elif RegistrationStatus.REGISTRATION_ERROR == registration_status:
        await ctx.respond(f"Error with query for discord user {discord_username}")
        await ctx.respond("Error changing name for user.")

    username = ctx.options.first_name + " " + ctx.options.last_name
    username_status = check_username_status(discord_id, username)
    if UsernameStatus.NAME_AVAILABLE == username_status:
        update_string = f"UPDATE users SET username='{username}' WHERE discord_id={discord_id};"
        query_db(update_string)
        await ctx.respond(f"Discord user {discord_username} updated username to \"{username}\".")
    elif UsernameStatus.NAME_TAKEN_THIS_USER == username_status:
        await ctx.respond(f"WARNING: Already registered under username \"{username}\". Name not changed.")
    elif UsernameStatus.NAME_TAKEN_OTHER_USER == username_status:
        await ctx.respond(f"ERROR: Another user already registered under username \"{username}\". Name not changed.")
        return;
    elif UsernameStatus.NAME_ERROR == username_status:
        await ctx.respond("ERROR: Name  query failed")
        return;


@plugin.command()
@lightbulb.command("unregister", "Unregister.")
@lightbulb.implements(lightbulb.SlashCommand)
async def unregister(ctx: lightbulb.SlashContext) -> None:
    discord_id = ctx.author.id
    discord_username = ctx.author.username
    user_object = get_user_by_discord_id(discord_id)
    if None != user_object:
        update_string = f"UPDATE users SET active=false WHERE discord_id={discord_id};"
        query_db(update_string)
        await ctx.respond(
            f"Successfully unregistered discord user \"{user_object.mDiscordUsername}\" with registered name \"{user_object.mUsername}\".")
    else:
        await ctx.respond(f"Discord user {discord_username} not registered. Taking no action.")


def load(bot):
    bot.add_plugin(plugin)


def unload(bot):
    bot.remove_plugin(plugin)
