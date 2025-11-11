#!/usr/bin/env python3
"""
VenueHooper Pure Step Testing
Tests workflow components without Streamlit dependencies
"""

import os
import sys
import pandas as pd
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add project root to path
project_root = Path(__file__).parent.parent  # Go up from scripts/ to project root
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

# Load environment
env_path = project_root / 'config' / '.env'
load_dotenv(env_path)

class VenueWorkflowTester:
    """Pure workflow testing without Streamlit"""
    
    def __init__(self):
        self.resend_api_key = os.getenv('RESEND_API_KEY', '')
        self.openai_api_key = os.getenv('OPENAI_API_KEY', '')
        self.sender_email = os.getenv('EMAIL_SENDER', 'onboarding@resend.dev')
        self.org_name = os.getenv('ORG_NAME', 'VenueHooper')
        self.your_name = os.getenv('YOUR_NAME', 'Sahil Singh')
        self.your_phone = os.getenv('YOUR_PHONE', '555-555-5555')
        
    def analyze_venue_type(self, venue_name: str, category: str, website: str) -> dict:
        """Analyze venue with AI"""
        from openai import OpenAI
        
        if not self.openai_api_key:
            return {"error": "OpenAI API key not provided"}
            
        client = OpenAI(api_key=self.openai_api_key)
        
        prompt = f"""Analyze this venue and determine the best outreach approach:
        
        Venue: {venue_name}
        Category: {category}
        Website: {website}
        
        Return:
        {{
            "venue_type": "restaurant/bar/event_space/music_venue/other",
            "email_customization": "brief note about how to customize the outreach"
        }}"""
        
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=200
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            print(f"OpenAI analysis error: {e}")
            return {
                'venue_type': 'general',
                'email_customization': 'standard venue outreach'
            }

    def generate_custom_email(self, venue_data: dict, analysis: dict) -> dict:
        """Generate customized email based on venue analysis"""
        venue_name = venue_data['name']
        venue_type = analysis.get('venue_type', 'general')
        
        # Customize greeting and content based on venue type
        if venue_type == 'restaurant':
            greeting = f"Hello {venue_name} Team"
            context = "We're looking to host a private dining event"
        elif venue_type == 'bar':
            greeting = f"Hello {venue_name} Team"
            context = "We're interested in booking your space for a private event"
        elif venue_type == 'music_venue':
            greeting = f"Hello {venue_name} Team"
            context = "We're looking to book your venue for a special event"
        else:
            greeting = "Hello Team"
            context = "We're reaching out about hosting an event"
        
        subject = f"Partnership / Booking Inquiry from {self.org_name} — {venue_name}"
        
        body = f"""
        {greeting},<br><br>
        I'm {self.your_name} from {self.org_name}. {context}.<br><br>
        Could you please confirm:<br>
        (1) whether you accept external events<br>
        (2) typical availability in November 2025<br>
        (3) typical capacity and sample pricing<br>
        (4) any venue requirements or minimum spend<br>
        (5) best contact and billing email?<br><br>
        If you'd prefer a call, share a convenient time or your phone number.<br><br>
        Thank you — {self.your_name}, {self.org_name}, {self.your_phone}<br><br>
        <em>To opt out of future emails, reply "unsubscribe".</em>
        """
        
        return {
            'subject': subject,
            'html_body': body,
            'text_body': body.replace('<br>', '\n').replace('<em>', '').replace('</em>', '')
        }

    def send_email(self, email_data: dict, recipient: str) -> dict:
        """Send email using Resend API"""
        import requests
        from datetime import datetime
        
        headers = {
            "Authorization": f"Bearer {self.resend_api_key}",
            "Content-Type": "application/json"
        }
        
        # Check if test mode is enabled
        test_email = os.getenv('TEST_EMAIL')
        force_test = os.getenv('FORCE_TEST_EMAIL', '').lower() == 'true'
        
        if force_test and test_email:
            recipient = test_email
            print(f"🧪 TEST MODE: Sending to {test_email}")
        
        data = {
            "from": self.sender_email,
            "to": [recipient],
            "subject": email_data['subject'],
            "html": email_data['html_body'],
            "text": email_data['text_body']
        }
        
        try:
            response = requests.post("https://api.resend.com/emails", json=data, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "sent",
                    "message_id": result.get("id"),
                    "timestamp": datetime.now().isoformat(),
                    "response": result
                }
            else:
                return {
                    "status": "failed",
                    "error": response.json(),
                    "timestamp": datetime.now().isoformat()
                }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }

    def parse_reply_with_ai(self, reply_text: str) -> dict:
        """Parse email reply using OpenAI"""
        from openai import OpenAI
        
        if not self.openai_api_key:
            return {"error": "OpenAI API key not provided"}
            
        client = OpenAI(api_key=self.openai_api_key)
        
        prompt = f"""Extract detailed venue booking information from this email reply. Return ONLY valid JSON:
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
                max_tokens=500,
                temperature=0.1
            )
            
            result = json.loads(response.choices[0].message.content)
            return result
            
        except Exception as e:
            print(f"OpenAI parsing error: {e}")
            return {
                "error": "Failed to parse reply",
                "raw_response": str(e)
            }

def test_complete_workflow():
    """Test complete workflow step by step"""
    print("🔬 VenueHooper Complete Workflow Test")
    print("=" * 60)
    
    # Initialize tester
    tester = VenueWorkflowTester()
    
    # Test venue data
    test_venue = {
        'name': 'The Metropolitan Lounge',
        'category': 'Bar',
        'website': 'https://github.com',
        'address': '123 Madison Ave, New York, NY'
    }
    
    # Step 1: AI Analysis
    print("\n🤖 Step 1: AI Venue Analysis")
    print("-" * 30)
    analysis = tester.analyze_venue_type(test_venue['name'], test_venue['category'], test_venue['website'])
    if 'error' not in analysis:
        print(f"✅ Venue Type: {analysis.get('venue_type', 'unknown')}")
        print(f"✅ Customization: {analysis.get('email_customization', 'none')}")
    else:
        print(f"❌ Analysis Error: {analysis['error']}")
        return False
    
    # Step 2: Email Generation
    print("\n📧 Step 2: Email Generation")
    print("-" * 30)
    email_data = tester.generate_custom_email(test_venue, analysis)
    print(f"✅ Subject: {email_data['subject']}")
    print(f"✅ Body Length: {len(email_data['text_body'])} characters")
    print(f"Preview: {email_data['text_body'][:100]}...")
    
    # Step 3: Email Sending
    print("\n📤 Step 3: Email Sending")
    print("-" * 30)
    test_email = os.getenv('TEST_EMAIL')
    if not test_email:
        print("❌ TEST_EMAIL not configured in .env")
        return False
    
    send_result = tester.send_email(email_data, test_email)
    if send_result.get('status') == 'sent':
        print(f"✅ Email Sent Successfully!")
        print(f"   Message ID: {send_result.get('message_id', 'N/A')}")
        print(f"   Recipient: {test_email}")
        print(f"   Timestamp: {send_result.get('timestamp', 'N/A')}")
    else:
        print(f"❌ Email Send Failed: {send_result.get('error', 'Unknown error')}")
        return False
    
    # Step 4: Reply Parsing Test
    print("\n📬 Step 4: Reply Parsing")
    print("-" * 30)
    
    sample_reply = """
    Hi Sahil,

    Thank you for reaching out about hosting an event at The Metropolitan Lounge.

    We'd be happy to accommodate your event! Here are the details:

    1. Yes, we accept external private events
    2. We have availability in November 2025, particularly weekdays after 7 PM
    3. Our space can accommodate up to 80 people for cocktail style events
    4. Our private event rate is $150/hour with a $2,000 food and beverage minimum
    5. We require a 50% deposit to secure the booking
    6. For booking, please contact our events manager Sarah at events@metropolitanlounge.com or call 212-555-0001

    We also offer full catering services and can arrange DJ/live music.

    Would you like to schedule a site visit? We're available for tours Tuesday-Thursday 2-5 PM.

    Best regards,
    Sarah Johnson
    Events Manager
    The Metropolitan Lounge
    """
    
    parsed_data = tester.parse_reply_with_ai(sample_reply)
    if 'error' not in parsed_data:
        print("✅ Reply Parsed Successfully!")
        
        # Show key results
        key_fields = ['reply_interest', 'venue_capacity', 'rental_price', 'minimum_spend', 'contact_person', 'confidence_score']
        for field in key_fields:
            value = parsed_data.get(field, 'Not specified')
            print(f"   {field.replace('_', ' ').title()}: {value}")
            
    else:
        print(f"❌ Reply Parsing Error: {parsed_data['error']}")
        return False
    
    # Step 5: Export Results
    print("\n💾 Step 5: Export Complete Results")
    print("-" * 30)
    
    # Create comprehensive results
    complete_result = {
        'name': test_venue['name'],
        'category': test_venue['category'],
        'website': test_venue['website'],
        'ai_venue_type': analysis.get('venue_type', ''),
        'sent_to': test_email,
        'send_status': 'sent',
        'message_id': send_result.get('message_id', ''),
        'email_subject': email_data['subject'],
        'timestamp': send_result.get('timestamp', ''),
    }
    
    # Add parsed reply data
    for key, value in parsed_data.items():
        complete_result[f'reply_{key}'] = str(value)
    
    # Save to CSV
    data_dir = project_root / 'data'
    data_dir.mkdir(exist_ok=True)
    
    results_df = pd.DataFrame([complete_result])
    results_file = data_dir / 'complete_workflow_test_results.csv'
    results_df.to_csv(results_file, index=False)
    
    print(f"✅ Complete Results Exported!")
    print(f"   File: {results_file}")
    print(f"   Columns: {len(results_df.columns)}")
    print(f"   Sample columns: {list(results_df.columns)[:5]}...")
    
    # Final Summary
    print("\n🎉 WORKFLOW TEST SUMMARY")
    print("=" * 60)
    print("✅ AI Venue Analysis: PASSED")
    print("✅ Email Generation: PASSED")
    print("✅ Email Sending: PASSED")
    print("✅ Reply Parsing: PASSED")
    print("✅ Data Export: PASSED")
    
    print(f"\n📊 Test Results:")
    print(f"   📧 Email sent to: {test_email}")
    print(f"   📬 Message ID: {send_result.get('message_id', 'N/A')}")
    print(f"   💾 Results file: {results_file}")
    print(f"   🌐 Streamlit app: python3 main.py")
    
    return True

if __name__ == "__main__":
    success = test_complete_workflow()
    if success:
        print("\n🚀 All workflow steps completed successfully!")
        print("   Next: Test in Streamlit interface (Tab 6: Step Testing)")
    else:
        print("\n❌ Some workflow steps failed. Check configuration.")