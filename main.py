import streamlit as st
import pandas as pd
import numpy as np
import random
import re
import time
import heapq
#import functions


st.set_page_config(layout="wide")
#st.write(st.session_state)


if "cards" not in st.session_state:
    st.session_state['cards'] = {}

if "teams" not in st.session_state:
    st.session_state['teams'] = []

if "number_of_teams" not in st.session_state:
    st.session_state['number_of_teams'] = 3


if "latest_prel_time" not in st.session_state:
    st.session_state['latest_prel_time'] = -5

#st.session_state.latest_prel_time

if "groups_new_positions" not in st.session_state:
    st.session_state.groups_new_positions = []

if "result" not in st.session_state:
    st.session_state.result = []

if "winner_time" not in st.session_state:
    st.session_state.winner_time = 100000



if "attackers_in_turn" not in st.session_state:
    st.session_state.attackers_in_turn = []


if "group_to_move" not in st.session_state:
    st.session_state['group_to_move'] = 0

if "play_round" not in st.session_state:
    st.session_state['play_round'] = False

if "track" not in st.session_state:
    st.session_state['track'] = '11112222FFFFFFFFF'

if "checkfall2" not in st.session_state:
    st.session_state['checkfall2'] = False

if "round" not in st.session_state:
    st.session_state['round'] = 0

if "team_to_choose" not in st.session_state:
    st.session_state['team_to_choose'] = 'Me'

if "track" not in st.session_state:
    st.session_state['track'] = '-F'

if "trackname" not in st.session_state:
    st.session_state['trackname'] = ''

if "riders" not in st.session_state:
    st.session_state.riders = []

if "level" not in st.session_state:
    st.session_state.level = 0

if "game_started" not in st.session_state:
    st.session_state.game_started = False

if "riders2" not in st.session_state:
    st.session_state.riders2 = []

if "rdf" not in st.session_state:
    st.session_state['rdf'] = pd.DataFrame()

if "confirmcards" not in st.session_state:
    st.session_state['confirmcards'] = []

if "gcdf" not in st.session_state:
    st.session_state['gcdf'] = pd.DataFrame()

if "placering" not in st.session_state:
    st.session_state['placering'] = 0

if "ryttervalg2" not in st.session_state:
    st.session_state.ryttervalg2 = 'select'

if "ryttervalg" not in st.session_state:
    st.session_state.ryttervalg = 'select'

if "human_chooses_cards" not in st.session_state:
    st.session_state.human_chooses_cards = 9

if "ready_for_calculate" not in st.session_state:
    st.session_state.ready_for_calculate = False

if "computer_chooses_cards" not in st.session_state:
    st.session_state.computer_chooses_cards = True

if "goto3" not in st.session_state:
    st.session_state.goto3   = False

if "sprint_groups" not in st.session_state:
    st.session_state.sprint_groups   = []


def visrytterkort(ryttervalg):
    a, b, c, d = random.sample(range(len(cards[ryttervalg]['cards'])), 4)
    col1.radio('hvilket kort?',
                   (cards[ryttervalg]['cards'][a], cards[ryttervalg]['cards'][b], cards[ryttervalg]['cards'][c], cards[ryttervalg]['cards'][d]))


def get_points(df, level):
    points = 30
    ratio = 1
    df = df.sort_values(by='ranking')
    for rider in df[df.team == 'Me']['NAVN'].tolist():
        points = points + ratio * (9 - int(df[df.NAVN == rider]['ranking'])) ** 2
        points = points - ratio * (int(df[df.NAVN == rider]['favorit']) ** 2) / 2
        ratio = ratio / 3

    points = points * (level + 10)
    return int(points)


def has_numbers(inputString):
    return bool(re.search(r'\d', inputString))

def convert_to_seconds(number):

    #number = number ## + random.randint(int(-number**+.5),int(number**+.5))
    minutes = int(np.floor(number/60))
    seconds = str(int(np.floor(number - minutes*60)))
    if len(seconds)<2:

        seconds = "0" + seconds
    return (str(minutes)+':'+str(seconds))


def convert_to_seconds_plain(number):

    minutes = int(np.floor(number/60))
    seconds = str(int(np.floor(number - minutes*60)))
    if len(seconds)<2:

        seconds = "0" + seconds
    return (str(minutes)+':'+str(seconds))

def get_slipstream_value(pos1, pos2, track):
    pos1 = int(pos1)
    pos2 = int(pos2)
    if '0' in track[pos1:pos2+1]:
        return 0
    if '1' in track[pos1:pos2+1]:
        return 1
    else:
        return 2

def tjek_stejl(pos1, pos2, track):
    pos1 = int(pos1)
    pos2 = int(pos2)
    if '0' in track[pos1-1:pos2]:
        return 1
    else:
        return 0

generate = False


def get_value(track):
    #st.write(track)
    tr = track[0:track.find('F') + 1]

    tr = tr.replace('_', '2')

    tr = list(tr)

    tr = tr[0:tr.index('F')]
    #st.write(tr)
    sum = 0
    for number in tr:
        #st.write(number)
        sum = int(number) + sum
    #st.write('success')
    return 100*(2 - sum / len(tr))**2

def get_length(track):
    tr = track[0:track.find('F') + 1]
    tr = tr.replace('2', '6')
    tr = tr.replace('_', '9')
    tr = tr.replace('1', '3')
    tr = tr.replace('0', '2')

    tr = list(tr)

    for i in reversed(range(len(tr))):

        if tr[i] in ['1', '2', '3', '4', '5', 'F']:
            last = tr[i]

        if tr[i] == '^' or tr[i] == '*':
            tr[i] = last

    tr = tr[0:tr.index('F')]
    sum = 0
    for number in tr:
        if number == 'F':
            break
        else:
            sum = int(number) + sum

    # sum
    # tr = tr.replace('^',last)

    for number in tr[-13::]:
        sum = sum - int(number) * 0.23
        # print(number)

    sum = sum / 6
    return int(sum)


def detect_sprint_groups(df):
    sprint_groups = []

    for gro_pos in df.position.unique():
        if gro_pos > track.find('F') - 1:
            sprint_groups.append(df[df['position'] == gro_pos].group.tolist()[0])


    sprint_groups.sort()
            # col3.write('group' + str(group_numbers[i]) + 'sprints')

    return sprint_groups



def check_vedhang(moved_fields, pos2, track):
    pos1 = pos2 - moved_fields
    vedhang = 0
    if has_numbers(track[pos1:pos2]):
        vedhang = int(list(filter(str.isdigit, track[pos1:pos2]))[0])

    return vedhang


def sprint(sprint_groups, cards, df, winner_time, result, latest_pt, sprint_type):
    for sprint_group in sprint_groups:
        for rider in cards:
            if cards[rider]['group'] == sprint_group:
                for card in cards[rider]['discarded']:
                    cards[rider]['cards'].append(card)
                cards[rider]['discarded'] = []
                random.shuffle(cards[rider]['cards'])

                cards_available = []

                tk_penalty = 0
                if sprint_type in [0,1]:
                    sprint_value = 2
                if sprint_type == 2:
                    sprint_value = 1
                for i in range(0, min(4, len(cards[rider]['cards']))):
                    cards_available.append(cards[rider]['cards'][i][sprint_value])

                for i in range(4, min(8, len(cards[rider]['cards']))):
                    if cards[rider]['cards'][i][0] == 'kort: 16':
                        tk_penalty = tk_penalty+1

                while len(cards_available) < 4:
                    cards_available.append(2)

                cards_available.sort(reverse=True)
                #st.write(rider, cards[rider]['sprint'], cards_available)
                cards[rider]['sprint_points'] = cards[rider]['sprint'] * 1.05 + cards_available[0] + cards_available[1] + \
                                                cards_available[2] * 0.01 + cards_available[3] * 0.001 - tk_penalty
                #st.write(cards[rider]['sprint_points'])
                cards[rider]['tk_penalty'] = tk_penalty

        sorted(cards.items(), key=lambda item: (item[1]["sprint_points"]), reverse=True)
        #df.loc[df['group'] == sprint_group, ['prel_time']] = df.loc[df['group'] == sprint_group, ['prel_time']].min()
        df = df.sort_values(by='prel_time', ascending=True)
        winner_time = min(winner_time, df[df.group == 1]['prel_time'].min())
        df['time'] = df['prel_time'] - winner_time
        latest_pt = max(df[df.group == sprint_group].time.tolist()[0], latest_pt + 5)

        col4.header('SPRINT: GROUP ' + str(sprint_group))
        col4.markdown('(' + convert_to_seconds(latest_pt) + ')')
        col4.markdown('(Position:' + str(df[df.group == sprint_group].position.tolist()[0]) + ')' )

        for rider in sorted(cards.items(), key=lambda item: (item[1]["sprint_points"]), reverse=True):
            # print(, 'points')
            if cards[rider[0]]['group'] == sprint_group:
                st.session_state['placering'] = st.session_state['placering'] + 1
                col4.caption(str(st.session_state['placering']) + '. ' + str(rider[0]) + ' - ' + str(int(cards[rider[0]]['sprint_points'])) + ' ' + 'sprint points' + ' (Sprint stat: ' + str(int(cards[rider[0]]['sprint'])) + ' + TK_penalty: ' + str(cards[rider[0]]['tk_penalty']))
                result.append([st.session_state['placering'], str(rider[0]), convert_to_seconds(df[df.group == sprint_group].time.tolist()[0]), df[df.NAVN == rider[0]].team.tolist()[0]])
                cards[rider[0]]['ranking'] = st.session_state['placering']

    return cards, df, winner_time, result, latest_pt




def transfer_ECs(df, dict):
    st.write('transfer ECs')
    sdf = df[df.method_takes_ECs == 1]
    for rider in sdf.NAVN.tolist():
        ECs = int(sdf[sdf.NAVN == rider].ECs)
        #st.write(rider + ':' + str(ECs) + 'ECs')
        for i in range(ECs):
            dict[rider]['cards'].insert(0, ['EC 15',2,2])
            #
            #st.write('done')

    #df['ECs'] = 0

    return dict

def transfer_groups(df, dict):
    #st.write('transfer ECs')
    for rider in df.NAVN.tolist():
        group = int(df[df.NAVN == rider].group)
        #st.write(rider + ':' + str(ECs) + 'ECs')

        dict[rider]['group'] = group

    return dict


def pick_value(rider, track):

    favorit = rider['favorit']
    if rider['attacking_status'] == 'attacker':
        ideal_move = 100
        uphill = True

    #if random.random() < favorit * 1.5 / 100:
        #ideal_move = 100

    #random.shuffle(rider['cards'])

    # for card in rider['cards'][0:4]:
    # st.write(str(card[0]) + '-' + str(card[1]) + '-' + str(card[2]))

    else:
        len_left = track.find('F') - rider['position']
        print(len_left)
        diff_left = len_left / get_length(track)

        # jo længere til mål, jo lavere
        ideal_move = 8 - (len_left / (20 / (favorit + 2) ** 0.3))

        ideal_move = ideal_move - 1 + 2 * rider['takes_lead']
        uphill = False


        if track[rider['position']] == '_':
            ideal_move = -10
        #/// check if correct
        #if '0' in track[rider['position']:rider['position']+7]:
        #    ideal_move = ideal_move / 2 + (1.5 * diff_left)
        #    uphill = True

        #if '1' in track[rider['position']:rider['position']+7]:
        #    ideal_move = (1.5 * diff_left) + ideal_move / 2
        #    uphill = True



        ideal_move = ideal_move + rider['favorit']/5
        ideal_move = ideal_move - random.random() * 2
        # st.write(rider)
    # st.write(ideal_move)
    selected = rider['cards'][0]

    penalty = 0

    for card in rider['cards'][0:4]:
        #st.write(card[1], 'in pick_value')

        if card[1] == -1:
            penalty = 1

    if uphill == True:
        for card in rider['cards'][0:4]:
            value = card[2] - penalty
            if abs(value - ideal_move) + card[1] / 100 < abs(selected[2] - ideal_move) + selected[1] / 100:
                selected = card
                print(selected)

    if uphill == False:
        print(rider['cards'][0:4])
        for card in rider['cards'][0:4]:
            value = card[1]-penalty
            print(abs(card[1] - ideal_move))
            print(abs(selected[1] - ideal_move))

            if abs(value - ideal_move) < abs(selected[1] - ideal_move):
                print('yes')
                selected = card
                #print('selected' + selected)

    # st.write('selected=' + str(selected[0]))

    #rider['played_card'] = selected
    #rider['cards'].remove(selected)
    #st.write(rider, selected)
    #//// selected must be either number 1 or 2
    if track[rider['position']:rider['position']+selected[1]] == '2' * selected[1]:
        selected = selected[1]

    else:
        selected = selected[2]

    return selected - penalty



def next_to_choose(team_to_choose, teams):
    return teams[(teams.index(team_to_choose)+1) % len(teams)]

def colour_track(track):
    stigning = 0
    #track = track.replace('*','')
    track2 = track
    i = 0

    while i < 20:
        # print('s2',stigning)
        # print(track2)
        # print(track2[stigning:])

        if track2.replace('0','1')[stigning:].find('1') == -1:
            break

        stigning = track2.replace('0','1')[stigning:].find('1') + stigning
        # print('stigning', stigning)

        track2 = track2[0:stigning] + ':red[' + track2[stigning:]
        # print(track2)

        ned_igen = track2[stigning:].find('_')
        if ned_igen == -1:
            ned_igen = 1000

        ned_igen2 = track2[stigning:].find('2')
        if ned_igen2 == -1:
            ned_igen2 = 1000

        ned_igen = min(ned_igen, ned_igen2)

        if ned_igen == 1000:
            i = 21

        # print(ned_igen)

        track2 = track2[0:stigning + ned_igen] + ']' + track2[stigning + ned_igen:]
        stigning = stigning + ned_igen + 2
        # print('s',stigning)

    nedad = 0

    i = 0
    # blue
    while i < 20:

        if track2[nedad:].find('_') == -1:
            break

        nedad = track2[nedad:].find('_') + nedad
        # print('stigning', stigning)

        track2 = track2[0:nedad] + ':blue[' + track2[nedad:]
        # print(track2)

        ned_igen = track2[nedad:].find('2')
        if ned_igen == -1:
            ned_igen = 1000

        ned_igen2 = track2.replace('0','1')[nedad:].find('1')
        if ned_igen2 == -1:
            ned_igen2 = 1000

        ned_igen = min(ned_igen, ned_igen2)

        if ned_igen == 1000:
            i = 21

        # print(ned_igen)

        track2 = track2[0:nedad + ned_igen] + ']' + track2[nedad + ned_igen:]
        nedad = nedad + ned_igen + 2
        # print('s',stigning)

    if track2.find('F')>-1:

        track2 = track2[0:track2.find('F')] + ':green[F]' + track2[track2.find('F')+1:]
    # blue

    return track2


def get_number_ecs(rider):
    ecs = 0
    for card in rider['cards']:
        if card[0] == 'kort: 16':
            ecs = ecs + 1
    for card in rider['discarded']:
        if card[0] == 'kort: 16':
            ecs = ecs + 1

    return ecs

def get_fatigue(rider):
    #ecs = get_number_ecs(rider)
    ecs = 0
    for card in rider['cards']:
        if card[1] == -1:
            ecs = ecs + 1
    for card in rider['discarded']:
        if card[1] == -1:
            ecs = ecs + 1

    ecs = ecs*1.5 + get_number_ecs(rider)

    return ecs / (len(rider['cards']) + len(rider['discarded']))

def get_number_tk1(rider):
    ecs = 0
    for card in rider['cards']:
        if card[1] == -1:
            ecs = ecs + 1
    for card in rider['discarded']:
        if card[1] == -1:
            ecs = ecs + 1
    string_ = ':red[' + str(ecs) + '] TK-1 out of ' + str(len(rider['cards'])+len(rider['discarded'])) + ' cards'
    return string_



def transfer_positions(dict,df, include_played_card=False):
    #df = df.sort_values(by='index', ascending=True)
    i = 0
    for rider in dict:
        df.loc[df['NAVN'] == rider, 'position'] = dict[rider]['position']
        df.loc[df['NAVN'] == rider, 'group'] = dict[rider]['group']
        df.loc[df['NAVN'] == rider, 'moved_fields'] = dict[rider]['moved_fields']
        df.loc[df['NAVN'] == rider, 'prel_time'] = dict[rider]['prel_time']
        if include_played_card==True:
            df.loc[df['NAVN'] == rider, 'played_card'] = dict[rider]['played_card'][0]
        df.loc[df['NAVN'] == rider, 'takes_lead'] = dict[rider]['takes_lead']
        #st.write(dict[rider]['played_card'][0])
        #df[df['NAVN' == rider]]['position'] = dict[rider]['position']
        #i = 1 + i
    return(df)

def rankings_from_dict_to_df(dict,df):
    #df = df.sort_values(by='index', ascending=True)

    for rider in dict:
        df.loc[df['NAVN'] == rider, 'ranking'] = dict[rider]['ranking']
        # df[df['NAVN' == rider]]['position'] = dict[rider]['position']
        # i = 1 + i
    return (df)
        #i = 1 + i



def from_dict_to_df(dict,df):
    #df = df.sort_values(by='index', ascending=True)
    i = 0
    for rider in df['NAVN'].tolist():
        dict[rider]['position'] = df[df['NAVN'] == rider]['position'].tolist()[0]
        dict[rider]['played_card'] = 0
        dict[rider]['group'] = df[df['NAVN']==rider]['group'].tolist()[0]
        dict[rider]['favorit'] = df[df['NAVN'] == rider]['favorit'].tolist()[0]

        #df[df['NAVN' == rider]]['position'] = dict[rider]['position']
        #i = 1 + i
    return(dict)


def assign_new_group_numbers(df, cards):
    df = df.sort_values(by='position', ascending=False)
    positions = df.position.unique().tolist()
    # st.write('positions', positions)

    # assign groups
    i = 1
    for position in positions:
        for rider in df.NAVN.tolist():
            # st.write(rider)

            if cards[rider]['position'] == position:
                cards[rider]['group'] = i
                df.loc[df.NAVN == rider, 'group'] = i
            else:
                r = 0
        i = i + 1
    return df, cards


def get_longest_hill(track):
    longest = 0
    current = 0
    for i in track:
        if i in ['0','1']:
            current = 1 + current
        if i == '2':
            current = 0
        if i == '_':
            current = 0
        longest = max(longest, current)

    return longest

def takes_lead_fc(rider, df, attacking_status, number_of_teams):
    if attacking_status == 'attacker':
        return 1

    group = df[df['NAVN'] == rider]['group'].tolist()[0]
    sdf = df[df['group'] == group]
    group_size = sdf.shape[0]
    len_left = track.find('F') - st.session_state.cards[rider]['position']
    best_sel_card = 100
    favorit = (st.session_state.cards[rider]['favorit']+2)

    team = df[df['NAVN'] == rider]['team'].tolist()[0]
    fra_team_i_gruppe = sdf[sdf.team == team].shape[0]
    ratio = fra_team_i_gruppe / group_size
    if ratio == 1:
        return 1

    for card in st.session_state.cards[rider]['cards'][0:4]:
        best_sel_card = min(best_sel_card, int(card[0][-2:-1] + card[0][-1]))


    #st.write(attack_prob, 'attack_prob')

    if attacking_status != 'attacked':
        attack_prob_percent = 50 / (len_left * favorit)
        attack_prob_percent = attack_prob_percent / (best_sel_card)
        attack_prob_percent = attack_prob_percent / (group ** 1.45 / (1 + 0.1 * favorit))
        attack_prob_percent = attack_prob_percent / max(1,get_slipstream_value(st.session_state.cards[rider]['position'], st.session_state.cards[rider]['position']+8, track))
        attack_prob_percent = attack_prob_percent / len(df) * 9
        #attack_prob_percent = attack_prob_percent * ((group_size ** 1.5)/2
        attack_prob = int(1/attack_prob_percent) + 1

        #st.write(rider, 'attack_prob', attack_prob)
        if random.randint(0, attack_prob) == 1:

                    if group_size > 1:
                        st.write(rider, 'attacks')
                        return 2

    takes_lead = 0

    favorit = df[df['NAVN'] == rider]['favorit'].tolist()[0]



    #hvis man har ryttere foran
    ssdf = df[df['group'] <= group]
    riders_ahead = ssdf.shape[0] - sdf.shape[0]
    own_riders_ahead = ssdf[ssdf.team == team].shape[0]-sdf[sdf.team == team].shape[0]

    own_riders_ahead_share = (own_riders_ahead+0.1)/(riders_ahead+0.3)

    ratio = ratio + 0.333 - own_riders_ahead_share

    ratio = ratio * ((sdf[sdf.team == team].favorit.min() / favorit) ** fra_team_i_gruppe)

    if group_size > 3:
        ratio = ratio - (favorit**(1+group_size/20)/100)

    ratio = ratio + random.randint(0, 8) / 100
    ratio = ratio - random.randint(0, 8) / 100
    ratio = ratio - st.session_state.cards[rider]['takes_lead']*.15
    if random.random() * (2/number_of_teams) < ratio:
        takes_lead = 1

    return takes_lead


def slipstream_value(cards, track, group):
    return 'ppop'


def nyehold(df, track, number_of_teams, riders_per_team, puncheur, same=False):
    #global cards

    number_of_teams = int(number_of_teams)
    riders_per_team = int(riders_per_team)
    peloton_size = number_of_teams * riders_per_team

    if same == True:
        rdf = df[0:peloton_size]

    elif same == False:
        df = df.head(66)
        df = df.iloc[1:]
        rdf = df.sample(peloton_size)
    #rdf = df[0:9]
    rdf = rdf.reset_index(drop=True)
    rdf['team'] = 'V'
    rdf['method'] = 'V'
    counter = 0
    teams = ['Me']
    for i in range(1,number_of_teams):
        teams.append('Comp'+str(i))

    counter = 0
    for team in teams:
        for rider in range(0,riders_per_team):
            rdf.at[counter, 'team'] = team
            counter = counter + 1

    st.write('checkpoint 1')
    st.dataframe(rdf)
    #rdf['team'][0:3] = 'Me'
    #rdf['team'][3:6] = 'Comp1'
    #rdf['team'][6:9] = 'Comp2'
    #rdf['method'] = 'V'
    #rdf['method'][0:3] = 'Human'
    #rdf['method'][3:6] = 'Comp1'
    #rdf['method'][6:9] = 'Comp1'
    rdf['method_takes_ECs'] = 1
    #rdf['method_takes_ECs'][3:9] = 1
    rdf['takes_lead'] = 1
    rdf['played_card'] = ''
    rdf['moved_fields'] = 0
    rdf['position'] = 0
    rdf['old_position'] = 0
    rdf['index2'] = range(0,peloton_size)
    rdf['noECs'] = 0
    rdf['group'] = 2
    rdf['index'] = range(1,1+peloton_size)
    rdf['ECs'] = 0
    rdf['prel_time'] = 100000

    riders = rdf.NAVN.tolist()

    track = track[0:track.find('F')+1]

    riderteams = []
    for team in teams:
        for i in range(0, riders_per_team):
            riderteams.append(team)
    cards = {}
    i = -1
    udbrud = random.randint(0,peloton_size)

    longest_hill = get_longest_hill(track)
    puncheur_factor = min(1, 2 / longest_hill) * puncheur
    st.write(puncheur_factor)

    rdf['BJERG'] = rdf['BJERG']+rdf['PUNCHEUR']*puncheur_factor

    for rider in riders:
        i = i + 1
        cards[rider] = {}
        cards[rider]['position'] = 0
        cards[rider]['cards'] = []
        cards[rider]['discarded'] = []
        cards[rider]['attacking_status'] = 'no'
        cards[rider]['group'] = 2
        cards[rider]['played_card'] = 0
        cards[rider]['selected_value'] = 0
        cards[rider]['moved_fields'] = 0
        cards[rider]['sprint'] = rdf.iloc[i]['SPRINT']
        cards[rider]['sprint_points'] = 0
        cards[rider]['ranking'] = 0
        cards[rider]['takes_lead'] = 1
        cards[rider]['noECs'] = 0
        cards[rider]['prel_time'] = 1000000
        cards[rider]['team'] = riderteams[i]
        cards[rider]['fatigue'] = 0

        if i == udbrud:
            cards[rider]['position'] = 5
            cards[rider]['group'] = 1



        rpf = int(rdf.iloc[i]['PUNCHEUR'] * puncheur_factor)

        l = []

        if rpf != 0:
            for k in range(1, 16):
                if k % (16 / (abs(rpf) + 1)) < 1:
                    l.append(int(rpf / abs(rpf)))
                else:
                    l.append(0)
        else:
            l = [0]*15

        #st.write(rider, rpf, l)
        for j in range(15):
            if i == udbrud:
                if j == 5:
                    cards[rider]['cards'].append(['kort: 16', 2, 2])
                if j == 10:
                    cards[rider]['cards'].append(['kort: 16', 2, 2])
                else:
                    cards[rider]['cards'].append(
                        ['kort: ' + str(j + 1), int(rdf.iloc[i, 17 + j]), int(rdf.iloc[i, 32 + j])+l[j]])

            else:
                cards[rider]['cards'].append(['kort: ' + str(j + 1), int(rdf.iloc[i, 17 + j]), int(rdf.iloc[i, 32 + j]) +l[j] ])



        random.shuffle(cards[rider]['cards'])
        #cards['select']={}


    #assign favorit
    track21 = min(get_value(track), 7) / max(get_value(track), 7)
    rdf['fav_points'] = (rdf['BJERG'] - 60) * get_value(track) * get_longest_hill(track)**0.5+ rdf[
        'SPRINT'] * 15 + (rdf['BJERG 3'] - 21) * 2 * get_value(track[-15::]) + (rdf['BJERG 3'] - 21) * 3 * track21 + (rdf['FLAD']+rdf['SPRINT']-65) * (50 / (get_value(track[-17::])+1) )
    rdf = rdf.sort_values(by='fav_points', ascending=True)
    rdf['favorit'] = range(1, peloton_size+1)
    rdf['favorit'] = rdf['favorit'] / (peloton_size/9)
    gcdf = rdf.copy()
    gcdf['prel_time'] = 1000
    st.dataframe(rdf)
    rdf = transfer_positions(cards, rdf, False)

    riders = rdf[rdf.team == 'Me'].NAVN.tolist()
    return cards, rdf, gcdf, riders, teams



def write_situation():
    with col3:
        if st.session_state.rdf.shape[0] > 0:
            st.session_state.rdf = st.session_state.rdf.sort_values(by=['group', 'position'], ascending=[True, False])
            max_position = st.session_state.rdf['position'].max()
            # st.write('max_gruppe:', st.session_state.rdf['group'].max(), type(st.session_state.rdf['group'].max()))

            for i in st.session_state.rdf['group'].unique():
                time = 13 * (max_position - st.session_state.rdf[st.session_state.rdf['group'] == i]['position'].max())
                if time != 0:
                    time = time + random.randint(-5,5)
                time_string = convert_to_seconds(time)
                max_position = st.session_state.rdf['position'].max()
                km_left = get_length(st.session_state['track'][max_position::])
                if i == 1:
                    st.header(str(km_left) + 'km left')
                    st.header('Group ' + str(i) + ' (' + time_string + ')')
                else:
                    st.header('Group ' + str(i) + ' (' + time_string + ')')

                try:
                    minimum = int(st.session_state.rdf[st.session_state.rdf['group'] == i]['position'].min())
                except:
                    minimum = 1000
                st.markdown(str(minimum) + ':   ' + colour_track(st.session_state['track'][minimum:minimum + 10]))
                st.text('')
                riders = \
                st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)[
                    'NAVN'].tolist()
                positions = \
                st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)[
                    'position'].tolist()
                ECs = \
                st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)[
                    'ECs'].tolist()
                takes_lead = \
                st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position', ascending=False)[
                    'takes_lead'].tolist()
                teams = \
                    st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='position',
                                                                                         ascending=False)[
                        'team'].tolist()

                for i in range(len(riders)):
                    if ECs[i] > 0:

                        st.write(riders[i] + ' . ' + str(positions[i]) + ' (' + teams[i] + ')' + ' :red[takes ' + str(
                            int(ECs[i])) + ' ECs]')

                    else:
                        st.caption(riders[i] + ' . ' + str(positions[i]) + ' (' + teams[i] + ')')
                    #if takes_lead[i] == 1:
                        #st.caption(':blue[takes the lead]')



#hvis alt går galt
#st.session_state.cards, st.session_state.rdf, st.session_state.riders2 = nyehold(pd.read_csv('FRData -FRData.csv'))



col1, col2, col3, col4, col5 = st.columns([1,1,1,1,1], gap='small')

col1.title('Actions')
col1.write('------------')
col2.title(st.session_state['trackname'])
col2.write('------------')
col3.title('Situation')
col3.write('------------')
col4.title('Round actions')
col4.write('------------')
col5.title('The Riders')
#col4.subheader('and their stats')
col5.write('------------')


#col3.write(st.session_state.cards)

##################
#track = '^^1---------^^^^3__------------^^^^^^^^^4------^^^^^2_----^^1-----FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
track = st.session_state['track']
track2 = colour_track(st.session_state['track'][0:st.session_state['track'].find('F')+1])
#human_chooses_cards = False
computer_chooses_cards = False
ready_for_calculate = False


#st.session_state.level = col1.slider('Level',-10,10,0,1)

def get_group_position_from_cards(cards, group_number):
    best_pos = 0
    for rider in cards:
#        st.write(rider)
        if cards[rider]['group'] == group_number:
            best_pos = max(cards[rider]['position'], best_pos)

    return best_pos



def generate():
    #col1.write('generate')
    with col2:
        #st.session_state.rdf, st.session_state.cards = assign_new_group_numbers(st.session_state.rdf,
        #                                                                        st.session_state.cards)
        st.write('[The rules](https://docs.google.com/document/d/1y1VYN319_xGjjzF7sfPihixB8yjLmWH7yoMsEkzCpfU/edit)')


    #    st.write(st.session_state['trackname'] + '. Full Track: ' + track2)
    #    st.write('---------')
    #    st.write('-' + '= flat')
    #    st.write(':blue[_] = downhill')
    #    st.write(':red[^] = uphill')
    #    st.write(':red[*] = steep uphill')
    #    st.write(':red[1,2,3,4,5] = end of ascent where group splits')
    #    st.write(':green[F] = Finish')
    #    st.write('---------')
    #    st.subheader('Level: ' + str(st.session_state.level))
        #st.write('ryttere tilbage', len(st.session_state.riders))


        #st.write()
        #min_position = 0
        min_position = st.session_state.rdf['position'].min()

        for i in range(min_position, track.find('F')+1):
            text = str(i)
            color = '#999999'
            if track[i] == '_':
                colour = '#2986cc'
            if track[i] == '1':
                colour = '#cc0000'
                text = text + '--SV1'
            if track[i] == '0':
                colour = '#c809b8'
                text = text + '--SV0'
            if track[i] == '2':
                colour = '#999999'
                text = text + '--SV2'
            if track[i] == 'F':
                colour = '#ffc30b'
            #else:
            #    colour = '#c41122'

            riders_on_field = st.session_state.rdf[st.session_state.rdf['position'] == i].NAVN.tolist()

            if i == track.find('F')+1:
                riders_on_field.append(st.session_state.rdf[st.session_state.rdf['position'] > i].NAVN.tolist())

            if len(riders_on_field) > 0:
                text = text + ': GROUP ' + str(st.session_state.rdf[st.session_state.rdf['position'] == i].group.tolist()[0])
                for rider in riders_on_field:
                    team = st.session_state.rdf[st.session_state.rdf['NAVN'] == rider].team.tolist()[0]
                    text = text + ', ' + str(rider) + ' (' + team + ')'


            #yellow = #ffc30b
            #blue = # 2986cc
            #"+fontColor+"
            st.markdown('<p style="background-color:{};color:black;font-size:12px;border-radius:0%;">{}</p>'.format(colour, text),
                        unsafe_allow_html=True)

        #st.markdown(line)


#st.session_state['track'] = '**1FFFFFF'
if st.session_state.sprint_groups:
    col4.write('SPRINT')

    st.session_state.cards, st.session_state.rdf, st.session_state.winner_time, st.session_state.result, st.session_state.latest_prel_time= sprint(st.session_state.sprint_groups, st.session_state.cards, st.session_state.rdf, st.session_state.winner_time, st.session_state.result, st.session_state.latest_prel_time, int(track[track.find('F')-1]))
    st.session_state.sprint_groups = []
    st.session_state.rdf = rankings_from_dict_to_df(st.session_state.cards, st.session_state.rdf)
    st.session_state.rdf = st.session_state.rdf.sort_values(by='ranking', ascending=True)

        # del st   .session_state.cards[rider]
        # st.session_state.riders.remove(rider)
    #st.session_state.riders = st.session_state.rdf[st.session_state.rdf.team == 'Me']['NAVN'].tolist()

    riders_left = []
    for rider in st.session_state.cards:
        riders_left.append(rider)

    for rider in riders_left:
        if st.session_state.cards[rider]['ranking'] > 0:
            # col3.write(rider + 'gets removed')
            del st.session_state.cards[rider]
            st.session_state.rdf = st.session_state.rdf.loc[st.session_state.rdf['NAVN'] != rider]
            if rider in st.session_state.riders:
                st.session_state.riders.remove(rider)

            #st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider,
            #'played_card'] = 'Finished 15'

            #st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider,
            #'time'] = int(st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider]['time'])
            #st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider,
            #'prel_time'] = int(st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider]['prel_time'])

            #st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider,
            #'ranking'] = int(st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider]['ranking'])

            #st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider,
            #'played_card'] = 'Finished 15'

            #st.session_state.rdf = st.session_state.rdf.drop(
#                st.session_state.rdf[st.session_state.rdf['NAVN'] == rider].index)

    # position = 100+position, played_card = 15
    # st.write('rdf:')

    # st.write('gcdf:')
 #   st.session_state.gcdf['time'] = st.session_state.gcdf['prel_time'] - st.session_state.gcdf['prel_time'].min()

    # st.write(st.session_state.gcdf[
    #         ['NAVN', 'position', 'group', 'ECs', 'played_card',
    #         'prel_time', 'time', 'ranking']])

    # col3.write(st.session_state.cards)

    col3.header(':green[Results]')
    st.session_state.rdf = st.session_state.rdf.sort_values(by='ranking', ascending=True)

    #for rider in st.session_state.rdf[st.session_state.rdf.ranking > 0].NAVN.tolist():
    #    col4.write(str(int(st.session_state.rdf.loc[st.session_state.gcdf['NAVN'] == rider][
    #                           'ranking'])) + '. ' + rider + '(' + str(
    #        st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider]['team'].tolist()[0])
    #               + '): ' + str(convert_to_seconds_plain(
    #        int(st.session_state.rdf.loc[st.session_state.rdf['NAVN'] == rider]['time']))))

    #                if st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider]['team'] == 'Me':
    #                    col2.write(":green[", str(int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider][
    #                                       'ranking'])) + '. ' + rider + ': ' + str(
    #                    convert_to_seconds_plain(int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider]['time']))), "]")
    #                else:
    #                    col2.write(str(int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider][
    #                                                      'ranking'])) + '. ' + rider + ': ' + str(
    #                        convert_to_seconds_plain(
    #                           int(st.session_state.gcdf.loc[st.session_state.gcdf['NAVN'] == rider]['time']))))

    if st.session_state.rdf.shape[0] == 0:
        col3.header('Race is over')

        for result in st.session_state.result:
            if result[3] == 'Me':
                col3.write(':blue[' + str(result[0]) + '. ' + result[1] + ' (' + result[2] + ') ' + ']')
            else:
                col3.write(str(result[0]) + '. ' + result[1] + ' (' + result[2] + ') ')

tracks = ['sprinttest', 'World Championship 2019 (Yorkshire)','Liege-Bastogne-Liege', 'Bemer Cyclassics', 'Hautacam','Giro DellEmilia', 'GP Industria', 'UAE Tour', 'Kiddesvej', 'Kassel-Winterberg', 'Allerød-Køge', 'bjerg-flad', 'Askersund-Ludvika']

if st.session_state.game_started == False:
    st.session_state['trackname'] = col1.radio('start new race', tracks)
    puncheur = col1.checkbox('puncheur stats', key='puncheut', value=True)
    checkbxtrack = col1.checkbox('choose', key='track_choose', value=False)
    riders_per_team = st.text_input('choose number of riders in each team', value=3)

    number_of_teams = st.text_input('choose number of teams', value=3)
    shorten_track = st.text_input('shorten_track', value=0)
    st.session_state.number_of_teams = int(number_of_teams)
    riders_per_team = int(riders_per_team)
    if checkbxtrack:
        #st.session_state.level = col1.slider('Level', -10, 10, 0, 1)
        #checkbxlevel = col1.checkbox('choose', key='level_choose', value=False)
        #checkbxtrack = False
        #if checkbxlevel:
            #if st.session_state['trackname'] == 'Fleche Wallone':
            #    st.session_state['track'] = '211-----------------------****2----------^^^3----------^2------*****1FFFFFFFFFFFFFF'
            #elif st.session_state['trackname'] == 'Amstel Gold Race':
            #    st.session_state['track'] = '-------^3------*2--^4--***2-----------*2-----^^3------^3-------FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
        if st.session_state['trackname'] == 'Liege-Bastogne-Liege':
            st.session_state['track'] = '2211111___222222222111222222222200000_2222222222222211122222222222222FFFFFFFFF'
        elif st.session_state['trackname'] == 'World Championship 2019 (Yorkshire)':
            st.session_state['track'] = '22222222222211222222222222221122222222222222112222222222222211222222FFFFFFFFF'
        elif st.session_state['trackname'] == 'Bjerg-Flad':
            st.session_state['track'] = '111111111111___2222222222222222222222222222222222222222222222FFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'Bemer Cyclassics':
            st.session_state['track'] = '2222222222222222222222222222212222211222222211222222222222222222FFFFFFFFFFFFF'

        elif st.session_state['trackname'] == 'Hautacam':
            st.session_state['track'] = '222111111111111111_______222221111111111111000000111111111111FFFFFFFFF'
        elif st.session_state['trackname'] == 'Giro DellEmilia':
            st.session_state['track'] = '___1111111_11___1111111_11___1111111_11___1111111_11___1111111FFFFFFFFFF'
        elif st.session_state['trackname'] == 'sprinttest':
            st.session_state['track'] = '111111FFFFFFFFFF'
        elif st.session_state['trackname'] == 'GP Industria':
            st.session_state['track'] = '2222222222222111111__222222222222222222222222111111__22222222222FFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'Kassel-Winterberg':
            st.session_state['track'] = '222222222222222222222222222222221111111122222222222222__1111111222FFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'Askersund-Ludvika':
            st.session_state[
                'track'] = '22222222222222222222222222222222222222222222222222221111__22222FFFFFFFFFF'
        elif st.session_state['trackname'] == 'UAE Tour':
            st.session_state[
                'track'] = '2222222222222222222222222222222222222222111111111111111111111FFFFFFFFFF'
        elif st.session_state['trackname'] == 'Kiddesvej':
            st.session_state[
                'track'] = '22222222222222211222222222220022222222222002222222222222200FFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'Allerød-Køge':
            st.session_state[
                'track'] = '2222222222222222222222222222222222222222222222222222222222222FFFFFFFFFF'

        st.session_state['track'] = st.session_state['track'][int(shorten_track)::]
        track2 = colour_track(st.session_state['track'][0:st.session_state['track'].find('F') + 1])
        #col3.write(st.session_state['track'])
        st.session_state.cards, st.session_state.rdf, st.session_state.gcdf, st.session_state.riders, st.session_state.teams = nyehold(pd.read_csv('FRData -FRData.csv', encoding='utf-8'),  st.session_state['track'],st.session_state.number_of_teams, riders_per_team, puncheur, False)
        #rdf['team'] = 'None'




        st.session_state['placering'] = 0

        st.session_state.human_chooses_cards = 9

        from_dict_to_df(st.session_state.cards, st.session_state.rdf)
        col1.button('start game')
        checkbxlevel = False
        generate()
        st.session_state.game_started = True
        #st.write(st.session_state.riders2[0])


if st.session_state.game_started:
    with col5:
        #for team in st.session_state.rdf['team'].unique():


        #WRITE THE RIDERS IN THE RIGHT COLUMN
        for team in st.session_state.teams:
            st.title(':blue[' + team + ']')
            for rider in st.session_state.rdf[st.session_state.gcdf.team == team]['NAVN'].unique():
            #for rider in ['Me', 'Comp1', 'Comp2']:
                stars = ''
                for i in range(int(st.session_state.gcdf[st.session_state.gcdf.NAVN == rider]['favorit'])):
                    if int(i % 2) == 0:
                        stars = stars + '*'
                st.markdown(':green[' + rider + ' ' + stars + ']')
                st.write('Flat:' + str(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['FLAD'])) + '  Uphill:' + str(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['BJERG'])) + '  Sprint:' + str(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['SPRINT'])))
                if st.button('View cards', key = (rider + 'VC')):
                    keystring = str(rider) + str( random.randint(0,999999))
                    st.write(st.session_state.cards[rider])



                #st.caption()
                #st.caption('Sprint:' + str(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['SPRINT'])))
                flatlist = []
                for i in range(1, 16):
                    # field = 'FLAD'+str(i)
                    flatlist.append(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['FLAD' + str(i)].tolist()[0]))

                j = 0
                flatstr = ''
                for i in flatlist:
                    flatstr = flatstr + str(i)
                    j = 1 + j
                    if j % 5 == 0:
                        flatstr = flatstr + '|'





                uplist = []
                for i in range(1, 16):
                    # field = 'BJERG'+str(i)
                    uplist.append(int(st.session_state.rdf[st.session_state.rdf.NAVN == rider]['BJERG' + str(i)].tolist()[0]))

                j = 0
                upstr = ''
                for i in uplist:
                    upstr = upstr + str(i)
                    j = 1 + j
                    if j % 5 == 0:
                        upstr = upstr + '|'

                st.caption('Flat:' + flatstr + '  Up:' + upstr)

        if st.button('Current pull values'):
            st.write(pull_value, paces)

        if st.button('Current dataframe'):
            st.dataframe(st.session_state.rdf)

        if st.button('Current sprint groups'):
            st.write(st.session_state.sprint_groups)

        if st.button('Result'):
            for result in st.session_state.result:
                if result[3] == 'Me':
                    st.write(':blue[' + str(result[0]) + '. ' + result[1] + ' (' + result[2] + ') ' + ']')
                else:
                    st.write( str(result[0]) + '. ' + result[1] + ' (' + result[2] + ') ')


        new_pos = st.text_input('Edit positions', value = '')
        if new_pos != '':
            st.session_state.cards[new_pos.split(',')[0]]['position'] = int(new_pos.split(',')[1])
            new_pos = ''
            st.session_state.rdf, st.session_state.cards = assign_new_group_numbers(st.session_state.rdf,
                                                                                    st.session_state.cards)

        get_group = st.text_input('Get group from cards')
        if get_group != '':
            st.write(get_group_position_from_cards(st.session_state.cards, int(get_group)))

        remove_rider = st.text_input('Remove EC (Front = 0, Back = 1)')
        if remove_rider != '':
            if remove_rider.split(',')[1] == '0':
                st.session_state.cards[remove_rider.split(',')[0]]['cards'].remove(['kort: 16', 2, 2])
            if remove_rider.split(',')[1] == '1':
                st.session_state.cards[remove_rider.split(',')[0]]['discarded'].remove(['kort: 16', 2, 2])
            #st.session_state.rdf = transfer_positions(st.session_state.cards, st.session_state.rdf, False)
            #generate()


        if st.button('generate'):
            generate()
#def human_chooses_cards(cards, riders):
###? HVAD GØR DENNE??? ###
def riders_in_group_to_string(riders_in_group, riders_in_group_me):
    outp = ''
    for rider in riders_in_group:
        if rider in riders_in_group_me:
            outp = outp + ':blue[' + rider + '], '
        else:
            outp = outp + rider + ', '
    outp = outp[0:len(outp)-2]
    return outp
def get_penalty(rider):
    penalty = 0

    for card in st.session_state.cards[rider]['cards'][0:4]:

        if card[1] == -1:
            penalty = 1
        ###TEST
        elif card[0] == 'kort: 16':
            penalty = penalty + 0
        ###TEST

    return penalty


def get_pull_value(_list, sv):
    if sv > 1:
        try:
            a = heapq.nlargest(2, _list)[1]
            if a == 0:
                return heapq.nlargest(2, _list)[0], 1
            else:
                a = heapq.nlargest(2, _list)
                if a[1] + 1 >= a[0]:
                    return a[1], 2
                else:
                    return a[0],1


        except:
            return _list[0],1
    else:
        return heapq.nlargest(1, _list)[0],1





def choose_card_to_play(cards, sv, penalty, speed, chosen_value):
    cards.append(['tk_extra 15', 2,2])
    chosen_card = False
    if chosen_value > 0:
        managed = True

        for card in cards:
            if sv > 1:
                card_value = card[1] - penalty
            elif sv<2:
                card_value = card[2] - penalty
            if card_value  == chosen_value:

                if chosen_card:
                    if int(card[0][-2:-1] + card[0][-1]) > sel_card_number:
                        chosen_card = card
                        sel_card_number = int(card[0][-2:-1] + card[0][-1])

                    else:
                        p = 0
                else:
                    chosen_card = card
                    sel_card_number = int(card[0][-2:-1] + card[0][-1])







    if chosen_value == 0:
        for card in cards:
            managed = True
            if sv > 1:
                card_value = card[1] - penalty
            elif sv<2:
                card_value = card[2] - penalty
            if card_value + sv  >= speed:
                if chosen_card:
                    if int(card[0][-2:-1] + card[0][-1]) > sel_card_number:
                        chosen_card = card
                        sel_card_number = int(card[0][-2:-1] + card[0][-1])

                    else:
                        p = 0
                else:
                    chosen_card = card
                    sel_card_number = int(card[0][-2:-1] + card[0][-1])


    if not chosen_card:
        managed = False
        sel_card_number = 210
        for card in cards:
            if int(card[0][-2:-1] + card[0][-1]) < sel_card_number:
                chosen_card = card
                sel_card_number = int(card[0][-2:-1] + card[0][-1])

    return chosen_card, managed

def move_riders(ridername, sv, rider, gruppefart1, speed, groups_new_positions, chosen_card, chosen_value, track, pull_value, riders_pulling):
    if sv == 2:
        sv = 3

    with col4:
        st.write(ridername, 'sv ', sv, 'gruppefart1 ', gruppefart1, 'speed ', speed, 'groups_new_positions[0][0] ',
                 groups_new_positions[0][0])

        if rider['attacking_status'] == 'attacker':
            if track[rider['position'] + speed] == 'F':
                rider['position'] = rider['position'] - 1
                st.write('attacking over finishing line')

        penalty = get_penalty(ridername)
        # st.write(ridername, 'penalty:', penalty)

        if penalty > 0:
            col1.write(':red[penalty: ' + str(penalty) + ']')

        speed = groups_new_positions[0][0] - rider['position']
        st.write('speed:', speed, ' sv: ', sv, 'rider pos. bef. ', rider['position'])
        st.write(groups_new_positions)
        riders_starting_position = rider['position']
        st.write('selected_value', chosen_value)
        speed2 = speed
        if track[rider['position']] == '_':

            speed2 = max(5, speed2)
        rider['takes lead'] = 0
        #managed = True
        managed = False

        if sv > 1:
            # Does the rider take lead on flat?

            if chosen_value >= pull_value:
                #sv = gruppefart1 - chosen_value
                #speed = gruppefart
                takes_lead = True
                st.write('takes lead')
                rider['takes lead'] = 1
            else:
                takes_lead = False
                rider['takes lead'] = 0
                chosen_value = 0


                # hvilket kort vælger han
            if not chosen_card:

                chosen_card, managed = choose_card_to_play(rider['cards'][0:4], sv, penalty, speed, chosen_value)
                st.write('selects(sv2):', chosen_card, managed)
                if track[rider['position']] == '_':
                    chosen_card[1] = max(chosen_card[1],5)


            sel_card_number = int(chosen_card[0][-2:-1] + chosen_card[0][-1])
            if chosen_card[1] + sv- penalty >= speed:
                managed = True
                rider['position'] = rider['position'] + speed
                st.write('speed', speed)
                st.write('new position', rider['position'], 'SV2')

        if sv <= 1:
            st.write('sv<=1')
            selected = False
            if chosen_value == pull_value:
                sv = 0
                speed = chosen_value
                # st.write('takes lead')
                rider['takes lead'] = 1
                takes_lead = True
            else:
                takes_lead = False
                chosen_value = 0
            # vælg kortet

            if not chosen_card:
                chosen_card, managed = choose_card_to_play(rider['cards'][0:4], sv, penalty, speed, chosen_value)
                if track[rider['position']] == '_':
                    chosen_card[2] = max(chosen_card[2], 5)

            if chosen_card[2] + sv - penalty >= speed:
                managed = True
                rider['position'] = rider['position'] + speed
                st.write('speed', speed)
                st.write('new position', rider['position'], 'SV1')

            st.write('selects(sv1):', chosen_card, managed)

        st.write('selected?', chosen_card)
        sel_card_number = int(chosen_card[0][-2:-1] + chosen_card[0][-1])
        rider['played_card'] = chosen_card

        if 'F' in track[riders_starting_position:rider['position']]:
            rider['position'] = rider['position']-1
        #if not managed:

        if sv > 1:
            value = chosen_card[1] - penalty + sv

        if sv < 2:
            value = chosen_card[2] - penalty + sv

        if track[rider['position']] == '_':
            value = 5 - penalty

        pot_position = min(rider['position'] + value, groups_new_positions[0][0])
        pot_position_wo_sv = pot_position-sv
        new_pot_position = pot_position_wo_sv

        for groups_position in groups_new_positions:
            if pot_position >= groups_position[0]:
                st.write('try position:', pot_position, 'to', groups_position, '(', groups_position[1])
                new_pot_position = max(groups_position[0], pot_position_wo_sv)
                st.write(pot_position, 'after trying')

        if new_pot_position > rider['position'] :

            rider['position'] = new_pot_position
            st.write('new new position', rider['position'])

        for card in rider['cards'][0:4]:
            rider['discarded'].append(card)
            rider['cards'].remove(card)

        #TEST!!!!!!!!!!!!!!
        if penalty > 0:
            rider['discarded'].remove(['TK-1: 99', -1, -1])
            rider['discarded'].append(['kort: 16', 2, 2])



        #### TEST STOP
        try:
            rider['discarded'].remove(chosen_card)

        except:
            p = 0

        st.write('sel_card_number:', sel_card_number)

        ecs = int(takes_lead)
        if takes_lead:
            ecs = 1

            if sel_card_number < 6:

                ecs = 2



        if sel_card_number > 10 and riders_pulling < 2:
            ecs = 0


        if not takes_lead:
            #if sv < 2:
            if sel_card_number < 6:
                ecs = 1

        #ecs = ecs + penalty
        if rider['attacking_status'] == 'attacker':
            ecs = 0

        if ecs > 0:
            rider['cards'].insert(0, ['kort: 16', 2, 2])
            st.write(ridername + 'takes' + str(ecs) + 'ECs')
        if ecs > 1:
            rider['discarded'].append(['kort: 16', 2, 2])

        if sel_card_number < 3:
            if rider['attacking_status'] != 'attacker':
                rider['cards'].insert(0, ['TK-1: 99', -1, -1])
                rider['cards'].remove(['kort: 16', 2, 2])

        if len(rider['cards']) < 4:
            # st.write('shuffling riders cards')
            random.shuffle(rider['discarded'])
            for card in rider['discarded']:
                rider['cards'].append(card)
            rider['discarded'] = []

        groups_new_positions.append([rider['position'], sv])

    return rider, groups_new_positions

def get_teams_in_group(group):
    teams = []
    for rider in st.session_state.cards:

        if st.session_state.cards[rider]['group'] == group:
            teams.append(st.session_state.cards[rider]['team'])
    return teams

def get_investment(team, groupy):
    investment = []
    riders_investing = []
    for rider in st.session_state.cards:
        if st.session_state.cards[rider]['team'] == team:
            #st.write(rider)
            if st.session_state.cards[rider]['group'] == groupy:
                a = takes_lead_fc(rider, st.session_state.rdf, st.session_state.cards[rider]['attacking_status'], st.session_state.number_of_teams)
                if sum(investment) > 1:
                    a = 0
                a = a * random.randint(0,1)
                a = a * a*random.randint(1,2)
                if a > 0:
                    riders_investing.append(rider)
                investment.append(a)
    return investment, riders_investing




def set_all_to_no_attackers(cards):
    for rider in cards:
        cards[rider]['attacking_status'] = 'no'

    return cards



def adjust_groups(df, attackers):
    # Create a copy of the dataframe to avoid modifying the original one
    X = st.session_state.rdf[(st.session_state.rdf.NAVN == attackers[0])].group.tolist()[0]
    df_copy = df.copy()

    # For all rows in the dataframe
    for i, row in df_copy.iterrows():
        # If the name is in the list of names, keep the group as X (don't increment)
        if row['NAVN'] in attackers:
            df_copy.at[i, 'group'] = X
        # Otherwise, if the group is >= X, increment by 1
        elif row['group'] >= X:
            df_copy.at[i, 'group'] += 1
        # If the group is less than X, leave it as is (this is implicit since no modification is made)

    return df_copy


#if sprint_groups:
#    if printo == True:
#        st.header(':green[6. SPRINT]')
#    for group in sprint_groups:
#        df.loc[df['group'] == group, ['prel_time']] = (track.find('F') - df['old_position']) / (
#                df['position'] - df['old_position']) * 100 + df['prel_time']

#        df.loc[df['group'] == group, ['prel_time']] = df[df['group'] == group]['prel_time'].min()

#play_round = st.checkbox('START NEW roundddd', value=False)
if st.session_state.group_to_move < 1:

    if st.button('play_next_round'):
        st.session_state.round = np.floor(1 + st.session_state.round)
        #generate()
        st.session_state.play_round = True


        st.session_state.team_to_choose = st.session_state.teams[int(st.session_state.round) % st.session_state.number_of_teams]

        st.session_state.groups_new_positions = []
        st.session_state['confirmcards'] = [False] * (st.session_state.group_to_move+10)
        st.session_state.rdf, st.session_state.cards = assign_new_group_numbers(st.session_state.rdf, st.session_state.cards)
        st.session_state.cards = set_all_to_no_attackers(st.session_state.cards)
        st.session_state.sprint_groups = detect_sprint_groups(st.session_state.rdf)

        if st.session_state.sprint_groups:
            text = 'Sprint with groups' + str(st.session_state.sprint_groups)
            st.button(text)

        st.session_state.group_to_move = st.session_state.rdf.group.max()
    #ALLE SKAL TIL ATTACKING = FALSE




if st.session_state.play_round:
    st.session_state.play_round == False
    #st.write('groups position till now:', st.session_state.groups_new_positions)
    round = st.session_state.round #if len(st.session_state.riders) > 0:
    generate()
    write_situation()


    with (col1):
        #print rider cards
        st.write('ROUND:', str(st.session_state.round))
        st.write('ALL YOUR CARDS')
        for rider in st.session_state.riders:
            #st.write(st.session_state.cards[rider])
            st.write(rider, ' - is in group ', st.session_state.cards[rider]["group"])
            for i in [0, 1, 2, 3]:
                st.write(str(st.session_state.cards[rider]['cards'][i][1]) + ' - ' + str(
                    st.session_state.cards[rider]['cards'][i][2]) + ' - ' + str(
                    st.session_state.cards[rider]['cards'][i][0]))

#####VÆLG HASTIGHED

        svs = []

        while st.session_state.group_to_move > 0:

            group = st.session_state.group_to_move
            attacking_group = False
            if len(st.session_state.rdf[(st.session_state.rdf.group == group)]) == 0:
                st.session_state.group_to_move = st.session_state.group_to_move - 1
                break
            st.write('---------')
            st.markdown('GROUP ' + str(group) + ' MOVES')

            #st.dataframe(st.session_state.rdf)
            #st.dataframe(st.session_state.rdf[(st.session_state.rdf.group == group)])
            group_position = st.session_state.rdf[(st.session_state.rdf.group == group)].iloc[0].position

            your_riders_in_group = st.session_state.rdf[
                (st.session_state.rdf.group == group) & (st.session_state.rdf.team == 'Me')].NAVN.tolist()

            riders_in_group = st.session_state.rdf[
                (st.session_state.rdf.group == group)].NAVN.tolist()
            st.write('In group: ', riders_in_group_to_string(riders_in_group, your_riders_in_group))
            st.write('group_position =', group_position)
            st.markdown(':green[Next 8 fields:] ' + colour_track(st.session_state['track'][group_position:group_position + 8]))
            paces = []


            #st.dataframe(st.session_state.rdf)
            allpaces = []
            #CHOOSE VALUE
            for i in range(1,st.session_state.number_of_teams + 1):
                #st.write('choose value 1391', str(i), 'group:', group, '...team: ', st.session_state.team_to_choose)


                #st.write(st.session_state.team_to_choose, ' is next to choose')

                if st.session_state.team_to_choose == 'Me':
                    if len(your_riders_in_group) == 0:
                        st.write('You have no riders in the group')
                        Me_played_value = [0]
                        paces.extend(Me_played_value)

                    else:
                        text = 'Your turn. You have '
                        for rider in your_riders_in_group:
                            text = text + rider + ' '

                        text = text + 'in the group.'

                        for rider in your_riders_in_group:
                            # st.write(st.session_state.cards[rider])
                            st.write(':blue[' + rider , "'s cards]:")
                            for i in [0, 1, 2, 3]:
                                st.write(str(st.session_state.cards[rider]['cards'][i][1]) + ' - ' + str(
                                    st.session_state.cards[rider]['cards'][i][2]) + ' - ' + str(
                                    st.session_state.cards[rider]['cards'][i][0]))
                        #st.write('What do you choose?')
                        #st.write(text)
                        Me_played_value = st.text_input('What do you choose?', key=str(round+group))

                        #success = False
                        #while success == False:
                        #    try:
                        #        Me_played_value2 = int(Me_played_value.split(',')[0])
                        #        success = 'True'
                        #    except:
                        #        pass
                        while Me_played_value == '':
                            time.sleep(1)
                        else:
                            Me_played_value = Me_played_value

                        st.write('You played', Me_played_value)


                        if int(Me_played_value.split(',')[0]) > 10:
                            Me_played_value = int(Me_played_value)
                            st.write(your_riders_in_group[Me_played_value%10-1], 'is attacking')
                            st.session_state.attackers_in_turn.append(your_riders_in_group[Me_played_value%10-1])
                            st.session_state.round = st.session_state.round + 0.1
                        else:
                            Me_played_value = Me_played_value.split(',')
                            Me_played_value = [eval(i) for i in Me_played_value]

                            if Me_played_value == [0]:
                                Me_played_value = [0]*len(your_riders_in_group)
                            for i in Me_played_value:
                                paces.append(int(i))







                else:
                    #st.write(st.session_state.team_to_choose, 'chooses')
                    pace = []
                    #for hver rytter i hvert Comp-hold.
                    for rider in st.session_state.rdf[(st.session_state.rdf.group == group) & (st.session_state.rdf.team == st.session_state.team_to_choose)].NAVN.tolist():
                        #st.write(st.session_state.cards[rider])
                        if st.session_state.cards[rider]['selected_value'] == -1:
                            st.session_state.cards[rider]['takes_lead'] = takes_lead_fc(rider, st.session_state.rdf,st.session_state.cards[rider]['attacking_status'], st.session_state.number_of_teams)
                            if st.session_state.cards[rider]['takes_lead'] == 2:

                                st.session_state.attackers_in_turn.append(rider)
                                st.session_state.cards[rider]['takes_lead'] = 0
                                #st.write('attackers_in_turn:', st.session_state.attackers_in_turn)

                            #st.write('takes_lead:', st.session_state.cards[rider]['takes_lead'])
                            selected = pick_value(st.session_state.cards[rider], st.session_state.track)
                        #st.write(selected)
                            #st.write('selected:', selected)
                            st.session_state.cards[rider]['selected_value'] = st.session_state.cards[rider]['takes_lead']*selected

                        pace.append(st.session_state.cards[rider]['selected_value'])

                    if len(pace) > 0:
                        paces.extend(pace)
                        st.write(st.session_state.team_to_choose, 'chooses ',  ", ".join(str(x) for x in pace))
                    else:
                        paces.append(0)
                        st.write(st.session_state.team_to_choose, 'has no riders in the group')

                    allpaces.append(pace)

                st.session_state.team_to_choose = next_to_choose(st.session_state.team_to_choose, st.session_state.teams)

            if len(st.session_state.attackers_in_turn) > 0:
                st.write(', '.join(st.session_state.attackers_in_turn), 'attack')
                for rider in st.session_state.rdf[(st.session_state.rdf.group == group)].NAVN.tolist():
                    st.session_state.cards[rider]['attacking_status'] = 'attacked'
                    st.session_state.cards[rider]['selected_value'] = -1

                st.session_state.rdf = adjust_groups(st.session_state.rdf, st.session_state.attackers_in_turn)



                for rider in st.session_state.attackers_in_turn:
                    st.session_state.cards[rider]['position'] = st.session_state.cards[rider]['position'] + 1
                    #st.write(rider, 'moved + 1 to ', st.session_state.cards[rider]['position'])
                    st.session_state.cards[rider]['attacking_status'] = 'attacker'
                    st.session_state.cards[rider]['selected_value'] = -1

                st.session_state.group_to_move = st.session_state.group_to_move + 1
                st.session_state.attackers_in_turn = []

                st.session_state.cards = transfer_groups(st.session_state.rdf, st.session_state.cards)
                st.session_state.rdf = transfer_positions(st.session_state.cards, st.session_state.rdf, False)
                #st.write(st.session_state.cards)
                st.session_state.round = st.session_state.round + 0.11
                st.dataframe(st.session_state.rdf)
                generate()
                #husk at gøre det muligt at anggribe i Takes LEad, Og gøre at attacking => højeste kort

                break

# find gruppefart ###########################
            gruppefart = max(paces)
            gruppefart = max([gruppefart, 2])

            if st.session_state.track[group_position] == '_':
                gruppefart = max(5, gruppefart)

            gruppefart1 = gruppefart
            sv = get_slipstream_value(group_position, group_position + gruppefart, st.session_state.track)

            st.write('gruppefart=', gruppefart)
            count = 0

            if sv > 1:

                for pace in paces:
                    if pace > gruppefart - 1.5:
                        count = 1 + count

                with col4:
                    st.write('count (how many could be pulling?) ', count)
            #st.write(count)
                if count > 1:
                    #hvis fælger
                    if st.session_state.track[gruppefart+1+group_position] in ['2','F']:
                        gruppefart = 1 + gruppefart

                if gruppefart > 6:
                    sv = 3
            sv2 = sv
            if sv == 2:
                sv2 = 3
            st.write('group ' + str(group) + "'s speed is " + str(gruppefart), '. SV is:', str(sv2) + '. You have to move at least' + str(gruppefart-sv2))

            #st.write([gruppefart + group_position, sv], 'gets appended gto groups_new_posts')
            st.session_state.groups_new_positions.append([gruppefart + group_position, sv])

            st.session_state.groups_new_positions = sorted(st.session_state.groups_new_positions, key=lambda x: x[0],
                                                           reverse=True)
            st.write('you have to move ' + str(st.session_state.groups_new_positions[0][0]-group_position) + ' to catch the frontmost group.')
            j = 0

            pull_value, riders_pulling = get_pull_value(paces, sv)
            st.write('pull_value: ', pull_value)

            st.session_state.team_to_choose = 'Me'
            st.write('choose cards, you played', str(Me_played_value))
            ###ÆNDRE NÆSTE LINIE
            p = -1
            for rider in your_riders_in_group:
                # st.write(st.session_state.cards[rider])

                keystring2 = rider
                if st.session_state.cards[rider]["group"] == group:
                    p = 1+p
                    st.write(rider + ' (' + str(Me_played_value[p]) + ')')
                    st.session_state.cards[rider]['played_card'] = col1.radio(
                        'hvilket kort?', (st.session_state.cards[rider]['cards'][0],
                                          st.session_state.cards[rider]['cards'][1],
                                          st.session_state.cards[rider]['cards'][2],
                                          st.session_state.cards[rider]['cards'][3],
                                          ['EC-Xtra 15', 2, 2]), key=keystring2)
                    #if st.checkbox('To kort mere?', value=False, key=keystring2+'2mere'):
                    #    st.session_state.cards[rider]['played_card'] = col1.radio(
                    #        'hvilket kort?', (st.session_state.cards[rider]['cards'][4],
                    #                          st.session_state.cards[rider]['cards'][5],
                    #                          key= keystring2 + '2mere2')
            keystring = str(group) + str(st.session_state.round) + 'confirmcards'
            st.session_state.confirmcards[group] = st.checkbox('confirm', value=False, key=keystring)

            while st.session_state.confirmcards[group] == False:
                time.sleep(1)
                if st.session_state.confirmcards[group] == True:
                    continue


            p = -1
            for rider in your_riders_in_group:#move riders
            #st.session_state

                #st.write('p=',p)
                if st.session_state.cards[rider]["group"] == group:
                    p= 1+p
                    st.write(rider, 'has ', get_number_ecs(st.session_state.cards[rider]), ' ecs')
                    #st.write('cards before:', st.session_state.cards[rider])

                    st.session_state.cards[rider], st.session_state.groups_new_positions = move_riders(rider, sv, st.session_state.cards[rider], gruppefart1, gruppefart, st.session_state.groups_new_positions, st.session_state.cards[rider]['played_card'],
                        Me_played_value[p], st.session_state.track, pull_value, riders_pulling)

                    st.markdown(':green[New position:' + str(st.session_state.cards[rider]['position']) + ']')
                    st.write(rider, 'has ', get_number_ecs(st.session_state.cards[rider]), ' ecs', get_number_tk1(st.session_state.cards[rider]))

                    st.session_state.cards[rider]['selected_value'] = -1
                    if st.session_state.cards[rider]['attacking_status'] == 'attacker':
                        attacking_group = True
                        ##TEST
                        st.session_state.cards[rider]['discarded'].append(['TK-1: 99', -1, -1])
                        ###TEST

                        st.session_state.cards[rider]['cards'].insert(0, ['TK-1: 99', -1, -1])
                        st.write('..and 2 more TK-1')





                        st.session_state.cards[rider]['attacking_status'] == 'no'

                    st.divider()


                    #st.write('cards after:', st.session_state.cards[rider])

                #st.session_state.team_to_choose = next_to_choose(st.session_state.team_to_choose)


            #for rider in st.session_state.rdf[(st.session_state.rdf.group == group) & (st.session_state.rdf.team == st.session_state.team_to_choose)].NAVN.tolist():

            #    st.session_state.cards[rider] = play_riders_cards(rider, sv, st.session_state.cards[rider], gruppefart1,
            #                                                  gruppefart, groups_new_positions, 0)

        #else: #IF COMPUTER MOVES
            #for rider in st.session_state.rdf.NAVN.tolist():
            #    st.write(rider, ' position: ', st.session_state.cards[rider]['position'])

            for j in range (0,st.session_state.number_of_teams - 1):
                st.session_state.team_to_choose = next_to_choose(st.session_state.team_to_choose, st.session_state.teams)    #st.write(allpaces[j])
                k = 0
                for rider in st.session_state.rdf[(st.session_state.rdf.group == group) & (st.session_state.rdf.team == st.session_state.team_to_choose)].NAVN.tolist():
                    #st.write('jk', j, k)
                    st.write(rider, 'has ', get_number_ecs(st.session_state.cards[rider]), ' ecs')
                    st.write('selected speed' + str(st.session_state.cards[rider]['selected_value'] ))
                    #st.write('cards before', st.session_state.cards[rider])
                    st.session_state.cards[rider], st.session_state.groups_new_positions = move_riders(rider, sv,
                                                                                                             st.session_state.cards[
                                                                                                                 rider],
                                                                                                             gruppefart1,
                                                                                                             gruppefart,
                                                                                                             st.session_state.groups_new_positions, False,
                                                                                                             st.session_state.cards[
                                                                                                                 rider][
                                                                                                                 'selected_value'],
                                                                                                             st.session_state.track,
                                                                                                             pull_value,
                                                                                                             riders_pulling)

                    #st.session_state.cards[rider], st.session_state.groups_new_positions = play_riders_cards(rider, sv, st.session_state.cards[rider], gruppefart1, gruppefart, st.session_state.groups_new_positions, st.session_state.cards[rider]['selected_value'] , st.session_state.track, pull_value, riders_pulling)
                    st.write('played:', str(st.session_state.cards[rider]['played_card'][1]) + '. ' + str(st.session_state.cards[rider]['played_card'][2]) + ' -- ' + str(st.session_state.cards[rider]['played_card'][0]) )
                    st.markdown(':green[New position:' + str(st.session_state.cards[rider]['position']) + ']')
                    st.write(rider, 'has ', get_number_ecs(st.session_state.cards[rider]), ' ecs', get_number_tk1(st.session_state.cards[rider]))
                    st.session_state.cards[rider]['selected_value'] = -1

                    if st.session_state.cards[rider]['attacking_status'] == 'attacker':
                        st.session_state.cards[rider]['discarded'].append(['TK-1: 99', -1, -1])
                        st.session_state.cards[rider]['cards'].insert(0, ['TK-1: 99', -1, -1])
                        st.write('..and 2 more TK-1')
                        st.session_state.cards[rider]['attacking_status'] == 'no'
                        attacking_group = True
                #    st.write('5')
                    #st.write('cards after:', st.session_state.cards[rider])
                    st.divider()
                    k = 1+k

            if attacking_group:
                #if 1 == 2:
                if get_group_position_from_cards(st.session_state.cards, group) in range(get_group_position_from_cards(st.session_state.cards, group +1), get_group_position_from_cards(st.session_state.cards, group +1) + sv + 1):
                    st.write('Pull attackers back??')
                    your_invest = st.text_input('how much are you willing to invest?')
                    while your_invest == '':
                        time.sleep(1)
                    else:
                        attacking_teams = get_teams_in_group(group)
                        team_investment = 0
                        riders_investing = []
                        for team in st.session_state.teams[1::]:
                            if team not in attacking_teams:
                                investment, riders_investing2 = get_investment(team, group+1)
                                riders_investing.extend(riders_investing2)
                                team_investment = sum(investment) + team_investment
                                st.write(team, 'invests', ', '.join(map(str,investment)))

                        invest = int(your_invest) + team_investment
                        your_invest = int(your_invest)
                        st.write('invest total:', invest, '...', ' ,'.join(riders_investing), 'invests')



                    #tildel tk-1ere
                    if your_invest > 0:
                        riders_defending = st.text_input('who invests from your team?')
                        for rider in riders_defending.split(','):
                            st.session_state.cards[rider]['cards'].insert(0, ['TK-1: 99', -1, -1])
                            st.write(rider, 'takes TK-1')
                        if len(riders_defending.split(',')) < 2 and your_invest == 2:
                            st.session_state.cards[rider]['discarded'].insert(0, ['TK-1: 99', -1, -1])
                            st.write(rider, 'and another for the bottom')

                    for rider in riders_investing:
                        st.session_state.cards[rider]['cards'].insert(0, ['TK-1: 99', -1, -1])
                        st.write(rider, 'takes TK-1')

                    if invest > 1:
                        st.write('attack is being pulled back')
                        for rider in st.session_state.rdf[(st.session_state.rdf.group == group)].NAVN.tolist():
                            st.session_state.cards[rider]['position'] = get_group_position_from_cards(st.session_state.cards, group +1)
                    else:
                        st.write('Not enough investment to pull attack back')
                else:
                    st.write('Too far away to pull back')






            if st.session_state.track[group_position + gruppefart] == 'F':
                track_length = st.session_state.track.find('F')

                for rider in st.session_state.rdf[(st.session_state.rdf.group == group)]['NAVN'].tolist():
                    if st.session_state.cards[rider]['position'] > track_length - 1:

                        st.session_state.cards[rider]['prel_time'] = np.floor(st.session_state.round) * 60
                        st.session_state.cards[rider]['prel_time'] = st.session_state.cards[rider]['prel_time'] + 60*(track_length-group_position)/(st.session_state.cards[rider]['position']-group_position)


                        col4.write(rider + 'prel_time' + str( st.session_state.cards[rider]['prel_time']))


            st.session_state.group_to_move = st.session_state.group_to_move - 1
            st.session_state.team_to_choose = next_to_choose(st.session_state.team_to_choose, st.session_state.teams)
        st.button('finish roundy')


            #if st.session_state.group_to_move > 1:
            #    if st.button('move next group'):
            #        st.session_state.group_to_move = st.session_state.group_to_move - 1
                #for rider in st.session_state.rdf.NAVN.tolist():
                #    st.write(rider, ' position: ', st.session_state.cards[rider]['position'])

        #for rider in st.session_state.rdf.NAVN.tolist():
        #    st.write(rider, ' position: ', st.session_state.cards[rider]['position'])

    st.write('finish round')
    st.session_state.rdf = transfer_positions(st.session_state.cards, st.session_state.rdf, False)
    st.dataframe(st.session_state.rdf)

    st.session_state.rdf = transfer_positions(st.session_state.cards, st.session_state.rdf, False)

    play_round = False








    #AFTER ALL GROUPS
    #CALCULATE NEW GROUPS
    # if st.session_state.human_chooses_cards ==9:
    # #transfer_positions()


    #START NEW ROUND




    #assing trætkort




#            checkbx2 = st.checkbox('choose card', value = False)
 #           if checkbx2:

  #              keystring3 = str(len(st.session_state.riders)) + '3'
   #             checkbx2 = False
    #            st.session_state.cards[st.session_state.ryttervalg]['takes_lead'] = col1.radio('takes the lead', (True, False), key=keystring3)

     #           checkbx3 = st.checkbox('confirm', value=False)

      #


#st.session_state.riders = []
#tracks = ['Amstel Gold Race', 'Fleche Wallone', 'Liege-Bastogne-Liege', 'World Championship 2019 (Yorkshire)']




#if col3.button('Start new game'):
#    st.session_state.game_started == False
    #st.write('Uphill:', flatlist)
#human_chooses_cards(st.session_state.cards, st.session_state.riders)

#if st.session_state.computer_chooses_cards:


###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD
###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD
###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD
###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD
###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD
###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD###########OLD











