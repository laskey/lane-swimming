import requests
from datetime import datetime, timedelta
import calendar
import json
import os

# Pool information
pools = [
    {'name': 'Piccininni', 'number': 509},
    {'name': 'Vaughan Road Academy', 'number': 1371},
    {'name': 'North Toronto', 'number': 189},
    {'name': 'Hillcrest Community Centre', 'number': 48},
    {'name': 'Wallace Emerson', 'number': 294}
]

# Drop-in session types to include; titles are matched by prefix so
# variants like "Leisure Swim: Older Adult" are included too
swim_types = ['Lane Swim', 'Leisure Swim']

# Match a session title against swim_types; returns (base type, variant)
# e.g. "Leisure Swim: Older Adult" -> ('Leisure Swim', 'Older Adult')
def match_swim_type(title):
    for base in swim_types:
        if title.startswith(base):
            return base, title[len(base):].strip(' :-')
    return None, None

# Function to get the schedule for a pool
def get_pool_schedule(pool_number, week_number):
    url = f'https://www.toronto.ca/data/parks/live/locations/{pool_number}/swim/week{week_number}.json'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        response.encoding = response.apparent_encoding
        try:
            return response.json()
        except ValueError as e:
            return None
    else:
        print(f'Error fetching data for pool {pool_number}, week {week_number}: {response.status_code}')
        return None

# Function to extract swim times
def extract_swim_times(schedule, pool_name, week_start_date):
    swim_times = []
    today = datetime.today()
    if schedule:
        for program in schedule.get('programs', []):
            if program['program'] == 'Swim - Drop-In':
                for day in program['days']:
                    swim_type, variant = match_swim_type(day['title'])
                    if swim_type:
                        for time in day['times']:
                            # Calculate the full date
                            day_name = time['day'].lower()
                            day_index = list(calendar.day_name).index(day_name.capitalize())
                            day_offset = (day_index - week_start_date.weekday()) % 7
                            full_date = week_start_date + timedelta(days=day_offset)
                            if full_date >= today - timedelta(days=1):
                                entry = {
                                    'date': full_date.strftime('%Y-%m-%d'),
                                    'pool_name': pool_name,
                                    'swim_type': swim_type,
                                    'time': time['title']
                                }
                                if variant:
                                    entry['variant'] = variant
                                swim_times.append(entry)
    return swim_times

# Sort key for a session's start time, e.g. "07:00 AM - 09:15 AM"
def start_time_key(entry):
    try:
        return datetime.strptime(entry['time'].split('-')[0].strip(), '%I:%M %p').time()
    except ValueError:
        return datetime.min.time()

# Main function to get schedules and output JSON
def main():
    all_swim_times = []
    today = datetime.today()
    week_start_date = today - timedelta(days=today.weekday())
    for pool in pools:
        for week in range(1, 5):
            schedule = get_pool_schedule(pool['number'], week)
            swim_times = extract_swim_times(schedule, pool['name'], week_start_date + timedelta(weeks=week-1))
            all_swim_times.extend(swim_times)
    all_swim_times.sort(key=lambda x: (x['date'], start_time_key(x), x['pool_name']))
    # Add last updated timestamp
    output_data = {
        'last_updated': today.strftime('%Y-%m-%d %H:%M:%S'),
        'swim_times': all_swim_times
    }
    # Save the JSON file in the web directory
    web_dir = os.path.join(os.path.dirname(__file__), '..', 'web')
    with open(os.path.join(web_dir, 'lane_swim_times.json'), 'w') as f:
        json.dump(output_data, f, indent=4)

if __name__ == '__main__':
    main()
