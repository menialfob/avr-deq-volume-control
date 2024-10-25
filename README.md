# avr-deq-volume-control

`avr-deq-volume-control` is a Python implementation that automatically monitors volume changes on your AV Receiver and adjusts over-corrected channels influenced by the built-in DEQ (Dynamic EQ). 

The script is meant for use in conjunction with  **OCA's (ObsessiveCompulsiveAudiophile)** A1 EVO Nexus audyssey optimization script. 
The original Dynamic EQ adjustment script was likewise created by OCA, and this repository merely adapts and extends upon his concept by using a more robust networking library for interacting with the AVR.

You should watch OCA's [video on how to get started](https://www.youtube.com/watch?v=tNj-nWR-Yyo) with Nexus before using this solution.

## Features
- Automatically scans for volume changes on your AV Receiver
- Adjusts channels that are over-corrected by the built-in DEQ
- Error handling and retry policy for failed requests
- Docker implementation

## Getting Started

### Prerequisites

Make sure you have the following:

- Completed A1 EVO Nexus and generated an .ady file
- A Marantz or Denon receiver
- The IP address of the receiver (Found in Network -> Information on the receiver menu or in Windows -> View Network Devices & Computers -> Select your receiver -> Properties)

### Running with Docker

  Add the manualREW.ady file in a folder named "config" next to where you are running the command from. 
If you want to place it somewhere else, then change the volume (-v) parameter below.

```bash
docker run -d --name avr-control \
  -v $(pwd)/config:/app/config \
  -e CONFIG_PATH=/app/config \
  -e RECEIVER_IP=<RECEIVER_IP_ADDRESS>\
  ghcr.io/menialfob/avr-deq-volume-control:latest
```

### Running with Docker Compose

1. Ensure Docker and Docker Compose is installed

2. Create or copy the docker-compose.yml file from this repo

3. Edit the docker-compose file to set the environment variables with your receiver's IP and .ady location (Default in /config)

4. Copy the .ady file to your set location from step 3

5. Build and run the docker file
   ```bash
    docker compose up
    ```

### Manual installation using Python

1. Clone the repository:
    ```bash
    git clone https://github.com/menialfob/avr-deq-volume-control.git
    cd avr-deq-volume-control
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Copy the .ady file created by OCA's Nexus to the /config folder.

4. Run the script:
    ```bash
    python .src/main.py
    ```

### Usage

- Once the script is running, it will automatically monitor your AV Receiver for any volume changes and apply adjustments accordingly. 
- Make sure that your AV Receiver is connected to the same network as your computer, and that the DEQ functionality is enabled.

### Configuration

You need to set two environment variables to make it run properly:
- CONFIG_PATH (Relative path to the folder where your .ady file is stored)
- RECEIVER_IP (IP Address of the AVR)

### Troubleshooting

If you encounter issues with the tool, verify the following:
- The AV Receiver is properly connected to your network.
- Ensure you have the correct IP address of the receiver

## Contributions

Feel free to submit issues or pull requests. All contributions are welcome to improve this tool and make it more robust.

## License

This project is licensed under the MIT License.

---

Original script created by **ObsessiveCompulsiveAudiophile**. For more information, check out his [YouTube channel](https://www.youtube.com/@ocaudiophile).

