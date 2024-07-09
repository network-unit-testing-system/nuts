from typing import Any, Dict


from nornir.core.inventory import Group, Groups, Host, Hosts, Inventory, ParentGroups
from nornir.plugins.inventory.simple import _get_defaults, _get_inventory_element


def serializ_inventory(inventory: Inventory) -> Dict[str, Dict[str, Any]]:
    data = {
        "hosts": {host: data.dict() for host, data in inventory.hosts.items()},
        "groups": {group: data.dict() for group, data in inventory.groups.items()},
        "defaults": inventory.defaults.dict(),
    }
    return data


class CachInventory:
    def __init__(
        self,
        hosts: Dict[str, Dict[str, Any]],
        groups: Dict[str, Dict[str, Any]],
        defaults: Dict[str, Any],
    ) -> None:
        """
        CachInventory inspired by the SimpleInventory.

        Args:

          hosts: Dict with host name and host.dict() data
          groups: Dict with group name and group.dict() data
          default: defaults.dict() dict data
        """

        self.hosts_dict = hosts
        self.groups_dict = groups
        self.defaults_dict = defaults

    def load(self) -> Inventory:

        defaults = _get_defaults(self.defaults_dict)

        hosts = Hosts()

        for n, h in self.hosts_dict.items():
            hosts[n] = _get_inventory_element(Host, h, n, defaults)

        groups = Groups()

        for n, g in self.groups_dict.items():
            groups[n] = _get_inventory_element(Group, g, n, defaults)

        for g in groups.values():
            g.groups = ParentGroups([groups[g] for g in g.groups])

        for h in hosts.values():
            h.groups = ParentGroups([groups[g] for g in h.groups])

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)
