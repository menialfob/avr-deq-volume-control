from json_loader import get_reference_volume, get_speaker_levels
import logging

logger = logging.getLogger(__name__)

MIN_LEVEL = 38
MAX_LEVEL = 62
latest_adjustment = None

half_change_speakers = {'SL', 'SR', 'SBL', 'SBR', 'SB'}
quarter_change_speakers = {'FHL', 'FHR', 'FWL', 'FWR', 'TFL', 'TFR', 'TML', 'TMR', 'TRL', 'TRR', 'RHL', 'RHR', 'FDL', 'FDR', 'SDL', 'SDR', 'BDL', 'BDR', 'SHL', 'SHR', 'TS', 'CH'}

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
        return str(db_volume).replace('.', '')


def parse_volume(mv_value: int) -> float:
    """
    Parse the main volume from the string.

    If the value has 3 digits, it represents a volume with decimal points (e.g., '505' means 50.5 dB).
    If the value has 2 digits, it represents a whole number volume (e.g., '50' means 50 dB).
    """
    return float(mv_value) / 10 if len(mv_value) == 3 else float(mv_value)

# Function to calculate the adjustment factor based on current and reference volume
def calculate_adjustment(absolute_volume, reference_volume):
    adjustment_factor = 0
    if absolute_volume >= reference_volume:
        return 0
    elif absolute_volume >= 55:
        adjustment_factor = (abs(reference_volume - absolute_volume) * 2) * 0.1
    elif absolute_volume >= 50:
        adjustment_factor = (abs(reference_volume - 55) * 2) * 0.1 + (abs(55 - absolute_volume) * 2) * 0.25
    elif absolute_volume >= 49:
        adjustment_factor = (abs(reference_volume - 55) * 2) * 0.1 + (abs(55 - 50) * 2) * 0.25 + (abs(50 - max(absolute_volume, 49)) * 2) * 0.5
    else:
        adjustment_factor = (abs(reference_volume - 55) * 2) * 0.1 + (abs(55 - 50) * 2) * 0.25 + (abs(50 - 49) * 2) * 0.5
    
    return round(-adjustment_factor * 2) / 2

# Function to apply volume adjustment to the speakers
async def adjust_speaker_volumes(initial_speaker_levels, adjustment_factor, send_adjustments):

    adjustments = []  # List to store the formatted adjustment strings as tuples

    logger.info(f"Adjustment factor: {adjustment_factor}")
    for speaker, initial_level in initial_speaker_levels.items():
        if speaker in quarter_change_speakers:
            quarter_adjustment_factor = round(adjustment_factor * 0.5 * 2) / 2
            # quarter_adjustment_factor = (round(adjustment_factor * 0.5 * 2) / 2)
            adjusted_level = initial_level + quarter_adjustment_factor
        else:
            adjusted_level = initial_level + adjustment_factor
        
        # Cap and round new level
        adjusted_level = max(MIN_LEVEL, min(MAX_LEVEL, (round(adjusted_level * 2) / 2))) 

        # Info about what changes we are doing
        logger.info(f'{speaker}: Initial {initial_level - 50}dB, Adjustment {adjusted_level - initial_level}dB, Final {adjusted_level - 50}dB')

        # Format the adjustments for sending via telnet
        adjustments.append(f"SSLEV{speaker} {format_volume(adjusted_level)}",)

    # Send all adjustments after the loop
    if adjustments:

        # Send the adjustments
        await send_adjustments(adjustments)

# Main function to trigger the adjustment logic when needed
async def on_volume_change(absolute_volume, reference_volume, initial_speaker_levels, send_adjustments):

    global latest_adjustment

    adjustment_factor = calculate_adjustment(absolute_volume, reference_volume)
    
    if latest_adjustment != adjustment_factor:
        logger.info(f"Applying surround/height boost correction: {round(adjustment_factor * 2) / 2}dB based on main volume: {absolute_volume}dB vs reference volume: {reference_volume}dB")
        await adjust_speaker_volumes(initial_speaker_levels, adjustment_factor, send_adjustments)
        latest_adjustment = adjustment_factor
    else:
        logger.info(f'No adjustment needed. Calculated adjustment factor is the same as previous volume: {adjustment_factor}dB')

# Example usage when volume change callback is triggered:
async def handle_volume_change_callback(absolute_volume, json_data, send_adjustments):
    reference_volume = get_reference_volume(json_data)
    
    if reference_volume is not None:
        initial_speaker_levels = get_speaker_levels(json_data)
        await on_volume_change(absolute_volume, reference_volume, initial_speaker_levels, send_adjustments)
    else:
        logger.warning("Reference volume not found in title")
