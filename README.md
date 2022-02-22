# Python: Asynchronous Python client for the Openmotics API

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
![Project Maintenance][maintenance-shield]
[![License][license-shield]](LICENSE.md)

[![Build Status][build-shield]][build]
[![Code Coverage][codecov-shield]][codecov]
[![Code Quality][code-quality-shield]][code-quality]

Asynchronous Python client for the OpenMotics API.

## About

An asynchronous python client for the OpenMotics API to control the outputs.

This library is created to support the integration in
[Home Assistant](https://www.home-assistant.io).

## Installation

```bash
cd pyhaopenmotics
pip install .
```

## Usage

```python
from pyhaopenmotics import CloudClient


async def main():
    async with CloudClient(
        client_id,
        client_secret,
    ) as bc:
        await bc.get_token()

    installations = await bc.installations.get_all()
    print(installations)

    i_id = installations[0].idx

    installation = await bc.installations.get_by_id(i_id)
    print(installation)
    print(installation.idx)
    print(installation.name)

    outputs = await bc.outputs.get_all(i_id)
    print(outputs)

    print(outputs[0].state)


if __name__ == "__main__":
    asyncio.run(main())
```

## Changelog & Releases

This repository keeps a change log using [GitHub's releases][releases]
functionality. The format of the log is based on
[Keep a Changelog][keepchangelog].

Releases are based on [Semantic Versioning][semver], and use the format
of `MAJOR.MINOR.PATCH`. In a nutshell, the version will be incremented
based on the following:

- `MAJOR`: Incompatible or major changes.
- `MINOR`: Backwards-compatible new features and enhancements.
- `PATCH`: Backwards-compatible bugfixes and package updates.

## Contributing

This is an active open-source project. We are always open to people who want to
use the code or contribute to it.

We've set up a separate document for our
[contribution guidelines](CONTRIBUTING.md).

Thank you for being involved! :heart_eyes:

## Setting up development environment

This Python project is fully managed using the [Poetry][poetry] dependency
manager. But also relies on the use of NodeJS for certain checks during
development.

You need at least:

- Python 3.8+
- [Poetry][poetry-install]
- NodeJS 12+ (including NPM)

To install all packages, including all development requirements:

```bash
npm install
poetry install
```

As this repository uses the [pre-commit][pre-commit] framework, all changes
are linted and tested with each commit. You can run all checks and tests
manually, using the following command:

```bash
poetry run pre-commit run --all-files
```

To run just the Python tests:

```bash
poetry run pytest
```

## Authors & contributors

The original setup of this repository is by [Wouter Coppens][woutercoppens].

For a full list of all authors and contributors,
check [the contributor's page][contributors].

## License

This project is licensed under the AGPLv3 License - see the LICENSE.md file for details

[build-shield]: https://github.com/woutercoppens/python-openmotics/workflows/Continuous%20Integration/badge.svg
[build]: https://github.com/woutercoppens/python-openmotics/actions
[contributors]: https://github.com/woutercoppens/python-openmotics/graphs/contributors
[woutercoppens]: https://github.com/woutercoppens/python-openmotics
[keepchangelog]: http://keepachangelog.com/en/1.0.0/
[maintenance-shield]: https://img.shields.io/maintenance/yes/2021.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-experimental-yellow.svg
[releases]: https://github.com/woutercoppens/python-openmotics/releases
[semver]: http://semver.org/spec/v2.0.0.html
