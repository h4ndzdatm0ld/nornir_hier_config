"""Test Execution of Hier Remediation Tasks."""
from datetime import datetime

from nornir_utils.plugins.functions import print_result

from nornir_hier_config.plugins.tasks import remediation

SINGLE_XR_DEVICE = "PHX_LAB_01_XR"
SINGLE_XE_DEVICE = "PHX_LAB_02_XE"
NOW = datetime.now()


def test_remediation_simple(nornir, configs):
    """Testing success of a simple execution of remediaton task.

    Remediation config already exists, no diff."""
    nr = nornir.filter(name=SINGLE_XR_DEVICE)
    test_path = f"{configs}/XR/simple_test_case"

    result = nr.run(
        remediation,
        running_config=f"{test_path}/running_config.txt",
        generated_config=f"{test_path}/intended_config.txt",
        remediation_config=f"{test_path}/remediation_config.txt",
    )
    assert not result[SINGLE_XR_DEVICE][0].failed
    assert not result[SINGLE_XR_DEVICE][0].diff


def test_remediation_simple_with_diff(nornir, configs):
    """Testing success of a simple execution of remediaton task.

    Remediation config doesn't exist, check diff."""
    nr = nornir.filter(name=SINGLE_XR_DEVICE)
    test_path = f"{configs}/XR/simple_test_case"

    result = nr.run(
        remediation,
        running_config=f"{test_path}/running_config.txt",
        generated_config=f"{test_path}/intended_config.txt",
        remediation_config=f"{test_path}/test_output/new-remediation-{NOW}.txt",
    )
    assert not result[SINGLE_XR_DEVICE][0].failed
    assert result[SINGLE_XR_DEVICE][0].diff


def test_remediation_missing_args(nornir, configs):
    """Testing failure, missing required args."""
    nr = nornir.filter(name=SINGLE_XR_DEVICE)
    test_path = f"{configs}/XR/simple_test_case"

    result = nr.run(
        remediation,
        running_config="",
        generated_config="",
        remediation_config=f"{test_path}/remediation_config.txt",
    )
    assert result[SINGLE_XR_DEVICE][0].failed
    assert not result[SINGLE_XR_DEVICE][0].diff


def test_remediation_config_generated_strings(nornir, configs):
    """Testing success remediation from strings not files."""
    nr = nornir.filter(name=SINGLE_XR_DEVICE)
    test_path = f"{configs}/XR/simple_test_case"

    running_config = """
    !
    hostname AS65000_PE1
    address-family ipv4 unicast
    !
    line console
    exec-timeout 0 0
    session-timeout 0
    !
    line default
    exec-timeout 0 0
    session-timeout 0
    transport input ssh
    !
    interface Loopback0
    description SYSTEM_LO_IP
    ipv4 address 172.16.0.11 255.255.255.255
    !
    interface Loopback33
    ipv4 address 3.3.3.3 255.255.255.255
    !
    interface Loopback100
    ipv4 address 1.1.1.1 255.255.255.255
    !
    interface Loopback123
    ipv4 address 1.2.3.4 255.255.255.255
    !
    interface MgmtEth0/0/CPU0/0
    ipv4 address dhcp
    !
    interface GigabitEthernet0/0/0/0
    description TO_CORE_PE2
    !
    interface GigabitEthernet0/0/0/1
    description TO_AS65001_CE1
    ipv4 address 10.1.0.1 255.255.255.254
    !
    interface GigabitEthernet0/0/0/1.1001
    description TO_AS65001_CE1
    ipv4 address 10.1.0.1 255.255.255.254
    encapsulation dot1q 1001
    !
    interface GigabitEthernet0/0/0/2
    description TO_AS65001_CE2
    ipv4 address 10.1.0.7 255.255.255.254
    !
    interface GigabitEthernet0/0/0/2.1001
    description TO_AS65001_CE2
    ipv4 address 10.1.0.7 255.255.255.254
    encapsulation dot1q 1001
    !
    interface GigabitEthernet0/0/0/3
    description TO_EDGE_PE2
    ipv4 address 10.0.0.0 255.255.255.254
    !
    interface GigabitEthernet0/0/0/4
    description TO_CORE_P1
    ipv4 address 10.0.0.2 255.255.255.254
    !
    interface GigabitEthernet0/0/0/5
    shutdown
    !
    interface GigabitEthernet0/0/0/6
    shutdown
    !
    route-policy PL-iBGP-RR-OUT
    set next-hop self
    end-policy
    !
    route-policy PL-EBGP-CE1-OUT
    set med 100
    pass
    end-policy
    !
    route-policy PL-EBGP-CE2-OUT
    set med 200
    pass
    end-policy
    !
    route-policy PL-EBGP-65001-IN
    pass
    end-policy
    !
    route-policy PL-EBGP-65001-OUT
    pass
    end-policy
    !
    router static
    address-family ipv4 unicast
    0.0.0.0/0 Null0
    0.0.0.0/0 192.168.2.1
    192.168.0.0/23 192.168.2.1
    192.168.4.0/23 192.168.2.1
    !
    !
    router isis core
    is-type level-2-only
    net 49.0000.1720.1600.0011.00
    address-family ipv4 unicast
    metric-style wide
    mpls traffic-eng level-2-only
    maximum-paths 8
    !
    interface Loopback0
    passive
    address-family ipv4 unicast
    !
    !
    interface GigabitEthernet0/0/0/3
    point-to-point
    address-family ipv4 unicast
    !
    !
    interface GigabitEthernet0/0/0/4
    point-to-point
    address-family ipv4 unicast
    !
    !
    !
    router bgp 65000
    bgp router-id 172.16.0.11
    address-family ipv4 unicast
    additional-paths receive
    additional-paths send
    !
    neighbor-group RR
    remote-as 65000
    update-source Loopback0
    address-family ipv4 unicast
    route-policy PL-iBGP-RR-OUT out
    !
    !
    neighbor 10.1.0.0
    remote-as 65001
    update-source Loopback0
    address-family ipv4 unicast
    route-policy PL-EBGP-65001-IN in
    route-policy PL-EBGP-CE1-OUT out
    !
    !
    neighbor 10.1.0.6
    remote-as 65001
    update-source Loopback0
    address-family ipv4 unicast
    route-policy PL-EBGP-65001-IN in
    route-policy PL-EBGP-CE2-OUT out
    !
    !
    neighbor 172.16.0.201
    use neighbor-group RR
    !
    neighbor 172.16.0.202
    use neighbor-group RR
    !
    !
    mpls oam
    !
    mpls ldp
    interface GigabitEthernet0/0/0/3
    !
    interface GigabitEthernet0/0/0/4
    !
    !
    xml agent tty
    iteration off
    !
    netconf agent tty
    !
    netconf-yang agent
    ssh
    !
    lldp
    !
    ssh server v2
    ssh server netconf vrf default
    end
    """
    generated_config = """
    !
    hostname AS65000_PE1
    address-family ipv4 unicast
    !
    line console
    exec-timeout 0 0
    session-timeout 0
    !
    line default
    exec-timeout 0 0
    session-timeout 0
    transport input ssh
    !
    ntp
     server 10.10.10.1
     source GigabitEthernet0/0/0/1
    !
    interface Loopback0
    description SYSTEM_LO_IP
    ipv4 address 172.16.0.11 255.255.255.255
    !
    interface Loopback33
    ipv4 address 3.3.3.3 255.255.255.255
    !
    interface Loopback100
    ipv4 address 1.1.1.1 255.255.255.255
    !
    interface Loopback123
    ipv4 address 1.2.3.4 255.255.255.255
    !
    interface MgmtEth0/0/CPU0/0
    ipv4 address dhcp
    !
    interface GigabitEthernet0/0/0/0
    description TO_CORE_PE2
    !
    interface GigabitEthernet0/0/0/1
    description TO_AS65001_CE1
    ipv4 address 10.1.0.1 255.255.255.254
    !
    interface GigabitEthernet0/0/0/1.1001
    description TO_AS65001_CE1
    ipv4 address 10.1.0.1 255.255.255.254
    encapsulation dot1q 1001
    !
    interface GigabitEthernet0/0/0/2
    description TO_AS65001_CE2
    ipv4 address 10.1.0.7 255.255.255.254
    !
    interface GigabitEthernet0/0/0/2.1001
    description TO_AS65001_CE2
    ipv4 address 10.1.0.7 255.255.255.254
    encapsulation dot1q 1001
    !
    interface GigabitEthernet0/0/0/3
    description TO_EDGE_PE2
    ipv4 address 10.0.0.0 255.255.255.254
    !
    interface GigabitEthernet0/0/0/4
    description TO_CORE_P1
    ipv4 address 10.0.0.2 255.255.255.254
    !
    interface GigabitEthernet0/0/0/5
    shutdown
    !
    interface GigabitEthernet0/0/0/6
    shutdown
    !
    route-policy PL-iBGP-RR-OUT
    set next-hop self
    end-policy
    !
    route-policy PL-EBGP-CE1-OUT
    set med 100
    pass
    end-policy
    !
    route-policy PL-EBGP-CE2-OUT
    set med 200
    pass
    end-policy
    !
    route-policy PL-EBGP-65001-IN
    pass
    end-policy
    !
    route-policy PL-EBGP-65001-OUT
    pass
    end-policy
    !
    router static
    address-family ipv4 unicast
    0.0.0.0/0 Null0
    0.0.0.0/0 192.168.2.1
    192.168.0.0/23 192.168.2.1
    192.168.4.0/23 192.168.2.1
    !
    !
    router isis core
    is-type level-2-only
    net 49.0000.1720.1600.0011.00
    address-family ipv4 unicast
    metric-style wide
    mpls traffic-eng level-2-only
    maximum-paths 8
    !
    interface Loopback0
    passive
    address-family ipv4 unicast
    !
    !
    interface GigabitEthernet0/0/0/3
    point-to-point
    address-family ipv4 unicast
    !
    !
    interface GigabitEthernet0/0/0/4
    point-to-point
    address-family ipv4 unicast
    !
    !
    !
    router bgp 65000
    bgp router-id 172.16.0.11
    address-family ipv4 unicast
    additional-paths receive
    additional-paths send
    !
    neighbor-group RR
    remote-as 65000
    update-source Loopback0
    address-family ipv4 unicast
    route-policy PL-iBGP-RR-OUT out
    !
    !
    neighbor 10.1.0.0
    remote-as 65001
    update-source Loopback0
    address-family ipv4 unicast
    route-policy PL-EBGP-65001-IN in
    route-policy PL-EBGP-CE1-OUT out
    !
    !
    neighbor 10.1.0.6
    remote-as 65001
    update-source Loopback0
    address-family ipv4 unicast
    route-policy PL-EBGP-65001-IN in
    route-policy PL-EBGP-CE2-OUT out
    !
    !
    neighbor 172.16.0.201
    use neighbor-group RR
    !
    neighbor 172.16.0.202
    use neighbor-group RR
    !
    !
    mpls oam
    !
    mpls ldp
    interface GigabitEthernet0/0/0/3
    !
    interface GigabitEthernet0/0/0/4
    !
    !
    xml agent tty
    iteration off
    !
    netconf agent tty
    !
    netconf-yang agent
    ssh
    !
    lldp
    !
    ssh server v2
    ssh server netconf vrf default
    end
    """
    result = nr.run(
        remediation,
        running_config=running_config,
        generated_config=generated_config,
        remediation_config=f"{test_path}/test_output/remediation_config-strings.txt",
    )
    assert not result[SINGLE_XR_DEVICE][0].failed


def test_remediation_with_options(nornir, configs):
    """Testing success with ios options from yaml file and tags."""
    nr = nornir.filter(name=SINGLE_XE_DEVICE)
    test_path = f"{configs}/XE/simple_test_case"
    extras = f"{configs}/hier_config_data"

    result = nr.run(
        remediation,
        running_config=f"{test_path}/running_config.txt",
        generated_config=f"{test_path}/intended_config.txt",
        remediation_config=f"{test_path}/test_output/remediation_config.txt",
        options=f"{extras}/ios_options.yml",
        tags=f"{extras}/ios_tags.yml",
    )
    assert not result[SINGLE_XE_DEVICE][0].failed
    assert result[SINGLE_XE_DEVICE][0].diff


def test_remediation_with_options_no_tags(nornir, configs):
    """Testing success with ios options from yaml file no tags"""
    nr = nornir.filter(name=SINGLE_XE_DEVICE)
    test_path = f"{configs}/XE/simple_test_case"
    extras = f"{configs}/hier_config_data"

    result = nr.run(
        remediation,
        running_config=f"{test_path}/running_config.txt",
        generated_config=f"{test_path}/intended_config.txt",
        remediation_config=f"{test_path}/test_output/remediation_config-with-options.txt",
        options=f"{extras}/ios_options.yml",
    )
    assert not result[SINGLE_XE_DEVICE][0].failed
    assert result[SINGLE_XE_DEVICE][0].diff
    print_result(result)


def test_remediation_with_both_exclude_ntp(nornir, configs):
    """Testing success with ios options,tags and exclude `ntp` tag."""
    nr = nornir.filter(name=SINGLE_XE_DEVICE)
    test_path = f"{configs}/XE/simple_test_case"
    extras = f"{configs}/hier_config_data"

    result = nr.run(
        remediation,
        running_config=f"{test_path}/running_config.txt",
        generated_config=f"{test_path}/intended_config.txt",
        remediation_config=f"{test_path}/test_output/remediation_config-no-ntp.txt",
        options=f"{extras}/ios_options.yml",
        tags=f"{extras}/ios_tags.yml",
        exclude_tags=["ntp"],
    )
    assert not result[SINGLE_XE_DEVICE][0].failed
    assert result[SINGLE_XE_DEVICE][0].diff
    assert "ntp" not in result[SINGLE_XE_DEVICE][0].diff["values_changed"]["root"]["diff"]


def test_remediation_no_remediation(nornir, configs):
    """Testing success no remediation specified."""
    nr = nornir.filter(name=SINGLE_XE_DEVICE)
    test_path = f"{configs}/XE/simple_test_case"
    extras = f"{configs}/hier_config_data"

    result = nr.run(
        remediation,
        running_config=f"{test_path}/running_config.txt",
        generated_config=f"{test_path}/intended_config.txt",
        options=f"{extras}/ios_options.yml",
        tags=f"{extras}/ios_tags.yml",
        exclude_tags=["ntp"],
    )
    assert result[SINGLE_XE_DEVICE][0].failed
    assert not result[SINGLE_XE_DEVICE][0].diff
