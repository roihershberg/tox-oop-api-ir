# Tox OOP API IR

This project is a Python script that parses the [c-toxcore](https://github.com/TokTok/c-toxcore) public
headers and generates a JSON file describing an Intermediate Representation of the appropriate Object-Oriented
API.

## Running

1. Install requirements:
   ```commandline
   pip install -r requirements.txt
   ```

2. In the first use, you should run the script with `--download-headers` option or manually put the headers
   in a `tox_headers` directory in the root of the project:
   ```commandline
   python main.py --download-headers
   ```

3. After the headers are present in the `tox_headers` directory you can just run:
   ```commandline
   python main.py
   ```

Output is in the `output` directory.

## Building documentation

1. Install requirements:
   ```commandline
   pip install -r docs_requirements.txt
   ```

2. Install custom plugin:
   ```commandline
   pip install -e reference_link_fixer
   ```

3. Build documentation (output in `site` directory):
   ```commandline
   mkdocs build
   ```
   or serve it in a local server:
   ```commandline
   mkdocs serve
   ```
