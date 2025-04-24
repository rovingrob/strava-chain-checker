#!/usr/bin/env python3
# Strava Chain Tracker using stravalib
# This script retrieves all activities from your Strava account and aggregates
# kilometers ridden, restarting the count whenever a ⛓️ emoji is encountered

import os
import datetime
import time
from dotenv import load_dotenv
from stravalib.client import Client
from stravalib import unithelper

# Load environment variables from .env file
load_dotenv()

# Strava API credentials - store these in a .env file
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
	six_months_ago = today - datetime.timedelta(days=180)  # Approximately 6 months

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


def format_results(chains):
	"""Format the results for output"""
	output = "# Strava Ride Chains Summary\n\n"

	for i, chain in enumerate(chains):
		start_date_str = chain['start_date'].strftime("%Y-%m-%d")
		end_date_str = chain['end_date'].strftime("%Y-%m-%d")

		output += f"## Chain {i + 1}\n"
		output += f"- **Period**: {start_date_str} to {end_date_str}\n"
		output += f"- **Total Kilometers**: {chain['total_km']:.2f} km\n"
		output += f"- **Number of Rides**: {len(chain['activities'])}\n\n"

		output += "### Activities in this Chain\n"
		output += "| Date | Activity Name | Distance (km) | Running Total (km) | Notes |\n"
		output += "|------|--------------|---------------|-------------------|-------|\n"

		running_total = 0
		for activity in chain['activities']:
			date_str = activity['date'].strftime("%Y-%m-%d")
			name_str = activity['name']
			distance = activity['distance_km']
			running_total += distance
			notes = []

			if activity.get('is_chain_start'):
				notes.append("Chain Start")
			if activity.get('is_chain_end'):
				notes.append("Chain End")

			notes_str = ", ".join(notes)

			output += f"| {date_str} | {name_str} | {distance} | {running_total:.2f} | {notes_str} |\n"

		output += "\n"

	return output


def save_results(content, filename='strava_chains_report.md'):
	"""Save results to a file"""
	with open(filename, 'w', encoding='utf-8') as f:
		f.write(content)
	print(f"Report saved to {filename}")


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

		# Format and save the results
		formatted_results = format_results(chains)
		save_results(formatted_results)

		print('Done!')

	except Exception as e:
		print(f"Error running the script: {e}")


if __name__ == "__main__":
	main()