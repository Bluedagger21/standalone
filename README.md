# standalone
A python script to parse Questa regression logs to produce standalone Questa commands

## usage
```
usage: standalone.py [-h] [--testname TESTNAME] [--outdir OUTDIR] [--novlog] [--novopt] [--novsim] [-v] logfile

positional arguments:
  logfile              log file to parse vopt/vsim commands from

optional arguments:
  -h, --help           show this help message and exit
  --testname TESTNAME  user defined name for the test
  --outdir OUTDIR      relative path directory for generated files
  --novlog             don't parse vlog commands
  --novopt             don't parse vopt commands
  --novsim             don't parse vsim commands
  -v, --verbose        increase output verbosity
```
## public use
Avoid any user identifying implementations. Handling unique scenarios is encouraged, but it must not reveal user identity. Please raise issues for any concerns.
