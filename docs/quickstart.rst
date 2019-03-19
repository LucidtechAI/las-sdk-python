=================
Quick start guide
=================


This section should talk you through everything you need to get started with Lucidtech AI Services Python SDK.


--------
Examples
--------

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Making a prediction on a document
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose we have credentials with access to the demo api and we wish to run inference on a document using Lucidtech's
invoice model.

.. code:: python

    import json

    from las import ApiClient

    api_client = ApiClient('https://demo.api.lucidtech.ai/v1')
    prediction = api_client.predict('document.jpeg', 'invoice')
    print(json.dumps(prediction, indent=2))


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Sending feedback to the model
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose we make a prediction that returns incorrect values and we wish to improve the model for future use. We can do so
by sending feedback to the model, telling it what the expected values should have been.

.. code:: python

    import json

    from las import ApiClient, Field

    api_client = ApiClient('https://demo.api.lucidtech.ai/v1')
    prediction = api_client.predict('document.jpeg', 'invoice')

    # We notice after manual inspection that some values were incorrect
    print(json.dumps(prediction, indent=2))

    # Constructing field instances with correct values and sending these to the model
    feedback = [Field(label='total_amount', value='100.00'), Field(label='purchase_date', value='2019-03-18')]
    api_client.send_feedback(prediction.document_id, feedback)


^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Revoking consent and deleting documents
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Suppose we wish to delete all documents associated with a customer in our ERP database or other systems. We need to
provide a consent_id to the prediction method that uniquely identifies the customer and use that consent_id to delete
documents.

.. code:: python

    import json

    from las import ApiClient

    api_client = ApiClient('https://demo.api.lucidtech.ai/v1')
    prediction = api_client.predict('document.jpeg', 'invoice', consent_id='example_customer_123')

    # Deleting the documents associated with 'example_customer_123'
    api_client.revoke_consent(prediction.consent_id)


-------------
Prerequisites
-------------

Python 3.6 or newer

------------
Installation
------------

.. code:: bash

    $ pip install lucidtech-las

-----------
Credentials
-----------

By default, lucidtech-las looks for credentials in a file located at ~/.lucidtech/credentials.cfg. The contents of
this file should be

.. code:: ini

    [default]
    access_key_id = <your access key id>
    secret_access_key = <your secret access key>
    api_key = <your api key>


Optionally you may provide a Credentials object when constructing the Api client. See details
`here <reference.html#module-las.credentials>`__

Contact Lucidtech at hello@lucidtech.ai to get access_key_id, secret_access_key and api_key
