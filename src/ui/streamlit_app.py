"""
VenueHooper - Complete Email Campaign Workflow
A comprehensive system for venue outreach automation
"""

import streamlit as st
import pandas as pd
import asyncio
import re
import requests
import time
import json
import os
import sys
from datetime import datetime
from playwright.async_api import async_playwright
from openai import OpenAI
from typing import List

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from src.utils.email_scraper_utils import scrape_emails_hybrid
    from src.automation import gmail_reply_automation
except ImportError as e:
    print(f"Import warning: {e}")
    # Fallback imports if needed

# Configuration
EMAIL_REGEX = r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+'

class VenueHooperWorkflow:
    def __init__(self):
        # Load environment variables (local development)
        from dotenv import load_dotenv
        env_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', '.env')
        load_dotenv(env_path)
        
        # Try Streamlit secrets first (cloud deployment), then environment variables
        def get_config(key, default=''):
            try:
                return st.secrets.get(key, os.getenv(key, default))
            except:
                return os.getenv(key, default)
        
        self.resend_api_key = st.session_state.get('resend_api_key', get_config('RESEND_API_KEY'))
        self.openai_api_key = st.session_state.get('openai_api_key', get_config('OPENAI_API_KEY'))
        self.sender_email = st.session_state.get('sender_email', get_config('EMAIL_SENDER', 'onboarding@resend.dev'))
        self.org_name = st.session_state.get('org_name', get_config('ORG_NAME', 'VenueHooper'))
        self.your_name = st.session_state.get('your_name', get_config('YOUR_NAME', 'Sahil Singh'))
        self.your_phone = st.session_state.get('your_phone', get_config('YOUR_PHONE', '555-555-5555'))
    
    def clean_dataframe(self, df):
        """Clean dataframe by handling NaN values and data types"""
        # Replace NaN values with empty strings for text columns
        text_columns = ['name', 'website', 'category', 'address', 'phone']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].fillna('').astype(str)
        
        # Remove rows where name is empty (required field)
        df = df[df['name'].str.strip() != '']
        
        return df
        
    async def scrape_email_from_website(self, url: str) -> List[str]:
        """Scrape emails from a website using improved hybrid method"""
        try:
            return await scrape_emails_hybrid(url)
        except Exception as e:
            st.error(f"Error scraping {url}: {e}")
            return []
    
    def analyze_venue_type(self, venue_name: str, category: str, website: str) -> dict:
        """Use OpenAI to analyze venue type and generate appropriate email"""
        if not self.openai_api_key:
            return {
                'venue_type': 'general',
                'email_customization': 'standard venue outreach'
            }
            
        client = OpenAI(api_key=self.openai_api_key)
        
        prompt = f"""Analyze this venue and return JSON:
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
            st.error(f"OpenAI analysis error: {e}")
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
        headers = {
            "Authorization": f"Bearer {self.resend_api_key}",
            "Content-Type": "application/json"
        }
        
        # Check if test mode is enabled
        def get_config(key, default=''):
            try:
                return st.secrets.get(key, os.getenv(key, default))
            except:
                return os.getenv(key, default)
        
        test_email = get_config('TEST_EMAIL')
        force_test = get_config('FORCE_TEST_EMAIL', '').lower() == 'true'
        
        if force_test and test_email:
            recipient = test_email
            st.warning(f"🧪 TEST MODE: Sending to {test_email} instead of original recipient")
        
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
        
        Email reply:
        {reply_text}"""
        
        try:
            response = client.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=[{'role': 'user', 'content': prompt}],
                max_tokens=500
            )
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            return {
                "reply_parsed_notes": f"Parse error: {e}",
                "needs_manual_review": True,
                "error": str(e)
            }

# Streamlit UI
def main():
    st.set_page_config(
        page_title="VenueHooper - Email Campaign Manager",
        page_icon="🏢",
        layout="wide"
    )
    
    st.title("🏢 VenueHooper - Venue Outreach Automation")
    st.markdown("Complete workflow for venue email campaigns")
    
    # Initialize workflow
    workflow = VenueHooperWorkflow()
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        st.session_state['resend_api_key'] = st.text_input(
            "Resend API Key",
            value=st.session_state.get('resend_api_key', ''),
            type="password",
            help="Your Resend API key for sending emails"
        )
        
        st.session_state['openai_api_key'] = st.text_input(
            "OpenAI API Key",
            value=st.session_state.get('openai_api_key', ''),
            type="password",
            help="OpenAI API key for AI analysis and parsing"
        )
        
        st.session_state['sender_email'] = st.text_input(
            "Sender Email",
            value=st.session_state.get('sender_email', 'onboarding@resend.dev'),
            help="Verified sender email address"
        )
        
        st.session_state['org_name'] = st.text_input(
            "Organization Name",
            value=st.session_state.get('org_name', 'VenueHooper')
        )
        
        st.session_state['your_name'] = st.text_input(
            "Your Name",
            value=st.session_state.get('your_name', 'Funda')
        )
        
        st.session_state['your_phone'] = st.text_input(
            "Your Phone",
            value=st.session_state.get('your_phone', '555-555-5555')
        )
    
    # Main workflow tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📁 Upload CSV", 
        "🔍 Scrape Emails", 
        "📧 Send Campaigns", 
        "📬 Manage Replies", 
        "📊 Results",
        "🧪 Step Testing"
    ])
    
    with tab1:
        st.header("📁 Upload Venue CSV")
        st.markdown("Upload your CSV file with venue information")
        
        uploaded_file = st.file_uploader(
            "Choose CSV file",
            type=['csv'],
            help="CSV should contain: name, category, address, phone_number, website, google_maps_link"
        )
        
        if uploaded_file:
            try:
                df = pd.read_csv(uploaded_file)
                
                # Clean the dataframe
                df = workflow.clean_dataframe(df)
                
                if len(df) == 0:
                    st.error("No valid venues found after cleaning data")
                else:
                    st.success(f"✅ Loaded {len(df)} venues")
                    st.dataframe(df.head())
                    
                    # Show data quality info
                    valid_websites = len(df[df['website'].str.strip() != ''])
                    st.info(f"📊 Data Quality: {valid_websites}/{len(df)} venues have websites")
                
                # Save uploaded data
                data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
                os.makedirs(data_dir, exist_ok=True)
                df.to_csv(os.path.join(data_dir, 'venues_input.csv'), index=False)
                st.session_state['venues_df'] = df
                
            except Exception as e:
                st.error(f"Error reading CSV: {e}")
    
    with tab2:
        st.header("🔍 Email Scraping")
        
        if 'venues_df' in st.session_state:
            df = st.session_state['venues_df']
            
            if st.button("🚀 Start Scraping Emails", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                results = []
                
                async def scrape_all():
                    for idx, row in df.iterrows():
                        venue_name = row['name']
                        website = row.get('website', '')
                        
                        # Handle NaN/empty website values
                        if pd.notna(website) and website and str(website).strip():
                            status_text.text(f"Scraping {venue_name}...")
                            
                            # Scrape emails
                            emails = await workflow.scrape_email_from_website(website)
                            
                            # Analyze venue type
                            analysis = workflow.analyze_venue_type(
                                venue_name, 
                                row.get('category', ''), 
                                website
                            )
                            
                            results.append({
                                **row.to_dict(),
                                'scraped_emails': '|'.join(emails) if emails else '',
                                'primary_email': emails[0] if emails else '',
                                'venue_analysis': json.dumps(analysis),
                                'scrape_timestamp': datetime.now().isoformat(),
                                'emails_found': len(emails)
                            })
                        else:
                            results.append({
                                **row.to_dict(),
                                'scraped_emails': '',
                                'primary_email': '',
                                'venue_analysis': '{}',
                                'scrape_timestamp': datetime.now().isoformat(),
                                'emails_found': 0
                            })
                        
                        progress_bar.progress((idx + 1) / len(df))
                
                # Run async scraping
                asyncio.run(scrape_all())
                
                # Save results
                results_df = pd.DataFrame(results)
                data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
                os.makedirs(data_dir, exist_ok=True)
                results_df.to_csv(os.path.join(data_dir, 'venues_scraped.csv'), index=False)
                st.session_state['scraped_df'] = results_df
                
                st.success(f"✅ Scraping complete! Found emails for {len([r for r in results if r['emails_found'] > 0])} venues")
                st.dataframe(results_df[['name', 'emails_found', 'primary_email']])
        else:
            st.warning("Please upload a CSV file first")
    
    with tab3:
        st.header("📧 Email Campaign")
        
        if 'scraped_df' in st.session_state:
            scraped_df = st.session_state['scraped_df']
            venues_with_emails = scraped_df[scraped_df['emails_found'] > 0]
            
            st.info(f"📊 Found {len(venues_with_emails)} venues with contact emails")
            
            # Business Selection Section
            st.subheader("🎯 Select Businesses to Email")
            
            if len(venues_with_emails) > 0:
                # Show venue details with selection
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    st.markdown("**Select venues to include in your email campaign:**")
                
                with col2:
                    if st.button("Select All"):
                        for i in range(len(venues_with_emails)):
                            st.session_state[f"venue_select_{i}"] = True
                    if st.button("Clear All"):
                        for i in range(len(venues_with_emails)):
                            st.session_state[f"venue_select_{i}"] = False
                
                # Venue selection with enhanced display
                selected_venues = []
                
                for idx, (_, venue) in enumerate(venues_with_emails.iterrows()):
                    col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
                    
                    with col1:
                        selected = st.checkbox(
                            "Select", 
                            key=f"venue_select_{idx}",
                            value=st.session_state.get(f"venue_select_{idx}", False)
                        )
                    
                    with col2:
                        st.write(f"**{venue['name']}**")
                        # Parse venue analysis for display
                        try:
                            analysis = json.loads(venue.get('venue_analysis', '{}'))
                            venue_type = analysis.get('venue_type', 'Unknown')
                            st.caption(f"Type: {venue_type.title()}")
                        except:
                            st.caption("Type: Unknown")
                    
                    with col3:
                        st.write(f"📧 {venue['primary_email']}")
                        if venue.get('website'):
                            st.caption(f"🌐 {venue['website'][:30]}...")
                    
                    with col4:
                        # Show AI analysis preview
                        try:
                            analysis = json.loads(venue.get('venue_analysis', '{}'))
                            customization = analysis.get('email_customization', 'Standard outreach')
                            st.caption(f"📝 {customization[:40]}{'...' if len(customization) > 40 else ''}")
                        except:
                            st.caption("📝 Standard outreach")
                    
                    if selected:
                        selected_venues.append(venue)
                
                st.divider()
                
                # Show selected venues summary
                if selected_venues:
                    st.success(f"✅ Selected {len(selected_venues)} venues for email campaign")
                    
                    # Group by venue type for summary
                    venue_types = {}
                    for venue in selected_venues:
                        try:
                            analysis = json.loads(venue.get('venue_analysis', '{}'))
                            v_type = analysis.get('venue_type', 'unknown')
                            venue_types[v_type] = venue_types.get(v_type, 0) + 1
                        except:
                            venue_types['unknown'] = venue_types.get('unknown', 0) + 1
                    
                    st.write("**Selected venue types:**")
                    for v_type, count in venue_types.items():
                        st.write(f"- {v_type.title()}: {count} venues")
                
                else:
                    st.warning("Please select at least one venue to send emails to")
            
                # Email preview section
                if selected_venues:
                    st.subheader("📝 Email Preview")
                    
                    # Preview selector
                    preview_venue = st.selectbox(
                        "Preview email for:",
                        options=range(len(selected_venues)),
                        format_func=lambda x: selected_venues[x]['name']
                    )
                    
                    if preview_venue is not None:
                        venue_data = selected_venues[preview_venue]
                        analysis = json.loads(venue_data.get('venue_analysis', '{}'))
                        
                        email_content = workflow.generate_custom_email(venue_data, analysis)
                        
                        col1, col2 = st.columns([2, 1])
                        
                        with col1:
                            st.markdown("**Subject:**")
                            st.code(email_content['subject'])
                            
                            st.markdown("**Email Body:**")
                            st.markdown(email_content['html_body'], unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown("**Venue Details:**")
                            st.write(f"**Name:** {venue_data['name']}")
                            st.write(f"**Type:** {analysis.get('venue_type', 'Unknown').title()}")
                            st.write(f"**Email:** {venue_data['primary_email']}")
                            if venue_data.get('website'):
                                st.write(f"**Website:** {venue_data['website']}")
                
                # Send emails section
                st.subheader("🚀 Send Email Campaign")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    test_mode = st.checkbox("🧪 Test Mode (send to test email only)", value=True)
                    
                    if test_mode:
                        test_email = st.text_input("Test Email Address", value="11k34sahilkumarsingh@gmail.com")
                
                with col2:
                    if selected_venues:
                        st.metric("Emails to Send", len(selected_venues))
                        estimated_time = len(selected_venues) * 0.5 / 60  # 0.5 seconds per email
                        st.metric("Estimated Time", f"{estimated_time:.1f} min")
                
                if selected_venues and st.button("📤 Send Email Campaign", type="primary"):
                    if not workflow.resend_api_key:
                        st.error("Please configure Resend API key in sidebar")
                        return
                    
                    if test_mode and not test_email:
                        st.error("Please enter a test email address")
                        return
                    
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    campaign_results = []
                    
                    for idx, venue_data in enumerate(selected_venues):
                        venue_name = venue_data['name']
                        
                        status_text.text(f"Sending to {venue_name}... ({idx+1}/{len(selected_venues)})")
                        
                        # Generate personalized email
                        analysis = json.loads(venue_data.get('venue_analysis', '{}'))
                        email_content = workflow.generate_custom_email(venue_data, analysis)
                        
                        # Send email
                        recipient = test_email if test_mode else venue_data['primary_email']
                        send_result = workflow.send_email(email_content, recipient)
                        
                        campaign_results.append({
                            **venue_data,
                            'sent_to': recipient,
                            'send_status': send_result.get('status'),
                            'message_id': send_result.get('message_id', ''),
                            'send_timestamp': send_result.get('timestamp'),
                            'send_response': json.dumps(send_result),
                            'email_subject': email_content['subject']
                        })
                        
                        progress_bar.progress((idx + 1) / len(selected_venues))
                        time.sleep(0.5)  # Rate limiting
                    
                    # Save campaign results
                    campaign_df = pd.DataFrame(campaign_results)
                    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
                    os.makedirs(data_dir, exist_ok=True)
                    campaign_df.to_csv(os.path.join(data_dir, 'campaign_results.csv'), index=False)
                    st.session_state['campaign_df'] = campaign_df
                    
                    successful_sends = len([r for r in campaign_results if r['send_status'] == 'sent'])
                    st.success(f"✅ Campaign complete! {successful_sends}/{len(campaign_results)} emails sent successfully")
                    
                    # Show results summary
                    st.subheader("📊 Campaign Results")
                    
                    results_col1, results_col2, results_col3 = st.columns(3)
                    
                    with results_col1:
                        st.metric("Total Sent", successful_sends)
                    
                    with results_col2:
                        failed_sends = len(campaign_results) - successful_sends
                        st.metric("Failed", failed_sends)
                    
                    with results_col3:
                        success_rate = (successful_sends / len(campaign_results)) * 100 if campaign_results else 0
                        st.metric("Success Rate", f"{success_rate:.1f}%")
                    
                    # Detailed results table
                    st.dataframe(campaign_df[['name', 'sent_to', 'send_status', 'message_id', 'email_subject']])
                
                elif not selected_venues:
                    st.info("👆 Please select venues above to send emails")
            
            else:
                st.info("No venues with emails found. Please run email scraping first.")
        else:
            st.warning("Please scrape emails first")
    
    with tab4:
        st.header("📬 Reply Management")
        
        if 'campaign_df' in st.session_state:
            campaign_df = st.session_state['campaign_df']
            
            # Gmail API Integration Section
            st.subheader("🤖 Automatic Reply Fetching")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔍 Check Gmail for New Replies", type="primary"):
                    with st.spinner("Checking Gmail for replies..."):
                        try:
                            # Import and run Gmail automation
                            from src.automation import gmail_reply_automation
                            success = gmail_reply_automation.fetch_and_process_replies()
                            
                            if success:
                                st.success("✅ Gmail check completed! Reloading results...")
                                # Reload updated results
                                try:
                                    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
                                    updated_df = pd.read_csv(os.path.join(data_dir, 'venues_email_send_results.csv'))
                                    st.session_state['campaign_df'] = updated_df
                                    st.rerun()
                                except:
                                    pass
                            else:
                                st.error("❌ Gmail check failed. Check credentials.")
                        except ImportError:
                            st.error("❌ Gmail automation not available. Install google-api-python-client first.")
                        except Exception as e:
                            st.error(f"❌ Error: {str(e)}")
            
            with col2:
                st.info("📋 **Gmail Setup Required:**\n1. Create Google Cloud project\n2. Enable Gmail API\n3. Download credentials.json\n4. Run authentication")
            
            # Show reply status
            if 'reply_raw' in campaign_df.columns:
                replies_count = len(campaign_df[campaign_df['reply_raw'].notna() & (campaign_df['reply_raw'] != '')])
                st.metric("Replies Received", replies_count)
                
                if replies_count > 0:
                    st.subheader("📨 Recent Replies")
                    replied_venues = campaign_df[campaign_df['reply_raw'].notna() & (campaign_df['reply_raw'] != '')]
                    
                    for _, venue in replied_venues.iterrows():
                        with st.expander(f"Reply from {venue['name']}"):
                            st.write(f"**From:** {venue.get('reply_from', 'Unknown')}")
                            st.write(f"**Subject:** {venue.get('reply_subject', 'No subject')}")
                            st.write(f"**Interest:** {venue.get('reply_reply_interest', 'Not parsed')}")
                            st.text_area("Full Reply:", venue['reply_raw'], height=150, disabled=True)
            
            st.divider()
            
            st.subheader("📥 Manual Reply Entry")
            st.markdown("*Manually add replies if Gmail API is not set up*")
            
            # Select venue for reply
            venue_names = campaign_df['name'].tolist()
            selected_venue = st.selectbox("Select Venue", venue_names)
            
            # Reply input
            reply_text = st.text_area(
                "Email Reply Content",
                height=200,
                placeholder="Paste the full email reply here..."
            )
            
            if st.button("🤖 Parse Reply with AI"):
                if reply_text and workflow.openai_api_key:
                    with st.spinner("Parsing reply with AI..."):
                        parsed_data = workflow.parse_reply_with_ai(reply_text)
                    
                    st.success("✅ Reply parsed successfully!")
                    st.json(parsed_data)
                    
                    # Update campaign data
                    mask = campaign_df['name'] == selected_venue
                    campaign_df.loc[mask, 'reply_raw'] = reply_text
                    campaign_df.loc[mask, 'reply_timestamp'] = datetime.now().isoformat()
                    
                    # Add parsed fields
                    for key, value in parsed_data.items():
                        campaign_df.loc[mask, f'reply_{key}'] = str(value)
                    
                    # Save updated results
                    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
                    os.makedirs(data_dir, exist_ok=True)
                    campaign_df.to_csv(os.path.join(data_dir, 'campaign_results_with_replies.csv'), index=False)
                    st.session_state['campaign_df'] = campaign_df
                    
                else:
                    st.error("Please enter reply text and configure OpenAI API key")
        else:
            st.warning("Please run email campaign first")
    
    with tab5:
        st.header("📊 Campaign Results")
        
        if 'campaign_df' in st.session_state:
            df = st.session_state['campaign_df']
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Venues", len(df))
            
            with col2:
                sent_count = len(df[df['send_status'] == 'sent'])
                st.metric("Emails Sent", sent_count)
            
            with col3:
                replied_count = len(df[df.get('reply_raw', '').notna() & (df.get('reply_raw', '') != '')])
                st.metric("Replies Received", replied_count)
            
            with col4:
                if replied_count > 0:
                    response_rate = f"{(replied_count/sent_count)*100:.1f}%"
                else:
                    response_rate = "0%"
                st.metric("Response Rate", response_rate)
            
            # Detailed results table
            st.subheader("📋 Detailed Results")
            
            # Filter columns for display
            display_columns = ['name', 'category', 'send_status', 'sent_to']
            
            # Add reply columns if they exist
            reply_columns = [col for col in df.columns if col.startswith('reply_')]
            if reply_columns:
                display_columns.extend(['reply_interest', 'reply_available_dates', 'reply_price_estimate'])
            
            # Filter existing columns
            available_columns = [col for col in display_columns if col in df.columns]
            
            st.dataframe(df[available_columns])
            
            # Download results
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download Complete Results",
                data=csv,
                file_name=f"venue_campaign_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
        else:
            st.info("No campaign results available yet. Run the workflow first!")
    
    with tab6:
        st.header("🧪 Step-by-Step Testing")
        st.markdown("Test each component of the workflow individually")
        
        # Create test sections
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🤖 AI Analysis Test")
            
            test_venue_name = st.text_input("Venue Name", "The Metropolitan Lounge", key="test_venue_name")
            test_venue_category = st.selectbox("Category", ["Bar", "Restaurant", "Event Space", "Music Venue"], key="test_category")
            test_venue_website = st.text_input("Website", "https://github.com", key="test_website")
            
            if st.button("🔍 Test AI Analysis", key="test_ai"):
                if test_venue_name and test_venue_category:
                    with st.spinner("Analyzing venue with AI..."):
                        try:
                            analysis = workflow.analyze_venue_type(test_venue_name, test_venue_category, test_venue_website)
                            st.success("✅ AI Analysis Complete!")
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.metric("Venue Type", analysis.get('venue_type', 'unknown'))
                            with col_b:
                                st.metric("Confidence", "High" if analysis else "Low")
                            
                            st.json(analysis)
                            st.session_state['test_analysis'] = analysis
                            
                        except Exception as e:
                            st.error(f"❌ AI Analysis Error: {e}")
                else:
                    st.warning("Please fill in venue name and category")
            
            st.subheader("📧 Email Generation Test")
            
            if st.button("📝 Generate Test Email", key="test_email_gen"):
                if 'test_analysis' in st.session_state:
                    try:
                        test_venue_data = {
                            'name': test_venue_name,
                            'category': test_venue_category,
                            'website': test_venue_website,
                            'address': '123 Test Street, Test City'
                        }
                        
                        email_data = workflow.generate_custom_email(test_venue_data, st.session_state['test_analysis'])
                        st.success("✅ Email Generated!")
                        
                        st.markdown("**Subject:**")
                        st.code(email_data['subject'])
                        
                        st.markdown("**Email Body:**")
                        st.text_area("Preview", email_data['text_body'], height=200, key="email_preview")
                        
                        st.session_state['test_email_data'] = email_data
                        
                    except Exception as e:
                        st.error(f"❌ Email Generation Error: {e}")
                else:
                    st.warning("Run AI Analysis first to generate personalized email")
            
            st.subheader("📤 Email Sending Test")
            
            test_recipient = st.text_input("Test Email", os.getenv('TEST_EMAIL', ''), key="test_recipient")
            
            if st.button("📨 Send Test Email", key="test_send"):
                if 'test_email_data' in st.session_state and test_recipient:
                    try:
                        with st.spinner("Sending test email..."):
                            result = workflow.send_email(st.session_state['test_email_data'], test_recipient)
                            
                        if result.get('status') == 'sent':
                            st.success("✅ Email Sent Successfully!")
                            st.info(f"📬 Message ID: {result.get('message_id', 'N/A')}")
                            st.info(f"🕒 Timestamp: {result.get('timestamp', 'N/A')}")
                            
                            # Store result for further testing
                            st.session_state['test_send_result'] = result
                            
                        else:
                            st.error("❌ Email Send Failed")
                            st.error(f"Error: {result.get('error', 'Unknown error')}")
                            
                    except Exception as e:
                        st.error(f"❌ Email Sending Error: {e}")
                else:
                    st.warning("Generate email first and provide recipient address")
        
        with col2:
            st.subheader("📬 Reply Parsing Test")
            
            sample_reply = st.text_area(
                "Sample Venue Reply", 
                """Hi Sahil,

Thank you for reaching out about hosting an event at The Metropolitan Lounge.

We'd be happy to accommodate your event! Here are the details:

1. Yes, we accept external private events
2. We have availability in November 2025, particularly weekdays after 7 PM  
3. Our space can accommodate up to 80 people for cocktail style events
4. Our private event rate is $150/hour with a $2,000 food and beverage minimum
5. We require a 50% deposit to secure the booking
6. For booking, please contact our events manager Sarah at events@metropolitanlounge.com

Best regards,
Sarah Johnson
Events Manager""",
                height=300,
                key="sample_reply"
            )
            
            if st.button("🤖 Parse Reply with AI", key="test_parse"):
                if sample_reply.strip():
                    try:
                        with st.spinner("Parsing reply with AI..."):
                            parsed_data = workflow.parse_reply_with_ai(sample_reply)
                        
                        st.success("✅ Reply Parsed Successfully!")
                        
                        # Display key parsed information
                        key_fields = [
                            ('reply_interest', 'Interest Level'),
                            ('available_dates', 'Availability'),
                            ('venue_capacity', 'Capacity'),
                            ('rental_price', 'Pricing'),
                            ('minimum_spend', 'Minimum Spend'),
                            ('contact_person', 'Contact Person'),
                            ('contact_email', 'Contact Email'),
                            ('confidence_score', 'Confidence Score')
                        ]
                        
                        col_p1, col_p2 = st.columns(2)
                        
                        for i, (field, label) in enumerate(key_fields):
                            with col_p1 if i % 2 == 0 else col_p2:
                                value = parsed_data.get(field, 'Not specified')
                                st.metric(label, str(value)[:50] + ('...' if len(str(value)) > 50 else ''))
                        
                        # Show full JSON
                        st.markdown("**Complete Parsed Data:**")
                        st.json(parsed_data)
                        
                        st.session_state['test_parsed_data'] = parsed_data
                        
                    except Exception as e:
                        st.error(f"❌ Reply Parsing Error: {e}")
                else:
                    st.warning("Please enter a sample reply to parse")
            
            st.subheader("💾 Export Test Data")
            
            if st.button("📊 Create Test Campaign Results", key="create_test_results"):
                try:
                    # Create sample complete workflow data
                    test_campaign_data = [{
                        'name': test_venue_name,
                        'category': test_venue_category,
                        'website': test_venue_website,
                        'scraped_emails': 'contact@venue.com|info@venue.com',
                        'sent_to': test_recipient or os.getenv('TEST_EMAIL', ''),
                        'send_status': 'sent' if 'test_send_result' in st.session_state else 'pending',
                        'message_id': st.session_state.get('test_send_result', {}).get('message_id', 'test-123'),
                        'email_subject': st.session_state.get('test_email_data', {}).get('subject', 'Test Subject'),
                        'timestamp': datetime.now().isoformat()
                    }]
                    
                    # Add parsed reply data if available
                    if 'test_parsed_data' in st.session_state:
                        parsed_data = st.session_state['test_parsed_data']
                        for key, value in parsed_data.items():
                            test_campaign_data[0][f'reply_{key}'] = str(value)
                    
                    # Create DataFrame and save
                    test_df = pd.DataFrame(test_campaign_data)
                    data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
                    os.makedirs(data_dir, exist_ok=True)
                    
                    test_results_file = os.path.join(data_dir, 'step_test_results.csv')
                    test_df.to_csv(test_results_file, index=False)
                    
                    st.success(f"✅ Test results exported!")
                    st.info(f"📁 File: {test_results_file}")
                    
                    # Show results preview
                    st.dataframe(test_df)
                    
                    # Download button
                    csv_data = test_df.to_csv(index=False)
                    st.download_button(
                        label="📥 Download Test Results",
                        data=csv_data,
                        file_name="step_test_results.csv",
                        mime="text/csv"
                    )
                    
                except Exception as e:
                    st.error(f"❌ Export Error: {e}")
        
        # Test summary section
        st.markdown("---")
        st.subheader("📋 Test Summary")
        
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        
        with col_s1:
            ai_status = "✅" if 'test_analysis' in st.session_state else "⏳"
            st.metric("AI Analysis", ai_status)
        
        with col_s2:
            email_status = "✅" if 'test_email_data' in st.session_state else "⏳"
            st.metric("Email Generation", email_status)
        
        with col_s3:
            send_status = "✅" if 'test_send_result' in st.session_state else "⏳"
            st.metric("Email Sending", send_status)
        
        with col_s4:
            parse_status = "✅" if 'test_parsed_data' in st.session_state else "⏳"
            st.metric("Reply Parsing", parse_status)
        
        if all(key in st.session_state for key in ['test_analysis', 'test_email_data', 'test_send_result', 'test_parsed_data']):
            st.success("🎉 All workflow steps tested successfully!")
            st.balloons()

if __name__ == "__main__":
    main()
