#!/usr/bin/env python3
# Modified Strava Chain Tracker that outputs a website
# This script retrieves activities from Strava and generates an HTML website

import os
import datetime
import time
from dotenv import load_dotenv
from stravalib.client import Client
from stravalib import unithelper

# Load environment variables from .env file
load_dotenv()

# Strava API credentials
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')
REFRESH_TOKEN = os.getenv('STRAVA_REFRESH_TOKEN')

# Chain emoji markers
CHAIN_START_EMOJI = '⛓️'
CHAIN_END_EMOJI = '⛓️‍💥'


def setup_client():
	"""Create and authenticate a Strava client"""
	client = Client()

	# Exchange the refresh token for a fresh access token
	refresh_response = client.refresh_access_token(
		client_id=CLIENT_ID,
		client_secret=CLIENT_SECRET,
		refresh_token=REFRESH_TOKEN
	)

	# Set the access token on the client
	client.access_token = refresh_response['access_token']

	return client


def fetch_all_activities(client):
	"""Fetch activities from Strava for the last 6 months"""
	print('Fetching activities from the last 6 months...')

	# Calculate date 6 months ago from today
	today = datetime.datetime.now()
	six_months_ago = today - datetime.timedelta(days=365)  # Approximately 6 months

	print(f"Getting activities since: {six_months_ago.strftime('%Y-%m-%d')}")

	# stravalib handles pagination internally when we use the iterator
	all_activities = []
	count = 0

	# Get activities using the iterator with the after parameter
	for activity in client.get_activities(after=six_months_ago):
		all_activities.append(activity)
		count += 1

		# Print progress after every 30 activities (approximately one page)
		if count % 30 == 0:
			print(f"Fetched {count} activities so far")

		# Be nice to the API rate limits
		if count % 10 == 0:  # Add a small delay every 10 activities
			time.sleep(0.1)

	print(f"Total activities fetched: {len(all_activities)}")
	return all_activities


def filter_ride_activities(activities):
	"""Filter only cycling activities"""
	return [activity for activity in activities if activity.type == 'Ride']


def has_chain_start_emoji(activity):
	"""Check if an activity contains the chain start emoji in name or description"""
	# Check in name
	if activity.name and CHAIN_START_EMOJI in activity.name and CHAIN_END_EMOJI not in activity.name:
		return True

	# Check in description
	if activity.description and CHAIN_START_EMOJI in activity.description and CHAIN_END_EMOJI not in activity.description:
		return True

	return False


def has_chain_end_emoji(activity):
	"""Check if an activity contains the chain end emoji in name or description"""
	# Check in name
	if activity.name and CHAIN_END_EMOJI in activity.name:
		return True

	# Check in description
	if activity.description and CHAIN_END_EMOJI in activity.description:
		return True

	return False


def aggregate_kilometers(activities):
	"""Aggregate kilometers based on chain start and end emoji markers"""
	# Sort activities by date (oldest first)
	activities.sort(key=lambda a: a.start_date)

	chains = []
	current_chain = None
	in_chain = False

	# Process each activity
	for activity in activities:
		# Check for chain markers
		is_chain_start = has_chain_start_emoji(activity)
		is_chain_end = has_chain_end_emoji(activity)

		# Convert distance to kilometers
		distance_km = float(unithelper.kilometers(activity.distance))
		activity_date = activity.start_date.replace(tzinfo=None)  # Remove timezone info for easier formatting

		# Start a new chain if we see the start emoji
		if is_chain_start:
			# If we were already in a chain, finalize it before starting a new one
			if in_chain and current_chain is not None:
				chains.append(current_chain)

			# Start a new chain
			current_chain = {
				'start_date': activity_date,
				'end_date': activity_date,  # Will be updated as we go
				'activities': [],
				'total_km': 0
			}
			in_chain = True

		# If we're in a chain, add the activity
		if in_chain and current_chain is not None:
			current_chain['activities'].append({
				'id': activity.id,
				'name': activity.name,
				'date': activity_date,
				'distance_km': round(distance_km, 2),
				'is_chain_start': is_chain_start,
				'is_chain_end': is_chain_end
			})

			current_chain['total_km'] += distance_km
			current_chain['end_date'] = activity_date

			# End the chain if we see the end emoji
			if is_chain_end:
				chains.append(current_chain)
				current_chain = None
				in_chain = False

	# Add the last chain if it's still open
	if in_chain and current_chain is not None and current_chain['activities']:
		chains.append(current_chain)

	return chains


def generate_html(chains):
	"""Generate a complete HTML website from the chains data"""

	# Calculate some overall statistics
	total_chains = len(chains)
	total_distance = sum(chain['total_km'] for chain in chains)
	total_activities = sum(len(chain['activities']) for chain in chains)

	# Find the longest chain by distance
	longest_chain = max(chains, key=lambda x: x['total_km']) if chains else None
	longest_chain_distance = longest_chain['total_km'] if longest_chain else 0
	longest_chain_index = chains.index(longest_chain) + 1 if longest_chain else 0

	html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Strava Chain Tracker</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            padding-top: 20px;
            padding-bottom: 40px;
        }}
        .chain-card {{
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .chain-header {{
            background-color: #fc4c02;
            color: white;
            padding: 15px;
            border-top-left-radius: 10px;
            border-top-right-radius: 10px;
        }}
        .chain-body {{
            padding: 20px;
        }}
        .stats-card {{
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        .chain-start {{
            background-color: #d4edda;
        }}
        .chain-end {{
            background-color: #f8d7da;
        }}
        .progress-column {{
            background: linear-gradient(90deg, 
                rgba(223, 240, 216, 0.5) 0%, 
                rgba(223, 240, 216, 0.5) var(--progress-percent), 
                transparent var(--progress-percent), 
                transparent 100%);
        }}
        .strava-header {{
            background-color: #fc4c02;
            color: white;
            padding: 15px 0;
            margin-bottom: 30px;
        }}
        .last-updated {{
            font-size: 0.8em;
            color: #6c757d;
            margin-top: 5px;
        }}
    </style>
</head>
<body>
    <div class="strava-header">
        <div class="container">
            <h1 class="display-4">⛓️ Strava Chain Tracker</h1>
            <p class="lead">Track your cycling chains and achievements</p>
            <p class="last-updated">Last updated: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M")}</p>
        </div>
    </div>

    <div class="container">
        <!-- Overall Statistics -->
        <div class="row stats-card">
            <div class="col-md-3">
                <h4>Total Chains</h4>
                <h2>{total_chains}</h2>
            </div>
            <div class="col-md-3">
                <h4>Total Distance</h4>
                <h2>{total_distance:.2f} km</h2>
            </div>
            <div class="col-md-3">
                <h4>Total Activities</h4>
                <h2>{total_activities}</h2>
            </div>
            <div class="col-md-3">
                <h4>Longest Chain</h4>
                <h2>{longest_chain_distance:.2f} km</h2>
                <p>Chain #{longest_chain_index}</p>
            </div>
        </div>

        <!-- Individual Chains -->
"""

	# Add each chain to the HTML
	for i, chain in enumerate(chains):
		start_date_str = chain['start_date'].strftime("%Y-%m-%d")
		end_date_str = chain['end_date'].strftime("%Y-%m-%d")

		html += f"""
        <div class="chain-card">
            <div class="chain-header">
                <h2>Chain {i + 1}</h2>
                <p class="mb-0">Period: {start_date_str} to {end_date_str}</p>
            </div>
            <div class="chain-body">
                <div class="row mb-3">
                    <div class="col-md-6">
                        <h4>Total Distance</h4>
                        <h3>{chain['total_km']:.2f} km</h3>
                    </div>
                    <div class="col-md-6">
                        <h4>Number of Rides</h4>
                        <h3>{len(chain['activities'])}</h3>
                    </div>
                </div>

                <table class="table table-striped">
                    <thead>
                        <tr>
                            <th>Date</th>
                            <th>Activity Name</th>
                            <th>Distance (km)</th>
                            <th>Running Total (km)</th>
                            <th>Notes</th>
                        </tr>
                    </thead>
                    <tbody>
"""

		running_total = 0
		for activity in chain['activities']:
			date_str = activity['date'].strftime("%Y-%m-%d")
			name_str = activity['name']
			distance = activity['distance_km']
			running_total += distance

			# Calculate progress percentage for background gradient
			progress_percent = (running_total / chain['total_km']) * 100

			row_class = ""
			notes = []

			if activity.get('is_chain_start'):
				row_class = "chain-start"
				notes.append("Chain Start")
			if activity.get('is_chain_end'):
				row_class = "chain-end"
				notes.append("Chain End")

			notes_str = ", ".join(notes)

			html += f"""
                        <tr class="{row_class}">
                            <td>{date_str}</td>
                            <td>{name_str}</td>
                            <td>{distance}</td>
                            <td class="progress-column" style="--progress-percent: {progress_percent}%;">{running_total:.2f}</td>
                            <td>{notes_str}</td>
                        </tr>
"""

		html += """
                    </tbody>
                </table>
            </div>
        </div>
"""

	# Close the HTML document
	html += """
    </div>

    <footer class="bg-light py-4 mt-4">
        <div class="container text-center">
            <p>Powered by the Strava API</p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0-alpha1/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

	return html


def save_html(content, filename='strava_chains_website.html'):
	"""Save the HTML website to a file"""
	with open(filename, 'w', encoding='utf-8') as f:
		f.write(content)
	print(f"Website saved to {filename}")


def main():
	"""Main function to run the script"""
	try:
		print('Starting Strava Chain Tracker...')

		# Set up the Strava client
		client = setup_client()

		# Fetch all activities
		all_activities = fetch_all_activities(client)

		# Filter only cycling activities
		ride_activities = filter_ride_activities(all_activities)
		print(f"Found {len(ride_activities)} cycling activities")

		# Process the data
		chains = aggregate_kilometers(ride_activities)
		print(f"Identified {len(chains)} chains")

		# Generate and save the HTML website
		html_content = generate_html(chains)
		save_html(html_content)

		print('Done! Website successfully generated.')

	except Exception as e:
		print(f"Error running the script: {e}")


if __name__ == "__main__":
	main()