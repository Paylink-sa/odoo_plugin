-- disable paylinksa payment provider
UPDATE payment_provider
   SET paylinksa_apiId = NULL,
       paylinksa_secretKey = NULL;
