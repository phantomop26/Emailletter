"""
Complete Gmail Reply Automation
Monitors Gmail for replies to Resend emails and processes them automatically
"""

import os
import base64
import re
import json
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import pandas as pd
from openai import OpenAI
from datetime import datetime, timedelta
import time

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def authenticate_gmail():
    """Authenticate with Gmail API"""
    creds = None
    
    # Get paths relative to project root
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    token_path = os.path.join(project_root, 'config', 'token.json')
    credentials_path = os.path.join(project_root, 'config', 'credentials.json')
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(credentials_path):
                print("❌ credentials.json not found in config/!")
                print("📋 To set up Gmail API:")
                print("1. Go to https://console.cloud.google.com/")
                print("2. Create a project and enable Gmail API")
                print("3. Create OAuth credentials and download as 'config/credentials.json'")
                print(f"4. Your Gmail Client ID: {os.getenv('GMAIL_CLIENT_ID', 'Not set in .env')}")
                return None
                
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for the next run
        with open(token_path, 'w') as token:
            token.write(creds.to_json())
    
    return build('gmail', 'v1', credentials=creds)

def extract_email_body(payload):
    """Extract email body from Gmail API payload"""
    body = ""
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
                break
            elif part['mimeType'] == 'text/html' and 'data' in part['body'] and not body:
                data = part['body']['data']
                body = base64.urlsafe_b64decode(data).decode('utf-8')
    else:
        # Simple email structure
        if payload.get('mimeType') == 'text/plain' and 'data' in payload.get('body', {}):
            data = payload['body']['data']
            body = base64.urlsafe_b64decode(data).decode('utf-8')
    
    return body

def parse_reply_with_openai(reply_text, venue_name=""):
    """Parse email reply using OpenAI to extract detailed venue booking information"""
    client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    prompt = f"""Extract detailed venue booking information from this email reply from "{venue_name}". Return ONLY valid JSON:

{{
  "reply_interest": "interested/not_interested/maybe/unclear",
  "available_dates": "specific dates/date ranges or 'not specified'",
  "venue_capacity": "maximum capacity number or 'not specified'",
  "rental_price": "hourly/daily rates or total cost or 'not specified'",
  "minimum_spend": "food/beverage minimums or 'not specified'",
  "deposit_required": "deposit amount/percentage or 'not specified'",
  "contract_link": "any booking links/forms mentioned or 'not provided'",
  "contact_person": "specific contact name or 'not specified'",
  "contact_email": "booking email address or 'not specified'",
  "contact_phone": "phone number for bookings or 'not specified'",
  "special_requirements": "setup, catering, AV requirements or 'none specified'",
  "cancellation_policy": "cancellation terms mentioned or 'not specified'",
  "preferred_contact_method": "email/phone/meeting/form/not specified",
  "next_steps": "what they want us to do next",
  "urgency": "immediate/flexible/specific_timeline/not specified",
  "confidence_score": 0.90,
  "booking_summary": "concise summary of their offer/availability"
}}

Email Reply:
{reply_text}"""
    
    try:
        response = client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[{'role': 'user', 'content': prompt}],
            max_tokens=400,
            temperature=0.1
        )
        
        result = json.loads(response.choices[0].message.content)
        return result
        
    except Exception as e:
        print(f"❌ OpenAI parsing error: {e}")
        return {
            "reply_summary": "Failed to parse with AI",
            "needs_manual_review": True,
            "error": str(e)
        }

def is_likely_reply_to_our_campaign(subject, body, sent_venues):
    """Check if this email is likely a reply to our venue outreach"""
    
    # Check subject for common reply indicators
    reply_subjects = ['re:', 'reply:', 'response', 'booking', 'event', 'venue']
    subject_lower = subject.lower()
    
    # Check if any venue names appear in the email
    for _, venue in sent_venues.iterrows():
        venue_name = venue['name'].lower()
        if venue_name in body.lower() or venue_name in subject_lower:
            return True
    
    # Check for common venue/booking keywords
    booking_keywords = ['venue', 'booking', 'event', 'space', 'rental', 'available', 'date', 'price']
    body_lower = body.lower()
    
    keyword_matches = sum(1 for keyword in booking_keywords if keyword in body_lower)
    
    return keyword_matches >= 2 or any(indicator in subject_lower for indicator in reply_subjects)

def fetch_and_process_replies():
    """Main function to fetch and process Gmail replies"""
    print("🔍 Starting Gmail reply monitoring...")
    
    # Authenticate with Gmail
    service = authenticate_gmail()
    if not service:
        return False
        
    # Load campaign results from project root
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    campaign_file = os.path.join(project_root, 'data', 'campaign_results.csv')
    
    try:
        campaign_df = pd.read_csv(campaign_file)
        sent_emails = campaign_df[campaign_df['send_status'] == 'sent'].copy()
        print(f"📧 Monitoring replies for {len(sent_emails)} sent emails")
    except FileNotFoundError:
        print("❌ No campaign results file found. Run email campaign first.")
        print(f"Expected file: {campaign_file}")
        return False
    
    # Search for recent emails in inbox
    # Look for emails from the last 3 days
    query = 'in:inbox newer_than:3d'
    
    try:
        result = service.users().messages().list(userId='me', q=query, maxResults=50).execute()
        messages = result.get('messages', [])
        
        print(f"📬 Found {len(messages)} recent emails to analyze")
        
        new_replies_count = 0
        
        for msg in messages:
            try:
                # Get full message details
                msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
                
                # Extract headers
                payload = msg_detail['payload']
                headers = payload.get('headers', [])
                
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), '')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), '')
                date_str = next((h['value'] for h in headers if h['name'] == 'Date'), '')
                
                # Extract email body
                body = extract_email_body(payload)
                
                # Skip if no body content
                if not body.strip():
                    continue
                
                # Check if this looks like a reply to our campaign
                if not is_likely_reply_to_our_campaign(subject, body, sent_emails):
                    continue
                
                print(f"🎯 Potential reply found from: {sender[:50]}...")
                
                # Try to match this reply to a specific venue
                matched_venue = None
                for idx, venue in sent_emails.iterrows():
                    venue_name = venue['name'].lower()
                    if (venue_name in body.lower() or 
                        venue_name in subject.lower() or
                        venue.get('sent_to', '').lower() in sender.lower()):
                        matched_venue = idx
                        break
                
                if matched_venue is not None:
                    # Check if we already processed this reply
                    if pd.notna(campaign_df.loc[matched_venue, 'reply_raw']) and campaign_df.loc[matched_venue, 'reply_raw']:
                        print(f"⏭️  Reply already processed for {campaign_df.loc[matched_venue, 'name']}")
                        continue
                    
                    # Parse the reply with OpenAI
                    venue_name = campaign_df.loc[matched_venue, 'name']
                    print(f"🤖 Parsing reply for {venue_name}...")
                    
                    parsed_data = parse_reply_with_openai(body, venue_name)
                    
                    # Update the campaign results
                    campaign_df.loc[matched_venue, 'reply_raw'] = body
                    campaign_df.loc[matched_venue, 'reply_timestamp'] = datetime.now().isoformat()
                    campaign_df.loc[matched_venue, 'reply_from'] = sender
                    campaign_df.loc[matched_venue, 'reply_subject'] = subject
                    
                    # Add parsed fields
                    for key, value in parsed_data.items():
                        campaign_df.loc[matched_venue, f'reply_{key}'] = str(value)
                    
                    new_replies_count += 1
                    print(f"✅ Processed reply for {venue_name}")
                    
                else:
                    print(f"❓ Could not match reply to specific venue: {subject[:50]}...")
                    
            except Exception as e:
                print(f"❌ Error processing message: {e}")
                continue
        
        # Save updated results
        if new_replies_count > 0:
            campaign_df.to_csv(campaign_file, index=False)
            print(f"💾 Saved {new_replies_count} new replies to results file")
            
            # Also save to a separate replies file
            replies_file = os.path.join(project_root, 'data', 'campaign_results_with_replies.csv')
            campaign_df.to_csv(replies_file, index=False)
            print(f"📊 Updated replies file: {replies_file}")
        else:
            print("📭 No new replies found")
        
        return True
        
    except Exception as e:
        print(f"❌ Gmail API error: {e}")
        return False

def monitor_replies_continuously(check_interval_minutes=10):
    """Run reply monitoring in a loop"""
    print(f"🔄 Starting continuous reply monitoring (checking every {check_interval_minutes} minutes)")
    
    while True:
        try:
            fetch_and_process_replies()
            print(f"⏰ Next check in {check_interval_minutes} minutes...")
            time.sleep(check_interval_minutes * 60)
        except KeyboardInterrupt:
            print("🛑 Monitoring stopped by user")
            break
        except Exception as e:
            print(f"❌ Monitoring error: {e}")
            print(f"⏰ Retrying in {check_interval_minutes} minutes...")
            time.sleep(check_interval_minutes * 60)

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--monitor':
        # Run continuous monitoring
        monitor_replies_continuously()
    else:
        # Run once
        success = fetch_and_process_replies()
        if success:
            print("✅ Reply processing completed successfully")
        else:
            print("❌ Reply processing failed")
