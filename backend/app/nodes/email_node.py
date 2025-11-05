from app.email_utils import send_email

def send_email_node(state):
    recipient = state.get("email_id") or state.get("email") or None
    body = state.get("message", f"Candidate {state.get('phone_number')} passed thresholds.")
    if recipient:
        send_email(recipient, "Automated Agentic Update", body)
    else:
        print("No recipient to send email to.")
    return state
