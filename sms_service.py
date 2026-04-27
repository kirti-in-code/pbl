import os
import logging
from twilio.rest import Client

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def send_sms_alert(to_number, message):
    """
    Sends a real SMS using Twilio if credentials are provided.
    Otherwise, logs the message to the console for simulation.
    """
    twilio_sid = os.getenv("TWILIO_SID")
    twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    twilio_from = os.getenv("TWILIO_PHONE_NUMBER")

    # Basic validation for Twilio credentials
    has_credentials = all([twilio_sid, twilio_auth_token, twilio_from])
    
    # Ensure they aren't just the placeholder strings from .env.example
    is_not_placeholder = twilio_sid != "your_sid_here" and twilio_from != "your_twilio_number_here"

    if has_credentials and is_not_placeholder:
        try:
            client = Client(twilio_sid, twilio_auth_token)
            client.messages.create(
                body=message,
                from_=twilio_from,
                to=to_number
            )
            logger.info(f"REAL SMS SENT to {to_number}: {message}")
            return True, f"Alert sent successfully to {to_number}!"
        except Exception as e:
            logger.error(f"Failed to send real SMS: {str(e)}")
            return False, f"Twilio Error: {str(e)}"
    else:
        # Simulation Mode
        logger.warning("Twilio credentials not fully configured. Running in SIMULATION MODE.")
        logger.info(f"SIMULATED SMS to {to_number}: {message}")
        return True, f"Simulation: SMS alert sent to {to_number}. (Check .env for Twilio setup)"
