# Strava Chain Tracker

A Python application that helps cyclists track and analyze their riding streaks using Strava data. The tool identifies "chains" of consecutive rides based on special emoji markers in activity names or descriptions.

## Features

- 🔄 Tracks consecutive riding streaks using emoji markers
- 📊 Calculates total distance for each chain
- 📅 Provides detailed activity breakdowns
- 📝 Generates formatted reports
- 🔐 Secure OAuth2 authentication with Strava
- ⏱️ Respects Strava API rate limits
- 🌐 Generates HTML reports for web viewing
- 📈 Tracks running totals within chains

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/ChainChecker.git
cd ChainChecker
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Create a Strava API application at [Strava API Settings](https://www.strava.com/settings/api)
   - Set the Authorization Callback Domain to `localhost`
   - Note down your Client ID and Client Secret

2. Set up your environment variables:
   ```bash
   # Copy the sample environment file
   cp sample.env .env
   
   # Edit the .env file with your credentials
   nano .env  # or use your preferred text editor
   ```
   - Replace `your_client_id_here` with your Strava Client ID
   - Replace `your_client_secret_here` with your Strava Client Secret

3. Run the authentication helper:
```bash
python auth_helper.py
```
   - This will open a web browser for Strava authentication
   - After authenticating, enter the code from the URL
   - The script will automatically update your .env file with the refresh token

## Usage

### Marking Activities

1. In your Strava activities, use the following emojis:
   - ⛓️ - Start a new chain (e.g., "Morning Ride ⛓️")
   - ⛓️‍💥 - End the current chain (e.g., "Final Ride ⛓️‍💥")

2. Run the chain tracker:
```bash
python strava_chain_tracker.py
```

3. View the generated reports:
   - Markdown report: `strava_chains_report.md`
   - HTML report: `strava_chains_website.html`

### Example Activity Names

```
Morning Ride ⛓️
Afternoon Training
Weekend Long Ride
Final Ride ⛓️‍💥
```

## Output Examples

### Markdown Report
```markdown
# Strava Ride Chains Summary

## Chain 1
- **Period**: 2024-01-01 to 2024-01-15
- **Total Kilometers**: 250.5 km
- **Number of Rides**: 5

### Activities in this Chain
| Date | Activity Name | Distance (km) | Running Total (km) | Notes |
|------|--------------|---------------|-------------------|-------|
| 2024-01-01 | Morning Ride ⛓️ | 50.2 | 50.20 | Chain Start |
| 2024-01-05 | Afternoon Training | 45.8 | 96.00 | |
| 2024-01-10 | Weekend Long Ride | 75.3 | 171.30 | |
| 2024-01-15 | Final Ride ⛓️‍💥 | 79.2 | 250.50 | Chain End |
```

### HTML Report
The HTML report provides an interactive view of your chains with:
- Expandable/collapsible chain sections
- Activity details in a sortable table
- Visual progress indicators
- Mobile-responsive design

## Requirements

- Python 3.x
- stravalib
- python-dotenv

## Troubleshooting

### Authentication Issues
1. **Invalid Refresh Token**
   - Run `auth_helper.py` again to get a new refresh token
   - The script will automatically update your .env file

2. **API Rate Limits**
   - The script automatically handles rate limits
   - If you see rate limit errors, wait a few minutes and try again

### Common Problems
1. **No Activities Found**
   - Ensure you have cycling activities in your Strava account
   - Check that your activities are within the last 6 months
   - Verify your Strava API permissions

2. **Missing Chains**
   - Double-check emoji usage in activity names
   - Ensure emojis are copied correctly (some platforms may render them differently)

## Development

### Project Structure
```
ChainChecker/
├── .env                    # Environment variables (not in git)
├── sample.env             # Template for environment variables
├── auth_helper.py         # Authentication helper
├── strava_chain_tracker.py # Main chain tracking logic
├── strava_chains_report.md # Generated report
└── strava_chains_website.html # HTML report
```

### Adding New Features
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. When contributing:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Support

If you encounter any issues or have questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Search for existing issues
3. If your issue is new, please open an issue in the GitHub repository with:
   - A clear description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Relevant error messages

## Acknowledgments

- [Strava API](https://developers.strava.com/) for providing the activity data
- [stravalib](https://github.com/hozn/stravalib) for the Python Strava API client
