# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 12:51:16 2019

@author: Marc-Kevin
"""

import pandas as pd
from collections import Counter
from sklearn.preprocessing import StandardScaler

def fw_ratings(team):
    url = 'http://www.puckon.net/?_ga=2.210512981.1165101973.1547008033-2109006389.1546797137'
    raw = pd.read_html(url,header=1)[0]
    raw_cut = raw[['Team','GP','SA.1','ESVA.1']]
    df = raw_cut[['SA.1','ESVA.1']]
    get_names = df.columns
    scaler = StandardScaler()
    scaled_df = scaler.fit_transform(df)
    scaled_df = pd.DataFrame(scaled_df,columns=get_names)
    new = pd.concat([scaled_df,raw_cut[['Team']]],axis=1)
    sa = pd.pivot_table(new,values = 'SA.1',columns = 'Team')
    esva = pd.pivot_table(new,values = 'ESVA.1',columns = 'Team')
    rating_lst = []

    if team in sa.columns:
        sa_1 = sa.loc['SA.1',f'{team}']
        esva_1 = esva.loc['ESVA.1',f'{team}']
        rating = -1.7051343491288098e-15 -0.19222278*sa_1 + 0.28562659*esva_1
        return rating
    elif team == 'league':

        for t in sa.columns:
            sa_1 = sa.loc['SA.1',f'{t}']
            esva_1 = esva.loc['ESVA.1',f'{t}']
            rating = -1.7051343491288098e-15 -0.19222278*sa_1 + 0.28562659*esva_1
            rating_lst.append(rating)

        keys = sa.columns
        values = rating_lst
        r_dict = dict(zip(keys,values))
        rating_df = pd.DataFrame(r_dict,index=[0])
        rating_df = pd.melt(rating_df,var_name='Tm',value_name='Fw_rating')
        rating_df['Tm'].replace({'L.A':'LAK','N.J':'NJD','S.J':'SJS','T.B':'TBL','VGK':'VEG'},inplace=True)
        
        return rating_df

    else:
        print('Not Happening')


def sp_ratings():

    t_lst = []

    team_lst = ['TBL','TOR','BOS','BUF','MTL','FLA','DET','OTT','WSH','PIT',
            'CBJ','NYI','NYR','CAR','NJD','PHI','WPG','NSH','DAL','COL',
           'MIN','CHI','STL','CGY','VEG','SJS','ANA','VAN','EDM','ARI','LAK']

    for team in team_lst:
        url = f'https://www.hockey-reference.com/teams/{team}/2019_gamelog.html'
        df = pd.read_html(url,header=1)[0]
        df.columns = ['GP', 'Date', 'Loc', 'Opponent', 'GF', 'GA', 'Win/Loss',
                      'OT/SO', 'Unnamed: 8', 'S', 'PIM', 'PPG', 'PPO', 'SHG',
                      'Unnamed: 14', 'S.1', 'PIM.1', 'PPG.1', 'PPO.1', 'SHG.1', 'Unnamed: 20',
                      'CF', 'CA', 'CF%', 'FF', 'FA', 'FF%', 'FOW', 'FOL', 'FO%', 'oZS%',
                      'PDO']
         #df.drop(['Unnamed: 8','Unnamed: 14','Unnamed: 20','S', 'PIM', 'PPG', 'PPO', 'SHG',
         #   'Unnamed: 14', 'S.1', 'PIM.1', 'PPG.1', 'PPO.1', 'SHG.1', 'Unnamed: 20'],axis=1,inplace=True)
        df['Loc'] = df['Loc'].fillna('H')
        df['OT/SO'] = df['OT/SO'].fillna('reg')
        df['Tm'] = f'{team}'
        df.set_index(['Date'],inplace=True)

        t_lst.append(df)

    season = pd.concat(t_lst)
    season = season[['GP','Loc','GF','GA','Win/Loss','PIM','PPG','PPO','PIM.1','PPG.1','PPO.1','Tm']]
    to_nums = ['GP','GF','GA','PIM','PPG','PPO','PIM.1','PPG.1','PPO.1']
    season.drop('Date',inplace=True)
    season.dropna(inplace=True)
    season[to_nums] = season[to_nums].apply(pd.to_numeric)
    df = season.groupby(['Tm']).sum()
    gp = dict(Counter(season['Tm']))
    d = pd.DataFrame.from_dict(gp,orient='index',columns=['Gp'])
    d.reset_index(inplace=True)
    d.columns = ['Tm','Gp']
    sp_summ = df.merge(d,on='Tm')
    sp_summ.drop(['GP'],axis=1,inplace=True)

    sp_summ.set_index('Tm',inplace=True)
    for stat in sp_summ.columns:
        sp_summ[f'{stat}'] = sp_summ[f'{stat}']/sp_summ['Gp']
    rating = sp_summ.round(3)
    osp_rating = rating[['PPG','PPO']]
    dsp_rating = rating[['PPG.1','PPO.1']]
    fr = pd.merge(osp_rating,dsp_rating,on='Tm')
    fr['PPG/O'] = fr['PPG'] / fr['PPO']
    fr['oPPG/O'] = fr['PPG.1'] / fr['PPO.1']
    fr.reset_index(inplace=True)
    return fr[['Tm','PPO','PPO.1','PPG/O','oPPG/O']]

def ovr_rankings():

    ovr = fw_ratings('league')
    st = sp_ratings()
    df = pd.merge(ovr,st,on='Tm')
    df['PPG/g'] = df['PPO']*df['PPG/O']
    df['oPPG/g'] = df['PPO.1']*df['oPPG/O']
    df['SPdiff'] = df['PPG/g'] - df['oPPG/g']
    df['ovr_rating'] = df['Fw_rating'] + df['SPdiff']
    
    return df[['Tm','ovr_rating']].sort_values(by='ovr_rating',ascending=False).reset_index(drop=True)

