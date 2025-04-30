from typing import Any, Dict, List, Literal
from pathlib import Path

import typer
from ruamel.yaml import YAML, CommentedMap


def get_host_data(
    platform: Literal["ios", "nxos_ssh", "eos", "junos", "iosxr"],
) -> Dict[str, Any]:

    # connection_options = CommentedMap(
    #     {
    #         "napalm": CommentedMap({"extras": CommentedMap()}),
    #         "netmiko": CommentedMap({"extras": CommentedMap()}),
    #     }
    # )

    # if platform == "iosxr":
    #     connection_options["napalm"]["platform"] = "iosxr_netconf"
    #     option_args = CommentedMap()
    #     option_args.yaml_add_eol_comment("Workaround for ncclient")
    #     connection_options["napalm"]["extras"]["optional_args"] = option_args

    return {
        # "platform": platform,
        "hostname": "127.0.0.1",
        "groups": [platform],
        # "connection_options": connection_options,
    }


def get_group_data(
    platform: Literal["ios", "nxos_ssh", "eos", "junos", "iosxr"],
) -> CommentedMap:

    connection_options = CommentedMap(
        {
            "napalm": CommentedMap({"extras": CommentedMap()}),
            "netmiko": CommentedMap({"extras": CommentedMap()}),
        }
    )

    if platform == "iosxr":
        connection_options["napalm"]["platform"] = "iosxr_netconf"
        option_args = CommentedMap()
        option_args.yaml_add_eol_comment("Workaround for ncclient")
        connection_options["napalm"]["extras"]["optional_args"] = option_args

    group = CommentedMap(
        {
            "platform": platform,
            "connection_options": connection_options,
        }
    )
    group.insert(0, "username", "admin")
    group.insert(
        1,
        "password",
        "admin",
        comment="Consider using a transform_function: e.g. "
        "https://github.com/nornir-automation/nornir_utils/blob/master/docs/html/tutorials/load_credentials.ipynb",  # noqa: E501
    )
    return group


def get_nornir_config(inventory_dir: Path) -> CommentedMap:
    inventory = CommentedMap(
        {
            "plugin": "SimpleInventory",
            "options": CommentedMap(
                {
                    "hosts_file": str(inventory_dir / "hosts.yaml"),
                    "groups_file": str(inventory_dir / "groups.yaml"),
                }
            ),
        }
    )
    inventory.insert(
        2,
        "transform_function",
        None,
        comment='consider using "load_credentials" from nornir_utils',
    )
    config = CommentedMap(
        {
            "inventory": inventory,
            "runner": CommentedMap(
                {
                    "plugin": "threaded",
                    "options": CommentedMap(
                        {
                            "num_workers": 100,
                        }
                    ),
                }
            ),
        },
    )
    return config


def get_lldp_neighbors_count_test(hosts: List[str]) -> List[Dict[str, Any]]:
    lldp_neighbors_data = []
    for host in hosts:
        test_data = CommentedMap(
            {
                "host": host,
            }
        )
        test_data.insert(
            1,
            "neighbor_count",
            3,
            comment="Number of LLDP neighbors need to be updated",
        )
        lldp_neighbors_data.append(test_data)
    lldp_neighbors = [
        {
            "test_class": "TestNapalmLldpNeighborsCount",
            "test_data": lldp_neighbors_data,
        },
    ]
    return lldp_neighbors


def nuts_init(
    test_dir: Path = typer.Option(
        help="Location for test files.",
        prompt=True,
        default="./tests",
        show_default=True,
        writable=True,
        file_okay=False,
        dir_okay=True,
    ),
    nornir_config: Path = typer.Option(
        help="Location for nornir config file.",
        prompt="nornir config file",
        show_default=True,
        default="./nr_config.yaml",
        writable=True,
        file_okay=True,
        dir_okay=False,
    ),
    inventory_dir: Path = typer.Option(
        help="Location for inventory files.",
        prompt="inventory directory",
        show_default=True,
        default="./inventory",
        writable=True,
        file_okay=False,
        dir_okay=True,
    ),
    create_simple_inventory: bool = typer.Option(
        help="Create a simple inventory.",
        prompt="create simple inventory",
        show_default=True,
        default=False,
    ),
    cisco_xe: bool = typer.Option(
        help="Add a Cisco XE host to the inventory",
        prompt="add cisco xe host",
        show_default=True,
        default=False,
    ),
    juniper_junos: bool = typer.Option(
        help="Add a Juniper Junos host to the inventory",
        prompt="add Juniper Junos host",
        show_default=True,
        default=False,
    ),
    arista_eos: bool = typer.Option(
        help="Add a Arista EOS host to the inventory",
        prompt="add Arista EOS host",
        show_default=True,
        default=False,
    ),
    cisco_nxos: bool = typer.Option(
        help="Add a Cisco NX host to the inventory",
        prompt="add Cisco NX host",
        show_default=True,
        default=False,
    ),
    cisco_xr: bool = typer.Option(
        help="Add a Cisco XR host to the inventory",
        prompt="add Cisco XR host",
        show_default=True,
        default=False,
    ),
) -> None:
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)

    hosts = CommentedMap()
    if cisco_xe:
        hosts["cisco-xe-demo-01"] = get_host_data("ios")
    if arista_eos:
        hosts["arista-eos-demo-01"] = get_host_data("eos")
    if juniper_junos:
        hosts["juniper-junos-demo-01"] = get_host_data("junos")
    if cisco_nxos:
        hosts["cisco-nx-demo-01"] = get_host_data("nxos_ssh")
    if cisco_xr:
        hosts["cisco-xr-demo-01"] = get_host_data("iosxr")

    groups = CommentedMap()
    if cisco_xe:
        groups["ios"] = get_group_data("ios")
    if arista_eos:
        groups["eos"] = get_group_data("eos")
    if juniper_junos:
        groups["junos"] = get_group_data("junos")
    if cisco_nxos:
        groups["nxos_ssh"] = get_group_data("nxos_ssh")
    if cisco_xr:
        groups["iosxr"] = get_group_data("iosxr")

    if create_simple_inventory:
        inventory_dir = Path("inventory")
        inventory_dir.mkdir(parents=True, exist_ok=True)
        with (inventory_dir / "hosts.yaml").open("w") as f:
            yaml.dump(hosts, f)
        with (inventory_dir / "groups.yaml").open("w") as f:
            yaml.dump(groups, f)

    with nornir_config.open("w") as f:
        yaml.dump(get_nornir_config(inventory_dir), f)

    test_dir.mkdir(parents=True, exist_ok=True)
    lldp_neighbors = get_lldp_neighbors_count_test(hosts.keys())
    with (test_dir / "test_lldp_neighbors_demo.yaml").open("w") as f:
        yaml.dump(lldp_neighbors, f)


def run() -> None:
    typer.run(nuts_init)


if __name__ == "__main__":
    run()
