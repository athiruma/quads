#!/usr/bin/env python3

import argparse
import logging

from quads.config import Config
from quads.server.dao.cloud import CloudDao
from quads.server.dao.host import HostDao
from quads.tools.external.ssh_helper import SSHHelper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")


def verify(cloud):
    _cloud_obj = CloudDao.get_cloud(cloud)
    logger.info(f"Cloud qinq: {_cloud_obj.qinq}")
    if not _cloud_obj:
        logger.error("Cloud not found.")
        return

    hosts = HostDao.filter_hosts(cloud=_cloud_obj)
    if args.all:
        hosts = [hosts[0]]

    for host in hosts:
        if args.all:
            logger.info(f"{host.name}:")
        if host and host.interfaces:
            interfaces = sorted(host.interfaces, key=lambda k: k["name"])
            for i, interface in enumerate(interfaces):
                ssh_helper = SSHHelper(interface.switch_ip, Config["junos_username"])
                try:
                    if interface == interfaces[-1]:
                        _, vlan_member_out = ssh_helper.run_cmd(
                            f"show configuration interfaces {interface.switch_port}"
                        )
                        vlan_member = vlan_member_out[0].split(";")[0].split()[1]
                        if vlan_member.startswith("QinQ"):
                            vlan_member = vlan_member[7:]
                    else:
                        _, vlan_member_out = ssh_helper.run_cmd(
                            f"show configuration vlans | display set | match {interface.switch_port}.0"
                        )
                        vlan_member = vlan_member_out[0].split()[2][4:].strip(",")
                except IndexError:
                    logger.warning(
                        "Could not determine the previous VLAN member for %s, switch %s, switch port %s "
                        % (
                            interface.name,
                            interface.switch_ip,
                            interface.switch_port,
                        )
                    )
                    vlan_member = 0

                ssh_helper.disconnect()

                logger.info(
                    f"Interface em{i+1} appears to be a member of VLAN {vlan_member}",
                )

        else:
            logger.error("The cloud has no hosts or the host has no interfaces defined")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="List switch configs for a cloud")
    parser.add_argument(
        "--cloud",
        dest="cloud",
        type=str,
        default=None,
        help="Cloud name to verify switch configuration for.",
        required=True,
    )
    parser.add_argument(
        "--all",
        action="store_true",
        default=False,
        help="List all hosts interfaces",
    )

    args = parser.parse_args()
    try:
        verify(args.cloud)
    except KeyboardInterrupt:
        pass
