import os
import json
import logging
from .json_loader import get_reference_volume, get_speaker_levels

logger = logging.getLogger(__name__)

latest_adjustment = None

MIN_LEVEL = 38
MAX_LEVEL = 62

half_change_speakers = {}
quarter_change_speakers = {}


def load_speaker_config():

    default_speaker_config = json.dumps(
        {
            "half": ["SL", "SR", "SBL", "SBR", "SB"],
            "quarter": [
                "FHL",
                "FHR",
                "FWL",
                "FWR",
                "TFL",
                "TFR",
                "TML",
                "TMR",
                "TRL",
                "TRR",
                "RHL",
                "RHR",
                "FDL",
                "FDR",
                "SDL",
                "SDR",
                "BDL",
                "BDR",
                "SHL",
                "SHR",
                "TS",
                "CH",
            ],
        }
    )

    speaker_config_json = os.getenv("SPEAKER_CONFIG", default_speaker_config)
    speaker_config = json.loads(speaker_config_json)

    half_change_speakers = set(speaker_config.get("half", []))
    quarter_change_speakers = set(speaker_config.get("quarter", []))

    overlap = half_change_speakers.intersection(quarter_change_speakers)
    if overlap:
        raise ValueError(
            f"Invalid configuration: Overlap detected in speaker sets. Conflicting speakers: {overlap}"
        )

    return half_change_speakers, quarter_change_speakers


def format_volume(db_volume: float) -> str:
    """
    Format a dB volume into a string which the receiver understands.

    A dB volume could be 50.5dB which should be formatted into 505
    """
    # Check if the volume is an integer
    if db_volume.is_integer():
        # Return the integer formatted as a string without decimals
        return str(int(db_volume))
    else:
        # Multiply by 10, round the result, and return it as a string
        return str(db_volume).replace(".", "")


def parse_volume(mv_value: int) -> float:
    """
    Parse the main volume from the string.

    If the value has 3 digits, it represents a volume with decimal points (e.g., '505' means 50.5 dB).
    If the value has 2 digits, it represents a whole number volume (e.g., '50' means 50 dB).
    """
    return float(mv_value) / 10 if len(mv_value) == 3 else float(mv_value)


def calculate_reference(reference_volume):
    """
    The reference volume informed max boosted amount.
    This is the dB value (Example 5.5 at 65 reference volume) which will be reduced at the lowest relative volumes.
    The calculate_adjustment function serves to calculate how much less to boost in between this value and the reference volume.
    """
    return 0.2 * (reference_volume - 55) + 3.5


# Function to calculate the adjustment factor based on current and reference volume
def calculate_adjustment(absolute_volume, reference_volume):
    adjustment_factor = 0
    if absolute_volume >= reference_volume:
        return 0
    elif absolute_volume >= 55:
        adjustment_factor = 0.2 * absolute_volume - 7.5
    elif absolute_volume >= 50:
        adjustment_factor = 0.5 * absolute_volume - 24
    elif absolute_volume > 49:
        adjustment_factor = 0.5
    else:
        adjustment_factor = 0

    # Subtract the boosted value from the reference value informed amount
    adjustment_factor = calculate_reference(reference_volume) - adjustment_factor

    # Round to nearest 0.5
    adjustment_factor = int((adjustment_factor * 2) + 0.5) / 2
    # adjustment_factor = round(adjustment_factor * 2) / 2

    # Negative values not allowed
    adjustment_factor = max(adjustment_factor, 0)

    return adjustment_factor


# Function to apply volume adjustment to the speakers
async def adjust_speaker_volumes(
    initial_speaker_levels, adjustment_factor, send_adjustments, reset: bool
):

    adjustments = []  # List to store the formatted adjustment strings as tuples
    adjustment_type = None

    logger.info(f"Adjustment factor: {adjustment_factor}")
    for speaker, initial_level in initial_speaker_levels.items():
        if reset == True:
            adjustment_type = "Resetting adjustment"
            adjusted_level = initial_level + adjustment_factor
        elif speaker in quarter_change_speakers:
            adjustment_type = "Quarter adjustment"
            quarter_adjustment_factor = round(adjustment_factor * 0.5 * 2) / 2
            adjusted_level = initial_level + quarter_adjustment_factor
        elif speaker in half_change_speakers:
            adjustment_type = "Half adjustment"
            adjusted_level = initial_level + adjustment_factor
        else:
            continue

        # Cap and round new level
        adjusted_level = max(MIN_LEVEL, min(MAX_LEVEL, (round(adjusted_level * 2) / 2)))

        # Info about what changes we are doing
        logger.info(
            f"{speaker}: {adjustment_type}, Initial {initial_level - 50}dB, Adjustment {adjusted_level - initial_level}dB, Final {adjusted_level - 50}dB"
        )

        # Format the adjustments for sending via telnet
        adjustments.append(
            f"SSLEV{speaker} {format_volume(adjusted_level)}",
        )

    # Send all adjustments after the loop
    if adjustments:

        # Send the adjustments
        await send_adjustments(adjustments)


# Main function to trigger the adjustment logic when needed
async def on_volume_change(
    absolute_volume, reference_volume, initial_speaker_levels, send_adjustments
):

    global latest_adjustment

    adjustment_factor = calculate_adjustment(absolute_volume, reference_volume)

    if latest_adjustment != adjustment_factor:
        logger.info(
            f"Applying surround/height boost correction: {round(adjustment_factor * 2) / 2}dB based on main volume: {absolute_volume}dB vs reference volume: {reference_volume}dB"
        )
        await adjust_speaker_volumes(
            initial_speaker_levels, adjustment_factor, send_adjustments, False
        )
        latest_adjustment = adjustment_factor
    else:
        logger.info(
            f"No adjustment needed. Calculated adjustment factor is the same as previous volume: {adjustment_factor}dB"
        )


# Example usage when volume change callback is triggered:
async def handle_volume_change_callback(absolute_volume, json_data, send_adjustments):
    global half_change_speakers
    global quarter_change_speakers

    # Try to get the REFERENCE_VOLUME environment variable as an integer
    reference_volume_env = os.getenv("REFERENCE_VOLUME")
    if reference_volume_env and reference_volume_env.isdigit():
        reference_volume = int(reference_volume_env)
        logger.info("Retrieving reference volume from environment variable")
    else:
        # Fallback if REFERENCE_VOLUME is empty or not a valid integer
        reference_volume = get_reference_volume(json_data)
        logger.info("Retrieving reference volume from ady file")
    try:
        half_change_speakers, quarter_change_speakers = load_speaker_config()
    except ValueError as e:
        logger.error(e)

    if reference_volume is not None:
        initial_speaker_levels = get_speaker_levels(json_data)
        await on_volume_change(
            absolute_volume, reference_volume, initial_speaker_levels, send_adjustments
        )
    else:
        logger.error("Reference volume not found")
