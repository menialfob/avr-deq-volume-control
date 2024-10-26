import asyncio
import denonavr
from adjustmentlogic import handle_volume_change_callback, parse_volume, adjust_speaker_volumes
from json_loader import load_json_data, get_speaker_levels
import logging
import os
import signal
import platform

debounce_task = None
latest_volume = None
json_data = None
shutdown_flag = False
tasks = set()  # Set to track ongoing tasks

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def debounce_send_volume(volume: str, delay: float = 5.0):
    """Debounce the volume and send only the latest after a delay."""
    global debounce_task, latest_volume
    latest_volume = volume
    if debounce_task is not None:
        debounce_task.cancel()

    debounce_task = asyncio.create_task(delayed_send_volume(delay))
    tasks.add(debounce_task)  # Track the task
    debounce_task.add_done_callback(tasks.discard)  # Remove from set when done

async def delayed_send_volume(delay: float):
    """Wait for the debounce delay, then send the latest volume."""
    global latest_volume
    try:
        await asyncio.sleep(delay)
        await handle_volume_change_callback(latest_volume, json_data, send_adjustments)
    except asyncio.CancelledError:
        logging.info("Delayed volume send task was cancelled.")

async def send_adjustments(adjustments, force_send=False):
    logger.info("Sending adjustments")
    try:
        await receiver.async_send_telnet_commands(*adjustments)
    except Exception as e:
        logger.error(f"Failed to send adjustments: {e}")

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

# async def handle_shutdown(loop, signame=None):
#     global shutdown_flag
#     if signame:
#         logger.info(signame)
#     shutdown_flag = True

async def handle_shutdown(loop, signame=None):
    global shutdown_flag
    logger.info(f"Handling shutdown due to {signame}")
    shutdown_flag = True

    # Await completion of the reset task explicitly if it's running
    if debounce_task and not debounce_task.done():
        debounce_task.cancel()
        try:
            await debounce_task
        except asyncio.CancelledError:
            logger.info("Debounce task canceled during shutdown.")

    # Reset speaker volumes explicitly
    await reset_speaker_volume(json_data)

    # Close the loop after reset to ensure all commands are sent
    loop.stop()

# Main entry point
def main():
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    if platform.system() != "Windows":
        for signame in {'SIGINT', 'SIGTERM'}:
            loop.add_signal_handler(
                getattr(signal, signame),
                lambda signame=signame: asyncio.create_task(handle_shutdown(loop, signame))
            )

    loop.run_until_complete(main_async())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt received, initiating shutdown...")
        loop.run_until_complete(handle_shutdown(loop, "KeyboardInterrupt"))
    finally:
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
