import requests
from django.conf import settings
from requests.auth import HTTPBasicAuth

def get_mpesa_access_token():
    """Fetch M-Pesa access token using API credentials."""
    url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    consumer_key = settings.MPESA_CONSUMER_KEY
    consumer_secret = settings.MPESA_CONSUMER_SECRET

    response = requests.get(url, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        raise Exception(f"Failed to get M-Pesa access token: {response.text}")






def register_mpesa_urls():
    """Register confirmation and validation URLs with M-Pesa API."""
    url = "https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl"
    access_token = get_mpesa_access_token()

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "ShortCode": "600000",
        "ResponseType": "Completed",
        "ConfirmationURL": " https://1740-102-212-236-135.ngrok-free.app/payment/confirmation",
        "ValidationURL": " https://1740-102-212-236-135.ngrok-free.app/payment/validation",
    }

    response = requests.post(url, json=payload, headers=headers)

    return response.json()
