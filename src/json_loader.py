import os
import json
import aiofiles
import logging

# Set up logging for error and info messages
logger = logging.getLogger(__name__)

async def load_json_data(config_path):
    try:
        # Ensure that config_path is supplied
        if not config_path:
            raise ValueError("config_path is required but not provided.")

        # Check if the directory exists
        if not os.path.isdir(config_path):
            raise FileNotFoundError(f"Config directory '{config_path}' does not exist.")

        # List all files in the directory
        files = os.listdir(config_path)
        
        # Find the first file that matches the criteria
        json_file = next((file for file in files if file.startswith('manualREW') and file.endswith('.ady')), None)
        
        if not json_file:
            logger.error('Error loading calibration file: No file starting with "manualREW" and ending with ".ady" found.')
            return None

        # Full path to the JSON file
        json_file_path = os.path.join(config_path, json_file)

        # Read the file asynchronously
        async with aiofiles.open(json_file_path, mode='r', encoding='utf-8') as file:
            file_data = await file.read()

        # Parse the JSON data
        json_data = json.loads(file_data)
        logger.info('Loaded calibration file.')

        return json_data

    except Exception as err:
        logger.error('Error loading calibration file: %s', err)
        return None

import re

def get_reference_volume(json_data):
    """
    Extracts the reference volume from the 'title' field of the given JSON data.

    Args:
        json_data (dict): A dictionary containing the 'title' string.
    
    Returns:
        int or None: The extracted reference volume as an integer, or None if no match is found or title is missing.
    """
    # Retrieve the title from the json_data, return None if title is not present
    title = json_data.get('title', '')
    
    # Improved regex to handle optional spaces between 'MV' and 'dB'
    match = re.search(r'MV\s*(-?\d+)\s*dB', title)
    
    # Returning None if no match is found, otherwise converting the match to an integer
    return int(match.group(1)) if match else None


def get_speaker_levels(json_data):
    """
    Processes JSON data to generate speaker levels for each channel, excluding certain predefined channels.

    Args:
        json_data (dict): A dictionary containing detected channel data.
    
    Returns:
        dict: A dictionary of speaker levels keyed by channel command ID, rounded to 1 decimal place.
    """
    # Exclude specific channels based on predefined command IDs
    excluded_channels = {'FL', 'FR', 'C'}  # Use a set for faster lookup
    speaker_levels = {}

    # Ensure 'detectedChannels' exists and is iterable
    channels = json_data.get('detectedChannels', [])
    
    for channel in channels:
        command_id = channel.get('commandId')

        # Trim the trailing 'A' from 'SLA' or 'SRA' to match naming conventions
        if command_id == "SLA" or command_id == "SRA":
            command_id = command_id[:-1]

        custom_level = channel.get('customLevel')
        
        # Validate that the required fields exist
        if command_id and custom_level is not None:
            # Exclude specified channels and those starting with 'SW'
            if command_id not in excluded_channels and not command_id.startswith('SW'):
                try:
                    # Round the custom level to 1 decimal place
                    speaker_levels[command_id] = round(float(custom_level), 1) + 50
                except ValueError:
                    # Handle the case where custom_level is not a valid float
                    logger.warning(f"Invalid custom level for {command_id}: {custom_level}")
    
    return speaker_levels
