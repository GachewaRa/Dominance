import base64
import requests
from django.utils.timezone import now
from django.conf import settings
from celery import shared_task
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from Dominance.dominance.users.models import Order
from Dominance.dominance.users.payment_utils.mpesa import get_mpesa_access_token

def lipa_na_mpesa(phone_number, amount, order_id):
    """
    Initiates an STK push request to the user's phone via M-Pesa API.
    """
    access_token = get_mpesa_access_token()
    timestamp = now().strftime("%Y%m%d%H%M%S")
    business_short_code = settings.MPESA_SHORTCODE
    passkey = settings.MPESA_PASSKEY

    password = base64.b64encode(f"{business_short_code}{passkey}{timestamp}".encode()).decode()
    
    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": phone_number,
        "CallBackURL": settings.MPESA_CALLBACK_URL,
        "AccountReference": f"Order-{order_id}",
        "TransactionDesc": "Payment for Order"
    }

    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.post(settings.MPESA_STK_PUSH_URL, json=payload, headers=headers)
    
    return response.json()


@csrf_exempt
def mpesa_callback(request):
    """
    Handles M-Pesa webhook notifications.
    """
    data = json.loads(request.body)
    result_code = data["Body"]["stkCallback"]["ResultCode"]
    order_id = data["Body"]["stkCallback"]["MerchantRequestID"]
    transaction_id = data["Body"]["stkCallback"].get("CallbackMetadata", {}).get("Item", [])[0].get("Value", "")

    if result_code == 0:  # Payment successful
        try:
            order = Order.objects.get(id=order_id)
            order.mark_as_paid(transaction_id)
        except Order.DoesNotExist:
            return JsonResponse({"error": "Order not found"}, status=404)

    return JsonResponse({"message": "Received"})





@shared_task
def check_payment_status(order_id):
    """
    Periodically checks if payment was successful.
    """
    order = Order.objects.get(id=order_id)
    if order.is_paid():
        return f"Order {order_id} already paid."

    # Call M-Pesa API to check status
    response = requests.get(f"{settings.MPESA_STATUS_URL}/{order_id}")

    if response.json().get("status") == "completed":
        order.mark_as_paid(response.json().get("transaction_id"))
    
    return f"Checked payment for Order {order_id}"

