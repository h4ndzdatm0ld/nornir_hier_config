# Nornir Hier Config

[![codecov](https://codecov.io/gh/h4ndzdatm0ld/nornir_hier_config/branch/develop/graph/badge.svg?token=C8QDR45SJQ)](https://codecov.io/gh/h4ndzdatm0ld/nornir_hier_config)
[![Develop](https://github.com/h4ndzdatm0ld/nornir_hier_config/actions/workflows/ci.yml/badge.svg)](https://github.com/h4ndzdatm0ld/nornir_hier_config/actions/workflows/ci.yml/badge.svg)

## Documentation

[Documentation](https://h4ndzdatm0ld.github.io/nornir_hier_config/index.html) is self-generated from `develop` branch and is hosted with Github Pages.

### Hier Config

[Hier Config](https://github.com/netdevops/hier_config) is a python library to build remediation steps in CLI format after evaluating a running configuration to an intended configuration.

[Hier Config Documentation](https://netdevops.io/hier_config/) How to & general information.

## Installation

In order to use this Nornir Plugin, you will additionally need to install hier-config library from Pypi.

```bash
pip install hier-config
```
&
```bash
pip install nornir_hier_config
```

### Tasks

- `remediation` - Task available to use with Nornir to generate a remediation config.

## Examples

Below is an example of using the remediation task. A running_config, generated_config and remediation_config (file path to save remediation) are required args. The options, tags, include & exclude tags are able to be passed in as a path to a YAML file or can be set from Group Vars. Precedence to a YAML file is given if both options are present.

If you would like to see a few more examples, please head over to the `tests` directory and review the integration tests.

Snippet:

```python
    nr = nornir.filter(name="PHX-01-69")

    result = nr.run(
        remediation,
        running_config="running_config.txt",
        generated_config="intended_config.txt",
        remediation_config="remediation_config-no-ntp.txt",
        options="ios_options.yml",
        tags="ios_tags.yml",
        exclude_tags=["ntp"],
    )
```

### Group Vars

Unlike the Ansible collection which takes advantage of roles, the Nornir tasks uses Group Vars as the backup choice location if no YAML file is provided for several args. Lets take a look at our directory structure:

```bash
inventory_data
├── defaults.yml
├── groups.yml
└── hosts.yml

0 directories, 3 files
```

**Below is an example of two hosts, using two different groups: `iosxr` and `ios`.**

NOTE:
Any keys to be accessed from group vars must be under the `data` key and should map to the following:

```text
hier_options [Dict] - Hier Config Options for device platform

hier_tags [Dict] - Hier Config Tags for device platform

hier_include_tags [List] - Hier Config Include Tags for remediation output

hier_exclude_tags [List] - Hier Config Exclude Tags for remediation output
```

<details>
  <summary> Click to Expand! </summary>

```yaml
---
iosxr:
  username: "netconf"
  password: "NCadmin123"
  port: 830
  platform: "iosxr"
  data:
    hier_options:
      # Indicates the style of the configuration
      style: "iosxr"
      ordering:
        - lineage:
            - startswith: "no ipv4 access-list"
          order: 400
        - lineage:
            - startswith: "router bgp"
            - startswith: "no neighbor"
          order: 600
        - lineage:
            - startswith: "router bgp"
            - startswith: "address-family"
            - startswith: "no neighbor"
          order: 600

      # if there is a delta, overwrite these parents instead of one of their children
      sectional_overwrite: []
      # - lineage:
      #  - re_search: ^((ip|ipv4|ipv6) )?access-list

      sectional_overwrite_no_negate:
        - lineage:
            - startswith: "as-path-set"
        - lineage:
            - startswith: "prefix-set"
        - lineage:
            - startswith: "route-policy"
        - lineage:
            - startswith: "extcommunity-set"
        - lineage:
            - startswith: "community-set"

      parent_allows_duplicate_child: []
      # - lineage:
      #  - startswith: route-policy

      sectional_exiting:
        - lineage:
            - startswith: "router bgp"
            - startswith: "address-family"
          exit_text: "exit-address-family"

      # adds +1 indent to lines following start_expression and removes the +1 indent for lines following end_expression
      indent_adjust: []
      # - start_expression: ^\s*template
      #   end_expression: ^\s*end-template

      # substitions against the full multi-line config text
      full_text_sub: []
      # - search: 'banner\s(exec|motd)\s(\S)\n(.*\n){1,}(\2)'
      #   replace: ''

      # substitions against each line of the config text
      per_line_sub: []
      # - search: ^Building configuration.*
      #  replace: ''

      idempotent_commands_blacklist: []
      # - lineage:
      #  - lineage expression

      # These commands do not require negation, they simply overwrite themselves
      idempotent_commands:
        - lineage:
            - startswith: "router bgp"
            - endswith: "peer-group"
            # - lineage:
            # - startswith: "router bgp"
            # - re_search: "neighbor (\d+\.\d+\.\d+\.\d+) peer-group)"
      # - lineage:
      #  - startswith: interface
      #  - startswith: ipv4 address

      # Default when expression: list of lineage expressions
      negation_default_when: []
      # - lineage:
      #  - lineage expression

      # Negate substitutions: lineage expression -> negate with
      negation_negate_with: []
      # - lineage:
      #  - lineage expression
      #  use: command
    hier_tags:
      - lineage:
          - startswith:
              - "ipv4 access-list"
              - "no ipv4 access-list"
        add_tags: "push"
      - lineage:
          - startswith: "router bgp"
          - startswith: "address-family"
          - startswith:
              - "neighbor"
              - "no neighbor"
              - "maximum-paths"
              - "exit-address-family"
        add_tags: "push"
      - lineage:
          - startswith: "router bgp"
          - startswith:
              - "neighbor"
              - "no neighbor"
        add_tags: "push"
      - lineage:
          - startswith: "aaa"
        add_tags: "ignore"
ios:
  username: "developer"
  password: "C1sco12345"
  platform: "ios"
```

</details>

### Result Diff

Unlike the Ansible Collection, this Nornir task provides a friendly diff of what the remediation configuration will include. This happens if there is a change detected only. The underlying library providing the diff is [DeepDiff](https://deepdiff.readthedocs.io/en/latest/).

```bash
*************
* PHX_LAB_02_XE ** changed : True **********************************************
vvvv remediation ** changed : True vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv INFO
{ 'values_changed': { 'root': { 'diff': '--- \n'
                                        '+++ \n'
                                        '@@ -0,0 +1,5 @@\n'
                                        '+no ntp server 10.20.30.40\n'
                                        '+no ntp server 10.10.10.1\n'
                                        '+interface GigabitEthernet3\n'
                                        '+  ip address 192.168.0.100 '
                                        '255.255.255.0\n'
                                        '+  no shutdown',
                                'new_value': 'no ntp server 10.20.30.40\n'
                                             'no ntp server 10.10.10.1\n'
                                             'interface GigabitEthernet3\n'
                                             '  ip address 192.168.0.100 '
                                             '255.255.255.0\n'
                                             '  no shutdown',
                                'old_value': ''}}}
^^^^ END remediation ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
```

## Contributions

------------

No line of code shall go un tested! Any contribution will need to be accounted by the coverage report and satisfy all linting.

Linters:

- Fake8
- Black
- Yamllint
- Pylint
- Pydocstyle
- Bandit
- MyPy

### Testing

To test within a local docker environment

```bash
git clone https://github.com/h4ndzdatm0ld/nornir_hier_config
```

```bash
docker-compose build && docker-compose run test
```

To test locally with pytest

```bash
poetry install && poetry shell
```

```bash
pytest --cov=nornir_hier_config --color=yes --disable-pytest-warnings -vvv
```
