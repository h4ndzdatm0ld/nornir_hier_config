"""Test Execution of Hier Remediation Tasks."""
from nornir_utils.plugins.functions import print_result

from nornir_hier_config.plugins.tasks import remediation

SINGLE_XR_DEVICE = "PHX_LAB_01_XR"


def test_remediation_simple(nornir, configs):
    """Testing success of a simple execution of remediaton task."""
    nr = nornir.filter(name=SINGLE_XR_DEVICE)
    test_path = f"{configs}/XR/simple_test_case"

    result = nr.run(
        remediation,
        running_config=f"{test_path}/running_config.txt",
        generated_config=f"{test_path}/intended_config.txt",
        remediation_config=f"{test_path}/remediation_config.txt",
    )
    print_result(result)
