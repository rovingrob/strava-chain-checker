# auth_helper.py
from stravalib.client import Client
import webbrowser
import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Get credentials from environment variables
CLIENT_ID = os.getenv('STRAVA_CLIENT_ID')
CLIENT_SECRET = os.getenv('STRAVA_CLIENT_SECRET')

# Check if credentials are set
if not CLIENT_ID or not CLIENT_SECRET:
    print("Error: STRAVA_CLIENT_ID and STRAVA_CLIENT_SECRET must be set in .env file")
    exit(1)

# Create the client
client = Client()

# Get the authorization URL
auth_url = client.authorization_url(
    client_id=CLIENT_ID,
    redirect_uri='http://localhost',
    scope=['read', 'activity:read_all']
)

# Open the authorization URL in a browser
print("Opening browser for authorization...")
webbrowser.open(auth_url)

# Ask the user for the code from the redirect
code = input("Enter the code from the URL after authorization (after 'code=' in the URL): ")

# Exchange the code for tokens
token_response = client.exchange_code_for_token(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    code=code
)

# Update or create .env file
env_path = '.env'
env_lines = []

# Read existing .env file if it exists
if os.path.exists(env_path):
    with open(env_path, 'r') as f:
        env_lines = f.readlines()

# Update or add STRAVA_REFRESH_TOKEN
refresh_token_line = f"STRAVA_REFRESH_TOKEN={token_response['refresh_token']}\n"
found = False

for i, line in enumerate(env_lines):
    if line.startswith('STRAVA_REFRESH_TOKEN='):
        env_lines[i] = refresh_token_line
        found = True
        break

if not found:
    env_lines.append(refresh_token_line)

# Write back to .env file
with open(env_path, 'w') as f:
    f.writelines(env_lines)

print("\nSuccessfully updated .env file with new refresh token!")
print("You can now run strava_chain_tracker.py")