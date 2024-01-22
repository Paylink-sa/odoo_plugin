# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import requests
from werkzeug.urls import url_join
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.addons.payment_paylinksa import const
import json
_logger = logging.getLogger(__name__)



class PaymentProvider(models.Model):
    _inherit = 'payment.provider'

    name = fields.Char(string="Name", required=True, translate=True, readonly=True)
    state = fields.Selection(
        string="Status",
        help="In test mode, a fake payment is processed through a test payment interface.\n"
             "This mode is advised when setting up the provider.",
        selection=[('test', "Test Environment"), ('enabled', "Production Environment"), ('disabled', "Disabled")],
        default='disabled', required=True, copy=False)

    code = fields.Selection(
        selection_add=[('paylinksa', "Paylink")], ondelete={'paylinksa': 'set default'}
    )
    minimum_amount = fields.Monetary(
        string="Minimum Amount",
        help="The minimum payment amount that this payment provider is available. ",
        currency_field='main_currency_id', default=5, readonly=True)
    paylinksa_apiId = fields.Char(
        string="API ID",
        help="API ID that Paylink gives. If you need the API ID, subscribe to a package that supports API.",
        required_if_provider='paylinksa',)
    website_id = fields.Many2one(
        "website",
        check_company=True,
        ondelete="restrict",
        required_if_provider='paylinksa'
    )
    paylinksa_secretKey = fields.Char(string="Secret Key", required_if_provider='paylinksa', groups='base.group_system')
    persistToken = fields.Boolean(string="Persist Token",help="If set to true, then the returned token is valid for 30 hours. Otherwise, the returned token will be good for 30 minutes.", groups='base.group_system')


    # === COMPUTE METHODS ===#


    def _compute_feature_support_fields(self):
        """ Override of `payment` to enable additional features. """
        super()._compute_feature_support_fields()
        self.filtered(lambda p: p.code == 'paylinksa').update({
            'support_tokenization': True,
        })

    # === BUSINESS METHODS ===#

    @api.model
    def _get_compatible_providers(self, *args, is_validation=False, **kwargs):
        """ Override of `payment` to filter out paylink providers for validation operations. """
        providers = super()._get_compatible_providers(*args, is_validation=is_validation, **kwargs)

        if is_validation:
            providers = providers.filtered(lambda p: p.code != 'paylinksa')

        return providers



    def _get_supported_currencies(self):
        """ Override of `payment` to return the supported currencies. """
        supported_currencies = super()._get_supported_currencies()
        if self.code == 'paylinksa':
            supported_currencies = supported_currencies.filtered(
                lambda c: c.name in const.SUPPORTED_CURRENCIES
            )
        return supported_currencies


    def _paylink_make_auth(self):

        if self.state == 'enabled':
            url = 'https://restapi.paylink.sa/api/auth'
        else:
            url = 'https://restpilot.paylink.sa/api/auth'
        headers = {
            'Content-Type': 'application/json'
        }
        #headers = {'Authorization': f'Bearer {self.paylinksa_secretKey}'}
        if self.persistToken:
            persist = "true"
        else:
            persist = "false"

        payload = json.dumps({
            "apiId": self.paylinksa_apiId,
            "secretKey": self.paylinksa_secretKey,
            "persistToken": persist
        })
        response = requests.request("POST", url, headers=headers, data=payload)
        result = json.loads(response.text)
        return result
    def _paylink_make_request(self, endpoint, auth=None, payload=None, method='POST'):
        """ Make a request to Paylink API at the specified endpoint.

        Note: self.ensure_one()

        :param str endpoint: The endpoint to be reached by the request.
        :param dict payload: The payload of the request.
        :param str method: The HTTP method of the request.
        :return The JSON-formatted content of the response.
        :rtype: dict
        :raise ValidationError: If an HTTP error occurs.
        """
        self.ensure_one()

        if self.state == 'enabled':
            url = url_join('https://restapi.paylink.sa/api/', endpoint)
        else:
            url = url_join('https://restpilot.paylink.sa/api/', endpoint)

        headers = {'Authorization': f'Bearer {auth}'}
        try:
            if method == 'GET':
                response = requests.get(url, params=payload, headers=headers, timeout=10)
            else:
                response = requests.post(url, json=payload, headers=headers, timeout=10)
            try:
                response.raise_for_status()
            except requests.exceptions.HTTPError:
                _logger.exception(
                    "Invalid API request at %s with data:\n%s", url, pprint.pformat(payload),
                )
                _logger.exception(response.text)
                # detail
                detail = json.loads(response.text)
                raise ValidationError(_(detail['detail']))
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            _logger.exception("Unable to reach endpoint at %s", url)
            raise ValidationError(
                "Paylink: " + _("Could not establish the connection to the API.")
            )
        return response.json()

    def _product_description(self, order_ref):
        sale_order = self.env["sale.order"].search([("name", "=", order_ref)])
        res = []
        if sale_order:
            for line in sale_order.order_line:
                dic = {
                          "description": line.name,
                          "price": line.price_subtotal,
                          "qty": line.product_uom_qty,
                          "title": line.product_template_id.name
                        }
                res.append(dic)
        return res

    def _get_default_payment_method_codes(self):
        """ Override of `payment` to return the default payment method codes. """
        default_codes = super()._get_default_payment_method_codes()
        if self.code != 'paylinksa':
            return default_codes

        return const.DEFAULT_PAYMENT_METHODS_CODES