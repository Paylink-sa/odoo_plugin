# Part of Odoo. See LICENSE file for full copyright and licensing details.

API_VERSION = "2024-09-22"  # The API version of Paylink implemented in this module

PRODUCTION_API_URL = "https://restapi.paylink.sa"
TEST_API_URL = "https://restpilot.paylink.sa"
DEFAULT_TEST_API_ID = "APP_ID_1123453311"
DEFAULT_TEST_SECRET_KEY = "0662abb5-13c7-38ab-cd12-236e58f43766"

# The codes of the payment methods to activate when Stripe is activated.
DEFAULT_PAYMENT_METHODS_CODES = [
    "mada",
    "visaMastercard",
    "amex",
    "tabby",
    "tamara",
    "stcpay",
    "urpay",
]

STATUS_MAPPING = {
    "draft": ("requires_confirmation", "requires_action"),
    "pending": ("processing", "pending"),
    "authorized": ("requires_capture",),
    "done": ("succeeded",),
    "cancel": ("canceled",),
    "error": ("requires_payment_method", "failed"),
}

# Events which are handled by the webhook
HANDLED_WEBHOOK_EVENTS = [
    "payment_intent.processing",
    "payment_intent.amount_capturable_updated",
    "payment_intent.succeeded",
    "payment_intent.payment_failed",
    "setup_intent.succeeded",
    "charge.refunded",  # A refund has been issued.
    "charge.refund.updated",  # The refund status has changed, possibly from succeeded to failed.
]

# The countries supported by Stripe. See https://stripe.com/global page.
SUPPORTED_CURRENCIES = {
    "SAR",
    "GBP",
    "CAD",
    "XAF",
    "CLP",
    "COP",
    "EGP",
    "EUR",
    "GHS",
    "GNF",
    "KES",
    "MWK",
    "MAD",
    "NGN",
    "RWF",
    "SLL",
    "STD",
    "ZAR",
    "TZS",
    "UGX",
    "USD",
    "XOF",
    "ZMW",
}

PAYMENT_METHODS_MAPPING = {
    "bank_transfer": "banktransfer",
}
