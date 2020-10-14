import json
import re
from datetime import datetime

data = json.loads(input())

# Fields with attributes: type, required, format(regex)
fields = {
    'bus_id': [int, True, None],
    'stop_id': [int, True, None],
    'stop_name': [str, True, '^[A-Z].*(?:Avenue|Street|Boulevard|Road)$'],
    'next_stop': [int, True, None],
    'stop_type': [str, False, '^[SOF]$'],
    'a_time': [str, True, r'([01][0-9]|2[0-3]):[0-5][0-9]$'],
    # 'a_time': [str, True, r'([01]?[0-9]|2[0-3]):[0-5][0-9]'],
}


def check_valid(data):
    errors_total = 0
    errors = {}

    for entry in data:
        for field_name, field_attr in fields.items():
            if field_name not in errors:
                errors[field_name] = 0
            field_value = entry.get(field_name, '')
            field_type, field_req, field_format = field_attr

            if field_req and (field_value is None or field_value == ''):
                errors[field_name] += 1
            elif not isinstance(field_value, field_type):
                errors[field_name] += 1
            elif field_value and field_format and re.match(field_format, field_value) is None:
                errors[field_name] += 1
        errors_total = sum(errors.values())

    print(f'Type and required field validation: {errors_total} errors')
    for k, v in errors.items():
        print(f'{k}: {v}')


def find_lines(data):
    bus_lines = {}
    for entry in data:
        bus_id = entry['bus_id']
        if bus_id not in bus_lines:
            bus_lines[bus_id] = set()
        bus_lines[bus_id].add(entry['stop_name'])

    print('Lines names and number of stops:')
    for bus_line, stops in bus_lines.items():
        print(f'bus_id: {bus_line}, stops: {len(stops)}')


def find_stops(data):
    bus_starts = {}
    bus_stops = {}
    bus_finishes = {}
    bus_all_stops = {}
    bus_lines = set()
    for entry in data:
        bus_id = entry['bus_id']
        bus_lines.add(bus_id)
        stop_type = entry['stop_type']
        if bus_id not in bus_stops:
            bus_stops[bus_id] = set()
        if bus_id not in bus_all_stops:
            bus_all_stops[bus_id] = set()
        bus_all_stops[bus_id].add(entry['stop_name'])
        if stop_type == 'S':
            if bus_id not in bus_starts:
                bus_starts[bus_id] = set()
            bus_starts[bus_id].add(entry['stop_name'])
        elif stop_type == 'F':
            if bus_id not in bus_finishes:
                bus_finishes[bus_id] = set()
            bus_finishes[bus_id].add(entry['stop_name'])
        else:
            bus_stops[bus_id].add(entry['stop_name'])

    all_starts = set()
    all_finishes = set()
    all_transfers = set()
    bus_lines = sorted(bus_lines)

    for i, line in enumerate(bus_lines):
        if line not in bus_starts or len(bus_starts[line]) != 1:
            print(f'There is no start for the line: {line}')
            return
        if line not in bus_finishes or len(bus_finishes[line]) != 1:
            print(f'There is no finish for the line: {line}')
            return
        all_starts |= bus_starts[line]
        all_finishes |= bus_finishes[line]
        for j in range(i + 1, len(bus_lines)):
            all_transfers |= bus_all_stops[line] & bus_all_stops[bus_lines[j]]

    print(f'Start stops: {len(all_starts)} {sorted(all_starts)}')
    print(f'Transfer stops: {len(all_transfers)} {sorted(all_transfers)}')
    print(f'Finish stops: {len(all_finishes)} {sorted(all_finishes)}')

    return


def get_bus_stop(data, bus_id, stop_type=None, stop_id=None):
    for entry in data:
        if entry['bus_id'] == bus_id:
            if stop_type and entry['stop_type'] == stop_type:
                return entry
            if stop_id and entry['stop_id'] == stop_id:
                return entry
    return None


def get_bus_start(data, bus_id):
    # Not sure whether the start is the entry with the S stop_type or the one with the lowest stop_id
    line_stops_ids = [e['stop_id'] for e in data if e['bus_id'] == bus_id]
    start_id = min(line_stops_ids)
    return get_bus_stop(data, bus_id, stop_id=start_id)


def get_bus_finish(data, bus_id):
    line_stops_ids = [e['stop_id'] for e in data if e['bus_id'] == bus_id]
    finish_id = max(line_stops_ids)
    return get_bus_stop(data, bus_id, stop_id=finish_id)


def get_bus_transfers(data, bus_id):
    line_stops_ids = [e['stop_id'] for e in data if e['bus_id'] == bus_id]
    transfers = [e for e in data if e['bus_id'] != bus_id and e['stop_id'] in line_stops_ids]
    return transfers


def check_time(data):
    bus_lines = list(set([e['bus_id'] for e in data]))
    bus_lines.sort()
    all_times_ok = True
    for line in bus_lines:
        bus_stop = get_bus_stop(data, line, stop_type="S")
        stop_time = datetime.strptime(bus_stop['a_time'], '%H:%M')
        next_stop = bus_stop['next_stop']
        while bus_stop['stop_type'] != "F":
            bus_stop = get_bus_stop(data, line, stop_id=next_stop)
            this_time = datetime.strptime(bus_stop['a_time'], '%H:%M')
            next_stop = bus_stop['next_stop']
            if this_time <= stop_time:
                print(f'bus_id line {line}: wrong time on station {bus_stop["stop_name"]}')
                all_times_ok = False
                break
            stop_time = this_time
    if all_times_ok:
        print('OK')
    return


def check_on_demand(data):
    bus_lines = list(set([e['bus_id'] for e in data]))
    bus_lines.sort()
    wrong_stops = set()
    print('On demand stops test:')
    for line in bus_lines:
        stops = []
        stops.append(get_bus_start(data, line))
        stops.append(get_bus_finish(data, line))
        stops.extend(get_bus_transfers(data, line))
        wrong_stops.update([s['stop_name'] for s in stops if s['stop_type'] == 'O'])
    if len(wrong_stops):
        print(f'Wrong stop type: {sorted(wrong_stops)}')
    else:
        print('OK')


# find_lines(data)
# find_stops(data)
# check_time(data)
check_on_demand(data)

'''
Test1
[{"bus_id" : 128, "stop_id" : 1, "stop_name" : "Prospekt Avenue", "next_stop" : 3, "stop_type" : "S", "a_time" : "08:12"}, {"bus_id" : 128, "stop_id" : 3, "stop_name" : "Elm Street", "next_stop" : 5, "stop_type" : "", "a_time" : "08:19"}, {"bus_id" : 128, "stop_id" : 5, "stop_name" : "Fifth Avenue", "next_stop" : 7, "stop_type" : "O", "a_time" : "08:25"}, {"bus_id" : 128, "stop_id" : 7, "stop_name" : "Sesame Street", "next_stop" : 0, "stop_type" : "F", "a_time" : "08:37"}, {"bus_id" : 256, "stop_id" : 2, "stop_name" : "Pilotow Street", "next_stop" : 3, "stop_type" : "S", "a_time" : "09:20"}, {"bus_id" : 256, "stop_id" : 3, "stop_name" : "Elm Street", "next_stop" : 6, "stop_type" : "", "a_time" : "09:45"}, {"bus_id" : 256, "stop_id" : 6, "stop_name" : "Sunset Boulevard", "next_stop" : 7, "stop_type" : "", "a_time" : "09:59"}, {"bus_id" : 256, "stop_id" : 7, "stop_name" : "Sesame Street", "next_stop" : 0, "stop_type" : "F", "a_time" : "10:12"}, {"bus_id" : 512, "stop_id" : 4, "stop_name" : "Bourbon Street", "next_stop" : 6, "stop_type" : "S", "a_time" : "08:13"}, {"bus_id" : 512, "stop_id" : 6, "stop_name" : "Sunset Boulevard", "next_stop" : 0, "stop_type" : "F", "a_time" : "08:16"}]
'''