import os
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime
from threading import Thread

app = Flask(__name__)

CSV_FILE = 'participants.csv'
ASSIGNMENTS_FILE = 'assignments.csv'

# Initialize CSV file if it doesn't exist
if not os.path.exists(CSV_FILE):
    df = pd.DataFrame(columns=['Name', 'Email', 'Phone', 'Address', 'RegisteredAt'])
    df.to_csv(CSV_FILE, index=False)

# Initialize assignments file
if not os.path.exists(ASSIGNMENTS_FILE):
    df = pd.DataFrame(columns=['Giver_Name', 'Giver_Email', 'Receiver_Name', 'Receiver_Email', 'Receiver_Phone', 'Receiver_Address', 'EmailSent', 'SentAt'])
    df.to_csv(ASSIGNMENTS_FILE, index=False)

def load_participants():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE)
    return pd.DataFrame(columns=['Name', 'Email', 'Phone', 'Address', 'RegisteredAt'])

def load_assignments():
    if os.path.exists(ASSIGNMENTS_FILE):
        try:
            df = pd.read_csv(ASSIGNMENTS_FILE)
            # If file is empty or has no columns, return empty DataFrame
            if df.empty or len(df.columns) == 0:
                return pd.DataFrame(columns=['Giver_Name', 'Giver_Email', 'Receiver_Name', 'Receiver_Email', 'Receiver_Phone', 'Receiver_Address', 'EmailSent', 'SentAt'])
            return df
        except (pd.errors.EmptyDataError, Exception) as e:
            print(f"Warning: Could not load assignments file: {e}")
            return pd.DataFrame(columns=['Giver_Name', 'Giver_Email', 'Receiver_Name', 'Receiver_Email', 'Receiver_Phone', 'Receiver_Address', 'EmailSent', 'SentAt'])
    return pd.DataFrame(columns=['Giver_Name', 'Giver_Email', 'Receiver_Name', 'Receiver_Email', 'Receiver_Phone', 'Receiver_Address', 'EmailSent', 'SentAt'])

def is_duplicate(name, email):
    """Check if name or email already exists"""
    df = load_participants()
    if df.empty:
        return False, None
    
    # Check for duplicate email (case-insensitive)
    email_exists = df['Email'].str.lower().eq(email.lower()).any()
    # Check for duplicate name (case-insensitive)
    name_exists = df['Name'].str.lower().eq(name.lower()).any()
    
    if email_exists:
        return True, "email"
    if name_exists:
        return True, "name"
    return False, None

def save_participant(name, email, phone, address):
    df = load_participants()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_entry = pd.DataFrame([[name, email, phone, address, timestamp]], 
                             columns=['Name', 'Email', 'Phone', 'Address', 'RegisteredAt'])
    df = pd.concat([df, new_entry], ignore_index=True)
    df.to_csv(CSV_FILE, index=False)

def send_confirmation_email(sender_email, sender_password, participant):
    """Send confirmation email after registration"""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = participant['Email']
    msg['Subject'] = "🎄 Secret Santa Registration Confirmed!"

    body = f"""
    Ho Ho Ho, {participant['Name']}! 🎅

    You have successfully registered for Secret Santa!
    
    Your Details:
    Name: {participant['Name']}
    Email: {participant['Email']}
    Phone: {participant['Phone']}
    Address: {participant['Address']}
    
    You will receive your Secret Santa assignment via email once the admin triggers the matching process.
    
    Merry Christmas! 🎄
    - The Secret Santa Bot 🤖
    """
    msg.attach(MIMEText(body, 'plain'))

    # Use SMTP_SSL on port 465 with custom SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10, context=context)
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, participant['Email'], msg.as_string())
    server.quit()

def send_confirmation_email_safe(sender_email, sender_password, participant):
    """Wrapper for sending confirmation email with error handling (for background thread)"""
    try:
        send_confirmation_email(sender_email, sender_password, participant)
        print(f"✓ Confirmation email sent to {participant['Email']}")
    except Exception as e:
        print(f"✗ Failed to send confirmation email to {participant['Email']}: {str(e)}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name')
    email = request.form.get('email')
    phone = request.form.get('phone')
    address = request.form.get('address')
    
    if not (name and email and phone and address):
        return render_template('error.html', 
                             error_message="Missing required fields. Please fill out all fields."), 400
    
    # Check for duplicates
    is_dup, dup_type = is_duplicate(name, email)
    if is_dup:
        if dup_type == "email":
            return render_template('error.html', 
                                 error_message=f"This email ({email}) is already registered!")
        elif dup_type == "name":
            return render_template('error.html', 
                                 error_message=f"This name ({name}) is already registered!")
    
    # Save participant
    save_participant(name, email, phone, address)
    
    # Send confirmation email in background (non-blocking)
    email_user = os.environ.get('EMAIL_ADDRESS')
    email_pass = os.environ.get('EMAIL_PASSWORD')
    
    if email_user and email_pass:
        participant = {'Name': name, 'Email': email, 'Phone': phone, 'Address': address}
        # Run email sending in background thread so it doesn't block the response
        Thread(target=send_confirmation_email_safe, args=(email_user, email_pass, participant)).start()
    
    return render_template('success.html', name=name)

@app.route('/admin')
def admin():
    """Admin dashboard showing registered users and assignments"""
    participants_df = load_participants()
    assignments_df = load_assignments()
    
    participants = participants_df.to_dict('records') if not participants_df.empty else []
    assignments = assignments_df.to_dict('records') if not assignments_df.empty else []
    
    # Check for unassigned participants
    unassigned = []
    if not assignments_df.empty and not participants_df.empty:
        assigned_emails = set(assignments_df['Giver_Email'].tolist())
        all_emails = set(participants_df['Email'].tolist())
        unassigned_emails = all_emails - assigned_emails
        
        if unassigned_emails:
            unassigned = participants_df[participants_df['Email'].isin(unassigned_emails)].to_dict('records')
    
    return render_template('admin.html', 
                         participants=participants,
                         assignments=assignments,
                         unassigned=unassigned,
                         total_participants=len(participants),
                         total_assignments=len(assignments))

@app.route('/assign-match')
def assign_match():
    """
    Admin endpoint to generate Secret Santa assignments.
    Does NOT send emails - just creates the assignments for review.
    """
    df = load_participants()
    participants = df.to_dict('records')
    
    if len(participants) < 2:
        return "Need at least 2 participants!"

    # Assignment Logic: Ensure no one gets themselves
    receivers = participants[:]
    while True:
        random.shuffle(receivers)
        valid = True
        for i, p in enumerate(participants):
            if p['Email'] == receivers[i]['Email']:
                valid = False
                break
        if valid:
            break
            
    # Create assignments (WITHOUT sending emails)
    assignments_data = []

    for giver, receiver in zip(participants, receivers):
        # Record assignment without sending email
        assignments_data.append({
            'Giver_Name': giver['Name'],
            'Giver_Email': giver['Email'],
            'Receiver_Name': receiver['Name'],
            'Receiver_Email': receiver['Email'],
            'Receiver_Phone': receiver.get('Phone', ''),
            'Receiver_Address': receiver['Address'],
            'EmailSent': False,
            'SentAt': ''
        })
    
    # Save assignments to CSV
    assignments_df = pd.DataFrame(assignments_data)
    assignments_df.to_csv(ASSIGNMENTS_FILE, index=False)

    # Redirect to admin to review assignments
    return redirect(url_for('admin'))

@app.route('/regenerate-assignments')
def regenerate_assignments():
    """
    Regenerate Secret Santa assignments.
    Only works if emails have NOT been sent yet.
    """
    # Check if any emails have already been sent
    assignments_df = load_assignments()
    
    if not assignments_df.empty:
        # Check if any email was sent
        emails_sent = (assignments_df['EmailSent'] == True).any() or (assignments_df['EmailSent'] == 'True').any()
        if emails_sent:
            return "Error: Cannot regenerate assignments - emails have already been sent to participants!"
    
    # If no emails sent, regenerate assignments (same logic as assign_match)
    df = load_participants()
    participants = df.to_dict('records')
    
    if len(participants) < 2:
        return "Need at least 2 participants!"

    # Assignment Logic: Ensure no one gets themselves
    receivers = participants[:]
    while True:
        random.shuffle(receivers)
        valid = True
        for i, p in enumerate(participants):
            if p['Email'] == receivers[i]['Email']:
                valid = False
                break
        if valid:
            break
            
    # Create new assignments (WITHOUT sending emails)
    assignments_data = []

    for giver, receiver in zip(participants, receivers):
        # Record assignment without sending email
        assignments_data.append({
            'Giver_Name': giver['Name'],
            'Giver_Email': giver['Email'],
            'Receiver_Name': receiver['Name'],
            'Receiver_Email': receiver['Email'],
            'Receiver_Phone': receiver.get('Phone', ''),
            'Receiver_Address': receiver['Address'],
            'EmailSent': False,
            'SentAt': ''
        })
    
    # Save new assignments to CSV
    assignments_df = pd.DataFrame(assignments_data)
    assignments_df.to_csv(ASSIGNMENTS_FILE, index=False)

    # Redirect to admin to review new assignments
    return redirect(url_for('admin'))

@app.route('/send-assignment-emails')
def send_assignment_emails():
    """
    Send assignment emails after admin confirms.
    This reads from assignments.csv and sends emails.
    """
    assignments_df = load_assignments()
    
    if assignments_df.empty:
        return "No assignments found! Please assign matches first."
    
    email_user = os.environ.get('EMAIL_ADDRESS')
    email_pass = os.environ.get('EMAIL_PASSWORD')

    if not email_user or not email_pass:
        return "Error: EMAIL_ADDRESS or EMAIL_PASSWORD env vars not set."
    
    sent_count = 0
    failed_count = 0
    
    # Update assignments with email status
    for index, row in assignments_df.iterrows():
        if row.get('EmailSent') == True or row.get('EmailSent') == 'True':
            # Already sent
            sent_count += 1
            continue
            
        giver = {
            'Name': row['Giver_Name'],
            'Email': row['Giver_Email']
        }
        receiver = {
            'Name': row['Receiver_Name'],
            'Email': row['Receiver_Email'],
            'Phone': row.get('Receiver_Phone', 'Not provided'),
            'Address': row['Receiver_Address']
        }
        
        try:
            send_assignment_email(email_user, email_pass, giver, receiver)
            assignments_df.at[index, 'EmailSent'] = True
            assignments_df.at[index, 'SentAt'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            sent_count += 1
        except Exception as e:
            assignments_df.at[index, 'EmailSent'] = False
            print(f"✗ Failed to send assignment email to {giver['Email']}: {str(e)}")
            failed_count += 1
    
    # Save updated assignments
    assignments_df.to_csv(ASSIGNMENTS_FILE, index=False)
    
    return redirect(url_for('admin'))

def send_assignment_email(sender_email, sender_password, giver, receiver):
    """Send Secret Santa assignment email"""
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = giver['Email']
    msg['Subject'] = "🎅 Your Secret Santa Match Details! 🎁"

    body = f"""
    Ho Ho Ho, {giver['Name']}! 🎄

    You are the Secret Santa for:
    
    Name: {receiver['Name']}
    Email: {receiver['Email']}
    Phone: {receiver.get('Phone', 'Not provided')}
    Address: {receiver['Address']}

    Please ensure your gift reaches them before Christmas!
    
    Merry Christmas! 
    - The Secret Santa Bot 🤖
    """
    msg.attach(MIMEText(body, 'plain'))

    # Use SMTP_SSL on port 465 with custom SSL context
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE
    
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10, context=context)
    server.login(sender_email, sender_password)
    text = msg.as_string()
    server.sendmail(sender_email, giver['Email'], text)
    server.quit()

if __name__ == '__main__':
    # Host 0.0.0.0 allows access from other devices on the network
    app.run(host='0.0.0.0', port=5000, debug=True)
