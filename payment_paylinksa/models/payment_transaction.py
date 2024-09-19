# Part of Odoo. See LICENSE file for full copyright and licensing details.

import logging
import pprint
import json
from werkzeug import urls

from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError

from odoo.addons.payment import utils as payment_utils
from odoo.addons.payment_paylinksa import const
from odoo.addons.payment_paylinksa.controllers.controllers import PaylinkController


_logger = logging.getLogger(__name__)


class PaymentTransaction(models.Model):
    _inherit = "payment.transaction"

    paylink_id_token = fields.Char(string="Paylink token ID")
    paylink_transaction_no = fields.Char(string="Paylink transactionNo")

    def _get_specific_rendering_values(self, processing_values):
        """Override of payment to return Paylink-specific rendering values.

        Note: self.ensure_one() from `_get_processing_values`

        :param dict processing_values: The generic and specific processing values of the transaction
        :return: The dict of provider-specific processing values.
        :rtype: dict
        """
        res = super()._get_specific_rendering_values(processing_values)
        if self.provider_code != "paylinksa":
            return res

        # Initiate the payment and retrieve the payment link data.
        # base_url = self.provider_id.get_base_url()

        auth = self.provider_id._paylink_make_auth()
        id_token = auth.get("id_token")
        _logger.info(id_token)

        base_url = self.provider_id.get_base_url()
        get_product = self.provider_id._product_description(self.reference)
        payload = {
            "amount": self.amount,
            "callBackUrl": urls.url_join(base_url, PaylinkController._return_url),
            "clientEmail": self.partner_email,
            "clientMobile": self.partner_phone,
            "clientName": self.partner_name,
            "note": self.company_id.name,
            "orderNumber": self.reference,
            "products": get_product,
            "currency": self.currency_id.name,
        }
        payment_link_data = self.provider_id._paylink_make_request(
            "addInvoice", auth=id_token, payload=payload
        )

        # Extract the payment link URL and embed it in the redirect form.
        rendering_values = {
            "api_url": payment_link_data["url"],
        }
        self.write(
            {
                "paylink_id_token": id_token,
                "paylink_transaction_no": payment_link_data["transactionNo"],
            }
        )
        return rendering_values

    def _get_tx_from_notification_data(self, provider_code, notification_data):
        """Override of payment to find the transaction based on Paylink data.

        :param str provider_code: The code of the provider that handled the transaction.
        :param dict notification_data: The notification data sent by the provider.
        :return: The transaction if found.
        :rtype: recordset of `payment.transaction`
        :raise ValidationError: If inconsistent data were received.
        :raise ValidationError: If the data match no transaction.
        """
        tx = super()._get_tx_from_notification_data(provider_code, notification_data)
        if provider_code != "paylinksa" or len(tx) == 1:
            return tx

        reference = notification_data.get("orderNumber")
        if not reference:
            raise ValidationError(
                "Paylink: " + _("Received data with missing reference.")
            )

        tx = self.search(
            [("reference", "=", reference), ("provider_code", "=", "paylinksa")]
        )
        if not tx:
            raise ValidationError(
                "Paylinksa: "
                + _("No transaction found matching reference %s.", reference)
            )
        return tx

    def _process_notification_data(self, notification_data):
        """Override of payment to process the transaction based on Paylink data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        :raise ValidationError: If inconsistent data were received.
        """
        super()._process_notification_data(notification_data)
        if self.provider_code != "paylinksa":
            return

        # Verify the notification data.
        getInvoice = f"getInvoice/{self.paylink_transaction_no}"
        verification_response_content = self.provider_id._paylink_make_request(
            getInvoice, payload=None, auth=self.paylink_id_token, method="GET"
        )
        _logger.info("=========verification_response_content========")
        _logger.info(verification_response_content)
        verified_data = verification_response_content

        # Update the provider reference.
        self.provider_reference = verified_data["transactionNo"]

        # Update payment method.
        payment_receipt = verified_data.get("paymentReceipt")
        payment_method_type = payment_receipt.get("paymentMethod").lower()
        payment_method = self.env["payment.method"]._get_from_code(
            payment_method_type, mapping=const.PAYMENT_METHODS_MAPPING
        )
        self.payment_method_id = payment_method or self.payment_method_id

        # Update the payment state.
        payment_status = verified_data["orderStatus"].lower()
        if payment_status == "pending":
            self._set_pending()
        elif payment_status == "paid":
            self._set_done()
            # self._paylink_tokenize_from_notification_data(verified_data)
        elif payment_status == "canceled":
            self._set_canceled()
        else:
            _logger.warning(
                "Received data with invalid payment status (%s) for transaction with reference %s.",
                payment_status,
                self.reference,
            )
            self._set_error(
                "Paylink: " + _("Unknown payment status: %s", payment_status)
            )

    def _paylink_tokenize_from_notification_data(self, notification_data):
        """Create a new token based on the notification data.

        Note: self.ensure_one()

        :param dict notification_data: The notification data sent by the provider.
        :return: None
        """
        self.ensure_one()

        token = self.env["payment.token"].create(
            {
                "provider_id": self.provider_id.id,
                "payment_method_id": self.payment_method_id.id,
                "payment_details": notification_data["paymentReceipt"]["receiptUrl"],
                "partner_id": self.partner_id.id,
                "provider_ref": notification_data["transactionNo"],
                "paylink_customer_email": notification_data["gatewayOrderRequest"][
                    "clientEmail"
                ],
                "active": False,
            }
        )
        self.write(
            {
                "token_id": token,
                "tokenize": False,
            }
        )
        _logger.info(
            "created token with id %(token_id)s for partner with id %(partner_id)s from "
            "transaction with reference %(ref)s",
            {
                "token_id": token.id,
                "partner_id": self.partner_id.id,
                "ref": self.reference,
            },
        )
