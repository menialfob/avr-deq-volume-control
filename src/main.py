import asyncio
import denonavr
from adjustmentlogic import handle_volume_change_callback, parse_volume, adjust_speaker_volumes
from json_loader import load_json_data, get_speaker_levels
import logging
import os
import signal

debounce_task = None
latest_volume = None
json_data = None
shutdown_flag = False

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

# Function to set up the AVR connection and register callback
async def setup_volume_monitoring():
    await receiver.async_setup()
    await receiver.async_telnet_connect()
    receiver.register_callback("MV", update_callback)
    
    await receiver.async_update()  # Initial update to get the current state

async def reset_speaker_volume(json_data):
    logger.info("Resetting speaker volumes to initial levels")
    initial_speaker_levels = get_speaker_levels(json_data)
    await adjust_speaker_volumes(initial_speaker_levels, 0, send_adjustments, True)

async def handle_shutdown(loop, signame=None):
    global shutdown_flag
    if signame:
        logger.info(signame)
    shutdown_flag = True

# Main entry point
def main():
    try:
        # Create a new event loop if one doesn't already exist
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    # Set signal handlers
    for signame in {'SIGINT', 'SIGTERM'}:
        loop.add_signal_handler(getattr(signal, signame), 
                                lambda signame=signame: asyncio.create_task(handle_shutdown(loop,signame)))

    # Run the setup asynchronously and register the callback
    loop.run_until_complete(main_async())

    # Now keep the loop running to listen for events
    try:
        while not shutdown_flag:
            loop.run_until_complete(asyncio.sleep(1))  # Run loop with periodic sleep checks
    finally:
        logger.info("Shutdown command received")
        logger.info("Resetting volumes to initial")

        # Resetting speaker levels with the same loop
        loop.run_until_complete(reset_speaker_volume(json_data))  

        # Cleaning up and shutting down
        loop.stop()
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()


# Function to run the async tasks
async def main_async():
    global json_data
    
    # Load the JSON calibration data
    config_path = os.getenv('CONFIG_PATH', 'config')
    json_data = await load_json_data(config_path)

    # Set up AVR with the loaded JSON data
    await setup_volume_monitoring()

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    # Get receiver IP from env variable
    receiver_ip = os.getenv('RECEIVER_IP')
    # Ensure that config_path is supplied
    if not receiver_ip:
        raise ValueError("Receiver IP is required but not provided. To set the environment variable use set RECEIVER_IP=<receiver ip> in Windows or export RECEIVER_IP=<receiver ip> in MacOS or Linux")
    receiver = denonavr.DenonAVR(receiver_ip)  # Define the receiver
    main()
