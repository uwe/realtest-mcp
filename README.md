# realtest-mcp

MCP Server for RealTest

## Installation and Setup (on Windows)

You need `git`, `python` and `uv` (a package manager) installed:

Run in a command line (`cmd`):
```
winget install Git.Git
winget install Python.Python.3.14
winget install astral-sh.uv
```

Check out the repository:
```
git clone https://github.com/uwe/realtest-mcp.git
cd realtest-mcp
```

Copy `.env.example` to `.env` and adjust `REALTEST_MCP_SCRIPT_PATH`:
```
copy .env.example .env
edit .env
```

To start:
```
uv run main.py
```

Configure `http://127.0.0.1:8000/mcp` (or whatever port you have choosen) as HTTP MCP Server.

## Remote MCP Setup (e. g. for Mac)

To use `realtest-mcp` from a Mac host, change `REALTEST_MCP_HOST` to your local IP address.
In this example I will use `192.168.3.211`. Then run the following command to tunnel the
port to your local machine:

`socat TCP-LISTEN:8765,bind=127.0.0.1,reuseaddr,fork TCP:192.168.3.211:8000`

You may need to install `socat` (`brew install socat`).

Then set it up as HTTP MCP Server (`http://127.0.0.1:8765/mcp`).
