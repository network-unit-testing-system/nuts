SaltStack Setup
===============

Nuts use SaltStack to execute the test commands on the Salt minion and with proxy minions on network devices.
If you not have a existing Salt environment, it's time to set one up. For testing you can use our `Vagrantfile <https://github.com/HSRNetwork/vagrant-nuts>`_

For the full installation guide please visit the `installation guide <https://docs.saltstack.com/en/latest/topics/installation/>`_.

If you have no experience with Salt it's recommended to do the `SaltStack Get Started <https://docs.saltstack.com/en/getstarted/>`_

SaltStack Execution Module
--------------------------

SaltStack use Execution Modules to run commands on managed systems. There are many modules shipped with Salt already.
For example you can use the command *usage* from the module *disk* to get the disk usage of your server.

.. code-block:: bash

    # salt '*' disk.usage

It's simple to write your own module and you can trigger other modules like cmd.run or napalm commands.
This was what we did. The documentation how to write a custom module is located `here <https://docs.saltstack.com/en/latest/ref/modules/>`_.
The module nuts returns all value in a well defined structure. This allows a easy validation. Of course you can use the
module directly

.. code-block:: bash

    # salt 'csr*' nuts.checkversion
    csr1k_01:
        ----------
        result:
            CSR1000V Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 15.5(2)S, RELEASE SOFTWARE (fc3)
        resulttype:
            single

    # salt '*' nuts.bandwidth 172.16.17.202
    gitlab.oiz-staging.ins:
        ----------
        result:
            927078031.861
        resulttype:
            single

To add the custom module, the easiest way is to copy it to ``/srv/salt/_modules``. This works perfectly, as long as
you don't have changed the default ``fileserver backend`` and the ``file_roots``.

.. code-block:: bash

    cp _modules/nuts.py /srv/salt/_modules/

After changing something on the master, the minions need to be synchronised. A restart of the ``salt-master`` service
is not necessary. Any of the following commands will synced the minions.

.. code-block:: bash

    salt \* state.apply
    salt \* saltutil.sync_modules
    salt \* saltutil.sync_all
