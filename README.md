# AudioEyes

## Introduction
This project aims to provide vision impaired persons a way to read through teseract optical character recognition and google text to speech. This code provides an interface for hardware to interact with and is able to provide positioning advice to a user, convert an image to text, and give a report on accuracy of transcription. However, the actual hardware component has not been created yet due to long shipping times with the current pandemic.

However, even the best optical character recognition can fail. To address this this project leverages NEAR blockchain technology to outsource manual transcription. The vision impaired user will have the option to tip the transcriber, therefore creating motivation to transcribe documents. These tips are not directly send to the transcriber; instead 10% of each tip is moved into a pool that is redistributed in order to provide bonuses to particularly active users.

## Running the Code
This project has three components: the automatic reader client, the smart contract, and the website and web server. Here are instructions for running each component.

### Automatic Reader Client
This component eventually aims to be combined with hardware to allow for usage by vision impaired persons. Because of this, the code is currently designed to be easily adaptable to hardware. However, as the neccessary hardware(raspi + camera + mic) was unobtainable in the time period of the hackathon, the reader client functionality is tested and demoed in jupyter notebook test_cases.ipynb. To read more about this client, simply run `jupyter lab` and open the notebook.

### NEAR Smart Contract
This smart contract is currently on the test network on the account thecydonian.testnet. To learn how to connect to this contract, read [this document](https://docs.near.org/docs/roles/developer/contracts/shell). To learn to build the contract yourself, read [this](https://docs.near.org/docs/roles/developer/contracts/near-sdk-rs).

### Website and Webserver
This website is currently being hosted locally and forwarded using ngrok. You can access with [this link](https://ba9be292.ngrok.io). I will keep this up until Friday May 22.

If you want to run it yourself, simply cd into the web directory and run `node server.js -p 8000`

## Hardware Considerations
In the future, I aim to connect this system to raspi based hardware, but, due to long shipping times, for now I will outline how my python interface should be connected to hardware.

* Camera should be horizontal to the ground and raised enough to easily fit a US letter into the FOV.
* Camera should have a led light next to it in order to light the document; without light, camera noise disrupts OCR.
* Raspi should have a microphone and constantly listen for command words.
* Raspi should call methods based on vocal commands.
* Raspi should pass the output of image_interface methods into reader methods to provide vocal feedback to vision impaired users

## Moving Forward
While the hackathon is over, this project has only just begun. This list decribes future actions that should be taken for this project.
1. Raspberry pi based hardware should be developed.
2. The python image interface should recognize when it receives a server timeout error.
3. The smart contract should be optimized for less timeouts.
4. The website should be expanded to more than just a homepage.
5. The website should be hosted and connected to the domain `audioeyes.eth` which I have purchased.

This list will be updated.
I intend to leverage GitCoin grants to fund further work on this project.
If you want to contribute please do and submit a PR.
