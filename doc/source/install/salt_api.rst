SaltStack API
=============

To use nuts you also need the salt-api which enables nuts to connect to the salt master over HTTP / HTTPS.
For the installation guide visit `cherrypy documentation <https://docs.saltstack.com/en/latest/ref/netapi/all/salt.netapi.rest_cherrypy.html>`_.


External Auth
-------------

Nuts needs the access to *runner modules* and the normal *execution modules*. `Documentation <https://docs.saltstack.com/en/latest/topics/eauth/index.html>`_

.. code-block:: yaml

    external_auth:
      pam:
        username:
          - .*
          - '@runner'

Example from Vagrant Test Environment
-------------------------------------

``/etc/salt/master.d/salt-api.conf``

.. code-block:: yaml

    rest_cherrypy:
      port: 8000
      disable_ssl: True
      expire_responses: False
    external_auth:
      pam:
        ubuntu:
          - .*
          - '@runner'