# Efficient Algorithms for Service Chaining in NFV-Enabled Satellite Edge Networks

This is a project that provides implementation of our proposed algorithm and a simulation of the SEC network.  The repository contains two directories, `algorithm` and `NFV`. 

## Algorithm

 This directory contains the implementation of the algorithm proposed in our research paper. 

The `auxiliary_algorithm.py` file contains the code for this algorithm. 

## NFV

This directory contains the implementation of the simulation of the SEC network. 

`processor.py` simulates the processing and forwarding of requests in the SEC network. 

`request.py`  contains the implementation of the request class.

`satellite.py` implements the satellite class.

`sec_network.py` implements the SEC network class. 

`service_chain.py` implements the SFC (Service Function Chain) and VNF (Virtual Network Function) classes.

`tools.py` contains some utility functions.

`properties.py` contains the simulation parameters.

## Usage

An executable file is provided in the root directory. Simply download and run the file to use the SEC network simulation.

## Installation

To use this project, follow the steps below:

1. Clone the repository: `git clone https://github.com/DarkMountain-wyz/NFV_SEC.git`
2. Install the required dependencies: `pip install -r requirements.txt`

## License

This project is licensed under the Apache License 2.0. See the `LICENSE` file for more details.