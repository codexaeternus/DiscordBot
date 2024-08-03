import discord
from discord.ext import commands
import mysql.connector
import bcrypt

# MySQL database configuration
db_config = {
    'host': 'YourIPHere',
    'user': 'YourUsernameHere',
    'password': 'DatbasePassword',
    'database': 'DatabaseName'
}

# Discord bot token
TOKEN = 'DiscordToken'

intents = discord.Intents.default()
intents.members = True  # Enable the 'members' intent

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.command()
async def register(ctx, login: str = None, email: str = None, password: str = None, repassword: str = None):
    if not login or not email or not password or not repassword:
        await ctx.send('Please provide all the required arguments: login, email, password, repassword')
        return
    
    cnx = mysql.connector.connect(**db_config)
    cursor = cnx.cursor()

    # Check if the Discord account is already bound
    cursor.execute("SELECT * FROM users WHERE discordid = %s", (str(ctx.author.id),))
    result = cursor.fetchone()
    if result:
        await ctx.send('You already have an account.')
        cursor.close()
        cnx.close()
        return
    
    # Check if the username or email already exists
    cursor.execute("SELECT * FROM users WHERE username = %s OR email = %s", (login, email))
    result = cursor.fetchone()
    if result:
        await ctx.send('An account with the same username or email already exists.')
        cursor.close()
        cnx.close()
        return
    
    # Check if the passwords match
    if password != repassword:
        await ctx.send('The passwords do not match.')
        cursor.close()
        cnx.close()
        return
    
    # Check the length of the login
    if len(login) < 3 or len(login) > 12:
        await ctx.send('Invalid login length.')
        cursor.close()
        cnx.close()
        return
    
    # Check if the login contains only alphanumeric characters
    if not login.isalnum():
        await ctx.send('Invalid login format. Only alphanumeric characters are allowed.')
        cursor.close()
        cnx.close()
        return
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    # Insert the user into the database
    insert_query = "INSERT INTO users (username, password, email, autoridade, secure_login, secure_token, discordid) VALUES (%s, %s, %s, %s, %s, %s, %s)"
    user_data = (login, hashed_password, email, 0, '1', '', str(ctx.author.id))
    cursor.execute(insert_query, user_data)
    cnx.commit()
    
    await ctx.send('Account created successfully. Enjoy!')
    
    cursor.close()
    cnx.close()

bot.run(TOKEN)
