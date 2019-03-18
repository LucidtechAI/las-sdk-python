=================
Quick start guide
=================


This section should talk you through everything you need to get started with Lucidtech AI Services Python SDK.


----------
An example
----------

Suppose we have credentials with access to the demo api and we wish to run inference on a document using Lucidtech's invoice model.

.. code:: python

    import json

    from las import ApiClient

    api_client = ApiClient('https://demo.api.lucidtech.ai/v1')
    prediction = api_client.predict('document.jpeg', 'invoice')
    print(json.dumps(prediction, indent=2))


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
