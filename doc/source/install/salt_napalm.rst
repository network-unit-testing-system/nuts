NAPALM and Salt
===============

To create a connection from the salt master to your network device of choice there's a fantastic library called NAPALM
which has an integration into SaltStack.
For the installation guide head to `napalm-salt repository <https://github.com/napalm-automation/napalm-salt/>`_.

A NAPALM minion-proxy is like a normal minion connected to the salt master. Every network vendor has it's on interface or
cli syntax. Even platforms from the same vendor can have different implementations. This makes life much harder for
a network automation engineer. On this point NAPALM comes in. NAPALM abstract the different interfaces and enables
the communication with the same interface. With NAPALM proxies it's possible to interact with network devices like Linux boxes.

.. code-block:: bash

    # salt \* net.facts
    sw8262-e:
        ----------
        comment:
        out:
            ----------
            fqdn:
                sw8262-e.ins
            hostname:
                sw8262-e
            interface_list:
                - Vlan1
                - Vlan4
                - GigabitEthernet0/1
                - GigabitEthernet0/2
                - GigabitEthernet0/3
                - GigabitEthernet0/4
                - GigabitEthernet0/5
                - GigabitEthernet0/6
                - GigabitEthernet0/7
                - GigabitEthernet0/8
                - GigabitEthernet0/9
                - GigabitEthernet0/10
                - Port-channel1
            model:
                WS-C2960CG-8TC-L
            os_version:
                C2960C Software (C2960c405ex-UNIVERSALK9-M), Version 15.2(2a)E1, RELEASE SOFTWARE (fc1)
            serial_number:
                FOC1824Y237
            uptime:
                8568300
            vendor:
                Cisco
        result:
            True

