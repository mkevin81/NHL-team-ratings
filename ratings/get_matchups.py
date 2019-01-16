# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 12:49:26 2019

@author: Marc-Kevin
"""

import pandas as pd

def get_matchups(date):
#date in yyyy-mm-dd

    url = 'https://www.hockey-reference.com/leagues/NHL_2019_games.html'
    schedule = pd.read_html(url)[0]
    schedule.drop(['G','G.1','Unnamed: 5','Att.','LOG','Notes'],axis=1,inplace=True)
    games = schedule[schedule['Date']==f'{date}']
    matchups = games[['Visitor','Home']].values.tolist()
    
    return matchups