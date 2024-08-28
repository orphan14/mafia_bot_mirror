# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

import lightbulb
from dotenv import load_dotenv
import os


env_path = os.path.join(os.path.dirname(__file__), '.', '.env')
load_dotenv(dotenv_path=env_path)

BOT_TOKEN = os.getenv("BOT_TOKEN")
print(BOT_TOKEN)
#Test block
"""
from extensions.Graph.Graph import *
from extensions.data_classes import *
queue = [Queue(1,"test_one"),Queue(2,"test_two"),Queue(3,"test_three"),Queue(4,"test_four")]
m_one_two = Matchup(1,2,10,0,0)
m_one_three = Matchup(1,3,30,0,0)
m_one_four = Matchup(1,4,30,0,0)

m_two_one = Matchup(2,1,2,0,0)
m_two_three = Matchup(2,3,None,0,0)
m_two_four = Matchup(2,4,2,0,0)

m_three_one = Matchup(3,1,30,0,0)
m_three_two = Matchup(3,2,None,0,0)
m_three_four = Matchup(3,4,1,0,0)

m_four_one = Matchup(4,1,25,0,0)
m_four_two = Matchup(4,2,1,0,0)
m_four_three = Matchup(4,3,1,0,0)

matchups = [m_one_two,
            m_one_three,
            m_one_four,
            m_two_one,
            m_two_three,
            m_two_four,
            m_three_one,
            m_three_two,
            m_three_four,
            m_four_one,
            m_four_two,
            m_four_three
            ]

g = MatchGraph(queue,matchups)
g.brute_force_pair()
del g

g = MatchGraph(queue,matchups)
#g.brute_force_pair()
g.remove_edge_pair()
"""

bot = lightbulb.BotApp(token=BOT_TOKEN,default_enabled_guilds=(1070099489030950942,1071826244527726682))
bot.load_extensions("extensions.admin_extensions")
bot.load_extensions("extensions.user_functions_extensions")
bot.load_extensions("extensions.user_registration_extensions")

bot.run()