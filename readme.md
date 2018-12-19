
# Quickstart

If you just want to run the samples you need an installed [Docker](https://www.docker.com/get-started) runtime.

Register a new inbox:

```sh
docker run infotechgmbh/socomap_receiver --insecure register <party>
```
returns the api key to access the inbox.

Send a message to the inbox:

```sh
docker run infotechgmbh/socomap_sender --data "some data to transfer" --insecure <party>
```

Receive the message on the inbox:

```sh
docker run infotechgmbh/socomap_receiver --insecure get <party> --api_key <api_key>
```

https://socomap.infotech.de is uses as default server.
If you want to use your own server, specify the parameter `--host`

# Introduction

This repository contains some usage examples of the [socomap](https://github.com/infotech-gmbh/socomap) server. The server provides [this](https://socomap.infotech.de) interface ([OpenAPI3](https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.0.md)). The examples in this repository are implemented with plain HTTP requests to generate as few external dependencies as possible.

# Sender Example

The [sender](https://github.com/infotech-gmbh/socomap-samples/blob/master/samples/socomap_sender.py) is able to send an UTF-8 String or a binary file to an inbox.

# Receiver Example

The [receiver](https://github.com/infotech-gmbh/socomap-samples/blob/master/samples/socomap_receiver.py) is able to register a new inbox and can pull the next incoming transmission out of the server.

# WSR EDI Context

The socomap server is designed to transfer WSR-Messages.
(Waiting for public documents to link)

TODO: provide special examples with end2end-encryption and
certificate management.

# Run your own Server

Have a look at the [socomap](https://github.com/infotech-gmbh/socomap) repository.

# Run the samples directly without docker

## Prerequisites

Install
* [Python 3.7+](https://www.python.org/downloads/release/python-371/)
* [requests 2.21.0+](https://pypi.org/project/requests/)


## Run the receiver

Get Help:

```sh
python socomap_receiver.py -h
```

Register a new inbox:

```sh
python socomap_receiver.py --insecure --host https://socomap.infotech.de register --email <email> <party>
```

Get next transmission:

```sh
python socomap_receiver.py --insecure --host https://socomap.infotech.de --insecure get <party> --api_key <api_key>
```

## Run the sender

Get Help:

```sh
python socomap_sender.py -h
```

Send some string data:

```sh
python socomap_sender.py --insecure --host https://socomap.infotech.de --data "some test data" <party>
```
