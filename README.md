# API Documentation Generation CLI

Command Line Interface (CLI) for generating API documentation through DocFX, that abstracts out the complexity of individual platform tools behind a simple set of commands.

## Supported platforms

| Platform   | `-platform` parameter value | Status            | 
|:-----------|:----------------------------|:------------------|
| JavaScript | `js`                        | 🧱 Not Started     |
| TypeScript | `ts`                        | 🧱 Not Started     |
| Python     | `py`                        | 🚧 In Development | 
| REST       | `rest`                      | 🧱 Not Started     |
| .NET       | `net`                       | 🧱 Not Started     |
| Java       | `java`                      | 🧱 Not Started     |

## Usage

### Python

To generate documentation for Python libraries, the current release supports artifacts from PyPI. To generate YAML documentation, run the following command:

```bash
python -m adg make --platform python --library azure-batch --out delta  
```

This will produce DocFX-compatible YAML files for the `azure-batch` library in the `delta` output folder.