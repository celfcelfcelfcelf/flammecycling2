#import gym
import gymnasium as gym
from gymnasium import spaces, make
import numpy as np
#from main import get_slipstream_value, get_pull_value
import random
import streamlit as st
from stable_baselines3 import PPO
import pandas as pd
#from gym import make


class GameEnv(gym.Env):
    def __init__(self, df):
        super(GameEnv, self).__init__()

        self.df = df  # Store the DataFrame

        # Initialize riders and track
        self.track, self.length = self.generate_terrain()
        self.riders = self.initialize_riders(self.df, self.track)
        self.groups = [2,1]


        # Define the observation space


        self.observation_space = spaces.Box(
            low=np.array(
                [0] * 9 +  # Cyclist Positions (9 values)
                [0] * 63 +  # Rider Attributes (9 riders * 7 attributes)
                [0] * 4 +  # Teammates' Positions and Favorite Numbers (2 positions + 2 favorites)
                [0] * 36 +  # Rider's and Teammates' Cards (3 riders * 4 cards * 3 values)
                [0] * 70,  # Track Terrain (70 values)
            ),
            high=np.array(
                [70] * 9 +  # Max positions
                [5] * 63 +  # Max attributes (assuming max of 5)
                [70] * 4 +  # Max positions and favorites
                [5] * 36 +  # Max card values (assuming max of 5)
                [5] * 70  # Max terrain values (assuming max of 5)
            ),
            dtype=np.float32
        )

        # Define the action space (3 or 4 possible actions)
        MAX_INVESTMENT = 10  # Set your maximum investment value
        #self.action_space = spaces.Tuple((spaces.Discrete(3), spaces.Box(low=0, high=9, shape=(1,), dtype=np.float32)  ))
        self.action_space = spaces.MultiDiscrete([3, 10])
        # Initialize the game state
        self.state = self.reset()


    def initialize_riders(self, df, track):

        df = df.head(66).iloc[1:]
        rdf = df.sample(9)

        # Set up team assignments
        team_assignments = ['Me'] * 3 + ['Comp1'] * 3 + ['Comp2'] * 3
        riders = rdf.NAVN.tolist()
        team_dict = {}
        for i, team in enumerate(team_assignments):
            if team not in team_dict:
                team_dict[team] = []
            team_dict[team].append(riders[i])

        # Initialize riders dictionary
        riders_dict = {}
        for i, rider in enumerate(riders):
            riders_dict[rider] = {
                'position': 0,
                'fatigue': 0,
                'sprint_stat': rdf.iloc[i]['SPRINT'],
                'flat_stat': rdf.iloc[i]['FLAD'],
                'mountain_3': rdf.iloc[i]['BJERG 3'],
                'mountain_stat': rdf.iloc[i]['BJERG'],
                'favorit': 0,  # Will set this later based on calculations
                'group': 2,
                'cards': [],
                'discarded': [],
                'chosen_value': 0,
                'attacking_status': 'no',
                'moved_fields': 0,
                'team': team_assignments[i],
                'sprint_points': 0,
                'ranking': 0,
                'takes_lead': 1,
                'noECs': 0,
                'prel_time': 1000000,
                'has_moved' : 0,
                'teammates': [r for r in team_dict[team_assignments[i]] if r != rider]
                # List of other riders on the same team

            }



            # Randomly set the position for one rider
            if i == random.randint(0, 8):
                riders_dict[rider]['position'] = 5
                riders_dict[rider]['group'] = 1

            # Initialize cards (you can customize this further)
            for j in range(15):
                if i == random.randint(0, 8):  # Change this logic as needed
                    if j in [5, 10]:
                        riders_dict[rider]['cards'].append(['kort: 16', 2, 2, 16])
                    else:
                        riders_dict[rider]['cards'].append(
                            ['kort: ' + str(j + 1), int(rdf.iloc[i, 17 + j]), int(rdf.iloc[i, 32 + j]), j+1]
                        )
                else:
                    riders_dict[rider]['cards'].append(['kort: ' + str(j + 1), int(rdf.iloc[i, 17 + j]), int(rdf.iloc[i, 32 + j]), j+1])

            random.shuffle(riders_dict[rider]['cards'])

        # Calculate favorite points and rankings
        track21 = min(self.get_value(track), 7) / max(self.get_value(track), 7)
        rdf['fav_points'] = (
            (rdf['BJERG'] - 60) * self.get_value(track) +
            rdf['SPRINT'] * 10 +
            (rdf['BJERG 3'] - 21) * 2 * self.get_value(track[-15:]) +
            (rdf['BJERG 3'] - 21) * 3 * track21 +
            (rdf['FLAD'] - 60) * (200 / (self.get_value(track[-17:]) + 1))
        )
        rdf = rdf.sort_values(by='fav_points', ascending=True)
        rdf['favorit'] = range(1, 10)  # Assign favorite rankings

        # Assign the favorite ranking to each rider
        for i, rider in enumerate(riders):
            riders_dict[rider]['favorit'] = rdf.iloc[i]['favorit']
        for rider in riders_dict:
            print(rider)
        return riders_dict

    def reset(self, seed=None, **kwargs):
        # Reset the game state to the initial state
        self.groups = [2,1]
        self.track, self.length = self.generate_terrain()
        self.riders = self.initialize_riders(pd.read_csv('FRData -FRData.csv'), self.track)
        self.global_ranking = 0

        # Additional reset logic, such as setting positions, fatigue, cards, etc.
         # Get the initial observations for each rider
        observations = []
        for rider in self.riders:
            observations = self.get_observations(rider)  # Assuming you have this method

        #observations = np.array(observations)
        # Return the initial observations (and optionally an info dictionary)
        return observations, {}

    def step(self, actions):
        print(f"Actions: {actions}")
        self.global_ranking = 0
        done = False  # Initialize done status
        actions = np.reshape(actions, (-1, 2))  # Each rider has [discrete_action, continuous_action]

        print(f"Actions after reshaping: {actions}")

        # Step 1: Loop over all groups
        for group in self.groups:
            riders_in_group = self.get_riders_in_group(group)
            attacking_riders = []
            group_actions = {}

            # Step 2: Collect actions for all riders in the group
            for rider_index, rider in enumerate(riders_in_group):
                observations = self.get_observations(rider)

                # Extract action components from MultiDiscrete action space
                discrete_action = actions[rider_index][0]  # Discrete action (0: Attack, 1: Pull, 2: Draft)
                continuous_action = actions[rider_index][1]  # Continuous action (Effort level from 0 to 9)
                print(f"Rider {rider_index} discrete action: {discrete_action}, continuous action: {continuous_action}")

                # Handle discrete action
                if discrete_action == 0:  # Attack
                    group_actions[rider] = 'attack'
                    self.riders[rider]['chosen_value'] = continuous_action  # Set to continuous effort value
                    attacking_riders.append(rider)
                elif discrete_action == 1:  # Pull
                    group_actions[rider] = continuous_action  # Use the investment value for pulling effort
                    self.riders[rider]['chosen_value'] = continuous_action
                elif discrete_action == 2:  # Draft
                    group_actions[rider] = 0  # Drafting may have no immediate effort
                    self.riders[rider]['chosen_value'] = 0

            # Step 3: Handle attacking riders
            if attacking_riders:
                # Reassign non-attacking riders to the next group
                for rider in riders_in_group:
                    if rider not in attacking_riders:
                        self.riders[rider]['group'] += 1  # Move non-attacking riders to the next group

                # Move all riders in groups behind to the next group
                for grp in range(group + 1, max(self.groups) + 1):
                    riders_behind = self.get_riders_in_group(grp)
                    for rider in riders_behind:
                        self.riders[rider]['group'] += 1

                # Calculate speed for the new group (group + 1)
                remaining_riders = self.get_riders_in_group(group + 1)
                speed, sv, gruppefart1, pull_value, riders_pulling = self.calculate_speed(group + 1, self.track)

                # Move remaining non-attacking riders in the new group
                for rider in remaining_riders:
                    chosen_action = group_actions.get(rider, 0)  # Default to 0 if not attacking
                    self.move_riders(
                        rider,
                        sv,
                        self.riders[rider],
                        gruppefart1,
                        speed,
                        group_actions,
                        False,
                        chosen_action,
                        self.track,
                        pull_value,
                        riders_pulling
                    )

                # Move attacking riders, apply attack penalties, and add an extra field
                for rider in attacking_riders:
                    self.riders[rider]['position'] += 1  # Gain one extra field for attacking
                    chosen_action = group_actions[rider]
                    self.move_riders(
                        rider,
                        sv,
                        self.riders[rider],
                        gruppefart1,
                        speed,
                        group_actions,
                        False,
                        chosen_action,
                        self.track,
                        pull_value,
                        riders_pulling
                    )
                    # Apply attack penalty
                    self.riders[rider]['cards'].insert(0, ['TK-1: 99', -1, -1])
                    self.riders[rider]['discarded'].append(['TK-1: 99', -1, -1])

            else:
                # Step 4: Handle non-attacking group (normal processing)
                speed, sv, gruppefart1, pull_value, riders_pulling = self.calculate_speed(group, self.track)

                # Move all riders in the group
                for rider, chosen_action in group_actions.items():
                    self.move_riders(
                        rider,
                        sv,
                        self.riders[rider],
                        gruppefart1,
                        speed,
                        group_actions,
                        False,
                        chosen_action,
                        self.track,
                        pull_value,
                        riders_pulling
                    )

        # Step 5: Update groups and check for sprint groups
        self.groups, sprint_groups = self.update_groups_after_round()
        for rider in self.riders:
            self.riders[rider]['has_moved'] = 0  # Reset 'has_moved' status for all riders

        if sprint_groups:
            # Handle sprint groups and update global ranking
            self.riders, self.global_ranking = self.sprint(sprint_groups, self.riders, self.global_ranking, self.track)
            done = True
            print('DONNNNNEEEEEE!!!!')# Set done to True if there are sprint groups

        # Calculate reward for the current step
        reward = self.calculate_reward()

        # Check if the game is over (based on finish line or other conditions)
        #done = self.check_if_done()

        # Optionally return additional info for debugging
        info = {}

        # Return observations, reward, done flag, and additional info
        return observations, reward, done, info

    # New helper function to handle attacking riders and group reassignment
    def get_value(self, track):
        # st.write(track)
        print(track)
        tr = track[0:track.find('F') + 1]

        tr = tr.replace('_', '2')

        tr = list(tr)

        tr = tr[0:tr.index('F')]
        # st.write(tr)
        sum = 0
        for number in tr:
            # st.write(number)
            sum = int(number) + sum
        # st.write('success')
        return 100 * (2 - sum / len(tr)) ** 2


    def calculate_reward(self):
        total_scores = 0
        rider_scores = {}

        # Calculate scores for each rider
        for rider in self.riders:
            len_left = self.track.index('F') - self.riders[rider]['position']
            sprint_points = self.riders[rider]['sprint_points']
            fatigue = self.riders[rider]['fatigue']
            share_1 = self.calculate_share_1(self.track, len_left)

            # Calculate rider score based on the formula
            score = ((1 / len_left) ** 5) * ((sprint_points / (share_1 + 0.2)) ** 0.6) / (fatigue + 0.5)
            rider_scores[rider] = score
            total_scores += score

        # Calculate probability of winning for each rider
        for rider in self.riders:
            self.riders[rider]['winning_probability'] = rider_scores[rider] / total_scores

        # Final ranking-based reward
        ranking_rewards = {1: 1000, 2: 100, 3: 10}

        # Sort riders by their current ranking (assuming rankings are updated elsewhere)
        sorted_riders = sorted(self.riders.items(), key=lambda item: item[1]['ranking'])

        # Initialize team rewards based on rankings
        team_rewards = {team: 0 for team in self.teams}

        # Assign ranking rewards to the teams of the top 3 riders
        for rank, (rider, data) in enumerate(sorted_riders[:3], start=1):
            team = data['team']
            if rank in ranking_rewards:
                team_rewards[team] += ranking_rewards[rank]

        return team_rewards

    def get_slipstream_value(pos1, pos2, track):
        pos1 = int(pos1)
        pos2 = int(pos2)
        if '0' in track[pos1:pos2 + 1]:
            return 0
        if '1' in track[pos1:pos2 + 1]:
            return 1
        else:
            return 2

    def handle_attacking_riders(self, group, attacking_riders):
        """
        This function handles the reassignment of group numbers when riders attack.
        """
        # Step 1: Reassign group numbers for non-attacking riders and groups behind the current group
        for rider, data in self.riders.items():
            if data['group'] >= group:  # Reassign only riders in the current and following groups
                self.riders[rider]['group'] += 1  # Push them back by one group

        # Step 2: Move the attacking riders to a new front group (X -> X+1)
        for rider in attacking_riders:
            self.riders[rider]['group'] = group  # Attacking riders stay in the same group (X)
            self.riders[rider]['position'] += 1
            #self.apply_attack_penalty(rider)
            #self.riders[rider]['cards'] += 1
            self.riders[rider]['cards'].insert(0, ['TK-1: 99', -1, -1, -1])
            self.riders[rider]['discarded'].append(0, ['TK-1: 99', -1, -1, -1])


            #Apply penalty for attacking

        # After adjusting the groups, the remaining riders in the new group (X+1) redo their turn

    def calculate_share_1(track, len_left):
        track = track.replace('_', '2')
        track = track.replace('0', '3')
        track = track.replace('2', '0')
        track = track.replace('3', '2')
        # track.replace
        weight = 1
        score = 0
        pot_score = 0
        for i in range(1, len_left):
            score = weight * int(track[track.index('F') - i]) + score
            weight = weight * 0.7
            pot_score = weight * 2 + pot_score
        return score / pot_score

    def get_new_actions(self, riders):
        """
        This function collects new actions for a group of riders who have been moved to a new group.
        """
        new_actions = {}
        for rider in riders:
            # Collect new actions based on some logic (e.g., random or decision-making logic)
            new_actions[rider] = self.choose_action_for_rider(rider)

        return new_actions

    def update_groups_after_round(self):
        # Step 1: Get all rider positions
        rider_positions = {}
        sprint_groups = []
        for rider in self.riders:
            position = self.riders[rider]['position']
            if position not in rider_positions:
                rider_positions[position] = []
            rider_positions[position].append(rider)

        # Step 2: Sort positions in descending order (frontmost riders first)
        sorted_positions = sorted(rider_positions.keys(), reverse=True)

        # Step 3: Assign group numbers based on sorted positions
        groups = []
        new_group_number = 1
        for position in sorted_positions:
            # Check if this group has passed the finish line
            if self.track[position] == 'F':
                sprint_groups.append(new_group_number)  # Mark this group as having passed the finish line

            # Assign new group numbers to riders at this position
            for rider in rider_positions[position]:
                self.riders[rider]['group'] = new_group_number
                groups.append(new_group_number)
            new_group_number += 1

        groups = list(set(groups))
        groups.reverse()
        # Optionally return something for verification if needed
        return groups, sprint_groups

    def get_penalty(rider):
        penalty = 0
        cards = self.riders[rider]['cards'][:4]  # Get the first 4 cards for the rider

        for card in cards:
            # Check card conditions for penalty calculation
            if card[1] == -1:  # Condition for penalty of 1
                penalty += 1  # Increment penalty by 1

        return penalty

    def move_riders(ridername, sv, rider, gruppefart1, speed, groups_new_positions, chosen_card, chosen_value, track,
                    pull_value, riders_pulling):
        if sv == 2:
            sv = 3

        penalty = get_penalty(ridername)

        speed = groups_new_positions[0] - rider['position']  # Adjust to handle list of integers
        riders_starting_position = rider['position']
        speed2 = max(5, speed) if track[rider['position']] == '_' else speed

        rider['takes lead'] = 0
        managed = False

        if sv > 1:
            if chosen_value >= pull_value:
                rider['takes lead'] = 1
            else:
                rider['takes lead'] = 0
                chosen_value = 0

            if not chosen_card:
                chosen_card, managed = choose_card_to_play(rider['cards'][0:4], sv, penalty, speed, chosen_value)
                if track[rider['position']] == '_':
                    chosen_card[1] = max(chosen_card[1], 5)

            if chosen_card[1] + sv - penalty >= speed:
                managed = True
                rider['position'] += speed

        if sv <= 1:
            if chosen_value == pull_value:
                rider['takes lead'] = 1
                speed = chosen_value
            else:
                chosen_value = 0

            if not chosen_card:
                chosen_card, managed = choose_card_to_play(rider['cards'][0:4], sv, penalty, speed, chosen_value)
                if track[rider['position']] == '_':
                    chosen_card[2] = max(chosen_card[2], 5)

            if chosen_card[2] + sv - penalty >= speed:
                managed = True
                rider['position'] += speed

        if 'F' in track[riders_starting_position:rider['position']]:
            rider['position'] -= 1

        value = max(5 - penalty, chosen_card[2] - penalty + sv) if sv < 2 else chosen_card[1] - penalty + sv

        pot_position = min(rider['position'] + value, groups_new_positions[0])
        new_pot_position = pot_position - sv

        for group_position in groups_new_positions:
            if pot_position >= group_position:
                new_pot_position = max(group_position, new_pot_position)

        if new_pot_position > rider['position']:
            rider['position'] = new_pot_position

        for card in rider['cards'][0:4]:
            rider['discarded'].append(card)
            rider['cards'].remove(card)

        rider['fatigue'] = get_fatigue(rider)
        rider['has_moved'] = 1
        groups_new_positions.append(rider['position'])

        # Sort groups_new_positions in descending order and keep only unique values
        groups_new_positions = sorted(set(groups_new_positions), reverse=True)

        return rider, groups_new_positions

    def get_number_ecs(rider):
        ecs = 0
        for card in self.riders[rider]['cards']:
            if card[0] == 'kort: 16':
                ecs = ecs + 1
        for card in self.riders[rider]['discarded']:
            if card[0] == 'kort: 16':
                ecs = ecs + 1

        return ecs


    def get_fatigue(rider):
        # ecs = get_number_ecs(rider)
        ecs = 0
        for card in self.riders[rider]['cards']:
            if card[1] == -1:
                ecs = ecs + 1
        for card in self.riders[rider]['discarded']:
            if card[1] == -1:
                ecs = ecs + 1

        ecs = ecs * 1.5 + get_number_ecs(rider)

        return ecs / (len(self.riders[rider]['cards']) + len(self.riders[rider]['discarded']))

    def sprint(sprint_groups, cards, sprint_type, global_ranking):
        for sprint_group in sprint_groups:
            # Step 1: Shuffle each rider's deck and prepare available cards
            for rider in cards:
                if cards[rider]['group'] == sprint_group:
                    # Re-add discarded cards and shuffle the deck
                    for card in cards[rider]['discarded']:
                        cards[rider]['cards'].append(card)
                    cards[rider]['discarded'] = []
                    random.shuffle(cards[rider]['cards'])

                    # Select available cards for sprint
                    cards_available = []
                    tk_penalty = 0

                    for i in range(0, min(4, len(cards[rider]['cards']))):
                        cards_available.append(cards[rider]['cards'][i][sprint_type])

                    for i in range(4, min(8, len(cards[rider]['cards']))):
                        if cards[rider]['cards'][i][0] == 'kort: 16':
                            tk_penalty += 1

                    # Ensure there are at least 4 cards to choose from
                    while len(cards_available) < 4:
                        cards_available.append(2)

                    # Sort cards in descending order (strongest first)
                    cards_available.sort(reverse=True)

                    # Calculate sprint points for the rider
                    cards[rider]['sprint_points'] = (
                            cards[rider]['sprint'] * 1.05
                            + cards_available[0]
                            + cards_available[1]
                            + cards_available[2] * 0.01
                            + cards_available[1] * 0.001
                            - tk_penalty
                    )
                    cards[rider]['tk_penalty'] = tk_penalty

            # Step 2: Rank riders within the sprint group based on sprint points
            sorted_riders = sorted(cards.items(), key=lambda item: item[1]["sprint_points"], reverse=True)

            # Step 3: Update global ranking based on the sorted sprint group
            for rider, rider_data in sorted_riders:
                if rider_data['group'] == sprint_group:
                    global_ranking += 1
                    cards[rider]['ranking'] = global_ranking

        return cards, global_ranking

    def get_observations(self, rider):
        # Initialize the observation array
        observations = []

        for rider in self.riders:
            # 1. Cyclist Position
            position = self.riders[rider]['position']  # 1 value
            observations.append(position)

            # 2. Rider Attributes (7 attributes for now)
            fatigue = self.riders[rider]['fatigue']  # Fatigue
            sprint_stat = self.riders[rider]['sprint_stat']  # Sprinting ability
            favorit = self.riders[rider]['favorit']  # Favorite ranking
            group = self.riders[rider]['group']  # Group ID or similar identifier
            flat_stat = self.riders[rider]['flat_stat']  # Flat terrain skill
            mountain_stat = self.riders[rider]['mountain_stat']  # Mountain terrain skill
            mountain_3 = self.riders[rider]['mountain_3']  # Specific mountain skill or stat

            # Extend observations with rider attributes
            observations.extend([
                fatigue,
                sprint_stat,
                favorit,
                group,
                flat_stat,
                mountain_stat,
                mountain_3
            ])  # Total 7 values

            # 3. Teammates' Positions and Favorit numbers
        teammates_positions = []
        teammates_favorit = []
        teammates = self.riders[rider]['teammates']  # List of teammates' identifiers

        for teammate in teammates:
            teammates_positions.append(self.riders[teammate]['position'])  # Teammates' positions
            teammates_favorit.append(self.riders[teammate]['favorit'])  # Teammates' favorit numbers

        observations.extend(teammates_positions)  # 2 values (for 2 teammates)
        observations.extend(teammates_favorit)  # 2 values (favorit numbers for 2 teammates)

        # 4. Rider's and Teammates' Cards (First 4 cards, with 3 values each)
        for teammate in [rider] + teammates:  # Include the rider and their 2 teammates
            cards = self.riders[teammate]['cards'][:4]  # Get the first 4 cards
            for card in cards:
                # Append the three values from each card (value 1, value 2, value 3)
                observations.extend([card[1], card[2], card[3]])

        # 5. Track Terrain (70 values)
        terrain = [int(self.track[i]) for i in range(self.length)]  # Convert characters to integers

        # Adjust for variable track lengths (pad or truncate to 70 values)
        if len(terrain) < 70:
            terrain = [2] * (70 - len(terrain)) + terrain  # Pad with 2's at the beginning if the track is shorter
        else:
            terrain = terrain[:70]
        observations.extend(terrain)

        #print(f"Observation length: {len(observations)}")  # Useful for debugging

        return np.array(observations, dtype=np.float32)

    def calculate_speed(self, group, track):
        """
        Calculate the speed of a group based on their paces and the track layout.

        Args:
            group (list): The group of riders.
            track (list): The current track layout.

        Returns:
            float: The calculated speed.
        """


        paces = [self.riders[rider]['chosen_value'] for rider in group if
                 self.riders[rider]['chosen_value'] != 'attack']
        group_position = self.riders[group[0]]['position']  # All riders in the group have the same position

        # Step 1: Calculate the max pace
        speed = max(paces)
        speed = max([speed, 2])

        if track[group_position] == '_':
            speed = max(5, speed)

        gruppefart1 = speed
        sv = self.get_slipstream_value(group_position, group_position + speed, track)

        count = 0

        if sv > 1:

            for pace in paces:
                if pace > speed - 1.5:
                    count += 1

            if count > 1:
                # hvis fælger
                if track[speed + 1 + group_position] in ['2', 'F']:
                    speed = 1 + speed

            if speed > 6:
                sv = 3

            pull_value, riders_pulling = self.get_pull_value(paces, sv)

        return speed, sv, gruppefart1, pull_value, riders_pulling


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
                        return a[0], 1


            except:
                return _list[0], 1
        else:
            return heapq.nlargest(1, _list)[0], 1

    def render(self, mode='human'):
        """
        Optionally render the game state (for visualization).
        """
        pass  # You can leave this empty or add visualization logic

    def generate_terrain(self):
        pot_tracks = ['World Championship 2019 (Yorkshire)', 'Liege-Bastogne-Liege', 'Hautacam',
                      'Giro DellEmilia', 'GP Industria', 'UAE Tour', 'Kassel-Winterberg', 'Askersund-Ludvika']

        trackname = pot_tracks[random.randint(0, len(pot_tracks) - 1)]  # Corrected index range
        print(trackname)
        if trackname == 'Liege-Bastogne-Liege':
            track = '2211111___222222222111222222222200000_2222222222222211122222222222222FFFFFFFFF'
        elif trackname == 'World Championship 2019 (Yorkshire)':
            track = '22222222222211222222222222221122222222222222112222222222222211222222FFFFFFFFF'
        elif trackname == 'Hautacam':
            track = '222111111111111111_______222221111111111111000000111111111111FFFFFFFFF'
        elif trackname == 'Giro DellEmilia':
            track = '___1111111_11___1111111_11___1111111_11___1111111_11___1111111FFFFFFFFFF'
        elif trackname == 'sprinttest':
            track = '111111FFFFFFFFFF'
        elif trackname == 'GP Industria':
            track = '2222222222222111111__222222222222222222222222111111__22222222222FFFFFFFFFFFFF'
        elif trackname == 'Kassel-Winterberg':
            track = '222222222222222222222222222222221111111122222222222222__1111111222FFFFFFFFFFFFF'
        elif trackname == 'Askersund-Ludvika':
            track = '22222222222222222222222222222222222222222222222222221111__22222FFFFFFFFFF'
        elif trackname == 'UAE Tour':
            track = '2222222222222222222222222222222222222222111111111111111111111FFFFFFFFFF'

        # Replace underscores with terrain type '4'
        track = track.replace('_', '4')

        # Calculate the length (before the first 'F')
        length = track.index('F')  # Position of the first 'F'

        return track, length

    def get_riders_in_group(self, group):
        """
        Get all riders currently assigned to a given group.

        Args:
            group (int): The group number to filter riders by.

        Returns:
            List: A list of riders in the specified group.
        """
        riders_in_group = []

        # Loop through all riders in self.riders and check their group assignment
        for rider, rider_data in self.riders.items():
            if rider_data['group'] == group:
                riders_in_group.append(rider)

        return riders_in_group

class Track:
    def __init__(self):
        self.terrain, self.length = self.generate_terrain()

    def generate_terrain(self):
        pot_tracks = ['World Championship 2019 (Yorkshire)', 'Liege-Bastogne-Liege', 'Hautacam',
                      'Giro DellEmilia', 'GP Industria', 'UAE Tour', 'Kassel-Winterberg', 'Askersund-Ludvika']

        trackname = pot_tracks[random.randint(0, len(pot_tracks) - 1)]  # Corrected index range

        if trackname == 'Liege-Bastogne-Liege':
            track = '2211111___222222222111222222222200000_2222222222222211122222222222222FFFFFFFFF'
        elif trackname == 'World Championship 2019 (Yorkshire)':
            track = '22222222222211222222222222221122222222222222112222222222222211222222FFFFFFFFF'
        elif trackname == 'Hautacam':
            track = '222111111111111111_______222221111111111111000000111111111111FFFFFFFFF'
        elif trackname == 'Giro DellEmilia':
            track = '___1111111_11___1111111_11___1111111_11___1111111_11___1111111FFFFFFFFFF'
        elif trackname == 'sprinttest':
            track = '111111FFFFFFFFFF'
        elif trackname == 'GP Industria':
            track = '2222222222222111111__222222222222222222222222111111__22222222222FFFFFFFFFFFFF'
        elif trackname == 'Kassel-Winterberg':
            track = '222222222222222222222222222222221111111122222222222222__1111111222FFFFFFFFFFFFF'
        elif trackname == 'Askersund-Ludvika':
            track = '22222222222222222222222222222222222222222222222222221111__22222FFFFFFFFFF'
        elif trackname == 'UAE Tour':
            track = '2222222222222222222222222222222222222222111111111111111111111FFFFFFFFFF'

        # Replace underscores with terrain type '4'
        track = track.replace('_', '4')

        # Calculate the length (before the first 'F')
        length = track.index('F')  # Position of the first 'F'

        return track

    def get_track(self):
        return self.terrain

    def get_length(self):
        return self.length









# Instantiate the environment
env = GameEnv(pd.read_csv('FRData -FRData.csv'))  # Initialize your environment

# Instantiate the PPO agent with MLP policy
model = PPO('MlpPolicy', env, verbose=1)

# Train the agent
model.learn(total_timesteps=100000)