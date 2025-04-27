import discord
import requests
from discord.ext import commands
from bs4 import BeautifulSoup

TOKEN = INSERTOWNTOKEN

# Set up bot with command prefix (not needed for slash commands)
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Store user-specific bus stop search results
bus_stop_results = {}

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    intro_message = (
        
    )
    for guild in bot.guilds:
        for channel in guild.text_channels:
            if channel.permissions_for(guild.me).send_messages:
                await channel.send(intro_message)
                break

@bot.event
async def on_message(message):
    if message.channel.type == discord.ChannelType.private and not message.author.bot:
        await message.channel.send("Hello! 👋 Thanks for adding me to your server! 🚆🚌\n"
        "To see train departures, type `/train` followed by a UK railway station name.\n"
        "To find bus departures, type `/bus` followed by an address or postcode.\n"
        "Use `/busselect` to pick a bus stop and display the times for it.\n"
        "Bot maintained by Kenneth Munro. ")


@bot.event
async def on_guild_join(guild):
    welcome_message = (
        "Hello! 👋 Thanks for adding me to your server! 🚆🚌\n"
        "To see train departures, type `/train` followed by a UK railway station name.\n"
        "To find bus departures, type `/bus` followed by an address or postcode.\n"
        "Use `/busselect` to pick a bus stop and display the times for it.\n"
        "Bot maintained by Kenneth Munro. "
    )
    
    # Try to send the message to the system channel
    if guild.system_channel and guild.system_channel.permissions_for(guild.me).send_messages:
        await guild.system_channel.send(welcome_message)
    else:
        # If no system channel, try sending a DM to the server owner
        try:
            await guild.owner.send(welcome_message)
        except Exception as e:
            print(f"Could not send welcome message to {guild.owner}: {e}")

@bot.tree.command(name="train", description="Get train times for a station")
async def train(interaction: discord.Interaction, station_code: str):
    """Fetches train times for a given station!!"""
    url = f"https://huxley2.azurewebsites.net/all/{station_code}?expand=true"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        departures = data.get("trainServices", [])
        if departures:
            reply = f"👋 Here are the next trains leaving from {station_code.upper()}:\n"
            for train in departures[:5]:  # Show next 5 trains
                destination = train["destination"][0]["locationName"]
                scheduled = train.get("sta", "N/A")
                platform = train.get("platform", "Unknown")
                etd = train.get("etd", "N/A")
                delay = "On time" if etd == "On time" else f"Sadly, this train will be delayed until {etd}"
                reply += f"{destination} - {scheduled} (Platform {platform}) - {delay}\n"
        else:
            reply = "Oops...no departures found for this station!"
    else:
        reply = "Error fetching train times!"
    
    await interaction.response.send_message(reply)

@bot.tree.command(name="bus", description="Search for your bus stop")
async def bus(interaction: discord.Interaction, location: str):
    """Search for bus stops near a location."""
    search_url = f"https://www.nextbuses.mobi/WebView/BusStopSearch/BusStopSearchResults?id={requests.utils.quote(location)}"
    response = requests.get(search_url)
    
    if response.status_code != 200:
        await interaction.response.send_message("Oops... an error fetching bus stops. Please try again!!")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    stop_elements = soup.select('.Stops a')
    stops = [(stop.text.strip(), f"https://www.nextbuses.mobi{stop['href']}") for stop in stop_elements if len(stop.text.strip()) >= 2 and "Show this Stop Only" not in stop.text]
    
    if not stops:
        await interaction.response.send_message("No bus stops found for this location! :( ")
        return
    
    bus_stop_results[interaction.user.id] = stops
    response_text = "**Select a bus stop by typing `/busselect <number>`**\n"
    response_text += "\n".join([f"**{i+1}.** {name}" for i, (name, _) in enumerate(stops)])
    
    await interaction.response.send_message(response_text)

@bot.tree.command(name="busselect", description="Get bus times for a selected stop")
async def busselect(interaction: discord.Interaction, stop_number: int):
    """Retrieve bus departure times for a chosen stop."""
    stops = bus_stop_results.get(interaction.user.id)
    if not stops or stop_number < 1 or stop_number > len(stops):
        await interaction.response.send_message("Invalid selection. Please search with `/bus` first.")
        return
    
    stop_name, stop_url = stops[stop_number - 1]
    response = requests.get(stop_url)
    
    if response.status_code != 200:
        await interaction.response.send_message("Error fetching bus times. Please try again.")
        return
    
    soup = BeautifulSoup(response.text, 'html.parser')
    table_rows = soup.select('#departure-list .BusStops tr')
    
    if not table_rows:
        await interaction.response.send_message(f"No departures found for {stop_name}.")
        return
    
    departures = []
    for row in table_rows[:5]:  # Show next 5 departures
        number = row.select_one('td.Number .Stops a').text.strip()
        dest_time = row.select_one('td:nth-child(2) .Stops').text.strip().split('(')
        destination = dest_time[0].strip()
        departure_time = dest_time[1].replace(')', '').strip() if len(dest_time) > 1 else 'N/A'
        departures.append(f"**{number}** to {destination} ✔️ {departure_time}")
    
    response_text = f"** Hi! 👋 Here are the next buses to leave from {stop_name}:**\n" + "\n".join(departures)
    await interaction.response.send_message(response_text)

@bot.event
async def setup_hook():
    await bot.tree.sync()

bot.run(TOKEN)
