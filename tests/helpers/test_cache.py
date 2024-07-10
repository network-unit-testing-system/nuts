from nornir.core.inventory import Inventory, Hosts, Groups, Defaults, Host, Group
from typing import Any, Dict

from nuts.helpers.cache import CacheInventory, serialize_inventory


def test_serialize_inventory():
    hosts = Hosts(
        {
            "host1": Host(
                name="host1", hostname="host1.example.com", data={"key": "value"}
            )
        }
    )
    groups = Groups({"group1": Group(name="group1", data={"key": "value"})})
    defaults = Defaults(hostname="hostname", data={"key": "value"})
    inventory = Inventory(hosts=hosts, groups=groups, defaults=defaults)

    serialized = serialize_inventory(inventory)

    expected = {
        "hosts": {
            "host1": {
                "name": "host1",
                "hostname": "host1.example.com",
                "port": None,
                "username": None,
                "password": None,
                "platform": None,
                "data": {"key": "value"},
                "connection_options": {},
                "groups": [],
            }
        },
        "groups": {
            "group1": {
                "connection_options": {},
                "data": {"key": "value"},
                "hostname": None,
                "groups": [],
                "name": "group1",
                "password": None,
                "platform": None,
                "port": None,
                "username": None,
            }
        },
        "defaults": {
            "connection_options": {},
            "data": {"key": "value"},
            "hostname": "hostname",
            "password": None,
            "platform": None,
            "port": None,
            "username": None,
        },
    }

    assert serialized == expected


def test_fail_serialize_inventory():
    hosts = Hosts(
        {
            "host1": Host(
                name="host1", hostname="host1.example.com", data={"key": "value"}
            )
        }
    )
    groups = Groups({"group1": Group(name="group1", data={"key": "value"})})
    defaults = Defaults(hostname="hostname", data={"key": "value"})
    inventory = Inventory(hosts=hosts, groups=groups, defaults=defaults)

    serialized = serialize_inventory(inventory)

    expected = {
        "hosts": {
            "host12": {
                "name": "host1",
                "hostname": "host1.example.com",
                "port": None,
                "username": None,
                "password": None,
                "platform": None,
                "data": {"key": "value"},
                "connection_options": {},
                "groups": [],
            }
        },
        "groups": {
            "group12": {
                "connection_options": {},
                "data": {"key": "value"},
                "hostname": None,
                "groups": [],
                "name": "group1",
                "password": None,
                "platform": None,
                "port": None,
                "username": None,
            }
        },
        "defaults": {
            "connection_options": {},
            "data": {"key": "value"},
            "hostname": "hostname",
            "password": None,
            "platform": None,
            "port": None,
            "username": "User",
        },
    }

    assert serialized != expected


def test_cache_inventory_load():
    hosts_dict = {
        "host1": {
            "name": "host1",
            "hostname": "host1.example.com",
            "data": {"key": "value"},
            "groups": [],
            "defaults": {"key": "value"},
        }
    }
    groups_dict = {
        "group1": {
            "name": "group1",
            "data": {"key": "value"},
            "groups": [],
            "defaults": {"key": "value"},
        }
    }
    defaults_dict = {"hostname": "hostname", "data": {"key": "value"}}

    cache_inventory = CacheInventory(
        hosts=hosts_dict, groups=groups_dict, defaults=defaults_dict
    )

    inventory = cache_inventory.load()

    assert inventory.hosts["host1"].hostname == "host1.example.com"
    assert inventory.hosts["host1"].data == {"key": "value"}
    assert inventory.groups["group1"].data == {"key": "value"}
    assert inventory.defaults.hostname == "hostname"
    assert inventory.defaults.hostname != "not the right hostname"
    assert inventory.defaults.data == {"key": "value"}


def test_empty_cache_inventory_load():
    hosts_dict: Dict[str, Dict[str, Any]] = {}
    groups_dict: Dict[str, Dict[str, Any]] = {}
    defaults_dict: Dict[str, Any] = {}

    cache_inventory = CacheInventory(
        hosts=hosts_dict, groups=groups_dict, defaults=defaults_dict
    )

    inventory = cache_inventory.load()

    assert inventory is not None
    assert inventory.hosts is not None
    assert inventory.groups is not None
    assert inventory.defaults is not None
