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
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import matplotlib as mpl


def starting_state():
    # state variables
    state = dict()
    state['Aksbardari Queue Length'] = 0
    state['Tashkil Parvandeh Queue Length'] = 0
    state['Takmil Parvandeh Queue Length'] = 0
    state['Karshenasi Queue Length'] = 0
    state['Shekayat Queue Length'] = 0
    state['Kharej Mohavateh Queue Length'] = 0
    state['Aksbardari Server Status'] = 0  # 0:all idle,    1:one busy server,  2:two busy server
    state[
        'Parvandeh Server Status'] = 0  # 0:all idle,    1:one busy server,  2:two busy server   ,    3:three busy server
    state['Karshenasi Server Status'] = 0  # 0:all idle,    1:one busy server,  2:two busy server
    state['Shekayat Server Status'] = 0  # 0:all idle,    1:one busy server

    # Data: will save everything
    data = dict()
    data['files'] = dict()  # To track each file, saving their arrival time, time service begins, etc.
    data['Last Time Aksbardari Queue Length Changed'] = 0  # Needed to calculate area under queue length curve
    data['Last Time Tashkil Parvandeh Queue Length Changed'] = 0
    data['Last Time Takmil Parvandeh Queue Length Changed'] = 0
    data['Last Time Karshenasi Queue Length Changed'] = 0
    data['Last Time Kharej Mohavateh Queue Length Changed'] = 0
    data['Last Time Shekayat Queue Length Changed'] = 0

    data['Last Time Aksbardari departure happened'] = 0  # Needed to calculate area under queue length curve
    data['Last Time Tashkil Parvandeh departure happened'] = 0
    data['Last Time Takmil Parvandeh departure happened'] = 0
    data['Last Time Karshenasi-Shekayat departure happened'] = 0
    data['Last Time Shekayat departure happened'] = 0
    data['Last Time Karshenasi-Takmil Parvandeh departure happened'] = 0

    data['Aksbardari Queue files'] = dict()
    data['Tashkil Parvandeh Queue files'] = dict()
    data['Takmil Parvandeh Queue files'] = dict()
    data['Karshenasi Queue files'] = dict()
    data['Kharej Mohavateh Queue files'] = dict()
    data['Shekayat Queue files'] = dict()

    # Cumulative Stats
    data['Cumulative Stats'] = dict()

    data['Cumulative Stats']['Aksbardari Server Busy Time'] = 0
    data['Cumulative Stats']['Parvandeh Server Busy Time'] = 0
    data['Cumulative Stats']['Karshenasi Server Busy Time'] = 0
    data['Cumulative Stats']['Shekayat Server Busy Time'] = 0

    data['Cumulative Stats']['Aksbardari Queue Waiting Time'] = 0
    data['Cumulative Stats']['Tashkil Parvandeh Queue Waiting Time'] = 0
    data['Cumulative Stats']['Takmil Parvandeh Queue Waiting Time'] = 0
    data['Cumulative Stats']['Karshenasi Queue Waiting Time'] = 0
    data['Cumulative Stats']['Kharej Mohavateh Queue Waiting Time'] = 0
    data['Cumulative Stats']['Shekayat Queue Waiting Time'] = 0

    data['Cumulative Stats']['Area Under Aksbardari Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Tashkil Parvandeh Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Takmil Parvandeh Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Karshenasi Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Kharej Mohavateh Queue Length Curve'] = 0
    data['Cumulative Stats']['Area Under Shekayat Queue Length Curve'] = 0

    data['Cumulative Stats']['Aksbardari Service Starters'] = 0
    data['Cumulative Stats']['Tashkil Parvandeh Service Starters'] = 0
    data['Cumulative Stats']['Takmil Parvandeh Service Starters'] = 0
    data['Cumulative Stats']['Karshenasi Service Starters'] = 0
    data['Cumulative Stats']['Shekayat Service Starters'] = 0

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
        event_time = clock + exponential(1 / 5)
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
        event_time = clock + triangular(5, 6, 7)
    elif event_type == 'arrival of karshenasi from tashkil parvandeh':
        event_time = clock
    elif event_type == 'arrival of karshenasi from shekayat':
        event_time = clock
    elif event_type == 'departure of karshenasi':
        event_time = clock + exponential(1 / 9)
    elif event_type == 'arrival of shekayat':
        event_time = clock
    elif event_type == 'departure of shekayat':
        event_time = clock + exponential(1 / 15)
    elif event_type == 'arrival of takmil parvandeh':
        event_time = clock
    elif event_type == 'departure of takmil parvandeh':
        event_time = clock + triangular(6, 8, 9)

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
        data['Kharej Mohavateh Queue files'][file] = clock  # add this file to the queue
        data['Last Time Kharej Mohavateh Queue Length Changed'] = clock
    else:
        if state['Aksbardari Queue Length'] > 0:
            if state['Aksbardari Queue Length'] == 20:
                data['Cumulative Stats']['Area Under Kharej Mohavateh Queue Length Curve'] += \
                    state['Kharej Mohavateh Queue Length'] * (
                            clock - data['Last Time Kharej Mohavateh Queue Length Changed'])
                state['Kharej Mohavateh Queue Length'] += 1
                data['Kharej Mohavateh Queue files'][file] = clock  # add this file to the queue
                data['Last Time Kharej Mohavateh Queue Length Changed'] = clock
            else:
                fel_maker(future_event_list, "arrival of dakhel mohavateh", clock, state, file)
        else:
            fel_maker(future_event_list, "arrival of dakhel mohavateh", clock, state, file)

    next_file = "C" + str(int(file[1:len(file) - 4]) + 1) + str(file[len(file) - 4:])
    fel_maker(future_event_list, "arrival", clock, state, next_file)


def arrival_of_dakhel_mohavateh(future_event_list, state, clock, data, file):
    # data["files"][file] = dict()
    data['files'][file]['arrival of dakhel mohavateh Time'] = clock
    data['files'][file]['File Name'] = file
    if state['Aksbardari Queue Length'] > 0:
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
                clock - data['files'][first_file_in_kharej_mohavateh_queue]['Arrival Time']

            state['Kharej Mohavateh Queue Length'] -= 1
            data['Kharej Mohavateh Queue files'].pop(first_file_in_kharej_mohavateh_queue, None)

            fel_maker(future_event_list, "arrival of dakhel mohavateh", clock, state,
                      first_file_in_kharej_mohavateh_queue)

            fel_maker(future_event_list, "departure of aksbardari", clock, state, first_file_in_aksbardari_queue)

        else:
            fel_maker(future_event_list, "departure of aksbardari", clock, state, first_file_in_aksbardari_queue)

    fel_maker(future_event_list, "arrival of tashkil parvandeh", clock, state, file)


def arrival_of_tashkil_parvandeh(future_event_list, state, clock, data, file):
    # data['files'][file] = dict()
    data['files'][file]['arrival of tashkil parvandeh Time'] = clock  # track every move of this file
    if state['Tashkil Parvandeh Queue Length'] == 0:
        if state['Parvandeh Server Status'] > 2:
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
        data['Tashkil Parvandeh Queue files'][file] = clock
        data['Last Time Tashkil Parvandeh Queue Length Changed'] = clock

    # print(data["files"]["C1,1,o"])


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


def arrival_of_karshenasi_from_shekayat(future_event_list, state, clock, data, file):
    # data['files'][file] = dict()
    data['files'][file]['arrival of karshenasi Time'] = clock

    if state['Karshenasi Server Status'] > 1:
        data['Cumulative Stats']['Area Under Karshenasi Queue Length Curve'] += \
            state['Karshenasi Queue Length'] * (
                    clock - data['Last Time Karshenasi Queue Length Changed'])
        state['Karshenasi Queue Length'] += 1
        data['Karshenasi Queue files'][file] = clock  # add this file to the queue
        data['Last Time Karshenasi Queue Length Changed'] = clock
    else:
        state['Karshenasi Server Status'] += 1
        fel_maker(future_event_list, 'departure of karshenasi', clock, state, file)
        data['files'][file]['Karshenasi Time Service Begins'] = clock  # track "every move" of this file
        data['Cumulative Stats']['Karshenasi Service Starters'] += 1


def arrival_of_karshenasi_from_tashkil_parvandeh(future_event_list, state, clock, data, file):
    # data['files'][file] = dict()
    data['files'][file]['arrival of karshenasi Time'] = clock  # track every move of this file
    if state['Karshenasi Server Status'] > 1:
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
    random_number1 = random.random()
    if random_number1 > 0.1:
        data['Last Time Karshenasi-Takmil Parvandeh departure happened'] = clock
        fel_maker(future_event_list, "arrival of takmil parvandeh", clock, state, file)
    else:
        data['Last Time Karshenasi-Shekayat departure happened'] = clock
        fel_maker(future_event_list, "arrival of shekayat", clock, state, file)

    data['Cumulative Stats']['Karshenasi Server Busy Time'] += clock - data['files'][file][
        'Karshenasi Time Service Begins']
    # data['files'].pop(file, None)

    if state['Karshenasi Queue Length'] == 0:
        state["Karshenasi Server Status"] -= 1

    else:
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


def arrival_of_shekayat(future_event_list, state, clock, data, file):
    # data['files'][file] = dict()
    data['files'][file]['arrival of shekayat Time'] = clock

    if state["Shekayat Server Status"] < 1:
        state["Shekayat Server Status"] += 1
        fel_maker(future_event_list, 'departure of shekayat', clock, state, file)
        data['files'][file]['Shekayat Time Service Begins'] = clock  # track "every move" of this file
        data['Cumulative Stats']['Shekayat Service Starters'] += 1

    else:
        data['Cumulative Stats']['Area Under Shekayat Queue Length Curve'] += \
            state['Shekayat Queue Length'] * (
                    clock - data['Last Time Shekayat Queue Length Changed'])
        state['Shekayat Queue Length'] += 1
        data['Shekayat Queue files'][file] = clock  # add this file to the queue
        data['Last Time Shekayat Queue Length Changed'] = clock


def departure_of_shekayat(future_event_list, state, clock, data, file):
    data['Cumulative Stats']['Shekayat Server Busy Time'] += clock - data['files'][file][
        'Shekayat Time Service Begins']
    # data['files'].pop(file, None)

    if state['Shekayat Queue Length'] == 0:
        state["Shekayat Server Status"] -= 1
    else:
        first_file_in_shekayat_queue = min(data['Shekayat Queue files'], key=data['Shekayat Queue files'].get)
        data['files'][first_file_in_shekayat_queue]['Shekayat Time Service Begins'] = clock
        data['Cumulative Stats']['Shekayat Queue Waiting Time'] += \
            clock - data['files'][first_file_in_shekayat_queue]['arrival of shekayat Time']
        data['Cumulative Stats']['Area Under Shekayat Queue Length Curve'] += \
            state['Shekayat Queue Length'] * (clock - data['Last Time Shekayat Queue Length Changed'])
        state['Shekayat Queue Length'] -= 1
        data['Cumulative Stats']['Shekayat Service Starters'] += 1
        data['Shekayat Queue files'].pop(first_file_in_shekayat_queue, None)
        data['Last Time Shekayat Queue Length Changed'] = clock
        data['Last Time Shekayat departure happened'] = clock
        fel_maker(future_event_list, "departure of shekayat", clock, state, first_file_in_shekayat_queue)
    fel_maker(future_event_list, "arrival of karshenasi from shekayat", clock, state, file)


def arrival_of_takmil_parvandeh(future_event_list, state, clock, data, file):
    # data['files'][file] = dict()
    data['files'][file]['arrival of takmil parvandeh Time'] = clock

    if state["Parvandeh Server Status"] < 3:
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
            elif current_event["Event Type"] == 'arrival of karshenasi from shekayat':
                arrival_of_karshenasi_from_shekayat(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'departure of karshenasi':
                departure_of_karshenasi(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'arrival of shekayat':
                arrival_of_shekayat(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'departure of shekayat':
                departure_of_shekayat(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'arrival of takmil parvandeh':
                arrival_of_takmil_parvandeh(future_event_list, state, clock, data, file)
            elif current_event["Event Type"] == 'departure of takmil parvandeh':
                departure_of_takmil_parvandeh(future_event_list, state, clock, data, file)
            future_event_list.remove(current_event)
        else:
            future_event_list.clear()
        # table.append(create_row(step, current_event, state, data, future_event_list))
        # step += 1

    # excel_main_header = create_main_header(state, data)
    # justify(table)
    # create_excel(table, excel_main_header)
    print('Simulation Ended!\n')

    # Wq_Takmil_Parvandeh = data['Cumulative Stats']['Takmil Parvandeh Queue Waiting Time'] /  data['Cumulative Stats']['Takmil Parvandeh Service Starters']
    # print(f'Wq_Takmil_Parvandeh = {Wq_Takmil_Parvandeh}')

    # Wq_Tashkil_Parvandeh = data['Cumulative Stats']['Tashkil Parvandeh Queue Waiting Time'] /  data['Cumulative Stats']['Tashkil Parvandeh Service Starters']
    # print(f'Wq_Tashkil_Parvandeh = {Wq_Tashkil_Parvandeh}')
    return data


num_of_replications = 20
num_of_days = 100
frame_length = 480
window_size = 3
tick_spacing = 5

# Set font and font size
mpl.rc('font', family='Times New Roman')
mpl.rc('font', size=12)

# Create an empty figure with two subplots
fig, ax = plt.subplots(nrows=4, ncols=1, figsize=(16, 12))



aksbardari_queue_waiting_time_frame_aggregate = dict()
karshenasi_queue_waiting_time_frame_aggregate = dict()
tashkil_parvandeh_queue_waiting_time_frame_aggregate = dict()
takmil_parvandeh_queue_waiting_time_frame_aggregate = dict()


def moving_average(input_list, m):
    output_list = []
    n = len(input_list)
    for i in range(n):
        output_list.append(sum(input_list[max(i - m // 2, 2 * i - n + 1, 0):min(i + m // 2 + 1, 2 * i + 1, n)]) / (
                min(i + m // 2, 2 * i, n - 1) - max(i - m // 2, 2 * i - n + 1, 0) + 1))
    return output_list

def calculate_aggregate_aksbardari_queue_waiting_time(start_time, end_time, files_data):
    cumulative_aksbardari_queue_waiting_time = 0
    for file in files_data:
        # print( files_data)
        # print(files_data.keys())
        if start_time <= files_data[file]['arrival of dakhel mohavateh Time'] < end_time:
            if files_data[file]['Aksbardari Time Service Begins'] < end_time:
                cumulative_aksbardari_queue_waiting_time += files_data[file][
                                                                       'Aksbardari Time Service Begins'] - \
                                                                   files_data[file][
                                                                       'arrival of dakhel mohavateh Time']

            else:
                cumulative_aksbardari_queue_waiting_time += end_time - \
                                                                   files_data[file][
                                                                       'arrival of dakhel mohavateh Time']

        elif start_time < files_data[file]['Aksbardari Time Service Begins'] < end_time:
            cumulative_aksbardari_queue_waiting_time += files_data[file][
                                                                   'Aksbardari Time Service Begins'] - \
                                                               start_time

        elif files_data[file]['arrival of dakhel mohavateh Time'] > end_time:
            break

    return cumulative_aksbardari_queue_waiting_time

def calculate_aggregate_karshenasi_queue_waiting_time(start_time, end_time, files_data):
    cumulative_karshenasi_queue_waiting_time = 0
    for file in files_data:
        # print( files_data)
        # print(files_data.keys())
        if start_time <= files_data[file]['arrival of karshenasi Time'] < end_time:
            if files_data[file]['Karshenasi Time Service Begins'] < end_time:
                cumulative_karshenasi_queue_waiting_time += files_data[file][
                                                                       'Karshenasi Time Service Begins'] - \
                                                                   files_data[file][
                                                                       'arrival of karshenasi Time']

            else:
                cumulative_karshenasi_queue_waiting_time += end_time - \
                                                                   files_data[file][
                                                                       'arrival of karshenasi Time']

        elif start_time < files_data[file]['Karshenasi Time Service Begins'] < end_time:
            cumulative_karshenasi_queue_waiting_time += files_data[file][
                                                                   'Karshenasi Time Service Begins'] - \
                                                               start_time

        elif files_data[file]['arrival of karshenasi Time'] > end_time:
            break

    return cumulative_karshenasi_queue_waiting_time



def calculate_aggregate_tashkil_parvandeh_queue_waiting_time(start_time, end_time, files_data):
    cumulative_tashkil_parvandeh_queue_waiting_time = 0
    for file in files_data:
        # print( files_data)
        # print(files_data.keys())
        if start_time <= files_data[file]['arrival of tashkil parvandeh Time'] < end_time:
            if files_data[file]['Tashkil Parvandeh Time Service Begins'] < end_time:
                cumulative_tashkil_parvandeh_queue_waiting_time += files_data[file][
                                                                       'Tashkil Parvandeh Time Service Begins'] - \
                                                                   files_data[file][
                                                                       'arrival of tashkil parvandeh Time']

            else:
                cumulative_tashkil_parvandeh_queue_waiting_time += end_time - \
                                                                   files_data[file][
                                                                       'arrival of tashkil parvandeh Time']

        elif start_time < files_data[file]['Tashkil Parvandeh Time Service Begins'] < end_time:
            cumulative_tashkil_parvandeh_queue_waiting_time += files_data[file][
                                                                   'Tashkil Parvandeh Time Service Begins'] - \
                                                               start_time

        elif files_data[file]['arrival of tashkil parvandeh Time'] > end_time:
            break

    return cumulative_tashkil_parvandeh_queue_waiting_time


def calculate_aggregate_takmil_parvandeh_queue_waiting_time(start_time, end_time, files_data):
    cumulative_takmil_parvandeh_queue_waiting_time = 0

    for file in files_data:
        # print( files_data)
        # print(files_data[file])
        if start_time <= files_data[file]['arrival of takmil parvandeh Time'] < end_time:
            if files_data[file]['Takmil Parvandeh Time Service Begins'] < end_time:
                cumulative_takmil_parvandeh_queue_waiting_time += files_data[file][
                                                                      'Takmil Parvandeh Time Service Begins'] - \
                                                                  files_data[file][
                                                                      'arrival of takmil parvandeh Time']

            else:
                cumulative_takmil_parvandeh_queue_waiting_time += end_time - \
                                                                  files_data[file][
                                                                      'arrival of takmil parvandeh Time']

        elif start_time < files_data[file]['Takmil Parvandeh Time Service Begins'] < end_time:
            cumulative_takmil_parvandeh_queue_waiting_time += files_data[file][
                                                                  'Takmil Parvandeh Time Service Begins'] - \
                                                              start_time

        elif files_data[file]['arrival of takmil parvandeh Time'] > end_time:
            break

    return cumulative_takmil_parvandeh_queue_waiting_time


simulation_time = num_of_days * 1440
num_of_frames = simulation_time // frame_length - 50

x = [i for i in range(1, num_of_frames + 1)]

for replication in range(1, num_of_replications + 1):

    simulation_data = simulation(num_of_days * 1440)
    # print(simulation_data)
    files_data = simulation_data['files']
    # print(files_data["C1,1,o"])
    # print(files_data)

    aksbardari_queue_waiting_time_frame_aggregate[replication] = []
    karshenasi_queue_waiting_time_frame_aggregate[replication] = []
    tashkil_parvandeh_queue_waiting_time_frame_aggregate[replication] = []
    takmil_parvandeh_queue_waiting_time_frame_aggregate[replication] = []

    # do calculations frame by frame
    for time in range(0, num_of_frames * frame_length, frame_length):

        aksbardari_queue_waiting_time_frame_aggregate[replication].append(
            calculate_aggregate_aksbardari_queue_waiting_time(time, time + frame_length, files_data))

        karshenasi_queue_waiting_time_frame_aggregate[replication].append(
            calculate_aggregate_karshenasi_queue_waiting_time(time, time + frame_length, files_data))

        tashkil_parvandeh_queue_waiting_time_frame_aggregate[replication].append(
            calculate_aggregate_tashkil_parvandeh_queue_waiting_time(time, time + frame_length, files_data))

        takmil_parvandeh_queue_waiting_time_frame_aggregate[replication].append(
            calculate_aggregate_takmil_parvandeh_queue_waiting_time(time, time + frame_length, files_data))
        # print(files_data)

    # plot outputs in each replication
    # ax[0].plot(x, aksbardari_queue_waiting_time_frame_aggregate[replication], alpha=0.5)
    # ax[1].plot(x, karshenasi_queue_waiting_time_frame_aggregate[replication], alpha=0.5)
    # ax[2].plot(x, tashkil_parvandeh_queue_waiting_time_frame_aggregate[replication], alpha=0.5)
    # ax[3].plot(x, takmil_parvandeh_queue_waiting_time_frame_aggregate[replication], alpha=0.5)

aksbardari_waiting_time_replication_average = []
karshenasi_waiting_time_replication_average = []
tashkil_parvandeh_waiting_time_replication_average = []
takmil_parvandeh_waiting_time_replication_average = []


for i in range(num_of_frames):

    average_aksbardari_waiting_time = 0
    average_karshenasi_waiting_time = 0
    average_tashkil_parvandeh_waiting_time = 0
    average_takmil_parvandeh_waiting_time = 0


    for replication in range(1, num_of_replications + 1):


        average_aksbardari_waiting_time += aksbardari_queue_waiting_time_frame_aggregate[replication][
                                                      i] * (1 / num_of_replications)

        average_karshenasi_waiting_time += karshenasi_queue_waiting_time_frame_aggregate[replication][i] * (
                1 / num_of_replications)

        average_tashkil_parvandeh_waiting_time += tashkil_parvandeh_queue_waiting_time_frame_aggregate[replication][
                                                      i] * (1 / num_of_replications)

        average_takmil_parvandeh_waiting_time += takmil_parvandeh_queue_waiting_time_frame_aggregate[replication][i] * (
                1 / num_of_replications)

    aksbardari_waiting_time_replication_average.append(average_aksbardari_waiting_time)
    karshenasi_waiting_time_replication_average.append(average_karshenasi_waiting_time)
    tashkil_parvandeh_waiting_time_replication_average.append(average_tashkil_parvandeh_waiting_time)
    takmil_parvandeh_waiting_time_replication_average.append(average_takmil_parvandeh_waiting_time)


aksbardari_waiting_time_moving_replication_average = moving_average(
    aksbardari_waiting_time_replication_average, window_size)
karshenasi_waiting_time_moving_replication_average = moving_average(
    karshenasi_waiting_time_replication_average, window_size)
tashkil_parvandeh_waiting_time_moving_replication_average = moving_average(
    tashkil_parvandeh_waiting_time_replication_average, window_size)
takmil_parvandeh_waiting_time_moving_replication_average = moving_average(
    takmil_parvandeh_waiting_time_replication_average, window_size)

fig.suptitle(f'Warm-up analysis over. {num_of_replications} replications')






ax[0].plot(x, aksbardari_waiting_time_moving_replication_average, 'r', linewidth=5,
           label="Aksbardari Average across replications")
ax[0].plot(x, aksbardari_waiting_time_moving_replication_average, 'k',
           label=f'Aksbardari Moving average (m = {window_size})')
ax[0].set_title('Aggregate Aksbardari Waiting Time')
ax[0].set_xlabel('Frame No.')
ax[0].set_ylabel('Aggregate Aksbardari Waiting Time')
ax[0].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax[0].legend()

ax[1].plot(x, karshenasi_waiting_time_moving_replication_average, 'r', linewidth=5,
           label="Karshenasi Average across replications")
ax[1].plot(x, karshenasi_waiting_time_moving_replication_average, 'k',
           label=f'Karshenasi Moving average (m = {window_size})')
ax[1].set_title('Aggregate Karshenasi Waiting Time')
ax[1].set_xlabel('Frame No.')
ax[1].set_ylabel('Aggregate Karshenasi Waiting Time')
ax[1].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax[1].legend()


ax[2].plot(x, tashkil_parvandeh_waiting_time_moving_replication_average, 'r', linewidth=5,
           label="Tashkil Parvandeh Average across replications")
ax[2].plot(x, tashkil_parvandeh_waiting_time_moving_replication_average, 'k',
           label=f'Tashkil Parvandeh Moving average (m = {window_size})')
ax[2].set_title('Aggregate Tashkil Parvandeh Waiting Time')
ax[2].set_xlabel('Frame No.')
ax[2].set_ylabel('Aggregate Tashkil Parvandeh Waiting Time')
ax[2].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax[2].legend()

ax[3].plot(x, takmil_parvandeh_waiting_time_moving_replication_average, 'r', linewidth=5,
           label="Takmil Parvandeh Average across replications")
ax[3].plot(x, takmil_parvandeh_waiting_time_moving_replication_average, 'k',
           label=f'Takmil Parvandeh Moving average (m = {window_size})')
ax[3].set_title('Aggregate Takmil Parvandeh Waiting Time')
ax[3].set_xlabel('Frame No.')
ax[3].set_ylabel('Aggregate Takmil Parvandeh Waiting Time')
ax[3].xaxis.set_major_locator(ticker.MultipleLocator(tick_spacing))
ax[3].legend()

fig.tight_layout()
fig.show()
fig.savefig('Multi server queue - Warm-up analysis - Time-Frame Approach')
