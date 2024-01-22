# Part of Odoo. See LICENSE file for full copyright and licensing details.

API_VERSION = '2024-01-01'  # The API version of Stripe implemented in this module


# The codes of the payment methods to activate when Stripe is activated.
DEFAULT_PAYMENT_METHODS_CODES = [
    # Brand payment methods.
    'card',
    'mada',
    'visa',
    'mastercard',
    'amex',
    'mada',
]


STATUS_MAPPING = {
    'draft': ('requires_confirmation', 'requires_action'),
    'pending': ('processing', 'pending'),
    'authorized': ('requires_capture',),
    'done': ('succeeded',),
    'cancel': ('canceled',),
    'error': ('requires_payment_method', 'failed',),
}

# Events which are handled by the webhook
HANDLED_WEBHOOK_EVENTS = [
    'payment_intent.processing',
    'payment_intent.amount_capturable_updated',
    'payment_intent.succeeded',
    'payment_intent.payment_failed',
    'setup_intent.succeeded',
    'charge.refunded',  # A refund has been issued.
    'charge.refund.updated',  # The refund status has changed, possibly from succeeded to failed.
]

# The countries supported by Stripe. See https://stripe.com/global page.
SUPPORTED_CURRENCIES = {
    'SAR',
    'GBP',
    'CAD',
    'XAF',
    'CLP',
    'COP',
    'EGP',
    'EUR',
    'GHS',
    'GNF',
    'KES',
    'MWK',
    'MAD',
    'NGN',
    'RWF',
    'SLL',
    'STD',
    'ZAR',
    'TZS',
    'UGX',
    'USD',
    'XOF',
    'ZMW',
}

PAYMENT_METHODS_MAPPING = {
    'bank_transfer': 'banktransfer',
}
