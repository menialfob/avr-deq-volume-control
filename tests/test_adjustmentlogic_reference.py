import pytest
from src.adjustmentlogic import calculate_reference

# Test data: Each tuple contains (input_value, expected_output)
reference_test_data = [
    (45, 1.5),
    (46, 1.7),
    (47, 1.9),
    (48, 2.1),
    (49, 2.3),
    (50, 2.5),
    (51, 2.7),
    (52, 2.9),
    (53, 3.1),
    (54, 3.3),
    (55, 3.5),
    (56, 3.7),
    (57, 3.9),
    (58, 4.1),
    (59, 4.3),
    (60, 4.5),
    (61, 4.7),
    (62, 4.9),
    (63, 5.1),
    (64, 5.3),
    (65, 5.5),
    (66, 5.7),
    (67, 5.9),
    (68, 6.1),
    (69, 6.3),
    (70, 6.5),
    (71, 6.7),
    (72, 6.9),
    (73, 7.1),
    (74, 7.3),
    (75, 7.5),
    (76, 7.7),
    (77, 7.9),
    (78, 8.1),
    (79, 8.3),
    (80, 8.5),
]


@pytest.mark.parametrize("reference_volume, expected", reference_test_data)
def test_calculate_reference(reference_volume, expected):
    result = calculate_reference(reference_volume)
    assert result == pytest.approx(
        expected, rel=1e-2
    ), f"Failed for input: {reference_volume}"
