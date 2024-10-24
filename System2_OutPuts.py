"""
Simulation of A car insurance expert center is working every day from 8 am to 6 pm. The door of the center is closed at 6:00 pm and only the cars that are in the center until that moment are served until the system is empty.
After the end of the working hours of the center every day, if there is a queue outside the premises, it will also disappear. In order to check and carry out the necessary measures, both vehicles must be present at the same time.
The distribution of visitors' arrival is a function of snowfall and rain and the time period of arrival.After entering the insurance center, if the cars are entered in pairs, if there is capacity (40), they will immediately enter the queue for the photo taking area, which has 2 attendants. Otherwise, the cars must wait outside the insurance area until the queue capacity is empty.
If a single car has entered the queue outside the area and remains in the same queue until the arrival of the second car, the second car will be added to the queue outside the area right behind the first car.
But if the clients have the possibility to enter the queue of the photo taking area inside the area, according to the insurance law, they will first be taken to the waiting parking area. After the arrival of the second car, to enter the photo queue inside the area, these cars have priority over the cars outside the photo area.
In this section, the cars that complete the case have priority over the cases that are filed. For this purpose, after the expert stage, the cars enter the complaint registration department, where an expert is working. After registering the complaint, the cars must go through the expert stages again and then complete the file. Finally, with the completion of the case, the cars will leave the insurance center.

Authors:Sana Mansoori,Fatemeh karimi
Date:7/5/2023
"""

import random
import math
import statistics
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl
random.seed(7)


def starting_state():
    # state variables
    state = dict()
    state['Aksbardari Queue Length'] = 0
    state['Tashkil Parvandeh Queue Length'] = 0
    state['Takmil Parvandeh Queue Length'] = 0
    state['Karshenasi Queue Length'] = 0
    state['Kharej Mohavateh Queue Length'] = 0
    state['Aksbardari Server Status'] = 0  # 0:all idle,    1:one busy server,  2:two busy server
    state['Parvandeh Server Status'] = 0  # 0:all idle,    1:one busy server,  2:two busy server   ,    3:three busy server      ,    4:four busy server
    state['Karshenasi Server Status'] = 0  # 0:all idle,    1:one busy server,  2:two busy server   ,    3:three busy server

    # Data: will save everything
    data = dict()
    data['files'] = dict()  # To track each file, saving their arrival time, time service begins, etc.
    data['Last Time Aksbardari Queue Length Changed'] = 0  # Needed to calculate area under queue length curve
    data['Last Time Tashkil Parvandeh Queue Length Changed'] = 0
    data['Last Time Takmil Parvandeh Queue Length Changed'] = 0
    data['Last Time Karshenasi Queue Length Changed'] = 0
    data['Last Time Kharej Mohavateh Queue Length Changed'] = 0

    data['Last Time Aksbardari departure happened'] = 0  # Needed to calculate area under queue length curve
    data['Last Time Tashkil Parvandeh departure happened'] = 0
    data['Last Time Takmil Parvandeh departure happened'] = 0
    data['Last Time Karshenasi-Takmil Parvandeh departure happened'] = 0
    data['Last Time Karshenasi-Takmil Parvandeh departure happened'] = 0

    data['Aksbardari Queue files'] = dict()
    data['Tashkil Parvandeh Queue files'] = dict()
    data['Takmil Parvandeh Queue files'] = dict()
    data['Karshenasi Queue files'] = dict()
    data['Kharej Mohavateh Queue files'] = dict()

    # Cumulative Stats
    data['Cumulative Stats'] = dict()

    data['Cumulative Stats']['Aksbardari Server Busy Time'] = 0
    data['Cumulative Stats']['Parvandeh Server Busy Time'] = 0
    data['Cumulative Stats']['Karshenasi Server Busy Time'] = 0

    data['Cumulative Stats']['Aksbardari Queue Waiting Time'] = 0
    data['Cumulative Stats']['Tashkil Parvandeh Queue Waiting Time'] = 0
    data['Cumulative Stats']['Takmil Parvandeh Queue Waiting Time'] = 0
    data['Cumulative Stats']['Karshenasi Queue Waiting Time'] = 0
    data['Cumulative Stats']['Kharej Mohavateh Queue Waiting Time'] = 0

    data['Cumulative Stats']['Area Under Aksbardari Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Takmil Parvandeh Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Karshenasi Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Kharej Mohavateh Queue Length Curve'] = 0

    data['Cumulative Stats']['Aksbardari Service Starters'] = 0
    data['Cumulative Stats']['Tashkil Parvandeh Service Starters'] = 0
    data['Cumulative Stats']['Takmil Parvandeh Service Starters'] = 0
    data['Cumulative Stats']['Karshenasi Service Starters'] = 0

    # starting FEL
    future_event_list = list()
    future_event_list.append({'Event Type': 'arrival', 'Event Time': 0, 'File': 'C1,1,o'})  # This is an event notice
    return state, future_event_list, data


def exponential(lambd):
    r = random.random()
    return -(1 / lambd) * math.log(r)


def triangular(a, c, b):
    r = random.random()
    if 0 < r < (c - a) / (b - a):
        return a + math.sqrt((b - a) * (c - a) * r)
    else:
        return b - math.sqrt((b - a) * (b - c) * (1 - r))


def fel_maker(future_event_list, event_type, clock, state, file=None):
    # Gets an Event Type
    # Generates activity time for that particular Event Type
    # Creates an event (or more precisely an event notice)
    # Appends the event to FEL

    event_time = 0

    if event_type == 'arrival':
        event_time = clock + exponential(1 / 3.2)
    elif event_type == 'arrival of dakhel mohavateh':
        if state['Kharej Mohavateh Queue Length'] > 0:
            event_time = clock
        else:
            event_time = clock
    elif event_type == 'departure of aksbardari':
        event_time = clock + exponential(1 / 6)
    elif event_type == 'arrival of tashkil parvandeh':
        event_time = clock
    elif event_type == 'departure of tashkil parvandeh':
        event_time = clock + triangular(6, 8, 10)
    elif event_type == 'arrival of karshenasi from tashkil parvandeh':
        event_time = clock
    elif event_type == 'departure of karshenasi':
        event_time = clock + exponential(1 / 8)
    elif event_type == 'arrival of takmil parvandeh':
        event_time = clock
    elif event_type == 'departure of takmil parvandeh':
        event_time = clock + triangular(3, 3.5, 4)

    new_event = {'Event Type': event_type, 'Event Time': event_time, 'File': file}
    future_event_list.append(new_event)

# tarif flowcharts

def arrival(future_event_list, state, clock, data, file):
    data["files"][file] = dict()
    data['files'][file]['Arrival Time'] = clock
    data['files'][file]['File Name'] = file
    if state['Kharej Mohavateh Queue Length'] > 0:
        data['Cumulative Stats']['Area Under Kharej Mohavateh Queue Length Curve'] += \
            state['Kharej Mohavateh Queue Length'] * (
                    clock - data['Last Time Kharej Mohavateh Queue Length Changed'])
        state['Kharej Mohavateh Queue Length'] += 1
        # print(file,state['Kharej Mohavateh Queue Length'])
        data['Kharej Mohavateh Queue files'][file] = clock  # add this file to the queue
        data['Last Time Kharej Mohavateh Queue Length Changed'] = clock
    else:
        if state['Aksbardari Queue Length'] > 0:
            if state['Aksbardari Queue Length'] == 20:
                data['Cumulative Stats']['Area Under Kharej Mohavateh Queue Length Curve'] += \
                    state['Kharej Mohavateh Queue Length'] * (
                            clock - data['Last Time Kharej Mohavateh Queue Length Changed'])
                state['Kharej Mohavateh Queue Length'] += 1
                # print(data.keys())
                data['Kharej Mohavateh Queue files'][file] = clock  # add this file to the queue
                data['Last Time Kharej Mohavateh Queue Length Changed'] = clock
            else:
                fel_maker(future_event_list, "arrival of dakhel mohavateh", clock, state, file)
        else:
            fel_maker(future_event_list, "arrival of dakhel mohavateh", clock, state, file)

    next_file = "C" + str(int(file[1:len(file) - 4]) + 1) + str(file[len(file) - 4:])
    fel_maker(future_event_list, "arrival", clock, state, next_file)


def arrival_of_dakhel_mohavateh(future_event_list, state, clock, data, file):
    # print(state)
    # print(file)
    # print(state['Aksbardari Queue Length'])
    # print(state['Kharej Mohavateh Queue Length'])
    data['files'][file]['arrival of dakhel mohavateh Time'] = clock
    data['files'][file]['File Name'] = file
    if state['Kharej Mohavateh Queue Length'] > 0:
        # data['files'].pop(file, None)

        data['Cumulative Stats']['Area Under Aksbardari Queue Length Curve'] += \
            state['Aksbardari Queue Length'] * (
                    clock - data['Last Time Aksbardari Queue Length Changed'])
        state['Aksbardari Queue Length'] += 1
        data['Aksbardari Queue files'][file] = clock  # add this file to the queue
        data['Last Time Aksbardari Queue Length Changed'] = clock
        # fel_maker(future_event_list, "departure of aksbardari", clock, state, first_file_in_aksbardari_queue)

    else:
        if state['Aksbardari Server Status'] > 1:
            data['Cumulative Stats']['Area Under Aksbardari Queue Length Curve'] += \
                state['Aksbardari Queue Length'] * (
                        clock - data['Last Time Aksbardari Queue Length Changed'])
            state['Aksbardari Queue Length'] += 1
            data['Aksbardari Queue files'][file] = clock  # add this file to the queue
            data['Last Time Aksbardari Queue Length Changed'] = clock
        else:
            state['Aksbardari Server Status'] += 1
            fel_maker(future_event_list, 'departure of aksbardari', clock, state, file)
            data['files'][file]['Aksbardari Time Service Begins'] = clock  # track "every move" of this file
            data['Cumulative Stats']['Aksbardari Service Starters'] += 1


def departure_of_aksbardari(future_event_list, state, clock, data, file):
    data['Cumulative Stats']['Aksbardari Server Busy Time'] += clock - data['files'][file][
        'Aksbardari Time Service Begins']
    # data['files'].pop(file, None)
    if state["Aksbardari Queue Length"] == 0:
        state["Aksbardari Server Status"] -= 1

    else:
        first_file_in_aksbardari_queue = min(data['Aksbardari Queue files'], key=data['Aksbardari Queue files'].get)

        data['files'][first_file_in_aksbardari_queue]['Aksbardari Time Service Begins'] = clock
        data['Cumulative Stats']['Aksbardari Queue Waiting Time'] += \
            clock - data['files'][first_file_in_aksbardari_queue]['arrival of dakhel mohavateh Time']
        data['Cumulative Stats']['Area Under Aksbardari Queue Length Curve'] += \
            state['Aksbardari Queue Length'] * (clock - data['Last Time Aksbardari Queue Length Changed'])
        state["Aksbardari Queue Length"] -= 1
        data['Cumulative Stats']['Aksbardari Service Starters'] += 1
        data['Aksbardari Queue files'].pop(first_file_in_aksbardari_queue, None)
        data['Last Time Aksbardari Queue Length Changed'] = clock
        data['Last Time Aksbardari departure happened'] = clock
        if state['Kharej Mohavateh Queue Length'] > 0:

            first_file_in_kharej_mohavateh_queue = min(data['Kharej Mohavateh Queue files'],
                                                       key=data['Kharej Mohavateh Queue files'].get)
            data['Cumulative Stats']['Kharej Mohavateh Queue Waiting Time'] += \
                clock - data['files'][first_file_in_kharej_mohavateh_queue ]['Arrival Time']

            state['Kharej Mohavateh Queue Length'] -= 1
            data['Kharej Mohavateh Queue files'].pop(first_file_in_kharej_mohavateh_queue, None)

            fel_maker(future_event_list, "arrival of dakhel mohavateh", clock, state,
                      first_file_in_kharej_mohavateh_queue)


            fel_maker(future_event_list, "departure of aksbardari", clock, state, first_file_in_aksbardari_queue)

        else:
            fel_maker(future_event_list, "departure of aksbardari", clock, state, first_file_in_aksbardari_queue)

    fel_maker(future_event_list, "arrival of tashkil parvandeh", clock, state, file)


def arrival_of_tashkil_parvandeh(future_event_list, state, clock, data, file):
    data['files'][file]['arrival of tashkil parvandeh Time'] = clock  # track every move of this file
    if state['Tashkil Parvandeh Queue Length'] == 0:
        if state['Parvandeh Server Status'] > 3:
            data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] += \
                state['Tashkil Parvandeh Queue Length'] * (
                        clock - data['Last Time Tashkil Parvandeh Queue Length Changed'])
            state['Tashkil Parvandeh Queue Length'] += 1
            data['Tashkil Parvandeh Queue files'][file] = clock  # add this file to the queue
            data['Last Time Tashkil Parvandeh Queue Length Changed'] = clock
            # first_file_in_tashkil_parvandeh_queue = min(data['Tashkil Parvandeh Queue files'],
            #                                             key=data['Tashkil Parvandeh Queue files'].get)
            # fel_maker(future_event_list, 'departure of tashkil parvandeh', clock, first_file_in_tashkil_parvandeh_queue)

        else:
            state['Parvandeh Server Status'] += 1
            fel_maker(future_event_list, 'departure of tashkil parvandeh', clock, state, file)
            data['files'][file]['Tashkil Parvandeh Time Service Begins'] = clock  # track "every move" of this file
            data['Cumulative Stats']['Tashkil Parvandeh Service Starters'] += 1
    else:
        data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] += \
            state['Tashkil Parvandeh Queue Length'] * (
                    clock - data['Last Time Tashkil Parvandeh Queue Length Changed'])
        state['Tashkil Parvandeh Queue Length'] += 1
        # first_file_in_tashkil_parvandeh_queue = min(data['Tashkil Parvandeh Queue files'],
        #                                             key=data['Tashkil Parvandeh Queue files'].get)

        # fel_maker(future_event_list, 'departure of tashkil parvandeh', clock, first_file_in_tashkil_parvandeh_queue)
        data['Tashkil Parvandeh Queue files'][file] = clock  # add this file to the queue
        data['Last Time Tashkil Parvandeh Queue Length Changed'] = clock


def departure_of_tashkil_parvandeh(future_event_list, state, clock, data, file):
    data['Cumulative Stats']['Parvandeh Server Busy Time'] += clock - data['files'][file][
        'Tashkil Parvandeh Time Service Begins']
    # data['files'].pop(file, None)

    if state["Takmil Parvandeh Queue Length"] == 0:
        if state["Tashkil Parvandeh Queue Length"] == 0:
            state['Parvandeh Server Status'] -= 1
        else:
            first_file_in_tashkil_parvandeh_queue = min(data['Tashkil Parvandeh Queue files'],
                                                        key=data['Tashkil Parvandeh Queue files'].get)
            data['files'][first_file_in_tashkil_parvandeh_queue]['Tashkil Parvandeh Time Service Begins'] = clock
            data['Cumulative Stats']['Tashkil Parvandeh Queue Waiting Time'] += \
                clock - data['files'][first_file_in_tashkil_parvandeh_queue]['arrival of tashkil parvandeh Time']
            data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] += \
                state['Tashkil Parvandeh Queue Length'] * (
                        clock - data['Last Time Tashkil Parvandeh Queue Length Changed'])
            state["Tashkil Parvandeh Queue Length"] -= 1
            data['Cumulative Stats']['Tashkil Parvandeh Service Starters'] += 1

            data['Tashkil Parvandeh Queue files'].pop(first_file_in_tashkil_parvandeh_queue, None)
            data['Last Time Tashkil Parvandeh Queue Length Changed'] = clock
            data['Last Time Tashkil Parvandeh departure happened'] = clock

            fel_maker(future_event_list, "departure of tashkil parvandeh", clock, state,
                      first_file_in_tashkil_parvandeh_queue)
    else:
        first_file_in_takmil_parvandeh_queue = min(data['Takmil Parvandeh Queue files'],
                                                   key=data['Takmil Parvandeh Queue files'].get)
        data['files'][first_file_in_takmil_parvandeh_queue]['Takmil Parvandeh Time Service Begins'] = clock
        data['Cumulative Stats']['Takmil Parvandeh Queue Waiting Time'] += \
            clock - data['files'][first_file_in_takmil_parvandeh_queue]['arrival of takmil parvandeh Time']
        data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] += \
            state['Takmil Parvandeh Queue Length'] * (
                    clock - data['Last Time Takmil Parvandeh Queue Length Changed'])
        state["Takmil Parvandeh Queue Length"] -= 1
        data['Cumulative Stats']['Takmil Parvandeh Service Starters'] += 1
        data['Takmil Parvandeh Queue files'].pop(first_file_in_takmil_parvandeh_queue, None)
        data['Last Time Takmil Parvandeh Queue Length Changed'] = clock
        data['Last Time Takmil Parvandeh departure happened'] = clock
        fel_maker(future_event_list, "departure of takmil parvandeh", clock, state,
                  first_file_in_takmil_parvandeh_queue)

    fel_maker(future_event_list, "arrival of karshenasi from tashkil parvandeh", clock, state, file)


def arrival_of_karshenasi_from_tashkil_parvandeh(future_event_list, state, clock, data, file):
    data['files'][file]['arrival of karshenasi Time'] = clock  # track every move of this file
    if state['Karshenasi Server Status'] > 2:
        data['Cumulative Stats']['Area Under Karshenasi Queue Length Curve'] += \
            state['Karshenasi Queue Length'] * (
                    clock - data['Last Time Karshenasi Queue Length Changed'])
        state['Karshenasi Queue Length'] += 1
        data['Karshenasi Queue files'][file] = clock  # add this file to the queue
        data['Last Time Karshenasi Queue Length Changed'] = clock
        # first_file_in_karshenasi_queue = min(data['Karshenasi Queue files'],
        #                                      key=data['Karshenasi Queue files'].get)
        # fel_maker(future_event_list, "departure of karshenasi", clock, first_file_in_karshenasi_queue)
    else:
        state['Karshenasi Server Status'] += 1
        fel_maker(future_event_list, 'departure of karshenasi', clock, state, file)
        data['files'][file]['Karshenasi Time Service Begins'] = clock  # track "every move" of this file
        data['Cumulative Stats']['Karshenasi Service Starters'] += 1


def departure_of_karshenasi(future_event_list, state, clock, data, file):
    data['Cumulative Stats']['Karshenasi Server Busy Time'] += clock - data['files'][file][
        'Karshenasi Time Service Begins']
    # data['files'].pop(file, None)

    if state['Karshenasi Queue Length'] == 0:
        state["Karshenasi Server Status"] -= 1

    else:
        data['Last Time Karshenasi-Takmil Parvandeh departure happened'] = clock
        first_file_in_karshenasi_queue = min(data['Karshenasi Queue files'], key=data['Karshenasi Queue files'].get)
        data['files'][first_file_in_karshenasi_queue]['Karshenasi Time Service Begins'] = clock
        data['Cumulative Stats']['Karshenasi Queue Waiting Time'] += \
            clock - data['files'][first_file_in_karshenasi_queue]['arrival of karshenasi Time']
        data['Cumulative Stats']['Area Under Karshenasi Queue Length Curve'] += \
            state['Karshenasi Queue Length'] * (clock - data['Last Time Karshenasi Queue Length Changed'])
        state['Karshenasi Queue Length'] -= 1
        data['Cumulative Stats']['Karshenasi Service Starters'] += 1
        data['Karshenasi Queue files'].pop(first_file_in_karshenasi_queue, None)
        data['Last Time Karshenasi Parvandeh Queue Length Changed'] = clock
        fel_maker(future_event_list, "departure of karshenasi", clock, state, first_file_in_karshenasi_queue)

        data['Last Time Karshenasi-Takmil Parvandeh departure happened'] = clock
    fel_maker(future_event_list, "arrival of takmil parvandeh", clock, state, file)


def arrival_of_takmil_parvandeh(future_event_list, state, clock, data, file):
    data['files'][file]['arrival of takmil parvandeh Time'] = clock

    if state["Parvandeh Server Status"] < 4:
        state["Parvandeh Server Status"] += 1
        fel_maker(future_event_list, "departure of takmil parvandeh", clock, state, file)
        data['files'][file]['Takmil Parvandeh Time Service Begins'] = clock  # track "every move" of this file
        data['Cumulative Stats']['Takmil Parvandeh Service Starters'] += 1
    else:
        data['Cumulative Stats']['Area Under Takmil Parvandeh Queue Length Curve'] += \
            state['Takmil Parvandeh Queue Length'] * (
                    clock - data['Last Time Takmil Parvandeh Queue Length Changed'])
        state['Takmil Parvandeh Queue Length'] += 1
        data['Takmil Parvandeh Queue files'][file] = clock  # add this file to the queue
        data['Last Time Takmil Parvandeh Queue Length Changed'] = clock

        # first_file_in_takmil_parvandeh_queue = min(data['Takmil Parvandeh Queue files'],
        #                                            key=data['Takmil Parvandeh Queue files'].get)
        # fel_maker(future_event_list, "arrival of takmil parvandeh", clock, first_file_in_takmil_parvandeh_queue)


def departure_of_takmil_parvandeh(future_event_list, state, clock, data, file):
    data['Cumulative Stats']['Parvandeh Server Busy Time'] += clock - data['files'][file][
        'Takmil Parvandeh Time Service Begins']
    # data['files'].pop(file, None)

    if state['Takmil Parvandeh Queue Length'] == 0:
        if state['Tashkil Parvandeh Queue Length'] == 0:
            state["Parvandeh Server Status"] -= 1
        else:
            first_file_in_tashkil_parvandeh_queue = min(data['Tashkil Parvandeh Queue files'],
                                                        key=data['Tashkil Parvandeh Queue files'].get)
            data['files'][first_file_in_tashkil_parvandeh_queue]['Tashkil Parvandeh Time Service Begins'] = clock
            data['Cumulative Stats']['Tashkil Parvandeh Queue Waiting Time'] += \
                clock - data['files'][first_file_in_tashkil_parvandeh_queue]['arrival of tashkil parvandeh Time']
            data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] += \
                state['Tashkil Parvandeh Queue Length'] * (
                        clock - data['Last Time Tashkil Parvandeh Queue Length Changed'])
            state["Tashkil Parvandeh Queue Length"] -= 1
            data['Cumulative Stats']['Tashkil Parvandeh Service Starters'] += 1
            data['Tashkil Parvandeh Queue files'].pop(first_file_in_tashkil_parvandeh_queue, None)
            data['Last Time Tashkil Parvandeh Queue Length Changed'] = clock
            fel_maker(future_event_list, "departure of tashkil parvandeh", clock, state,
                      first_file_in_tashkil_parvandeh_queue)

    else:
        first_file_in_takmil_parvandeh_queue = min(data['Takmil Parvandeh Queue files'],
                                                   key=data['Takmil Parvandeh Queue files'].get)
        data['files'][first_file_in_takmil_parvandeh_queue]['Takmil Parvandeh Time Service Begins'] = clock
        data['Cumulative Stats']['Takmil Parvandeh Queue Waiting Time'] += \
            clock - data['files'][first_file_in_takmil_parvandeh_queue]['arrival of takmil parvandeh Time']
        data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] += \
            state['Takmil Parvandeh Queue Length'] * (
                    clock - data['Last Time Takmil Parvandeh Queue Length Changed'])
        state["Takmil Parvandeh Queue Length"] -= 1
        data['Cumulative Stats']['Takmil Parvandeh Service Starters'] += 1
        data['Takmil Parvandeh Queue files'].pop(first_file_in_takmil_parvandeh_queue, None)
        data['Last Time Takmil Parvandeh Queue Length Changed'] = clock
        data['Last Time Takmil Parvandeh departure happened'] = clock
        fel_maker(future_event_list, "departure of takmil parvandeh", clock, state,
                  first_file_in_takmil_parvandeh_queue)


# def print_header():
#     print('Event Type'.ljust(20) + '\t' + 'Time'.ljust(15) + '\t' +
#           'Queue Length'.ljust(15) + '\t' + 'Server Status'.ljust(25))
#     print('-------------------------------------------------------------------------------------------------')


# def nice_print(current_state, current_event):
# print(str(current_event['Event Type']).ljust(20) + '\t' + str(round(current_event['Event Time'], 3)).ljust(15) +
# '\t' + str(current_state['Queue Length']).ljust(15) + '\t' + str(current_state['Server Status']).ljust(25))

"""
def create_row(step, current_event, state, data, future_event_list):
    sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])
    row = [step, current_event['Event Time'], current_event['Event Type'], current_event['File']]

    row.extend(list(state.values()))

    row.extend(list(data['Cumulative Stats'].values()))

    for event in sorted_fel:
        row.append(event['Event Time'])
        row.append(event['Event Type'])
        row.append(event['File'])
    return row


def justify(table):
    row_max_len = 0
    for row in table:
        if len(row) > row_max_len:
            row_max_len = len(row)
    for row in table:
        row.extend([""] * (row_max_len - len(row)))


def create_main_header(state, data):
    header = ['Step', 'Clock', 'Event Type', 'Event File']
    header.extend(list(state.keys()))
    header.extend(list(data['Cumulative Stats'].keys()))
    return header


def create_excel(table, header):
    row_len = len(table[0])
    header_len = len(header)
    i = 1
    for col in range((row_len - header_len) // 3):
        header.append('Future Event Time ' + str(i))
        header.append('Future Event Type ' + str(i))
        header.append('Future Event File ' + str(i))
        i += 1

    df = pd.DataFrame(table, columns=header, index=None)

    writer = pd.ExcelWriter(r'D:\output.xlsx', engine='xlsxwriter')

    df.to_excel(writer, sheet_name='Multi-server Queue Output', header=False, startrow=1, index=False)

    workbook = writer.book

    worksheet = writer.sheets['Multi-server Queue Output']

    header_formatter = workbook.add_format()

    header_formatter.set_align('center')
    header_formatter.set_align('vcenter')
    header_formatter.set_font('Times New Roman')
    header_formatter.set_bold('True')

    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num, value, header_formatter)

    for i, width in enumerate(get_col_widths(df)):
        worksheet.set_column(i - 1, i - 1, width)

    main_formatter = workbook.add_format()
    main_formatter.set_align('center')
    main_formatter.set_align('vcenter')
    main_formatter.set_font('Times New Roman')

    for row in range(1, len(df) + 1):
        worksheet.set_row(row, None, main_formatter)

    writer.close()


def get_col_widths(dataframe):
    idx_max = max([len(str(s)) for s in dataframe.index.values] + [len(str(dataframe.index.name))])
    return [idx_max] + [max([len(str(s)) for s in dataframe[col].values] + [len(col)]) for col in dataframe.columns]

"""
def simulation(simulation_time):
    state, future_event_list, data = starting_state()
    clock = 0
    table = []  # a list of lists. Each inner list will be a row in the Excel output.
    step = 1  # every event counts as a step.
    future_event_list.append({'Event Type': 'End Of Simulation', 'Event Time': simulation_time, "File": None})
    while clock < simulation_time:
        sorted_fel = sorted(future_event_list, key=lambda x: x['Event Time'])
        # print(sorted_fel, "\n")
        current_event = sorted_fel[0]  # find imminent event
        clock = current_event["Event Time"]
        # advance time
        file = current_event['File']
        if clock < simulation_time:  # if current_event["Event Type"] != "End of Simulation"
            if current_event["Event Type"] == "arrival":
                arrival(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == "arrival of dakhel mohavateh":
                arrival_of_dakhel_mohavateh(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'departure of aksbardari':
                departure_of_aksbardari(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'arrival of tashkil parvandeh':
                arrival_of_tashkil_parvandeh(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'departure of tashkil parvandeh':
                departure_of_tashkil_parvandeh(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'arrival of karshenasi from tashkil parvandeh':
                arrival_of_karshenasi_from_tashkil_parvandeh(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'departure of karshenasi':
                departure_of_karshenasi(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'arrival of takmil parvandeh':
                arrival_of_takmil_parvandeh(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'departure of takmil parvandeh':
                departure_of_takmil_parvandeh(future_event_list, state, clock, data, file)
            future_event_list.remove(current_event)
        else:
            future_event_list.clear()
        # nice_print(state, current_event)
        # table.append(create_row(step, current_event, state, data, future_event_list))
        # step += 1

    # print('-------------------------------------------------------------------------------------------------')

    # excel_main_header = create_main_header(state, data)
    # justify(table)
    # create_excel(table, excel_main_header)

    W_Aksbardari_Queue = data['Cumulative Stats']['Aksbardari Queue Waiting Time'] / data['Cumulative Stats']['Aksbardari Service Starters']
    W_Tashkil_Parvandeh_Queue = data['Cumulative Stats']['Tashkil Parvandeh Queue Waiting Time'] / data['Cumulative Stats']['Tashkil Parvandeh Service Starters']
    W_Takmil_Parvandeh_Queue = data['Cumulative Stats']['Takmil Parvandeh Queue Waiting Time'] / data['Cumulative Stats']['Takmil Parvandeh Service Starters']


    # print("W_Aksbardari_Queue:", W_Aksbardari_Queue)
    # print("W_Tashkil_Parvandeh_Queue:", W_Tashkil_Parvandeh_Queue)
    # print("W_Takmil_Parvandeh_Queue:", W_Takmil_Parvandeh_Queue)


    L_Aksbardari_Queue = data['Cumulative Stats']['Area Under Aksbardari Queue Length Curve'] / simulation_time
    L_Tashkil_Parvandeh_Queue = data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] / simulation_time
    L_Takmil_Parvandeh_Queue = data['Cumulative Stats']['Area Under Takmil Parvandeh Queue Length Curve'] / simulation_time

    # print("L_Aksbardari_Queue:",L_Aksbardari_Queue)
    # print("L_Tashkil_Parvandeh_Queue:",L_Tashkil_Parvandeh_Queue)
    # print("L_Takmil_Parvandeh_Queue:",L_Takmil_Parvandeh_Queue)


    W_Aksbardari_Queue_List.append(W_Aksbardari_Queue)
    W_Tashkil_Parvandeh_Queue_List.append(W_Tashkil_Parvandeh_Queue)
    W_Takmil_Parvandeh_Queue_List.append(W_Takmil_Parvandeh_Queue)
    L_Aksbardari_Queue_List.append(L_Aksbardari_Queue)
    L_Tashkil_Parvandeh_Queue_List.append(L_Tashkil_Parvandeh_Queue)
    L_Takmil_Parvandeh_Queue_List.append(L_Takmil_Parvandeh_Queue)
    # print('Simulation Ended!\n')


W_Aksbardari_Queue_List = []
W_Tashkil_Parvandeh_Queue_List = []
W_Takmil_Parvandeh_Queue_List = []
L_Aksbardari_Queue_List = []
L_Tashkil_Parvandeh_Queue_List = []
L_Takmil_Parvandeh_Queue_List = []




# num_of_cold_area_frames = max(system2,system1)
num_of_cold_area_frames = max(70,75)
frame_length = 480

num_of_replications = 50
for replication in range(1, num_of_replications):
    simulation(num_of_cold_area_frames*11*frame_length)

for replication in range(num_of_replications, num_of_replications+1):
    simulation(num_of_cold_area_frames * 11 * frame_length)


    # print(W_Aksbardari_Queue_List)
    # print(W_Tashkil_Parvandeh_Queue_List)
    # print(W_Takmil_Parvandeh_Queue_List)
    # print(L_Aksbardari_Queue_List)
    # print(L_Tashkil_Parvandeh_Queue_List)
    # print(L_Takmil_Parvandeh_Queue_List)


    Y_2_W_Aksbardari = statistics.mean(W_Aksbardari_Queue_List)
    Y_2_W_Tashkil_Parvandeh = statistics.mean(W_Tashkil_Parvandeh_Queue_List)
    Y_2_W_Takmil_Parvandeh = statistics.mean(W_Takmil_Parvandeh_Queue_List)
    Y_2_L_Aksbardari = statistics.mean(L_Aksbardari_Queue_List)
    Y_2_L_Tashkil_Parvandeh = statistics.mean(L_Tashkil_Parvandeh_Queue_List)
    Y_2_L_Takmil_Parvandeh = statistics.mean(L_Takmil_Parvandeh_Queue_List)
    print("Average_W_2_Aksbardari_Queue_List : ", Y_2_W_Aksbardari)
    print("Average_W_2_Tashkil_Parvandeh_Queue_List : ", Y_2_W_Tashkil_Parvandeh)
    print("Average_W_2_Takmil_Parvandeh_Queue_List : ", Y_2_W_Takmil_Parvandeh)
    print("Average_L_2_Aksbardari_Queue_List : ", Y_2_L_Aksbardari)
    print("Average_L_2_Tashkil_Parvandeh_Queue_List : ", Y_2_L_Tashkil_Parvandeh)
    print("Average_L_2_Takmil_Parvandeh_Queue_List : ", Y_2_L_Takmil_Parvandeh)

    Var_2_W_Aksbardari = statistics.variance(W_Aksbardari_Queue_List)
    Var_2_W_Tashkil_Parvandeh = statistics.variance(W_Tashkil_Parvandeh_Queue_List)
    Var_2_W_Takmil_Parvandeh = statistics.variance(W_Takmil_Parvandeh_Queue_List)
    Var_2_L_Aksbardari = statistics.variance(L_Aksbardari_Queue_List)
    Var_2_L_Tashkil_Parvandeh = statistics.variance(L_Tashkil_Parvandeh_Queue_List)
    Var_2_L_Takmil_Parvandeh = statistics.variance(L_Takmil_Parvandeh_Queue_List)
    print("Variance_W_2_Aksbardari_Queue_List : ", Var_2_W_Aksbardari)
    print("Variance_W_2_Tashkil_Parvandeh_Queue_List : ", Var_2_W_Tashkil_Parvandeh)
    print("Variance_W_2_Takmil_Parvandeh_Queue_List : ", Var_2_W_Takmil_Parvandeh)
    print("Variance_L_2_Aksbardari_Queue_List : ", Var_2_L_Aksbardari)
    print("Variance_L_2_Tashkil_Parvandeh_Queue_List : ", Var_2_L_Tashkil_Parvandeh)
    print("Variance_L_2_Takmil_Parvandeh_Queue_List : ", Var_2_L_Takmil_Parvandeh)


