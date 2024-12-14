import pytest
import sys

sys.path.append("../src")

from adjustmentlogic import calculate_reference

from .test_input_output_data import reference_test_data

# Test data: Each tuple contains (input_value, expected_output)


@pytest.mark.parametrize("reference_volume, expected", reference_test_data)
def test_calculate_reference(reference_volume, expected):
    result = calculate_reference(reference_volume)
    assert result == pytest.approx(
        expected, rel=1e-2
    ), f"Failed for input: {reference_volume}"
