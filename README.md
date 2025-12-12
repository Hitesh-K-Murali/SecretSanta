# 🎅 Secret Santa Application

A Flask-based web application for organizing Secret Santa gift exchanges with automated email assignments.

## Features

- Web-based participant registration form
- Automatic Secret Santa assignment (no one gets themselves)
- Automated email notifications with recipient details
- Excel-based participant storage

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Email Settings

Create a `.env` file with your Zoho Mail credentials:

```bash
cp .env.example .env
```

Edit `.env` and add your actual credentials:

```
EMAIL_ADDRESS=your-email@zohomail.com
EMAIL_PASSWORD=your-zoho-app-password
```

> **Note**: If using Zoho Mail with 2FA, you'll need to generate an app-specific password:
>
> 1. Go to Zoho Mail Account Settings
> 2. Navigate to Security → App Passwords
> 3. Generate a new app password
> 4. Use that password in your `.env` file

### 3. Load Environment Variables

Before running the app, load the environment variables:

```bash
export $(cat .env | xargs)
```

Or on each run:

```bash
export EMAIL_ADDRESS=your-email@zohomail.com
export EMAIL_PASSWORD=your-password
python app.py
```

### 4. Start the Application

```bash
python app.py
```

The server will start on `http://0.0.0.0:5000`

## How to Use

### Step 1: Register Participants

1. Share the registration URL with participants: `http://YOUR_IP:5000`
2. Each participant fills out:
   - Name
   - Email address
   - Mailing address
3. Participants are automatically saved to `participants.xlsx`

### Step 2: Assign Secret Santa Matches

When all participants have registered:

1. Visit: `http://localhost:5000/assign-match`
2. The system will:
   - Randomly assign Secret Santa pairs
   - Ensure no one gets themselves
   - Send emails **immediately** to all participants

⚠️ **WARNING**: Emails are sent immediately when you visit `/assign-match`. Make sure all participants have registered first!

## Email Content

Each participant receives an email like this:

```
Subject: 🎅 Your Secret Santa Match Details! 🎁

Ho Ho Ho, [Participant Name]! 🎄

You are the Secret Santa for:

Name: [Recipient Name]
Address: [Recipient Address]

Please ensure your gift reaches them before Christmas!

Merry Christmas! 
- The Secret Santa Bot 🤖
```

## File Structure

```
SecretSanta/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .env                    # Email credentials (DO NOT COMMIT)
├── .env.example           # Template for .env
├── participants.xlsx       # Participant data (auto-generated)
├── templates/
│   ├── index.html         # Registration form
│   └── success.html       # Registration confirmation
└── static/
    └── style.css          # Styling
```

## Security Notes

- Never commit `.env` to version control (add to `.gitignore`)
- Use app-specific passwords for email accounts with 2FA
- The `/assign-match` endpoint has no authentication - consider adding protection for production use

## Troubleshooting

### Email not sending?

- Verify your Zoho credentials are correct
- Check if you need an app-specific password (if 2FA is enabled)
- Ensure environment variables are loaded: `echo $EMAIL_ADDRESS`

### Not enough participants?

- You need at least 2 participants to run the assignment
- Check `participants.xlsx` to see who's registered

## Requirements

- Python 3.6+
- Flask
- pandas
- openpyxl
