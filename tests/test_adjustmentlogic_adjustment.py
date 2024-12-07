import pytest

from src.adjustmentlogic import calculate_adjustment

from .test_input_output_data import absolute_values, expected_results, reference_values

# Table data


# Generate test cases
adjustment_test_cases = [
    (abs_val, ref_val, expected_results[row_idx][col_idx])
    for row_idx, abs_val in enumerate(absolute_values)
    for col_idx, ref_val in enumerate(reference_values)
]


@pytest.mark.parametrize(
    "absolute_value, reference_value, expected", adjustment_test_cases
)
def test_calculate_adjustment(absolute_value, reference_value, expected):
    result = calculate_adjustment(absolute_value, reference_value)
    assert result == pytest.approx(
        expected, rel=1e-2
    ), f"Failed for inputs: {absolute_value}, {reference_value}"
