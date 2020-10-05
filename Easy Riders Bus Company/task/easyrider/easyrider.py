import json
# 15 min

data = json.loads(input())

fields = {
    'bus_id': int,
    'stop_id': int,
    'stop_name': str,
    'next_stop': int,
    'stop_type': str,
    'a_time': str,
}

errors_total = 0
errors = {}

for entry in data:
    for field_name, field_type in fields.items():
        if field_name not in errors:
            errors[field_name] = 0
        field_value = entry.get(field_name, '')
        if not field_value or not isinstance(field_value, field_type):
            errors[field_name] += 1
            errors_total += 1

print(f'Type and required field validation: {errors_total} errors')
for k, v in errors.items():
    print(f'{k}: {v}')
