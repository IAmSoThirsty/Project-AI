## Installation and Usage Instructions for Temporal CLI

### Homebrew
To install the Temporal CLI using Homebrew, run the following command:
```sh
brew install temporalio/tap/temporal
```

### Download
You can also download the Temporal CLI directly from the official GitHub releases:
1. Visit the [Temporal CLI Releases Page](https://github.com/temporalio/temporal/releases).
2. Download the appropriate binary for your operating system.
3. Follow the instructions in the release notes for installation.

### Docker
To run the Temporal CLI using Docker, use the following command:
```sh
docker run --rm temporalio/cli:latest
```

### Build from Source
If you prefer to build the Temporal CLI from source, follow these steps:
1. Ensure you have Go installed on your machine. If you don't have Go, you can download it from [golang.org](https://golang.org/dl/).
2. Clone the Temporal CLI repository:
```sh
git clone https://github.com/temporalio/temporal.git
```
3. Navigate into the cloned repository:
```sh
cd temporal
```
4. Build the CLI:
```sh
make build
```
5. The binary will be located in the `bin` directory after a successful build.
