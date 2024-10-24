# avr-deq-volume-control

`avr-deq-volume-control` is a Python implementation that automatically monitors volume changes on your AV Receiver and adjusts over-corrected channels influenced by the built-in DEQ (Dynamic EQ). The script was originally created by **OCA (ObsessiveCompulsiveAudiophile)**, and this repository adapts and extends his concept into a Python-based tool. 

- [OCA's Original Script](https://drive.google.com/drive/folders/1hoCVIZSNGvZIflUVULxZk3V2G9-uA8lv)
- [OCA YouTube Channel](https://www.youtube.com/@ocaudiophile)

## Features
- Automatically scans for volume changes on your AV Receiver
- Adjusts channels that are over-corrected by the built-in DEQ

## Getting Started

### Prerequisites

Make sure you have the following:

- Python 3.x
- Required Python libraries, which can be installed via `pip` (see [Installation](#installation) below)
- A marrantz or denon receiver
- The IP address of the receiver

### Installation

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

### Running with Docker Compose

1. Ensure Docker and Docer Compose is installed

2. Create or copy the docker-compose.yml file from this repo

3. Build and run the docker file
   ```bash
    docker compose up
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

