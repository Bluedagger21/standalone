#!/usr/bin/python
import os
import sys
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('logfile', help="bcsim2 log file to parse commands from")
parser.add_argument("--testname", help="user defined name for the test")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

# Open a file handle from the logfile argument
logFileHandle = open(args.logfile)
logFileContents = logFileHandle.read()

# Initialize constants
LOGFILE_NAME = logFileHandle.name
if args.testname:
    TEST_NAME = args.testname
else:
    # Use characters before first '.' in logfile as test name
    TEST_NAME = re.search(r'^([^.]+)', LOGFILE_NAME, flags=re.MULTILINE).group(1) 
MODELSIM_ARG = ""
VOPT_ARG = ""
VSIM_ARG = ""
VOPT_ARG_FILENAME = ""
VSIM_ARG_FILENAME = ""

# Search for vopt command while pulling out -modelsimini switch
voptArgsMatched = re.search(r'^/tools/bin/vopt (.*).+(.*-modelsimini.*.ini)(.*)', logFileContents, flags=re.MULTILINE)
vsimArgsMatched = re.search(r'^/tools/bin/vsim (.*).+(.*-modelsimini.*.ini)(.*)', logFileContents, flags=re.MULTILINE)

logFileHandle.close()

if voptArgsMatched:
    MODELSIM_ARG = voptArgsMatched.group(2)
    VOPT_ARG = voptArgsMatched.group(1) + voptArgsMatched.group(3)
    VOPT_ARG_FILENAME = "vopt_args_"+TEST_NAME+".f"

    # Create the vopt_arg_<testname>.f and write the args to it
    voptArgsFH = open(VOPT_ARG_FILENAME, "w")
    voptArgsFH.write(VOPT_ARG)
    voptArgsFH.close()

    # Create the run_vopt_<testname> executable, including the .f file and -modelsim arg
    runVopt = open("run_vopt_"+TEST_NAME, "w")
    runVopt.write("vopt -f "+VOPT_ARG_FILENAME+" "+MODELSIM_ARG)
    runVopt.close()
else:
    print("WARNING: No matches for vopt")

if vsimArgsMatched:
    VSIM_ARG = vsimArgsMatched.group(1) + vsimArgsMatched.group(3)
    VSIM_ARG_FILENAME = "vsim_args_"+TEST_NAME+".f"

    # Create the vsim_arg_<testname>.f and write the args to it
    vsimArgsFH = open(VSIM_ARG_FILENAME, "w")
    vsimArgsFH.write(VSIM_ARG)
    vsimArgsFH.close()

    # Create the run_vsim_<testname> executable, including the .f file and -modelsim arg
    runVopt = open("run_vsim_"+TEST_NAME, "w")
    runVopt.write("vsim -f "+VSIM_ARG_FILENAME+" "+MODELSIM_ARG)
    runVopt.close()
else:
    print("WARNING: No matches for vsim")



