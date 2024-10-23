import asyncio
import denonavr
from adjustmentlogic import handle_volume_change_callback, parse_volume, format_volume
from json_loader import load_json_data
import logging
import os

debounce_task = None
latest_volume = None
json_data = None

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def debounce_send_volume(volume: str, delay: float = 5.0):
    """Debounce the volume and send only the latest after a delay."""
    global debounce_task, latest_volume

    # Store the latest volume
    latest_volume = volume

    # If there's an existing debounce task, cancel it
    if debounce_task is not None:
        debounce_task.cancel()

    # Start a new debounce task
    debounce_task = asyncio.create_task(delayed_send_volume(delay))

async def delayed_send_volume(delay: float):
    """Wait for the debounce delay, then send the latest volume."""
    global latest_volume
    try:
        # Wait for the specified delay time
        await asyncio.sleep(delay)
        # After the wait, send the latest volume
        await handle_volume_change_callback(latest_volume, json_data, send_adjustments)
    except asyncio.CancelledError:
        # Task was cancelled (if a new volume change happened during the wait)
        pass

async def send_adjustments(adjustments):
    logger.info("Sending adjustments")
    await receiver.async_send_telnet_commands(*adjustments)

# Define the callback function
async def update_callback(zone, event, parameter):
    logger.info(f"Zone: {zone}, Event: {event}, Parameter: {parameter}")
    if zone == "Main" and event == "MV":

        await debounce_send_volume(parse_volume(parameter))
        # await handle_volume_change_callback(absolute_volume, json_data, send_adjustments)

# Function to set up the AVR connection and register callback
async def setup_volume_monitoring():
    await receiver.async_setup()
    await receiver.async_telnet_connect()
    receiver.register_callback("MV", update_callback)
    
    await receiver.async_update()  # Initial update to get the current state

# Main entry point
def main():
    try:
        # Create a new event loop if one doesn't already exist
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Run the setup asynchronously and register the callback
    loop.run_until_complete(main_async())

    # Now keep the loop running to listen for events
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Terminating connection.")
    finally:
        # Cleanup: close the loop when done
        loop.close()

# Function to run the async tasks
async def main_async():
    global json_data

    
    # Load the JSON calibration data
    config_path = os.getenv('CONFIG_PATH', 'config')
    if not config_path:
        raise ValueError("CONFIG_PATH environment variable is not set.")
    json_data = await load_json_data(config_path)

    # Set up AVR with the loaded JSON data
    await setup_volume_monitoring()

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    receiver = denonavr.DenonAVR(os.getenv('RECEIVER_IP', '192.168.1.142'))  # Define the receiver
    main()
