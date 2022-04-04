#!/usr/bin/env python3
import os
import sys
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('logfile', help="log file to parse vopt/vsim commands from")
parser.add_argument("--testname", help="user defined name for the test")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("--outdir", help="relative path directory for generated files")
args = parser.parse_args()

# Open a file handle from the logfile argument
logFileHandle = open(args.logfile)
logFileContents = logFileHandle.read()

# Initialize constants
LOGFILE_NAME = os.path.basename(logFileHandle.name)
if args.testname:
    TEST_NAME = args.testname
else:
    # Use characters before first '.' in logfile as test name
    TEST_NAME = re.search(r'^([^.]+)', LOGFILE_NAME, flags=re.MULTILINE).group(1) 

SCRIPT_DIRECTORY = os.path.dirname(__file__)
CWD = os.getcwd()
REL_OUT_DIR = args.outdir
if REL_OUT_DIR: 
    ABS_OUT_DIR = os.path.join(CWD, REL_OUT_DIR)
else:
    ABS_OUT_DIR = CWD
MODELSIM_ARG = ""
VOPT_ARG = ""
VSIM_ARG = ""
VOPT_ARG_FILENAME = ""
VSIM_ARG_FILENAME = ""

# Search for vopt command while pulling out -modelsimini switch
if args.verbose: print("Parsing for vopt...", end="")
voptArgsMatched = re.search(r'vopt (.*).+(.*-modelsimini.*.ini)(.*)', logFileContents, flags=re.MULTILINE)
if args.verbose: print("Done!")
if args.verbose: print("Parsing for vsim...", end="")
vsimArgsMatched = re.search(r'vsim (.*).+(.*-modelsimini.*.ini)(.*)', logFileContents, flags=re.MULTILINE)
if args.verbose: print("Done!")

logFileHandle.close()

# Make target directory if --outdir given
if REL_OUT_DIR:
    try:
        os.mkdir(ABS_OUT_DIR)
        if args.verbose: print("Directory "+ABS_OUT_DIR+" created")
    except FileExistsError:
        print("ERROR: Directory "+ABS_OUT_DIR+" already exists")
        quit()

if voptArgsMatched:
    MODELSIM_ARG = voptArgsMatched.group(2)
    VOPT_ARG = voptArgsMatched.group(1) + voptArgsMatched.group(3)
    VOPT_ARG_FILENAME = "vopt_args_"+TEST_NAME+".f"

    # Create the vopt_arg_<testname>.f and write the args to it
    if args.verbose: print("Writing vopt args to "+VOPT_ARG_FILENAME)
    voptArgsFH = open(os.path.join(ABS_OUT_DIR,VOPT_ARG_FILENAME), "w")
    voptArgsFH.write(VOPT_ARG)
    voptArgsFH.close()

    # Create the run_vopt_<testname> executable, including the .f file and -modelsim arg
    if args.verbose: print("Writing vopt command to "+VOPT_ARG_FILENAME)
    runVopt = open(os.path.join(ABS_OUT_DIR,"run_vopt_"+TEST_NAME), "w")
    runVopt.write("vopt -f "+VOPT_ARG_FILENAME+" "+MODELSIM_ARG)
    runVopt.close()
else:
    print("WARNING: No matches for vopt")

if vsimArgsMatched:
    VSIM_ARG = vsimArgsMatched.group(1) + vsimArgsMatched.group(3)
    VSIM_ARG_FILENAME = "vsim_args_"+TEST_NAME+".f"

    # Create the vsim_arg_<testname>.f and write the args to it
    if args.verbose: print("Writing vsim args to "+VSIM_ARG_FILENAME)
    vsimArgsFH = open(os.path.join(ABS_OUT_DIR,VSIM_ARG_FILENAME), "w")
    vsimArgsFH.write(VSIM_ARG)
    vsimArgsFH.close()

    # Create the run_vsim_<testname> executable, including the .f file and -modelsim arg
    if args.verbose: print("Writing vsim command to "+VSIM_ARG_FILENAME)
    runVopt = open(os.path.join(ABS_OUT_DIR, "run_vsim_"+TEST_NAME), "w")
    runVopt.write("vsim -f "+VSIM_ARG_FILENAME+" "+MODELSIM_ARG)
    runVopt.close()
else:
    print("WARNING: No matches for vsim")



