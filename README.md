# Secure Fingerprint Authentication System
Implemented by me, [Iosif Lazanakis](https://github.com/sifislaz), as part of my diploma thesis at the Department of Electrical and Computer Engineering of University of Patras.
## Prerequisites
In order for the system to run, you'll need:
* Python 3.10.4
* Java 17
## Installation Process
* Download the source code, or clone this repository.
* Create a python virtual environment, using the command: `python -m venv .venv`
* Activate the venv, by running the corresponding script (depends on the OS)
* Run the command `pip install -r requirements.txt` to install the required packages.
* Create a folder `./assets/`
* Download the dataset with the fingerprint samples you want and save it under `assets/`.
> **Don't forget to update the `dataset_dir_name` variable on `readwrite.py`**. <br>
> **Don't forget to update the photo dimensions in the `external/MainClass.java` file** and rebuild it with dependencies, using Maven (`external/pom.xml` file included)
## Demo App
There is a demo implemented, that offers a CLI to use the system. In order to use it, run the `app.py` file.
## Acknowledgements
To implement this system, the following libraries/software were used:
 * **CSIRO's Data61 [python-paillier](https://github.com/data61/python-paillier)**: To create and manage Paillier's public/private keys, as well as to perform encrypt/decrypt operations on data.
* **Robert Vazan's [SourceAFIS for Java](https://sourceafis.machinezoo.com/java)**: To extract minutiae features from fingerprint images