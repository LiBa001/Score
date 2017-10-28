import discord
import json
import urllib.request
import sqlib
import asyncio

client = discord.Client()
admin_ids = ["269959141508775937"]


class Help:
    def __init__(self, helpmsg):
        self.message = helpmsg


score_help = Help("Shows your score. "
                  "You score is the composition "
                  "of how active you are with messages, "
                  "reactions and helping other people.\n"
                  "For how you can show that someone helped you, "
                  "take a look at the help-site of `{prefix}thanks`.")
msg_reac_help = Help("Shows the number of your sent {0} "
                     "that has been recorded. "
                     "For more information, "
                     "about which {0} are recorded, "
                     "check out the help abut recording!")
messages_help = Help(msg_reac_help.message.format("messages"))
reactions_help = Help(msg_reac_help.message.format("reactions"))
stats_help = Help("Shows all your data:\n"
                  "score, messages, reactions")
thanks_help = Help("Gives you the possibility "
                   "to thank other users for helping you. "
                   "If you do this, the mentioned users "
                   "will get points for their score. "
                   "You can use it like this: \n"
                   "`{prefix}thanks @user @anotheruser ...`\n"
                   "The bot is just looking for the command and "
                   "the mentioned users, so after this "
                   "you can maybe write to them, "
                   "what you are thankful for.")
invite_help = Help("If you type this, I'll send an link. \n"
                   "Type this link into your browser, "
                   "to invite me to your Server. "
                   "All your recorded data will then "
                   "be available there to. "
                   "Please recognize that "
                   "bots can only be invited "
                   "by a server admin!")
prefix_help = Help("This is for changing the command-prefix. "
                   "The current prefix is `{prefix}` and "
                   "it has to stand before every command, "
                   "so the bot know that it is addressed. "
                   "If the current prefix is in trouble "
                   "with the prefix of an other bot, "
                   "change it like this:\n"
                   "`{prefix}prefix [new prefix]`\n"
                   "This can only be done by a server admin.")
help_help = Help("Shows a help message. "
                 "If you are an admin, I'll send it into the server channel, "
                 "otherwise I'll send you a private message.\n"
                 "You can also type `help` after any command to only get the specific help.\n"
                 "For example: `{prefix}stats help`")
r_lb_help = Help("Shows {0}. "
                 "It's the {1} of all users "
                 "that are registered in the bot's leaderboard. "
                 "That means there are also people "
                 "from other servers.\n"
                 "If you only want to know your {2}, try:\n"
                 "`{prefix}{command} here`.")
rank_help = Help(r_lb_help.message.format("your position on the leaderboard", "rank-position", "server-rank", command="rank", prefix="{prefix}"))
leaderboard_help = Help(r_lb_help.message.format("the top 10 of the leaderboard", "top 10", "server-leaderboard", command="leaderboard", prefix="{prefix}"))
recording_help = Help("Messages and reactions are recorded "
                      "while the bot is online and since you were "
                      "on one Server with the bot. On servers "
                      "where the bot isn't member or "
                      "has no reading permissions "
                      "it can't record anything.")
strike_help = Help("Allows admins to strike users who act against the server rules.\n"
                   "Syntax: `{prefix}strike [add/remove/show] [user-mention]`\n"
                   "For example: `{prefix}strike show @Score#6196 `\n"
                   "This command is only usable for server-admins.\n"
                   "Getting strikes affects the score. If you have three strikes, this will reset your score to zero.")
info_help = Help("Detailed information about the bot and more.")

footer = "~ bot by Linus Bartsch | LiBa01#8817"


def post_to_dbotsorg():
    count_json = json.dumps({
        "server_count": len(client.servers)
    })

    # Resolve HTTP redirects
    dbotsorg_redirect_url = urllib.request.urlopen(
        "https://discordbots.org/api/bots/{0}/stats".format(client.user.id)
    ).geturl()

    # Construct request and post server count
    dbotsorg_req = urllib.request.Request(dbotsorg_redirect_url)

    dbotsorg_req.add_header(
        "Content-Type",
        "application/json"
    )

    dbotsorg_req.add_header(
        "Authorization",
        "<API_KEY>"
    )

    urllib.request.urlopen(dbotsorg_req, count_json.encode("ascii"))


@client.event
async def on_ready():
    print(client.user.name)
    print("--------------")
    for server in client.servers:
        if sqlib.servers.get(server.id) is None:
            sqlib.servers.add_element(server.id, {'prefix': '$'})
    post_to_dbotsorg()


@client.event
async def on_message(message):
    if message.author.bot or message.server is None:
        return

    prefix = sqlib.servers.get(message.server.id, 'prefix')[0]

    if sqlib.users.get(message.author.id) is None:
        print(message.author.id)
        sqlib.users.add_element(message.author.id, {'messages': 1})
    else:
        sqlib.users.add_to_value(message.author.id, 'messages', 1)

    if sqlib.users.get(message.author.id, 'messages')[0] % 25 == 0:
        sqlib.users.add_to_value(message.author.id, 'score', 1)

    commands = ['score', 'messages', 'reactions', 'stats', 'statistics', 'thanks', 'invite', 'prefix', 'help', 'rank',
                'leaderboard', 'lb', 'strike', 'info', 'about']

    commands = list(map(lambda cmd: prefix + cmd, commands))

    if message.content.lower().startswith(tuple(commands)):
        await client.send_typing(message.channel)

    if message.content.lower().startswith(prefix + "score"):
        if message.content[7:] == "help":
            help_embed = discord.Embed(
                title="Score",
                description=score_help.message.format(prefix=prefix),
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        score = sqlib.users.get(message.author.id, 'score')[0]

        if score > 9000:
            msg = "**over 9000!** :eight_pointed_black_star: "
        else:
            msg = str(score)

        embed = discord.Embed(
            title="Your score is:",
            description=msg,
            color=0xd5c300
        )
        await client.send_message(message.channel, embed=embed)

        try:
            await client.delete_message(message)
        except discord.Forbidden:
            pass

    elif message.content.lower().startswith(prefix + "messages"):
        if message.content[10:] == "help":
            help_embed = discord.Embed(
                title="Messages",
                description=messages_help.message,
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        messages = sqlib.users.get(message.author.id, 'messages')[0]

        embed = discord.Embed(
            title="Your recorded messages:",
            description=str(messages),
            color=0xd5c300
        )
        await client.send_message(message.channel, embed=embed)

        try:
            await client.delete_message(message)
        except discord.Forbidden:
            pass

    elif message.content.lower().startswith(prefix + "reactions"):
        if message.content[11:] == "help":
            help_embed = discord.Embed(
                title="Reactions",
                description=reactions_help.message,
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        reactions = sqlib.users.get(message.author.id, 'reactions')[0]

        embed = discord.Embed(
            title="Your recorded reactions:",
            description=str(reactions),
            color=0xd5c300
        )
        await client.send_message(message.channel, embed=embed)

        try:
            await client.delete_message(message)
        except discord.Forbidden:
            pass

    elif message.content.lower().startswith(prefix + "stats") or message.content.lower().startswith(prefix + "statistics"):
        if message.content[7:] == "help" or message.content[12:] == "help":
            help_embed = discord.Embed(
                title="Statistics",
                description=stats_help.message,
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        data = sqlib.users.get(message.author.id, 'score, messages, reactions, strikes')
        score = data[0]
        messages = data[1]
        reactions = data[2]
        strikes = data[3]

        embed = discord.Embed(
            title="Statistics",
            description="These things are not always recorded. \n"
                        "For more information, check out the `{prefix}help` !".format(prefix=prefix),
            color=0xd5c300
        )
        embed.add_field(
            name="Score",
            value=score
        )
        embed.add_field(
            name="Messages",
            value=messages
        )
        embed.add_field(
            name="Reactions",
            value=reactions
        )
        embed.add_field(
            name="Strikes",
            value=strikes
        )
        embed.set_footer(
            text=footer
        )
        await client.send_message(message.channel, embed=embed)

        try:
            await client.delete_message(message)
        except discord.Forbidden:
            pass

    elif message.content.lower().startswith(prefix + "thanks"):
        if message.content[8:] == "help":
            help_embed = discord.Embed(
                title="Thanks",
                description=thanks_help.message.format(prefix=prefix),
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        users = message.mentions

        try:
            for user in users:
                if user.id == message.author.id:
                    await client.send_message(message.channel, "I think you're a great person, "
                                                               "but you still can`t thank yourself . . . ")
                elif user.id == client.user.id:
                    await client.send_message(message.channel, "I'm thankful that you use me. :smile:\n"
                                                               "(Nevertheless I won't add points for myself.)")
                else:
                    if sqlib.users.get(user.id) is None:
                        sqlib.users.add_element(user.id, {'score': 3})
                    else:
                        sqlib.users.add_to_value(user.id, 'score', 3)
                    await client.add_reaction(message, "✅")
        except IndexError:
            await client.send_message(message.channel, "Which user do you mean? Mention him!")

    elif message.content.lower().startswith(prefix + "invite"):
        if message.content[8:] == "help":
            help_embed = discord.Embed(
                title="Invite",
                description=invite_help,
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        link = "https://discordapp.com/oauth2/authorize?client_id=342017752434999306&scope=bot&permissions=27712"
        await client.send_message(message.channel, "Invite me to your Server:\n"
                                                   "{0}".format(link))

    elif message.content.lower().startswith(prefix + "prefix"):
        if message.content[8:] == "help":
            help_embed = discord.Embed(
                title="Prefix",
                description=prefix_help.message.format(prefix=prefix),
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        if not message.channel.is_private:
            if message.author.server_permissions.administrator or message.author.id in admin_ids:
                content = message.content[8:]
                if len(content) == 1:
                    sqlib.servers.update(message.server.id, {'prefix': content})
                    await client.send_message(message.channel, "New prefix: {0}".format(content))
                elif len(content) > 1:
                    await client.send_message(message.channel, "Too long. The prefix has to be **one** character.")
                elif len(content) < 1:
                    await client.send_message(message.channel, "Too short. Write the new prefix-character behind the command!")
            else:
                await client.send_message(message.channel, "You have to be admin for that.")
        else:
            await client.send_message(message.channel, "Sorry, this is only available on servers.")

        try:
            await client.delete_message(message)
        except discord.Forbidden:
            pass

    elif message.content.lower().startswith(prefix + "help"):
        if message.content[6:] == "help":
            help_embed = discord.Embed(
                title="Help",
                description=help_help.message.format(prefix=prefix),
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        embed = discord.Embed(
            title="Help",
            description="This is a list of all commands "
                        "that the bot is able to understand. "
                        "It also includes information, "
                        "about the bot and how it works.",
            color=0xd5c300
        )
        embed.add_field(
            name=prefix + "score",
            value=score_help.message.format(prefix=prefix)
        )
        embed.add_field(
            name=prefix + "messages",
            value=messages_help.message
        )
        embed.add_field(
            name=prefix + "reactions",
            value=reactions_help.message
        )
        embed.add_field(
            name=prefix + "stats",
            value=stats_help.message
        )
        embed.add_field(
            name=prefix + "thanks",
            value=thanks_help.message.format(prefix=prefix)
        )
        embed.add_field(
            name=prefix + "invite",
            value=invite_help.message
        )
        embed.add_field(
            name=prefix + "prefix",
            value=prefix_help.message.format(prefix=prefix)
        )
        embed.add_field(
            name=prefix + "help",
            value=help_help.message.format(prefix=prefix)
        )
        embed.add_field(
            name=prefix + "rank",
            value=rank_help.message.format(prefix=prefix)
        )
        embed.add_field(
            name=prefix + "leaderboard",
            value=leaderboard_help.message.format(prefix=prefix)
        )
        embed.add_field(
            name=prefix + "strike",
            value=strike_help.message.format(prefix=prefix)
        )
        embed.add_field(
            name=prefix + "info",
            value=info_help.message
        )
        embed.add_field(
            name="About recording:",
            value=recording_help.message
        )
        embed.set_footer(
            text=footer
        )
        embed.set_author(
            name="Score",
            url="https://discordapp.com/oauth2/authorize?client_id=342017752434999306&scope=bot&permissions=27712",
            icon_url="https://cdn.discordapp.com/app-icons/342017752434999306/708aeb56555c2b2ac5099c2c2f66959b.png"
        )
        try:
            if message.author.server_permissions.administrator:
                destination = message.channel
            else:
                destination = message.author
        except AttributeError:
            destination = message.author
        await client.send_message(destination, embed=embed)
        if destination == message.author:
            # await client.add_reaction(message, "🇸")
            # await client.add_reaction(message, "🇪")
            # await client.add_reaction(message, "🇳")
            # await client.add_reaction(message, "🇹")
            await client.add_reaction(message, "✅")

    elif message.content.startswith(prefix + "rank"):
        if message.content[6:] == "help":
            help_embed = discord.Embed(
                title="Rank",
                description=rank_help.message.format(prefix=prefix),
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        leaderboard = sqlib.users.sort('score')
        mytup = sqlib.users.get(message.author.id, 'id, score')

        if message.content[6:] == "here":
            l = lambda element: message.server.get_member(element[0]) in message.server.members
            serverboard = list(filter(l, leaderboard))

            position = serverboard.index(mytup) + 1

        else:
            position = leaderboard.index(mytup) + 1

        if position == 1:
            msg = "Congratulations, you're on first position " \
                  "on the leaderboard! :trophy: "
        elif position <= 10:
            msg = "Wow, you're in the top :keycap_ten: . " \
                  "Keep going!\n" \
                  "Your position on the leaderboard: {0}".format(position)
        elif position <= 50:
            msg = "Top 50! Not bad.\n" \
                  "Your position on the leaderboard: {0}".format(position)
        else:
            msg = "Your position on the leaderboard: {0}".format(position)

        await client.send_message(message.channel, msg)

        try:
            await client.delete_message(message)
        except discord.Forbidden:
            pass

    elif message.content.startswith(prefix + "leaderboard") or message.content.startswith(prefix + "lb"):
        if message.content[13:] == "help" or message.content[4:] == "help":
            help_embed = discord.Embed(
                title="Leaderboard",
                description=leaderboard_help.message.format(prefix=prefix),
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        rank_list = sqlib.users.sort('score')
        if message.content[13:] == "here" or message.content[4:] == "here":
            rank_list = rank_list[:500]
            mode = "this server"
            server_members = message.server.members
            l = lambda element: message.server.get_member(element[0]) in server_members
            leaderboard = list(filter(l, rank_list))

            def servermember(user_id):
                return message.server.get_member(user_id)

        else:
            rank_list = rank_list[:30]
            mode = "all registered users"
            leaderboard = rank_list

            def servermember(user_id):
                for server in client.servers:
                    member_obj = server.get_member(user_id)
                    if member_obj is None:
                        continue
                    return member_obj

        many = '10'
        for i in ['15', '20', '25']:
            if i in message.content:
                many = i

        embed = discord.Embed(
            title="Leaderboard",
            description="The top {many} of {mode}.".format(many=many, mode=mode),
            color=0xd5c300
        )
        for i in range(int(many)):
            try:
                member = servermember(leaderboard[i][0])  # fehler bei Dateischreibung
                if member is None:
                    continue
                score = leaderboard[i][1]
                embed.add_field(
                    name=str(i+1)+".",
                    value=member.name + ": " + str(score),
                    inline=False
                )
            except IndexError:
                pass

        if many != '10':
            dest = message.author
            await client.add_reaction(message, '✅')
        else:
            dest = message.channel

        try:
            await client.send_message(dest, embed=embed)

            if many == '10':
                await client.delete_message(message)
        except discord.Forbidden:
            pass
    
    elif message.content.startswith(prefix + "strike"):
        if message.author.id not in admin_ids:
            try:
                if not message.author.server_permissions.administrator:
                    return
            except AttributeError:
                pass

        option = message.content[8:]

        embed = discord.Embed(
            title="Edited values",
            description="The effects of the strike(s).",
            color=0xd5c300
        )

        if option == "help" or len(message.mentions) < 1:
            embed = discord.Embed(
                title="Strike",
                description=strike_help.message.format(prefix=prefix),
                color=0xd5c300
            )
            try:
                await client.send_message(message.channel, embed=embed)
            except discord.Forbidden:
                pass
            return

        elif option.startswith("add"):
            for mention in message.mentions:
                sqlib.users.add_to_value(mention.id, 'strikes', 1)
                embed.add_field(
                    name=mention.name,
                    value="{0} has {1} strike(s) now.".format(mention.name, sqlib.users.get(mention.id, 'strikes')[0])
                )

                sqlib.users.add_to_value(mention.id, 'score', -10)

                if sqlib.users.get(mention.id, 'strikes')[0] >= 3 and not sqlib.users.get(mention.id, 'messages')[0] <= 0:
                    sqlib.users.update(mention.id, {'score': 0})

                embed.add_field(
                    name="New score",
                    value=sqlib.users.get(mention.id, 'score')[0],
                    inline=False
                )

        elif option.startswith("remove"):
            for mention in message.mentions:
                if sqlib.users.get(mention.id, 'strikes')[0] <= 0:
                    await client.send_message(message.channel, "{0} has no strikes.".format(mention.name))
                    if len(message.mentions) <= 1:
                        return
                    else:
                        continue

                sqlib.users.add_to_value(mention.id, 'strikes', -1)
                embed.add_field(
                    name=mention.name,
                    value="{0} has {1} strike(s) now.".format(mention.name, sqlib.users.get(mention.id, 'strikes')[0]),
                )

        elif option.startswith("show"):
            mention = message.mentions[0]

            embed = discord.Embed(
                title=mention.name,
                description="{0} has {1} strike(s).".format(mention.name, sqlib.users.get(mention.id, 'strikes')[0]),
                color=0xd5c300
            )

        try:
            await client.send_message(message.channel, embed=embed)
        except discord.errors.Forbidden:
            pass
    
    elif message.content.startswith(prefix + 'setscore'):
        if message.author.id not in admin_ids:
            return 0
        
        content = message.content.split(' ')[1]
        
        sqlib.users.update(message.mentions[0].id, {'score': int(content)})

    elif message.content.lower().startswith((prefix + 'info', prefix + 'about')):
        if message.content[6:] == "help" or message.content[7:] == "help":
            help_embed = discord.Embed(
                title="Info/About",
                description=info_help.message,
                color=0xd5c300
            )
            await client.send_message(message.channel, embed=help_embed)
            return 0

        infotext = discord.Embed(
            title="Score",
            description="About the bot.",
            color=0xd5c300,
            url="https://liba001.github.io/Score/"
        )
        infotext.set_author(
            name="Linus Bartsch | LiBa01#8817",
            url="https://liba001.github.io/",
            icon_url="https://avatars0.githubusercontent.com/u/30984789?s=460&v=4"
        )
        infotext.set_thumbnail(
            url="https://images.discordapp.net/avatars/342017752434999306/708aeb56555c2b2ac5099c2c2f66959b.png?size=512"
        )
        infotext.add_field(
            name="Developer",
            value="Name: **Linus Bartsch**\n"
                  "Discord: **LiBa01#8817**\n"
                  "GitHub: [LiBa001](https://github.com/LiBa001)\n"
                  "I'm also at [Discordbots.org](https://discordbots.org/user/269959141508775937)",
            inline=True
        )
        infotext.add_field(
            name="Developed in:",
            value="Language: **Python3.6**\n"
                  "Library: **discord.py** (0.16.8)\n"
        )
        infotext.add_field(
            name="Commands",
            value="Type `{0}help` to get all commands.\n"
                  "Join the [Official Support Server](https://discord.gg/z3X3uN4) "
                  "if you have any questions or suggestions.".format(prefix)
        )
        infotext.add_field(
            name="Stats",
            value="Server count: **{0}**\n"
                  "Uptime: **{1}** hours, **{2}** minutes\n"
                  "Member count: {3}".format(len(client.servers), up_hours, up_minutes, len(list(client.get_all_members())))
        )
        infotext.set_footer(
            text="Special thanks to MaxiHuHe04#8905 who supported me a few times."
        )

        await client.send_message(message.channel, embed=infotext)
    
    elif client.user in message.mentions:
        await client.send_message(message.channel, "Type `{0}help` to see available commands.".format(prefix))


@client.event
async def on_member_join(member):
    if sqlib.users.get(member.id) is None:
        sqlib.users.add_element(member.id)


@client.event
async def on_reaction_add(reaction, user):
    if sqlib.users.get(user.id) is None:
        print(user.id)
        sqlib.users.add_element(user.id, {'reactions': 1})

    elif (not user.bot) and reaction.message.server is not None:
        reacts = sqlib.users.add_to_value(user.id, 'reactions', 1)
        if reacts % 5 == 0:
            sqlib.users.add_to_value(user.id, 'score', 1)

@client.event
async def on_reaction_remove(reaction, user):
    if (not user.bot) and reaction.message.server.id is not None:
        reacts = sqlib.users.add_to_value(user.id, 'reactions', -1)
        if reacts % 5 == 0:
            sqlib.users.add_to_value(user.id, 'score', -1)

@client.event
async def on_server_join(server):
    post_to_dbotsorg()
    if sqlib.servers.get(server.id) is None:
        sqlib.servers.add_element(server.id, {'prefix': '$'})

    await client.send_message(server.owner, "Hey, thank you that you or an other admin "
                                            "invited me to your server '{0}' :slight_smile: \n"
                                            "My default command prefix is `$`. "
                                            "For more information, please type `$help`!".format(server.name))


async def uptime_count():
    await client.wait_until_ready()
    global up_hours
    global up_minutes
    up_hours = 0
    up_minutes = 0

    while not client.is_closed:
        await asyncio.sleep(60)
        up_minutes += 1
        if up_minutes == 60:
            up_minutes = 0
            up_hours += 1


client.loop.create_task(uptime_count())
client.run("[BOT-TOKEN]")  # insert token
