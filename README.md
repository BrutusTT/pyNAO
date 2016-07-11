# pyNAO - A Python/Yarp Wrapper for the NAO robot

pyNAO is a collection of [Yarp](https://github.com/robotology/yarp) Modules to control the NAO.

## Installation

1- Install the dependencies:

You need Yarp installed with the python bindings. For more details see 
[full instructions](http://wiki.icub.org/yarpdoc/install.html).

Example: OSX using [Homebrew](http://brew.sh)

    brew tap homebrew/x11
    brew install --with-python yarp


2- Download the source code: 

    git clone https://github.com/BrutusTT/pyNAO

3- build and install:

    cd pyNAO
    python setup.py install


## Running the Modules

Each module can be started standalone using the following command line.


    python -m pyNAO.<ModuleName> [--ip <IP Address>] [--port <Port>] [--name <Name Prefix>]

Parameters:

    []            - denotes optional parameter
    <ModuleName>  - can be one of the following: - NaoController
    <IP Address>  - default is 127.0.0.1
    <Port>        - default is 9559
    <Name Prefix> - if a name is given it will be used as a prefix for the port names
                    e.g.:  --name test results in /test/<Module>/rpc

Example:

    python -m pyNAO.NaoController --name MyRobot


## General

The package contains Yarp modules that can be used to control the NAO robot. Once the 
modules are started, they provide RPC Ports.

The **NAOController** is used for high level control.

    command message: "look (<near-far> <left-right> <down-up>)"
        <near-far>:   float - distance in meters [ 0.0, inf ]
        <left-right>: float - distance in meters [ 0.0, inf ]
        <down-up>:    float - distance in meters [ 0.0, inf ]

    Example:
        look (1.0 0.5 0.0) - Looks to the left (Fixation Point: 1m in front + 50cm to the left side)

    command message: "point <arm> (<near-far> <left-right> <down-up>)"
        <arm>:        string - "left" or "right"
        <near-far>:   float - distance in meters [ 0, inf ]
        <left-right>: float - distance in meters [ 0, inf ]
        <down-up>:    float - distance in meters [ 0, inf ]

    Example:
        point left (1.0 0.5 0.0) - Points to the left (Point: 1m in front + 50cm to the left side)



Happy hacking!

## License

See COPYING for licensing info.
