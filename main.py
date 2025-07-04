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

if "stages" not in st.session_state:
    st.session_state['stages'] = []

if "no_of_stages" not in st.session_state:
    st.session_state['no_of_stages'] = 0

if "hill_type" not in st.session_state:
    st.session_state['hill_type'] = 'normal'

if "latest_prel_time" not in st.session_state:
    st.session_state['latest_prel_time'] = -5

#st.session_state.latest_prel_time

if "groups_new_positions" not in st.session_state:
    st.session_state.groups_new_positions = []

if "udbrud_start" not in st.session_state:
    st.session_state.udbrud_start = 5

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

def get_team_mates_in_group(rider):
    team_mates = []
    for rider2 in st.session_state.cards:
        if st.session_state.cards[rider2]['team'] == st.session_state.cards[rider]['team']:
            if st.session_state.cards[rider2]['group'] == st.session_state.cards[rider]['group']:
                if rider2 != rider:
                    team_mates.append(rider2)
    return team_mates

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
    if track[pos1] == '_': #NYNEDAD
        return 1
    if '0' in track[pos1:pos2+1]:
        return 0
    if '1' in track[pos1:pos2+1]:
        return 1
    if '2' in track[pos1:pos2+1]:
        return 2
    else:
        return 3

def tjek_stejl(pos1, pos2, track):
    pos1 = int(pos1)
    pos2 = int(pos2)
    if '0' in track[pos1-1:pos2]:
        return 1
    else:
        return 0

generate = False

def get_weighted_value(track, factor=0.5):
    #st.write(track)
    tr = track[0:track.find('F') + 1]
    tr = tr[0:tr.index('F')]
    tr=tr[::-1]
    tr = tr.replace('_', '3')

    tr = list(tr)


    #st.write(tr)
    sum = 0
    i = 1
    total_sum=0

    for number in tr:
        #st.write(number)
        if int(number) == 0:
            number = 0.5
        number = float(number)*2/3
        sum = (number*(1/i)**factor)  + sum
        total_sum = total_sum + (1/i)**factor
        #col4.write(total_sum)
        i = 1+i
    #col4.write(sum, total_sum)
    try:
        return sum / total_sum
    except:
        return 3
def get_value(track):
    #st.write(track)
    tr = track[0:track.find('F') + 1]

    tr = tr.replace('_', '3')

    tr = list(tr)

    tr = tr[0:tr.index('F')]
    #st.write(tr)
    sum = 0
    for number in tr:
        #st.write(number)
        sum = float(number) * 2/3 + sum
        #sum = sum * 2 / 3 #fordi gået fra 2 til 3 i SV.
    #st.write('success')
    try:
        return 100*(2 - sum / len(tr))**2

    except:
        return 100

def get_length(track):
    tr = track[0:track.find('F') + 1]
    tr = tr.replace('3', '6')
    tr = tr.replace('_', '9')
    tr = tr.replace('2', '4')
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

def get_group_size(group):
    i = 0
    for rider in st.session_state.cards:
        if st.session_state.cards[rider]['group'] == group:
            i = 1+i
    return i
def get_e_move_left(rider, cards, track):

    group_size = get_group_size(rider['group'])
    length_left = len(track[rider['position']:track.find('F')])


    diff_left = 2-get_weighted_value(track[rider['position']::])

    av_speed = 5 - 0.15*(diff_left * (70-rider['bjerg'])) - 1.5*rider['fatigue']
    track_value = 100*0.2+0.8*(100-get_value(track[rider['position']::]))

    moves_left = length_left / (av_speed+0.001*track_value*group_size**0.5)
    return moves_left

def get_favorit_points(rider):
    #factor = (get_weighted_value(st.session_state.track) - 0.3)*0.06
    return 1/(1.5 + rider['e_moves_left'])

def get_total_moves_left(cards, factor):
    sum = 0
    for rider in cards:
        sum = sum + cards[rider]['favorit_points']**factor
    return sum


def get_win_chance_wo_sprint(rider, sum, factor):
    return 100 * (rider['favorit_points'] ** factor / sum)



def get_win_chance(rider, sum, factor, sprint_weight):

    return (1-sprint_weight) * (rider['win_chance_wo_sprint'])+ (sprint_weight)*rider['sprint_chance']






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
                if sprint_type in [0,1,2]:
                    sprint_value = 2
                if sprint_type == 3:
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

def pick_value(rider, track, paces):
    if st.session_state.cards[rider]['takes_lead'] == 0:
        return 0
    #favorit = st.session_state.cards[rider]['favorit']
    if st.session_state.cards[rider]['attacking_status'] == 'attacker':
        ideal_move = 100
        uphill = True

    #if random.random() < favorit * 1.5 / 100:
        #ideal_move = 100

    #random.shuffle(rider['cards'])

    # for card in rider['cards'][0:4]:
    # st.write(str(card[0]) + '-' + str(card[1]) + '-' + str(card[2]))

    else:
        track_length = track.find('F')
        len_left = track_length  - st.session_state.cards[rider]['position']

        diff_left = len_left / get_length(track)

        # jo længere til mål, jo lavere
        best_left = max(1,track_length - st.session_state.rdf.position.max())

        ideal_move = (len_left/best_left)**2 + 4
        #st.write(ideal_move -3  , 'ideal move basis')


        ideal_move = ideal_move + takes_lead_fc(rider, st.session_state.rdf, st.session_state.cards[rider]['attacking_status'], st.session_state.number_of_teams, True, False)**0.4
        ideal_move = ideal_move - len_left / 20


        if track[st.session_state.cards[rider]['position']] == '_':
            if ideal_move < 7.2:
                ideal_move = -10

        #/// check if correct
        #if '0' in track[rider['position']:rider['position']+7]:
        #    ideal_move = ideal_move / 2 + (1.5 * diff_left)
        #    uphill = True

        #if '1' in track[rider['position']:rider['position']+7]:
        #    ideal_move = (1.5 * diff_left) + ideal_move / 2
        #    uphill = True



    #col1.write(rider + 'ideal_move: ' + str(int(ideal_move)))
    # st.write(rider)
    # st.write(ideal_move)
    sv = get_slipstream_value(st.session_state.cards[rider]['position'],st.session_state.cards[rider]['position'] + int(ideal_move), track)
    pvs = get_pull_value(paces, sv)

    if int(ideal_move) <= pvs[0]:
        if sv == 3 and pvs[1] == 1:
            print('sv3pvs1')
        else:
            #st.write('ideal_move', ideal_move, ' not enough')
            return 0

    selected = st.session_state.cards[rider]['cards'][0]

    penalty = 0

    for card in st.session_state.cards[rider]['cards'][0:4]:

        #st.write(card[1], 'in pick_value')

        if card[1] == -1:
            penalty = 1

    error = 1000
    # find det rigtige kort
    for card in st.session_state.cards[rider]['cards'][0:4]:
        sv = get_slipstream_value(st.session_state.cards[rider]['position'],
                                  st.session_state.cards[rider]['position'] + card[1], track)
        if sv < 3:

            value = card[2] - penalty
            error_card = abs(value - ideal_move) ** 2 + card[2] / 100
            errorTMs = 0
            for team_mate in get_team_mates_in_group(rider):

                errorTM = 25
                penalty = get_penalty(team_mate)
                for card in st.session_state.cards[team_mate]['cards'][0:4]:
                    value_tm = card[2] - penalty
                    errorTMcard = abs(value - value_tm + sv)
                    if errorTMcard < errorTM:
                        errorTM = errorTMcard

                errorTM = errorTM * st.session_state.cards[team_mate]['win_chance'] / 100

                print(team_mate, errorTM)
                errorTMs = errorTM + errorTMs

            len_left = track_length - st.session_state.cards[rider]['position']
            error_total = 4 * error_card / len_left + errorTMs
            print(rider, error_card / len_left, errorTMs)

            if error_total < error:
                selected = card
                error = error_total
            ##gammel if abs(value - ideal_move) + card[2] / 100 < abs(selected[2] - ideal_move) + selected[1] / 100:
            ## gammel selected = card

        else:
            value = card[1] - penalty

            error_card = abs(value - ideal_move) ** 2 + card[2] / 100
            errorTMs = 0
            for team_mate in get_team_mates_in_group(rider):

                errorTM = 25
                penalty = get_penalty(team_mate)
                for card in st.session_state.cards[team_mate]['cards'][0:4]:
                    value_tm = card[1] - penalty
                    errorTMcard = abs(value - value_tm + sv)
                    if errorTMcard < errorTM:
                        errorTM = errorTMcard

                errorTM = errorTM * st.session_state.cards[team_mate]['win_chance'] / 100

                print(team_mate, errorTM)
                errorTMs = errorTM + errorTMs

            len_left = track_length - st.session_state.cards[rider]['position']
            error_total = error_card / len_left + errorTMs
            print(rider, error_card / len_left, errorTMs)

            if error_total < error:
                selected = card
                error = error_total



    #if uphill == False:
    #    print(rider['cards'][0:4])
    #    for card in rider['cards'][0:4]:
    #        value = card[1]-penalty
    #        print(abs(card[1] - ideal_move))
    #        print(abs(selected[1] - ideal_move))

    #        if abs(value - ideal_move) < abs(selected[1] - ideal_move):
    #            print('yes')
    #            selected = card
                #print('selected' + selected)

    # st.write('selected=' + str(selected[0]))

    #rider['played_card'] = selected
    #rider['cards'].remove(selected)
    #st.write(rider, selected)
    #//// selected must be either number 1 or 2
    if sv == 3:
        selected = selected[1]

    else:
        selected = selected[2]

    if selected <= get_pull_value(paces, sv)[0]:
        if sv == 3 and pvs[1] == 1:
            print('sv3pvs1')
        else:
            st.write('selected', selected, ' not enough')
            return 0

    return selected - penalty

def pick_value_old(rider, track):
    if rider['takes_lead'] == 0:
        return 0
    
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
            ideal_move = ideal_move - 2 #NYNEDAD
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

    for card in rider['cards'][0:4]:
        sv = get_slipstream_value(rider['position'],rider['position'] + card[1], track)
        if sv < 2:
            value = card[2] - penalty
            if abs(value - ideal_move) + card[2] / 100 < abs(selected[2] - ideal_move) + selected[1] / 100:
                selected = card

        else:
            value = card[1] - penalty
            if abs(value - ideal_move) + card[1] / 100 < abs(selected[1] - ideal_move) + selected[1] / 100:
                selected = card



    #if uphill == False:
    #    print(rider['cards'][0:4])
    #    for card in rider['cards'][0:4]:
    #        value = card[1]-penalty
    #        print(abs(card[1] - ideal_move))
    #        print(abs(selected[1] - ideal_move))

    #        if abs(value - ideal_move) < abs(selected[1] - ideal_move):
    #            print('yes')
    #            selected = card
                #print('selected' + selected)

    # st.write('selected=' + str(selected[0]))

    #rider['played_card'] = selected
    #rider['cards'].remove(selected)
    #st.write(rider, selected)
    #//// selected must be either number 1 or 2
    if get_slipstream_value([rider['position'],rider['position']+selected[1]], track) == 2:
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

        ned_igen2 = track2[stigning:].find('3')
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

        ned_igen = track2[nedad:].find('3')
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
        df.loc[df['NAVN'] == rider, 'win_chance'] = dict[rider]['win_chance']
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
    longest = 1
    current = 0
    for i in track:
        if i in ['0','1']:
            current = 1 + current
        if i == '2':
            current = 0.5 + current

        if i == '3':
            current = 0
        if i == '_':
            current = 0
        longest = max(longest, current)

    return longest


def get_random_track():
    track = str(max(random.randint(0, 3), random.randint(0, 3)))
    ned = 0
    if track == '2' and random.random() > 0.4:
        track = '1'
    for i in range(0, 55 + random.randint(0, 6) + random.randint(0, 6)):

        if track[i] == '_' and random.random() < ned * 0.15:
            track = track + '_'

        elif track[i] != '_' and random.random() > (0.5 - int(track[i]) * 0.1):

            track = track + track[i]


        else:

            a = random.random()
            if a < 0.03:
                track = track + '0'
                ned = ned +1
            elif a < 0.25:
                track = track + '1'
                ned = ned + 1
            elif a < 0.32:
                track = track + '2'
                ned = ned + 0.5
            elif a < 0.62 and track[i] != '3':
                track = track + '_'
                ned = ned - 1.5
            else:
                track = track + '3'
                ned = 0

    track = track + 'FFFFFFFFFFF'
    st.write(track)
    return track

def takes_lead_fc(rider, df, attacking_status, number_of_teams, floating = False, write=False):
    if attacking_status == 'attacker':
        return 1

    group = st.session_state.cards[rider]['group']
    sdf = df[df['group'] == group]
    group_size = sdf.shape[0]
    teams_in_group = sdf.team.nunique()
    len_left = track.find('F') - st.session_state.cards[rider]['position']
    best_sel_card = 100
    favorit = (st.session_state.cards[rider]['favorit']+2)

    team = df[df['NAVN'] == rider]['team'].tolist()[0]
    sprint = df[df['NAVN'] == rider]['SPRINT'].tolist()[0]
    fra_team_i_gruppe = sdf[sdf.team == team].shape[0]
    ratio = fra_team_i_gruppe / group_size
    sv = get_slipstream_value(st.session_state.cards[rider]['position'], st.session_state.cards[rider]['position'] + 8,
                         track)


    if ratio == 1:
        if floating == False:
            return 1
        else:
            return 6

    bjerg = df[df['NAVN'] == rider]['BJERG'].tolist()[0]
    flad = df[df['NAVN'] == rider]['FLAD'].tolist()[0]

    fb_ratio = (flad / bjerg) **2
    if sv < 2:
        fb_ratio = 1/fb_ratio

    mentalitet = df[df['NAVN'] == rider]['MENTALITET'].tolist()[0]

    for card in st.session_state.cards[rider]['cards'][0:4]:
        best_sel_card = min(best_sel_card, int(card[0][-2:-1] + card[0][-1]))


    #st.write(attack_prob, 'attack_prob')

    if group_size > 2:
        if attacking_status != 'attacked':

            attack_prob_percent = 0.25
            if len(st.session_state.attackers_in_turn) > 0:
                attack_prob_percent = attack_prob_percent*4

            if ratio > 0.4999:
                attack_prob_percent = attack_prob_percent * (ratio / 0.4) ** 8

            attack_prob_percent = attack_prob_percent * ((20/len_left) ** (favorit/5))**0.5
            #st.write(rider, 'attack_prob', attack_prob_percent)
            attack_prob_percent = attack_prob_percent / (best_sel_card)
            #st.write(rider, '1attack_prob', attack_prob_percent)
            attack_prob_percent = attack_prob_percent / (group ** 1.45 )
            #st.write(rider, '2attack_prob', attack_prob_percent)
            attack_prob_percent = attack_prob_percent / (max(1,sv)**(favorit/5))
            #st.write(rider, '3attack_prob', attack_prob_percent, (max(1,sv)**(favorit/5)))
            attack_prob_percent = attack_prob_percent / len(df) * 9
            attack_prob_percent = attack_prob_percent * (mentalitet / 4)
            attack_prob_percent = attack_prob_percent * fb_ratio


            #attack_prob_percent = attack_prob_percent * ((group_size ** 1.5)/2
            attack_prob = int(1/attack_prob_percent) + 1


            #st.write(rider, 'attack_prob', attack_prob)
            if random.randint(0, attack_prob) == 1:

                if group_size > 2:
                    if floating == False:

                        st.write(rider, 'attacksy')
                        return 2

    takes_lead = 0
    prob_front = 0
    prob_team_front = 0
    prob_group = 0
    prob_team_back = 0
    prob_team_group = 0
    prob_back = 0
    team = st.session_state.cards[rider]['team']
    prob_others_front = 0
    back_own_team_sh = 0
    front_own_team_sh = 0
    team_members_in_group = 0

    for rider2 in st.session_state.cards:
        if st.session_state.cards[rider2]['group'] == group:

            if st.session_state.cards[rider2]['team'] == team:
                prob_team_group = prob_team_group + st.session_state.cards[rider2]['win_chance'] / 100
                prob_group = prob_group + st.session_state.cards[rider2]['win_chance'] / 100
                team_members_in_group = team_members_in_group + 1
            else:
                prob_group = prob_group + st.session_state.cards[rider2]['win_chance']/ 100
        if st.session_state.cards[rider2]['group'] < group:
            if st.session_state.cards[rider2]['team'] == team:
                prob_team_front = prob_team_front + st.session_state.cards[rider2]['win_chance']/ 100
                prob_front = prob_front+ st.session_state.cards[rider2]['win_chance']/ 100
            else:
                prob_front = prob_front + st.session_state.cards[rider2]['win_chance'] / 100
        if st.session_state.cards[rider2]['group'] > group:
            if st.session_state.cards[rider2]['team'] == team:
                prob_team_back = prob_team_back + st.session_state.cards[rider2]['win_chance']/ 100
                prob_back = prob_back + st.session_state.cards[rider2]['win_chance']/ 100
            else:
                prob_back = prob_back + st.session_state.cards[rider2]['win_chance'] / 100
    print(rider, prob_group, prob_back, prob_front, prob_team_group)
    prob_teammembers_in_group = prob_team_group - st.session_state.cards[rider]['win_chance']/ 100
    #st.write()
    helping_team = prob_team_group / (st.session_state.cards[rider]['win_chance']/ 100)

    if helping_team < team_members_in_group:
        captain = 1
    else:
        captain = 0

    prob_team_group_share = (prob_team_group - 0.1 * st.session_state.cards[rider]['win_chance']/ 100)/ prob_group


    chance_tl = 0
    #helping team, høj hvis man er meget hjælperytter


    try:
        front_own_team_sh = prob_team_front / (prob_front+0.1)
    except:
        print('no')
    try:
        back_own_team_sh = prob_team_back / (prob_back+0.1)
    except:
        print('no')

    #if floating == False:
    print(rider, 'team: (', st.session_state.cards[rider]['team'], 'prob_team_group', prob_team_group, 'back_wins_team_sh', back_own_team_sh, 'front_wins_team_sh', front_own_team_sh, 'helping team', helping_team)
    #chance_tl = 1

    #hvis dem foran har høj sandsynlighed. Og eget hold har lavere sandsynlighed.
    #Eller Hvis dem bagved har høj sandsynlighed. Og eget hold har lav sandsynlighed.
    #Kig hvor eget hold har størst sandsynlighed. Foran eller bagved.

    #Høj hastighed hvis høj (max prob_front, prob_back)
    #Høj hastighed hvis egen høj sandsynlighed i gruppen.
    #Høj hastighed hvis hjælperytter til stede.
    #if prob_team_group > max(prob_team_front,prob_team_back):
    #    benchmark = back_own_team_sh
    #else:
    #    benchmark = front_own_team_sh

####CALCULATE TAKE LEAD
    if prob_team_group_share > front_own_team_sh:
            #høj hvis man er favorit i gruppen
        chance_tl = ((prob_team_group_share - prob_team_front) * st.session_state.number_of_teams)**2

        if st.session_state.cards[rider]['attacking_status'] == 'attacked':
            chance_tl2 = chance_tl * (25/len_left)
            favort = 0
            for rider in st.session_state.attackers_in_turn:
                favorit = favorit + st.session_state.cards[rider].favorit

            chance_tl2 = chance_tl2 * (favorit / 5)

            chance_tl = max(chance_tl2,chance_tl)
            if floating == False:

                col4.caption('blevet angrebet')
                col4.write(chance_tl)

        if floating == False:

            col4.write(rider + '(' + st.session_state.cards[rider]['team'] + ')'+ 'w_c: ' + str(int(st.session_state.cards[rider]['win_chance'])))
            col4.caption('er der nogen foran?')
            col4.write(chance_tl)
        # høj hvis man er hjælperytter i gruppen
        chance_tl = chance_tl * ((helping_team-0.5*captain)/team_members_in_group)
        # men også høj hvis man er kaptain, holdkammerater er trætte og der er bakker.
        if floating == False:
            col4.caption('helping team')
            col4.write(chance_tl)

        if sv < 2 and st.session_state.cards[rider]['bjerg'] > 71:
            chance_tl2 = chance_tl * (st.session_state.cards[rider]['bjerg']-72)
            chance_tl2 = chance_tl2 * (10/len_left)
            chance_tl2 = chance_tl2 * (1/ best_sel_card)**0.5
            chance_tl = max(chance_tl2, chance_tl)
            if floating == False:
                col4.caption('captajn og bakke og sent')
                col4.write(chance_tl)


        #up hvis man har mange holdkammerater i gruppen
        chance_tl = chance_tl * ((team_members_in_group - captain) / (group_size / teams_in_group))
        if floating == False:
            col4.caption('er der mange holdkammerater?')
            col4.write(chance_tl)
        #op hvis dem foran eller bagved har høj sandsynlighed
        chance_tl = chance_tl * (max(1/number_of_teams, prob_front - prob_team_front*number_of_teams, prob_back-prob_team_back*number_of_teams) * number_of_teams)**2
        if floating == False:
            col4.caption('er der fare på færde fra dem foran?')
            col4.write(chance_tl)
            #chance_tl = chance_tl * (st.session_state.number_of_teams**0.5)

        #ned hvis man ikke har gode kort eller er træt.
        chance_tl = chance_tl * (1- st.session_state.cards[rider]['fatigue'])**0.5
        chance_tl = chance_tl * min(1,7/best_sel_card)**2
        if floating == False:
            col4.caption('træt og dårlige kort?')
            col4.write(chance_tl)

        chance_tl = chance_tl * (60/len_left)**0.5

        human = human_responsibility(group, ['Me'], group_size, teams_in_group, number_of_teams, len_left)
        col4.caption(human)
        chance_tl = chance_tl / max(1, human)**.5

        if write == True:
            col4.caption('mennesket')
            col4.write(chance_tl)
    else:
        if floating == False:
            st.write(rider + ' (' + st.session_state.cards[rider]['team'] + ') - vil ikke føre')


    if floating == False:
        if random.random() > 1/(chance_tl+0.001):
            takes_lead = 1
            st.write('TAKES_LEAD')
            col4.caption('takes leadchy!!')

    if floating == True:
        takes_lead = chance_tl

    return takes_lead

def takes_lead_fc_old(rider, df, attacking_status, number_of_teams, floating = False):
    if attacking_status == 'attacker':
        return 1

    group = df[df['NAVN'] == rider]['group'].tolist()[0]
    sdf = df[df['group'] == group]
    group_size = sdf.shape[0]
    len_left = track.find('F') - st.session_state.cards[rider]['position']
    best_sel_card = 100
    favorit = (st.session_state.cards[rider]['favorit']+2)

    team = df[df['NAVN'] == rider]['team'].tolist()[0]
    sprint = df[df['NAVN'] == rider]['SPRINT'].tolist()[0]
    fra_team_i_gruppe = sdf[sdf.team == team].shape[0]
    ratio = fra_team_i_gruppe / group_size
    sv = get_slipstream_value(st.session_state.cards[rider]['position'], st.session_state.cards[rider]['position'] + 8,
                         track)


    if ratio == 1:
        return 1

    bjerg = df[df['NAVN'] == rider]['BJERG'].tolist()[0]
    flad = df[df['NAVN'] == rider]['FLAD'].tolist()[0]

    fb_ratio = (flad / bjerg) **2
    if sv < 2:
        ratio = 1/ratio

    mentalitet = df[df['NAVN'] == rider]['MENTALITET'].tolist()[0]

    for card in st.session_state.cards[rider]['cards'][0:4]:
        best_sel_card = min(best_sel_card, int(card[0][-2:-1] + card[0][-1]))


    #st.write(attack_prob, 'attack_prob')
    if group_size > 2:
        if attacking_status != 'attacked':
            attack_prob_percent = .25
            attack_prob_percent = attack_prob_percent * ((20/len_left) ** (favorit/5))**0.5
            #st.write(rider, 'attack_prob', attack_prob_percent)
            attack_prob_percent = attack_prob_percent / (best_sel_card)
            #st.write(rider, '1attack_prob', attack_prob_percent)
            attack_prob_percent = attack_prob_percent / (group ** 1.45 )
            #st.write(rider, '2attack_prob', attack_prob_percent)
            attack_prob_percent = attack_prob_percent / (max(1,sv)**(favorit/5))
            #st.write(rider, '3attack_prob', attack_prob_percent, (max(1,sv)**(favorit/5)))
            attack_prob_percent = attack_prob_percent / len(df) * 9
            attack_prob_percent = attack_prob_percent * (mentalitet / 4)
            attack_prob_percent = attack_prob_percent * fb_ratio


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

    ratio = ratio + 1/number_of_teams - own_riders_ahead_share

    ratio = ratio * ((sdf[sdf.team == team].favorit.min() / favorit) ** fra_team_i_gruppe)

    if group_size > 3:
        ratio = ratio - (favorit**(1+group_size/20)/100)

    ratio = ratio + random.randint(0, 8) / 100
    ratio = ratio - random.randint(0, 8) / 100
    ratio = ratio - st.session_state.cards[rider]['takes_lead']*.2


    if random.random() < ratio * number_of_teams**1.15:
        takes_lead = 1

    if floating == True:
        takes_lead = ratio

    return takes_lead


def slipstream_value(cards, track, group):
    return 'ppop'

def human_responsibility(group, human_teams, group_size, teams_in_group, number_of_teams, len_left):
    print('HUMMANNN')#sdf = df[df['group'] == group]

    responss = []

    for team in human_teams:
        print(team)
        chance_tl = 0
        prob_front = 0
        prob_team_front = 0
        prob_group = 0
        prob_team_back = 0
        prob_team_group = 0
        prob_back = 0
        #team = st.session_state.cards[rider]['team']
        prob_others_front = 0
        back_own_team_sh = 0
        front_own_team_sh = 0
        team_members_in_group = 0

        for rider2 in st.session_state.cards:
            #print(rider2)
            if st.session_state.cards[rider2]['group'] == group:

                if team in st.session_state.cards[rider2]['team']:
             #       print(rider2)
                    prob_team_group = prob_team_group + st.session_state.cards[rider2]['win_chance'] / 100
                    prob_group = prob_group + st.session_state.cards[rider2]['win_chance'] / 100
                    team_members_in_group = team_members_in_group + 1
                else:
                    prob_group = prob_group + st.session_state.cards[rider2]['win_chance'] / 100
            if st.session_state.cards[rider2]['group'] < group:
                if team in st.session_state.cards[rider2]['team']:
                    prob_team_front = prob_team_front + st.session_state.cards[rider2]['win_chance'] / 100
                    prob_front = prob_front + st.session_state.cards[rider2]['win_chance'] / 100
                else:
                    prob_front = prob_front + st.session_state.cards[rider2]['win_chance'] / 100
            if st.session_state.cards[rider2]['group'] > group:
                if team in st.session_state.cards[rider2]['team']:
                    prob_team_back = prob_team_back + st.session_state.cards[rider2]['win_chance'] / 100
                    prob_back = prob_back + st.session_state.cards[rider2]['win_chance'] / 100
                else:
                    prob_back = prob_back + st.session_state.cards[rider2]['win_chance'] / 100
        #print(rider, prob_group, prob_back, prob_front, prob_team_group)

        prob_teammembers_in_group = prob_team_group / 100
        # st.write()
        #helping_team = prob_team_group / (st.session_state.cards[rider]['win_chance'] / 100)



        prob_team_group_share = prob_team_group  / prob_group

        chance_tl = 0
        # helping team, høj hvis man er meget hjælperytter

        try:
            front_own_team_sh = prob_team_front / (prob_front + 0.1)
        except:
            print('no')
        try:
            back_own_team_sh = prob_team_back / (prob_back + 0.1)
        except:
            print('no')



        ####CALCULATE TAKE LEAD
        if prob_team_group_share > front_own_team_sh:
            # høj hvis man er favorit i gruppen
            print(prob_team_group_share, prob_team_front, st.session_state.number_of_teams)
            chance_tl = ((prob_team_group_share - prob_team_front) * st.session_state.number_of_teams) ** 2
            print(chance_tl)




            # høj hvis man er hjælperytter i gruppen



            # up hvis man har mange holdkammerater i gruppen
            chance_tl = chance_tl * ((team_members_in_group) / (group_size / teams_in_group))
            print(chance_tl)
            # op hvis dem foran eller bagved har høj sandsynlighed
            chance_tl = chance_tl * (max(1 / number_of_teams, prob_front - prob_team_front * number_of_teams,
                                         prob_back - prob_team_back * number_of_teams) * number_of_teams) ** 2

            print(chance_tl)#chance_tl = chance_tl * (1 - st.session_state.cards[rider]['fatigue']) ** 0.5
            #chance_tl = chance_tl * min(1, 7 / best_sel_card) ** 2

            chance_tl = chance_tl * (60 / len_left) ** 0.5
            print(chance_tl)
        responss.append(chance_tl)

    print('END HUMAN')
    return max(responss)

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
    rdf['win_chance'] = 0

    riders = rdf.NAVN.tolist()
    brosten_factor = 0

    if track[-1] == 'B':
        col1.write('Brosten')
        brosten_factor = 1

    fladbrosten = 0
    if track[-1] == '*':
        fladbrosten = 1
        st.session_state['hill_type'] = 'pave'

    track = track[0:track.find('F')+1]

    riderteams = []
    for team in teams:
        for i in range(0, riders_per_team):
            riderteams.append(team)
    cards = {}
    i = -1
    udbrud = random.randint(0,peloton_size)
    udbrud = [udbrud]
    if peloton_size > 9:

#        udbrud = list(udbrud)
        udbrud.append(random.randint(0,peloton_size))

    longest_hill = get_longest_hill(track)
    puncheur_factor = min(1, 3 / max(longest_hill,3)) * puncheur
    col1.write(puncheur_factor)

    if fladbrosten == 1:
        rdf['BJERG'] = rdf['FLAD'] + rdf['BROSTEN']
        brosten_factor = 1
        for t in range(1,16):
            kolonne1 = 'BJERG'+str(t)
            kolonne2 = 'FLAD'+str(t)
            rdf[kolonne1] = rdf[kolonne2]
    else:
        rdf['BJERG'] = rdf['BJERG']+rdf['PUNCHEUR']*puncheur_factor + rdf['BROSTEN'] * brosten_factor



    for rider in riders:
        i = i + 1
        cards[rider] = {}
        cards[rider]['position'] = 0
        cards[rider]['cards'] = []
        cards[rider]['discarded'] = []
        cards[rider]['attacking_status'] = 'no'
        cards[rider]['group'] = 2
        cards[rider]['played_card'] = 0
        cards[rider]['selected_value'] = -1
        cards[rider]['moved_fields'] = 0
        cards[rider]['sprint'] = rdf.iloc[i]['SPRINT']
        cards[rider]['bjerg'] = rdf.iloc[i]['BJERG']
        cards[rider]['sprint_points'] = 0
        cards[rider]['ranking'] = 0
        cards[rider]['takes_lead'] = 0
        cards[rider]['noECs'] = 0
        cards[rider]['prel_time'] = 1000000
        cards[rider]['team'] = riderteams[i]
        cards[rider]['fatigue'] = 0
        cards[rider]['penalty'] = 0
        cards[rider]['e_moves_left'] = 12
        cards[rider]['favorit_points'] = 1
        cards[rider]['win_chance'] = 0
        cards[rider]['win_chance_wo_sprint'] = 0

        if i in udbrud:
            cards[rider]['position'] = st.session_state.udbrud_start
            cards[rider]['group'] = 1



        rpf = int(rdf.iloc[i]['PUNCHEUR'] * puncheur_factor)

        l = []
        #lave puncheurkort
        if rpf != 0:
            for k in range(1, 16):
                if k % (16 / (abs(rpf) + 1)) < 1:
                    l.append(int(rpf / abs(rpf)))
                else:
                    l.append(0)
        else:
            l = [0]*15

        m = []
        if brosten_factor == 1:
            rpf = rdf.iloc[i]['BROSTEN']
            for k in range(1, 16):
                if k % (16 / (abs(rpf) + 1)) < 1:
                    m.append(int(rpf / abs(rpf)))
                else:
                    m.append(0)

        else:
            m = [0]*15




        #st.write(rider, rpf, l)
        for j in range(15):
            if i in udbrud:
                if j == 5:
                    cards[rider]['cards'].append(['kort: 16', 2, 2])
                if j == 10:
                    cards[rider]['cards'].append(['kort: 16', 2, 2])
                else:
                    cards[rider]['cards'].append(
                        ['kort: ' + str(j + 1), int(rdf.iloc[i, 18 + j]), int(rdf.iloc[i, 33 + j])+l[j]+m[j]])

            else:
                cards[rider]['cards'].append(['kort: ' + str(j + 1), int(rdf.iloc[i, 18 + j]), int(rdf.iloc[i, 33 + j]) +l[j] + m[j]])



        random.shuffle(cards[rider]['cards'])
        #cards['select']={}


    #assign favorit
    track21 = min(get_value(track), 7) / max(get_value(track), 7)
    rdf['fav_points'] = 0.5 * (rdf['BJERG'] - 60) * get_value(track) * get_longest_hill(st.session_state.track) ** 0.5 + \
                        rdf['SPRINT'] * 15 + (rdf['BJERG 3'] - 21) * 1 * get_value(track[-15::]) + (
                        rdf['BJERG 3'] - 21) * 3 * track21 + (rdf['FLAD'] + rdf['SPRINT'] * 4 - 65) * (
                        15 / (get_value(track[-17::]) + 1))
    rdf = rdf.sort_values(by='fav_points', ascending=True)
    rdf['favorit'] = range(1, peloton_size+1)
    rdf['favorit'] = rdf['favorit'] / (peloton_size/9)

    rdf['sprint2'] = (rdf['SPRINT']+2)**1.5
    for rider in riders:
        cards[rider]['sprint_chance'] = (cards[rider]['sprint']+2)**1.5 / rdf['sprint2'].sum()


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
                st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='win_chance', ascending=False)[
                    'NAVN'].tolist()
                positions = \
                st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='win_chance', ascending=False)[
                    'position'].tolist()
                ECs = \
                st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='win_chance', ascending=False)[
                    'ECs'].tolist()
                takes_lead = \
                st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='win_chance', ascending=False)[
                    'takes_lead'].tolist()
                teams = \
                    st.session_state.rdf[st.session_state.rdf['group'] == i].sort_values(by='win_chance',
                                                                                         ascending=False)[
                        'team'].tolist()

                for i in range(len(riders)):
                    try:
                        if st.session_state.cards[riders[i]]['takes_lead'] == 1:

                            st.caption(riders[i] + ' . ' + str(positions[i]) + ' (' + teams[i] + ')' + ' :blue[takes lead] - ' + str(int(st.session_state.cards[riders[i]]['win_chance']))+'%')

                        else:
                            st.caption(riders[i] + ' . ' + str(positions[i]) + ' (' + teams[i] + ') - ' + str(int(st.session_state.cards[riders[i]]['win_chance']))+'%')
                    except:
                        pass#if takes_lead[i] == 1:
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
col4.caption('Take lead = 1TK')
col4.caption('Kort 1-2 = 1MK, Kort 3-5 = 1TK')
col4.caption('Max 1 penalty')
col4.caption('length = 63=200km + 1 pr 10')
col4.caption('ingen angreb hvis 2 i gruppen')
#col4.caption('sv 50% på flad')
col4.caption('Angreb koster 2MK + spillet kort')
col4.caption('nedad slipstream = 1, min 5')
#col4.caption('flad = sv 50%')
col4.write('------------')
col5.title('The Riders')
#col4.subheader('and their stats')
col5.write('------------')


#col3.write(st.session_state.cards)

##################
#track = '^^1---------^^^^3__------------^^^^^^^^^4------^^^^^2_----^^1-----FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF'
track = st.session_state['track']
track2 = colour_track(st.session_state['track'][0:st.session_state['track'].find('F')+1])
#human__cards = False
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
                colour = '#994444'
                text = text + '--SV2'
            if track[i] == '3':
                colour = '#999999'
                text = text + '--SV3'
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

tracks = ['sprinttest', 'World Championship 2019 (Yorkshire)','Liege-Bastogne-Liege', 'Bemer Cyclassics', 'Hautacam','Giro DellEmilia', 'GP Industria', 'UAE Tour', 'Kiddesvej', 'Kassel-Winterberg', 'Allerød-Køge', 'bjerg-flad', 'Askersund-Ludvika', 'Amstel Gold Race', 'Parma-Genova','FlandernRundt','BrostensTest','random']

if st.session_state.game_started == False:
    st.session_state['trackname'] = col1.radio('start new race', tracks)
    puncheur = col1.checkbox('puncheur stats', key='puncheut', value=True)
    checkbxtrack = col1.checkbox('choose', key='track_choose', value=False)
    riders_per_team = st.text_input('choose number of riders in each team', value=3)

    number_of_teams = st.text_input('choose number of teams', value=3)
    st.session_state.udbrud_start = st.text_input('udbrud start', value=5)
    st.session_state.udbrud_start = int(st.session_state.udbrud_start)
    st.session_state.number_of_teams = int(number_of_teams)
    shorten_track = '0'
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
            st.session_state['track'] = '3311111___333333333111333333333300000_3333333333333311133333333333333FFFFFFFFF'
        elif st.session_state['trackname'] == 'World Championship 2019 (Yorkshire)':
            st.session_state['track'] = '33333333333311333333333333331133333333333333113333333333333311333333FFFFFFFFF'
        elif st.session_state['trackname'] == 'bjerg-flad':
            st.session_state['track'] = '11111111111111111___33333333333333333333333333333333333333333FFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'Bemer Cyclassics':
            st.session_state['track'] = '3333333333333333333333333333313333311333333311333333333333333333FFFFFFFFFFFFF'

        elif st.session_state['trackname'] == 'Hautacam':
            st.session_state['track'] = '331111111111111111_______333331111111111111000000111111111111FFFFFFFFF'
        elif st.session_state['trackname'] == 'Giro DellEmilia':
            st.session_state['track'] = '___1111111_11___1111111_11___1111111_11___1111111_11___1111111FFFFFFFFFF'
        elif st.session_state['trackname'] == 'sprinttest':
            st.session_state['track'] = '111111FFFFFFFFFF'
        elif st.session_state['trackname'] == 'GP Industria':
            st.session_state['track'] = '3333333333333111111__333333333333333333333333111111__33333333333FFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'Kassel-Winterberg':
            st.session_state[
                'track'] = '333333333333333333333333333333331111111133333333333333__1111111333FFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'Askersund-Ludvika':
            st.session_state[
                'track'] = '3333333333333333333333333333333333333333333333333333331111__33333FFFFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'UAE Tour':
            st.session_state[
                'track'] = '33333333332222222221111111111111111111111111111111111111FFFFFFFFFF'
        elif st.session_state['trackname'] == 'Kiddesvej':
            st.session_state[
                'track'] = '33333333333333311333333333330033333333333003333333333333300FFFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'Allerød-Køge':
            st.session_state[
                'track'] = '3333333333333333333333333333333333333333333333333333333333333FFFFFFFFFF'
        elif st.session_state['trackname'] == 'Amstel Gold Race':
            st.session_state[
                'track'] = '33333333333113333113311330000333333333333003333311133333322333333FFFFFFFFFF'
        elif st.session_state['trackname'] == 'Parma-Genova':
            st.session_state[
                'track'] = '33222222222___3333333333111111111__333333333333333333333333FFFFFFFFFFFF'
        elif st.session_state['trackname'] == 'FlandernRundt':
            st.session_state[
                'track'] = '3333330033333311332233333333333330033333333331113333330033333333333FFFFFFFFFFFFFFB'
        elif st.session_state['trackname'] == 'BrostensTest':
            st.session_state[
                'track'] = '3333330033333311332233333333333330033333333331113333330033333333333FFFFFFFFFFFFFF*'
        elif st.session_state['trackname'] == 'random':
            st.session_state[
                'track'] = get_random_track()


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
    if _list == []:
        return 0, 0

    if sv > 2:
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





def choose_card_to_play(cards, sv, penalty, speed, chosen_value, extra = False):
    with col4:
        st.write('potential cards: ', cards[0:4])
    cards.append(['tk_extra 15', 2,2])
    chosen_card = False
    best_sel_card = 15
    #penalty = 0
    if chosen_value > 0:
        managed = True

        for card in cards[0:4]:
            if sv > 2:
                card_value = card[1] - penalty
            elif sv<3:
                card_value = card[2] - penalty
            if card_value  == chosen_value:

                if chosen_card:
                    if int(card[0][-2:-1] + card[0][-1]) > sel_card_number:
                        chosen_card = card
                        sel_card_number = int(card[0][-2:-1] + card[0][-1])
                        best_sel_card = min(sel_card_number, best_sel_card)

                    else:
                        p = 0
                else:
                    chosen_card = card
                    sel_card_number = int(card[0][-2:-1] + card[0][-1])
                    best_sel_card = min(sel_card_number, best_sel_card)



    if chosen_value == 0:
        if st.session_state.hill_type == 'pave':
            len_left = track.find('F') - st.session_state.cards[rider]['position']
            speed = 20/len_left + speed
        for card in cards[0:4]:
            managed = True
            if sv > 2:
                card_value = card[1] - penalty
            elif sv<3:
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
        if extra == True:
            best_sel_card = 100


            for card in cards[0:4]:
                sel_card_number = int(card[0][-2:-1] + card[0][-1])
                best_sel_card = min(sel_card_number, best_sel_card)

            col1.write('klarede den ikke. bedste kort:' + str(best_sel_card))

            if best_sel_card > 5:
                col1.write('takes two extra ccards')
                sel_card_number = 210
                for card in cards[0:6]:
                    if int(card[0][-2:-1] + card[0][-1]) < sel_card_number:
                        chosen_card = card
                        sel_card_number = int(card[0][-2:-1] + card[0][-1])

                return chosen_card, managed, 2

        #if best_sel_card > 5:



        managed = False
        sel_card_number = 210
        for card in cards[0:4]:
            if int(card[0][-2:-1] + card[0][-1]) < sel_card_number:
                chosen_card = card
                sel_card_number = int(card[0][-2:-1] + card[0][-1])

    return chosen_card, managed, 0

def move_riders(ridername, sv, rider, gruppefart1, speed, groups_new_positions, chosen_card, chosen_value, track, pull_value, riders_pulling):
    pull_value = max(pull_value,2)
    new_minus = rider['moved_fields']

    sv2 = sv
    #if sv == 3:
    #    sv2 = int(speed/2) #50%
        #st.write(sv)



    with col4:
        st.write(ridername, 'sv ', sv, 'gruppefart1 ', gruppefart1, 'speed ', speed, 'groups_new_positions[0][0] ',
                 groups_new_positions[0][0], 'chosen value:', chosen_value)



        penalty = get_penalty(ridername)
        # st.write(ridername, 'penalty:', penalty)

        if penalty > 0:
            col1.write(':red[penalty: ' + str(penalty) + ']')

        speed = groups_new_positions[0][0] - rider['position']


        st.write('speed:', speed, ' sv: ', sv, 'rider pos. bef. ', rider['position'])
        st.write(groups_new_positions)
        if rider['attacking_status'] == 'attacker':
            if track[rider['position'] + speed] == 'F':
                speed = speed - 1
                st.write('attacking over finishing line')
        riders_starting_position = rider['position']
        st.write('selected_value', chosen_value)
        speed2 = speed
        if track[rider['position']] == '_':
            speed2 = max(5, speed2)
            #NYNEDAD speed2 = max(5, speed2)
        rider['takes lead'] = 0
        #managed = True
        managed = False

        if sv > 2:
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

                chosen_card, managed, new_minus = choose_card_to_play(rider['cards'][0:6], sv2, penalty, speed, chosen_value, False)
                st.write('selects(sv2):', chosen_card, managed)
                if track[rider['position']] == '_':
                    chosen_card[1] = max(chosen_card[1],5)


            sel_card_number = int(chosen_card[0][-2:-1] + chosen_card[0][-1])
            if chosen_card[1] + sv2 - penalty >= speed:
                managed = True
                rider['position'] = rider['position'] + speed
                st.write('speed', speed)
                st.write('new position', rider['position'], 'SV2')

        if sv <= 2:
            st.write('sv<=2')
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
                chosen_card, managed, new_minus = choose_card_to_play(rider['cards'][0:4], sv2, penalty, speed, chosen_value, False)
                if track[rider['position']] == '_':
                    chosen_card[2] = max(chosen_card[2], 5)

            if chosen_card[2] + sv - penalty >= speed:
                managed = True
                rider['position'] = rider['position'] + speed
                st.write('speed', speed)
                st.write('new position', rider['position'])

            st.write('selects(sv1or2):', chosen_card, managed)

        st.write('selected?', chosen_card)
        sel_card_number = int(chosen_card[0][-2:-1] + chosen_card[0][-1])
        rider['played_card'] = chosen_card

        #if 'F' in track[riders_starting_position:rider['position']]:
        #    rider['position'] = rider['position']-1
        #if not managed:

        if sv > 2:
            value = chosen_card[1] - penalty + sv2

        if sv < 3:
            value = chosen_card[2] - penalty + sv

        if track[rider['position']] == '_':
            value = 5

        pot_position = min(rider['position'] + value, groups_new_positions[0][0])
        pot_position_wo_sv = pot_position-sv2
        new_pot_position = pot_position_wo_sv

        for groups_position in groups_new_positions:
            if pot_position >= groups_position[0]:
                #st.write('try position:', pot_position, 'to', groups_position, '(', groups_position[1])
                new_pot_position = max(groups_position[0], new_pot_position, pot_position_wo_sv)
                #st.write(pot_position, 'after trying')

        if new_pot_position > rider['position']:

            rider['position'] = new_pot_position
            #st.write('new new position', rider['position'])

        for card in rider['cards'][0:4]:
            rider['discarded'].append(card)
            rider['cards'].remove(card)

        #TEST!!!!!!!!!!!!!!
        if penalty > 0:
            rider['discarded'].remove(['TK-1: 99', -1, -1])
            rider['discarded'].append(['kort: 16', 2, 2])

        if new_minus == 2:
            col1.subheader('new minus = ' + str(new_minus))
            for card in rider['cards'][0:2]:
                rider['discarded'].append(card)
                rider['cards'].remove(card)

            rider['cards'].insert(0, ['TK-1: 99', -1, -1])
            rider['discarded'].append(['TK-1: 99', -1, -1])
            sel_card_number = 16
            rider['penalty'] = 2 + rider['penalty']

        #### TEST STOP
        try:
            rider['discarded'].remove(chosen_card)

        except:
            p = 0

        st.write('sel_card_number:', sel_card_number)

        ecs = int(takes_lead)

        if rider['attacking_status'] == 'attacker':
            takes_lead = False

        if takes_lead:
            col1.write('TAKES LEAD')
            ecs = 1

            if sel_card_number < 6:

                ecs = 2



            #if sel_card_number > 10 and riders_pulling < 2:
            #    ecs = 0


        if not takes_lead:
            rider['takes_lead'] = 0
            st.write('doesnot take lead')
            #if sv < 2:
            if sel_card_number < 6:
                ecs = 1

        #ecs = ecs + penalty
        #Forslag STÆRKT
        if rider['attacking_status'] == 'attacker':
            rider['takes_lead'] = 0
            ecs = 0
        if rider['attacking_status'] != 'attacker':
            if ecs > 0:
                rider['cards'].insert(0, ['kort: 16', 2, 2])
                st.write(ridername + 'takes' + str(ecs) + 'ECs')
            if ecs > 1:
                rider['discarded'].append(['kort: 16', 2, 2])

            if sel_card_number < 3:
                #if rider['attacking_status'] != 'attacker':
                rider['cards'].insert(0, ['TK-1: 99', -1, -1])
                rider['cards'].remove(['kort: 16', 2, 2])
                rider['penalty'] = 1 + rider['penalty']

        



        if len(rider['cards']) < 6:
            # st.write('shuffling riders cards')
            random.shuffle(rider['discarded'])
            for card in rider['discarded']:
                rider['cards'].append(card)
            rider['discarded'] = []

        groups_new_positions.append([rider['position'], sv])
        rider['moved_fields'] = 0



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
                a = takes_lead_fc(rider, st.session_state.rdf, st.session_state.cards[rider]['attacking_status'], st.session_state.number_of_teams, False, False)
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
        st.session_state['confirmcards'] = [False] * (st.session_state.group_to_move+20)
        st.session_state.rdf, st.session_state.cards = assign_new_group_numbers(st.session_state.rdf, st.session_state.cards)
        st.session_state.cards = set_all_to_no_attackers(st.session_state.cards)
        st.session_state.sprint_groups = detect_sprint_groups(st.session_state.rdf)
        for rider in st.session_state.cards:
            st.session_state.cards[rider]['fatigue'] = get_fatigue(st.session_state.cards[rider])
            #col4.write(rider + 'fatigue:' + str(st.session_state.cards[rider]['fatigue']))
            st.session_state.cards[rider]['e_moves_left'] = get_e_move_left(st.session_state.cards[rider], st.session_state.cards,
                                                                      st.session_state['track'])
            #col4.write(rider + 'e_moves_left:' + str( st.session_state.cards[rider]['e_moves_left']))
            st.session_state.cards[rider]['favorit_points'] = get_favorit_points(st.session_state.cards[rider])
        factor = 17 - 0.6 * st.session_state['round']
        total_points = get_total_moves_left(st.session_state.cards, factor)
        sprint_weight = get_weighted_value(st.session_state.track[st.session_state.rdf.sort_values(by='position', ascending=False).iloc[0].position.tolist()::])
        sprint_weight = 0.8*(sprint_weight - 1)**2
        ## new sprint_chance

        track_length = st.session_state.track.find('F')
        st.session_state.rdf['fields_left'] = track_length - st.session_state.rdf['position']
        min_pos = st.session_state.rdf.fields_left.min()
        col1.write('min_pos' + str(min_pos))
        st.session_state.rdf['sprint2'] = (st.session_state.rdf['SPRINT'] + 3) * ((min_pos / st.session_state.rdf['fields_left'])**2.5)
        st.session_state.rdf['sprint2'] = st.session_state.rdf['sprint2']**2
        #col4.dataframe(st.session_state.rdf))
        st.session_state.rdf['sprint_chance'] = st.session_state.rdf['sprint2'] / st.session_state.rdf['sprint2'].sum()
        st.session_state.rdf['sprint_chance'] = st.session_state.rdf['sprint_chance'].fillna(1/len(st.session_state.rdf))
        for rider in st.session_state.cards:
            st.session_state.cards[rider]['sprint_chance'] = 100 * st.session_state.rdf[st.session_state.rdf['NAVN'] == rider]['sprint_chance'].tolist()[0]

            #col4.write(st.session_state.cards[rider]['sprint_chance'])
        for rider in st.session_state.cards:
            st.session_state.cards[rider]['win_chance_wo_sprint'] = get_win_chance_wo_sprint(st.session_state.cards[rider], total_points, factor)
            st.session_state.cards[rider]['win_chance'] = get_win_chance(st.session_state.cards[rider], total_points,
                                                                        factor, sprint_weight)
        #    col4.write(rider + 'win_chance: ' + str(st.session_state.cards[rider]['win_chance']))
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


    with ((col1)):
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
                            st.session_state.cards[rider]['takes_lead'] = takes_lead_fc(rider, st.session_state.rdf,st.session_state.cards[rider]['attacking_status'], st.session_state.number_of_teams, False, True)
                            print(rider, st.session_state.cards[rider]['takes_lead'])
                            if st.session_state.cards[rider]['takes_lead'] == 2:

                                st.session_state.attackers_in_turn.append(rider)
                                st.write('Added to attackers in turn')
                                st.session_state.cards[rider]['takes_lead'] = 0
                                #st.write('attackers_in_turn:', st.session_state.attackers_in_turn)

                            #st.write('takes_lead:', st.session_state.cards[rider]['takes_lead'])
                            selected = pick_value(rider, st.session_state.track, paces)
                        #st.write(selected)
                            #st.write('selected:', selected)
                            st.session_state.cards[rider]['selected_value'] = st.session_state.cards[rider]['takes_lead']*selected

                        pace.append(st.session_state.cards[rider]['selected_value'])

                    if len(pace) > 0:
                        paces.extend(pace)
                        st.write(':green[' , st.session_state.team_to_choose, 'chooses ',  ", ".join(str(x) for x in pace) ,']')
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
            sv50 = sv
            if sv > 2:


                for pace in paces:
                    if pace > gruppefart - 1.5:
                        count = 1 + count

                with col4:
                    st.write('count (how many could be pulling?) ', count)
            #st.write(count)
                if count > 1:
                    #hvis fælger
                    if st.session_state.track[gruppefart+1+group_position] in ['3','F']:
                        gruppefart = 1 + gruppefart
                
                #sv50 = int(gruppefart/2) #50%
                        
                        

    

    
            st.write('group ' + str(group) + "'s speed is " + str(gruppefart), '. SV is:', str(sv50) + '. You have to move at least' + str(gruppefart-sv50))

            #st.write([gruppefart + group_position, sv], 'gets appended gto groups_new_posts')
            st.session_state.groups_new_positions.append([gruppefart + group_position, sv])

            st.session_state.groups_new_positions = sorted(st.session_state.groups_new_positions, key=lambda x: x[0],
                                                           reverse=True)
            st.write('you have to move ' + str(st.session_state.groups_new_positions[0][0]-group_position) + ' to catch the frontmost group.')
            j = 0

            pull_value, riders_pulling = get_pull_value(paces, sv)
            #st.write('pull_value: ', pull_value)

            st.session_state.team_to_choose = 'Me'
            st.write('choose cards, you played', str(Me_played_value))
            ###ÆNDRE NÆSTE LINIE
            p = -1
            ok = [False] * 20
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
                    keystring22 = rider + '2mere2'
                    ok[p] = st.checkbox('To kort mere?', value=False, key=keystring2+'2mere')
                    if ok[p] == True:
                        st.session_state.cards[rider]['played_card'] = col1.radio('hvilket kort?', (st.session_state.cards[rider]['cards'][0],
                                          st.session_state.cards[rider]['cards'][1],
                                          st.session_state.cards[rider]['cards'][2],
                                          st.session_state.cards[rider]['cards'][3], st.session_state.cards[rider]['cards'][4],
                        st.session_state.cards[rider]['cards'][5]), key = keystring22)
                        st.session_state.cards[rider]['moved_fields'] = 2
            keystring = str(group) + str(st.session_state.round) + 'confirmcards'
            st.session_state.confirmcards[group] = st.checkbox('confirm', value=False, key=keystring)

            while st.session_state.confirmcards[group] == False:
                time.sleep(1)
                if st.session_state.confirmcards[group] == True:
                    continue


            p = -1
            for rider in your_riders_in_group:#move riders




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
                        st.session_state.cards[rider]['penalty'] = 2 + st.session_state.cards[rider]['penalty']
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
                        st.session_state.cards[rider]['penalty'] = 2 + st.session_state.cards[rider]['penalty']
                        st.write('..and 2 more TK-1')
                        st.session_state.cards[rider]['attacking_status'] == 'no'
                        attacking_group = True
                #    st.write('5')
                    #st.write('cards after:', st.session_state.cards[rider])
                    st.divider()
                    k = 1+k

            if attacking_group:
                st.write(get_group_position_from_cards(st.session_state.cards, group),
                         get_group_position_from_cards(st.session_state.cards, group + 1),
                         get_group_position_from_cards(st.session_state.cards, group + 1) + sv + 1)

                #if 1 == 2:
                if get_group_position_from_cards(st.session_state.cards, group) in range(get_group_position_from_cards(st.session_state.cards, group +1) + 1, get_group_position_from_cards(st.session_state.cards, group +1) + sv + 1):
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
                            st.session_state.cards[rider]['penalty'] = 1 + st.session_state.cards[rider]['penalty']
                            st.write(rider, 'takes TK-1')
                        if len(riders_defending.split(',')) < 2 and your_invest == 2:
                            st.session_state.cards[rider]['discarded'].insert(0, ['TK-1: 99', -1, -1])
                            st.session_state.cards[rider]['penalty'] = 1 + st.session_state.cards[rider]['penalty']
                            st.write(rider, 'and another for the bottom')

                    for rider in riders_investing:
                        st.session_state.cards[rider]['cards'].insert(0, ['TK-1: 99', -1, -1])
                        st.session_state.cards[rider]['penalty'] = 1 + st.session_state.cards[rider]['penalty']
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
    #st.dataframe(st.session_state.rdf)

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











