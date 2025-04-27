Discord Transport Info Bot
Summary:
Developed a feature-rich Discord bot in Python using discord.py, requests, and BeautifulSoup to provide real-time UK public transport information.

Key Features:

Train Times:

Users can fetch the next train departures from any UK railway station using the /train command.

Data retrieved from a live Huxley2 API endpoint, formatted for easy reading within Discord.

Bus Stop Finder:

/bus command searches for nearby bus stops based on a given location or postcode.

Uses web scraping (BeautifulSoup) to parse and present available bus stops from NextBuses.mobi.

/busselect command lets users select a specific bus stop and view upcoming departures.

Interactive Server Support:

Welcomes new users and servers with onboarding messages.

Handles user-specific sessions for bus stop selections, ensuring personalised and intuitive interactions.

Technologies Used:

Python 3.11+

discord.py (for bot commands and events)

Requests (for RESTful API access)

BeautifulSoup (for web scraping)


Notable:

Emphasis on clean, asynchronous programming (async/await) for smooth performance.

Error handling for API failures and invalid user inputs to ensure robustness.

Custom welcome messages for both direct messages and server system channels.
