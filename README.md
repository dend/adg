# 🚀 `adg` - API Documentation Generation CLI

Command Line Interface (CLI) tool for generating API documentation with [DocFX](https://dotnet.github.io/docfx/), that abstracts out the complexity of individual platform tools behind a simple set of commands.

## Supported platforms

| Platform   | `-platform` parameter value | Status             | 
|:-----------|:----------------------------|:-------------------|
| JavaScript | `js`                        | 🧱 Not Started     |
| TypeScript | `ts`                        | 🧱 Not Started     |
| Python     | `python`                    | 🌱 Alpha           | 
| REST       | `rest`                      | 🧱 Not Started     |
| .NET       | `net`                       | 🧱 Not Started     |
| Java       | `java`                      | 🧱 Not Started     |

## Setup

At this time, `adg` does not yet have a package on [PyPI](https://pypi.org/), therefore installation is manual. To prepare everything, make sure to follow the steps:

1. Clone the repository or download the ZIP.
2. Create a new [Python virtual environment](https://docs.python.org/3/tutorial/venv.html) with `python -m venv adg_env`.
3. Activate the environment with `source adg_env/bin/activate` (_on macOS or Linux_) or `.\adg_env\Scripts\activate` (_on Windows with PowerShell_).
4. Run the documentation commands within the virtual environment.

## Usage

### Python

To generate documentation for Python libraries, the current release supports artifacts from PyPI. To generate YAML documentation, run the following command:

```bash
python -m adg make --platform python --library azure-batch --out delta
```

This will produce DocFX-compatible YAML files for the `azure-batch` library in the `delta` output folder. You can additionally specify the `--format` parameter to tell the tool whether you need to generate HTML or DocFX-compatible YAML.