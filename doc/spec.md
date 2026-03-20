# realtest-mcp

MCP Server for (RealTest)[https://mhptrading.com/] - backtesting software

## RealTest

RealTest is a Windows app for backtesting systematic trading rules. It offers
a (CLI version)[https://mhptrading.com/docs/topics/idh-topic1063.htm] for most
of its functionality:

- "parse" to check the script for syntax errors
- "import" to import data into a .rtd file
- "test" to run a backtest

During development of a .rts script use "parse" to check for syntax errors.
Before running a backtest ("test") you have to "import" the data.

## Configuration

- REALTEST_MCP_REALTEST_PATH = "C:\RealTest\"
- REALTEST_MCP_SCRIPT_PATH = "Z:\mcp\"
- REALTEST_MCP_SCRIPT_DIGITS = 4

For each MCP call a folder ("script-xxxx") is created below the script path.
The script itself is written to "script.rts". Script output is also written
in that directory via the "?scriptpath?" placeholder in RealTest with the
following settings:

```
	SaveStatsAs:	?scriptpath?\stats.csv
	SaveTradesAs:	?scriptpath?\trades.csv
	SavePositionsAs:	?scriptpath?\positions.csv
```

The RealTest executable is in the realtest path: "C:\RealTest\RealTest.exe".
In the same folder is also an errorlog "C:\RealTest\errorlog.txt". The last
line of that file contains the error message for "patch" if there was an error
(indicated by return code).

