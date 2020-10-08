import json
import re
# 15 min

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

find_lines(data)
