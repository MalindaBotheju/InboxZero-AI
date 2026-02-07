from nicegui import ui, app
import os
import imaplib
import email
from email.header import decode_header
from dotenv import load_dotenv
import ollama
import asyncio

# --- LOAD SECRETS ---
load_dotenv()
USERNAME = os.getenv("EMAIL_USER")
PASSWORD = os.getenv("EMAIL_PASS")
IMAP_SERVER = os.getenv("IMAP_SERVER")

# --- BACKEND LOGIC (Same as before, but cleaner) ---
def clean_text(text):
    if not text: return ""
    return text.replace("\r", "").replace("\n", " ").strip()[:300]

async def ask_llama(subject, body):
    """Async call to Llama so it doesn't freeze the UI"""
    prompt = f"""
    Classify this email into exactly ONE category: [URGENT, PROMOTION, SOCIAL, BILL, PERSONAL].
    Reply ONLY with the category name.
    
    Subject: {subject}
    Body: {body}
    """
    try:
        # We run this in a thread so the UI stays smooth
        response = await asyncio.to_thread(ollama.chat, model='llama3', messages=[{'role': 'user', 'content': prompt}])
        return response['message']['content'].strip().upper()
    except:
        return "ERROR"

async def fetch_emails():
    """Connects to email and fetches the last 5 unread messages."""
    try:
        mail = imaplib.IMAP4_SSL(IMAP_SERVER)
        mail.login(USERNAME, PASSWORD)
        mail.select("inbox")
        
        _, messages = mail.search(None, 'UNSEEN')
        email_ids = messages[0].split()
        
        results = []
        
        # Get last 5 emails (most recent)
        for e_id in reversed(email_ids[-5:]):
            _, msg_data = mail.fetch(e_id, "(RFC822)")
            for response_part in msg_data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    
                    # Decode Subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        subject = subject.decode(encoding if encoding else "utf-8")
                    
                    sender = msg.get("From")
                    
                    # Get Body
                    body = ""
                    if msg.is_multipart():
                        for part in msg.walk():
                            if part.get_content_type() == "text/plain":
                                body = part.get_payload(decode=True).decode()
                                break
                    else:
                        body = msg.get_payload(decode=True).decode()
                    
                    category = await ask_llama(subject, clean_text(body))
                    
                    results.append({
                        "Sender": sender,
                        "Subject": subject,
                        "Category": category,
                        "Body": clean_text(body)
                    })
        mail.logout()
        return results
    except Exception as e:
        ui.notify(f"Connection Error: {e}", type='negative')
        return []

# --- MODERN UI LAYOUT ---
@ui.page('/')
async def main_page():
    # 1. Header Area
    with ui.header().classes('bg-slate-900 text-white shadow-lg'):
        ui.label('InboxZero AI').classes('text-xl font-bold q-ml-md')
        ui.space()
        ui.label('Status: Online').classes('text-xs text-green-400 q-mr-md self-center')

    # 2. Main Content Container
    with ui.column().classes('w-full max-w-4xl mx-auto p-4 gap-6'):
        
        # Title Section
        with ui.row().classes('w-full items-center justify-between'):
            with ui.column().classes('gap-0'):
                ui.label('Dashboard').classes('text-3xl font-bold text-slate-800')
                ui.label('Your intelligent email overview').classes('text-slate-500')
            
            # Action Button
            scan_btn = ui.button('Scan Inbox', icon='refresh', on_click=lambda: update_dashboard()) \
                .classes('bg-blue-600 text-white shadow-md rounded-lg px-6')

        # 3. Metrics Cards (The "Dashboard" look)
        metrics_container = ui.row().classes('w-full gap-4')
        
        # 4. Email List Container
        email_container = ui.column().classes('w-full gap-4')

    async def update_dashboard():
        scan_btn.props('loading') # Show spinner on button
        
        # Clear previous results
        metrics_container.clear()
        email_container.clear()
        
        emails = await fetch_emails()
        
        # Calculate Stats
        urgent_count = sum(1 for e in emails if "URGENT" in e['Category'])
        promo_count = sum(1 for e in emails if "PROMOTION" in e['Category'])
        
        # --- RENDER METRICS ---
        with metrics_container:
            # Card 1: Total
            with ui.card().classes('w-1/3 bg-white shadow-sm border-l-4 border-blue-500 p-4'):
                ui.label('Unread Emails').classes('text-sm text-gray-500 font-bold')
                ui.label(str(len(emails))).classes('text-4xl font-black text-slate-800')
            
            # Card 2: Urgent
            with ui.card().classes('w-1/3 bg-white shadow-sm border-l-4 border-red-500 p-4'):
                ui.label('Urgent Action').classes('text-sm text-red-500 font-bold')
                ui.label(str(urgent_count)).classes('text-4xl font-black text-red-600')

            # Card 3: Spam/Promo
            with ui.card().classes('w-1/3 bg-white shadow-sm border-l-4 border-green-500 p-4'):
                ui.label('Low Priority').classes('text-sm text-green-600 font-bold')
                ui.label(str(promo_count)).classes('text-4xl font-black text-green-700')

        # --- RENDER EMAILS ---
        with email_container:
            if not emails:
                ui.label("🎉 All caught up! No new emails.").classes('text-xl text-gray-400 self-center mt-10')
            
            for email in emails:
                # Color coding badges
                badge_color = 'red' if 'URGENT' in email['Category'] else 'green'
                if 'BILL' in email['Category']: badge_color = 'orange'
                
                with ui.card().classes('w-full bg-white shadow-sm hover:shadow-md transition-shadow'):
                    with ui.row().classes('w-full items-center justify-between no-wrap'):
                        # Left side: Icon + Sender
                        with ui.row().classes('items-center gap-3'):
                            ui.icon('mail', color='gray').classes('text-2xl')
                            with ui.column().classes('gap-0'):
                                ui.label(email['Sender']).classes('font-bold text-slate-800')
                                ui.label(email['Subject']).classes('text-sm text-slate-500')
                        
                        # Right side: Category Badge
                        ui.badge(email['Category'], color=badge_color).classes('text-sm font-bold px-3 py-1')
                    
                    # Body Preview (Expandable)
                    with ui.expansion('Read Content').classes('w-full text-gray-400 text-sm'):
                        ui.markdown(f"**AI Summary:** \n {email['Body']}")

        scan_btn.props(remove='loading') # Stop spinner

ui.run(title="InboxZero AI", favicon="📧")
