# Python ThermoWorks Cloud

![GitHub branch check runs](https://img.shields.io/github/check-runs/a2hill/python-thermoworks-cloud/main)
[![PyPI - Version](https://img.shields.io/pypi/v/thermoworks-cloud)](https://pypi.org/project/thermoworks-cloud/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/thermoworks-cloud)
[![codecov](https://codecov.io/gh/a2hill/python-thermoworks-cloud/branch/main/graph/badge.svg?token=1QQENQPNB2)](https://codecov.io/gh/a2hill/python-thermoworks-cloud)
[![License](https://img.shields.io/github/license/a2hill/python-thermoworks-cloud)](https://raw.githubusercontent.com/a2hill/python-thermoworks-cloud/refs/heads/main/LICENSE.txt)


## About
Pull data from your ThermoWorks Cloud connected thermometers

This is an unofficial library written using the observed behavior of the ThermoWorks Cloud web client (https://cloud.thermoworks.com/home)

The primary purpose of this library is to make ThermoWorks data available for usage in the acompanying [Home Assistant ThermoWorks Cloud Ingegration](https://github.com/a2hill/ha-thermoworks-cloud) 

### Supported Devices
This library has been tested with the following devices:
* [ThermoWorks Node Wi-Fi sensor](https://www.thermoworks.com/node/)
* ThermaData
* Smoke
* RXF

More more information on supported devices see the discussion thread: [ThermoWorks Cloud Home Assistant Integration - Device Interoperability](https://github.com/a2hill/ha-thermoworks-cloud/discussions/6)


## Installation
```bash
pip install thermoworks-cloud
```

## Usage
See [examples/](examples/)

```bash
env $(cat .secrets) python3 examples/get_devices_for_user.py 
```

## Docs
See [API Documentation](https://a2hill.github.io/python-thermoworks-cloud/index.html)