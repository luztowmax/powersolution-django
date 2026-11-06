
import hashlib
import hmac
import json
import uuid

from decimal import Decimal, ROUND_HALF_UP

import requests

from django.conf import settings
from django.db import transaction
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from .models import Quote, Payment


PAYSTACK_BASE_URL = "https://api.paystack.co"


# -------------------------------------
# Paystack authentication
# -------------------------------------

def paystack_headers():
    return {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }


# -------------------------------------
# Convert Naira to Kobo
# -------------------------------------

def amount_to_kobo(amount):
    amount = Decimal(str(amount))

    return int(
        (amount * 100).quantize(
            Decimal("1"),
            rounding=ROUND_HALF_UP
        )
    )


# -------------------------------------
# Initialize full quotation payment
# -------------------------------------

@require_POST
def initialize_payment(request, quote_id):

    quote = get_object_or_404(Quote, pk=quote_id)

    if not settings.PAYSTACK_SECRET_KEY:
        return JsonResponse({
            "success": False,
            "error": "Paystack is not configured."
        }, status=503)

    if not quote.customer.email:
        return JsonResponse({
            "success": False,
            "error": "Customer email is required."
        }, status=400)

    # Prevent payment for an already-paid quote
    if Payment.objects.filter(
        quote=quote,
        status="success"
    ).exists():
        return JsonResponse({
            "success": False,
            "error": "This quotation has already been paid."
        }, status=409)

    amount = Decimal(str(quote.estimated_total))

    if amount <= 0:
        return JsonResponse({
            "success": False,
            "error": "Invalid quotation amount."
        }, status=400)

    reference = f"HP-{quote.id}-{uuid.uuid4().hex[:20]}"

    payment = Payment.objects.create(
        quote=quote,
        reference=reference,
        amount=amount,
        status="pending"
    )

    payload = {
        "email": quote.customer.email,
        "amount": amount_to_kobo(amount),
        "currency": "NGN",
        "reference": reference,
        "callback_url": request.build_absolute_uri(
            reverse("payment_callback")
        ),
        "metadata": {
            "quote_id": quote.id
        }
    }

    try:
        response = requests.post(
            f"{PAYSTACK_BASE_URL}/transaction/initialize",
            headers=paystack_headers(),
            json=payload,
            timeout=20
        )

        response.raise_for_status()
        result = response.json()

        if not result.get("status"):
            raise ValueError("Paystack initialization failed.")

        authorization_url = result["data"]["authorization_url"]

        return JsonResponse({
            "success": True,
            "reference": reference,
            "authorization_url": authorization_url
        })

    except (
        requests.RequestException,
        ValueError,
        KeyError
    ):
        payment.status = "failed"
        payment.save(update_fields=["status"])

        return JsonResponse({
            "success": False,
            "error": "Unable to start payment. Please retry."
        }, status=502)


# -------------------------------------
# Verify payment with Paystack
# -------------------------------------

def verify_payment(reference):

    payment = get_object_or_404(
        Payment,
        reference=reference
    )

    response = requests.get(
        f"{PAYSTACK_BASE_URL}/transaction/verify/{reference}",
        headers=paystack_headers(),
        timeout=20
    )

    response.raise_for_status()
    result = response.json()
    data = result.get("data") or {}

    customer = data.get("customer") or {}
    customer_email = customer.get("email") or ""
    expected_email = payment.quote.customer.email or ""

    valid = (
        result.get("status") is True
        and data.get("status") == "success"
        and data.get("reference") == reference
        and data.get("currency") == "NGN"
        and data.get("amount") == amount_to_kobo(payment.amount)
        and customer_email.lower() == expected_email.lower()
    )

    if valid:
        with transaction.atomic():

            locked_payment = (
                Payment.objects
                .select_for_update()
                .get(pk=payment.pk)
            )

            if locked_payment.status != "success":
                locked_payment.status = "success"
                locked_payment.paid_at = timezone.now()

                locked_payment.save(
                    update_fields=["status", "paid_at"]
                )

    payment.refresh_from_db()

    return payment.status == "success"


# -------------------------------------
# Paystack callback
# -------------------------------------

@require_GET
def payment_callback(request):

    reference = request.GET.get("reference", "")

    if not reference:
        return HttpResponse(
            "Missing payment reference.",
            status=400
        )

    try:
        success = verify_payment(reference)

    except (
        requests.RequestException,
        ValueError
    ):
        success = False

    return render(
        request,
        "payment_result.html",
        {
            "success": success,
            "reference": reference
        }
    )


# -------------------------------------
# Paystack webhook
# -------------------------------------

@csrf_exempt
@require_POST
def paystack_webhook(request):

    if not settings.PAYSTACK_SECRET_KEY:
        return HttpResponse(status=503)

    signature = request.headers.get(
        "x-paystack-signature",
        ""
    )

    expected_signature = hmac.new(
        settings.PAYSTACK_SECRET_KEY.encode(),
        request.body,
        hashlib.sha512
    ).hexdigest()

    if not hmac.compare_digest(
        signature,
        expected_signature
    ):
        return HttpResponse(status=403)

    try:
        event = json.loads(request.body)

        if event.get("event") == "charge.success":

            reference = (
                event.get("data") or {}
            ).get("reference")

            if reference and Payment.objects.filter(
                reference=reference
            ).exists():
                verify_payment(reference)

    except (
        ValueError,
        requests.RequestException
    ):
        return HttpResponse(status=503)

    return HttpResponse(status=200)
