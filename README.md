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

- Python 3.10 or higher (if not using docker)
- Completed A1 EVO Nexus and generated an .ady file
- A Marantz or Denon receiver
- The IP address of the receiver (Found in Network -> Information on the receiver menu or in Windows -> View Network Devices & Computers -> Select your receiver -> Properties)

### Running with Docker

  Add the manualREW.ady file in a folder named "config" next to where you are running the command from. 
If you want to place it somewhere else, then change the volume (-v) parameter below.

```bash
docker run -d --name avr-control \
  -v $(pwd)/config:/app/config \
  -e RECEIVER_IP=<RECEIVER_IP_ADDRESS>\
  ghcr.io/menialfob/avr-deq-volume-control:latest
```

### Running with Docker Compose

1. Ensure Docker and Docker Compose is installed

2. Create or copy the docker-compose.yml file from this repo

3. Edit the docker-compose file to set the environment variables with your receiver's IP

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

4. Set the required environment variables:
    #### Windows
    ```bash
    set RECEIVER_IP=<IP of your receiver>
    ```
    #### Unix (MacOS & Linux)
    ```bash
    export RECEIVER_IP=<IP of your receiver>
    ```

5. Run the script:
    ```bash
    python .src/main.py
    ```
### Additional features

### Resetting to initial values
If you exit the application with Ctrl+C, the initial unadjusted speaker volumes will be set, meaning the values would be set as if this application had not been run. Be aware that Docker won't output the logs of the reset action to the console after clicking Ctrl+C, but the reset action is still happening. You can see the logs of the actions after Ctrl+C by using:

Docker:
```bash
Docker logs <container name>
```

Docker compose:
```bash
Docker compose logs
```

#### Overriding the default adjustment setup
You can set the environment variable SPEAKER_CONFIG to override the default speaker adjustments. The SPEAKER_CONFIG has to be formatted in the following way:
```bash
SPEAKER_CONFIG='{"half": ["SL", "SR", "SBL", "SBR", "SB"], "quarter": ["FHL", "FHR", "FWL", "FWR", "TFL", "TFR", "TML", "TMR", "TRL", "TRR", "RHL", "RHR", "FDL", "FDR", "SDL", "SDR", "BDL", "BDR", "SHL", "SHR", "TS", "CH"]}'
```

For example, if you only want to adjust SL and SR by half and nothing else, the variable would look like this:
```bash
SPEAKER_CONFIG='{"half": ["SL", "SR"], "quarter": []}'
```

See the docker-compose.yml file for an example of how this is implemented.

#### Defining where to look for the .ady file
You can set the environment variable CONFIG_PATH to change where it looks for the .ady file. The default location is ./config

See the docker-compose.yml file for an example of how this is implemented.

### Usage

- Once the script is running, it will automatically monitor your AV Receiver for any volume changes and apply adjustments accordingly. 
- Make sure that your AV Receiver is connected to the same network as your computer, and that the DEQ functionality is enabled.

### Configuration

You need to set three environment variables to make it run properly:
- RECEIVER_IP (Required) - IP Address of the AVR
- CONFIG_PATH (Optional) (Default: /config) Relative path to the folder where your .ady file is stored. Only relevant when not using Docker.
- SPEAKER_CONFIG (Optional) (Default: See below) Overrides the default speaker adjustments.

SPEAKER_CONFIG default values (Used if env variable is not set):
```bash
SPEAKER_CONFIG='{"half": ["SL", "SR", "SBL", "SBR", "SB"], "quarter": ["FHL", "FHR", "FWL", "FWR", "TFL", "TFR", "TML", "TMR", "TRL", "TRR", "RHL", "RHR", "FDL", "FDR", "SDL", "SDR", "BDL", "BDR", "SHL", "SHR", "TS", "CH"]}'
```


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
