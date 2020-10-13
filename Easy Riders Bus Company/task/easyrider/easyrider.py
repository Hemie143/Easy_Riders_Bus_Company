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

def check_time(data):
    bus_lines = list(set([e['bus_id'] for e in data]))
    bus_lines.sort()
    # print(bus_lines)
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

    '''
    bus_time = datetime.strptime('00:00', '%H:%M')
    current_line = None
    skip_line = None
    time_errors = False
    print('Arrival time test:')
    for entry in data:
        bus_id = entry['bus_id']
        if bus_id == skip_line:
            continue
        if bus_id != current_line:
            bus_time = datetime.strptime('00:00', '%H:%M')
            current_line = bus_id
        if datetime.strptime(entry['a_time'], '%H:%M') > bus_time or entry['stop_type'] == 'F':
            bus_time = datetime.strptime(entry['a_time'], '%H:%M')
        else:
            print(f'bus_id line {bus_id}: wrong time on station {entry["stop_name"]}')
            skip_line = bus_id
            time_errors = True
    if not time_errors:
        print('OK')
    '''

# find_lines(data)
# find_stops(data)
check_time(data)
