import requests
from datetime import datetime, timedelta
import calendar
import json

# Pool information
pools = [
    {'name': 'Piccininni', 'number': 509},
    {'name': 'Vaughan Road Academy', 'number': 1371},
    {'name': 'North Toronto', 'number': 189},
    {'name': 'Hillcrest Community Centre', 'number': 48},
    {'name': 'Wallace Emerson', 'number': 294}
]

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

# Function to extract lane swim times
def extract_lane_swim_times(schedule, pool_name, week_start_date):
    lane_swim_times = []
    today = datetime.today()
    if schedule:
        for program in schedule.get('programs', []):
            if program['program'] == 'Swim - Drop-In':
                for day in program['days']:
                    if day['title'] == 'Lane Swim':
                        for time in day['times']:
                            # Calculate the full date
                            day_name = time['day'].lower()
                            day_index = list(calendar.day_name).index(day_name.capitalize())
                            day_offset = (day_index - week_start_date.weekday()) % 7
                            full_date = week_start_date + timedelta(days=day_offset)
                            if full_date >= today - timedelta(days=1):
                                lane_swim_times.append({
                                    'date': full_date.strftime('%A, %B %d, %Y'),
                                    'pool_name': pool_name,
                                    'lane_swim_time': time['title']
                                })
    return lane_swim_times

# Main function to get schedules and output table
def main():
    all_lane_swim_times = []
    today = datetime.today()
    week_start_date = today - timedelta(days=today.weekday())
    for pool in pools:
        for week in range(1, 5):
            schedule = get_pool_schedule(pool['number'], week)
            lane_swim_times = extract_lane_swim_times(schedule, pool['name'], week_start_date + timedelta(weeks=week-1))
            all_lane_swim_times.extend(lane_swim_times)
    # Sort the lane swim times by date
    all_lane_swim_times.sort(key=lambda x: datetime.strptime(x['date'], '%A, %B %d, %Y'))
    with open('lane_swim_times.json', 'w') as f:
        json.dump(all_lane_swim_times, f, indent=4)

if __name__ == '__main__':
    main()
