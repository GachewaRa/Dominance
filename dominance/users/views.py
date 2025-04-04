from django.shortcuts import render
from django.http import JsonResponse
import json

def mpesa_confirmation(request):
    """Handles M-Pesa confirmation callbacks."""
    if request.method == "POST":
        mpesa_body = json.loads(request.body)
        print("M-Pesa Payment Received:", mpesa_body)  # Log it for debugging

        # Process the payment here (e.g., update order status)

        return JsonResponse({"message": "Payment received successfully"}, status=200)
    
    return JsonResponse({"error": "Invalid request"}, status=400)
