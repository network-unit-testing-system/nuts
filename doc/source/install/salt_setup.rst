SaltStack Setup
===============

Nuts use SaltStack to execute the test commands on the Salt minions and with proxy minions on network devices.
If you do not have an existing Salt environment, it's time to set one up. For testing, you can use our `Vagrantfile <https://github.com/HSRNetwork/vagrant-nuts>`_

For the full installation guide for SaltStack, please visit the `official installation guide <https://docs.saltstack.com/en/latest/topics/installation/>`_.

If you have no experience with Salt it's recommended to do the `SaltStack Get Started <https://docs.saltstack.com/en/getstarted/>`_

SaltStack Execution Module
--------------------------

SaltStack use execution modules to run commands on managed systems. There are many modules shipped with Salt already.
For example you can use the ``usage`` command from the ``disk`` module to get disk usage of your servers.

.. code-block:: bash

    # salt '*' disk.usage
    srvlnx00001.local:
        ----------
        /:
            ----------
            1K-blocks:
                18307072
            available:
                13769124
            capacity:
                25%
            filesystem:
                /dev/mapper/centos_srvlnx0001-root
            used:
                4537948
        /boot:
            ----------
            1K-blocks:
                508588
            available:
                287240
            capacity:
                44%
            filesystem:
                /dev/sda1
            used:
                221348

It's simple to write your own module. You can trigger other modules like ``cmd.run`` or napalm commands.
This was what we did. The documentation how to write a custom module is located `here <https://docs.saltstack.com/en/latest/ref/modules/>`_.
The ``nuts`` module returns all value in a well defined structure. This allows for easy validation. Of course you can use the
module directly as well.

.. code-block:: bash

    # salt 'csr*' nuts.checkversion
    csr1k_01:
        ----------
        result:
            CSR1000V Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 15.5(2)S, RELEASE SOFTWARE (fc3)
        resulttype:
            single

    # salt '*' nuts.bandwidth 172.16.17.202
    srvlnx00001.local:
        ----------
        result:
            927078031.861
        resulttype:
            single

To add the custom module, the easiest way is to copy it to  the salt module directory (``/srv/salt/_modules`` unless
configured otherwise.

.. code-block:: bash

    cp _modules/nuts.py /srv/salt/_modules/

After changing modules on the master, the minions need to be synchronised. A restart of the ``salt-master`` service
is not necessary. Any of the following commands will sync the minions.

.. code-block:: bash

    salt \* state.apply
    salt \* saltutil.sync_modules
    salt \* saltutil.sync_all
