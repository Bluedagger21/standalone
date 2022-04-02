#!/usr/bin/python
import os
import sys
import re

if len(sys.argv) == 1:
    print("ERROR: Please specify a bcsim2 log as an argument")
    quit()

logFileHandle = open(sys.argv[1])
logFileContents = logFileHandle.read()

LOGFILE_NAME = logFileHandle.name
TEST_NAME = re.search(r'^([^.]+)', LOGFILE_NAME, flags=re.MULTILINE).group(1)
MODELSIM_ARG = ""
VOPT_ARG = ""
VSIM_ARG = ""
VOPT_ARG_FILENAME = ""
VSIM_ARG_FILENAME = ""

voptArgs = re.search(r'^/tools/bin/vopt (.*).+(.*-modelsimini.*.ini)(.*)', logFileContents, flags=re.MULTILINE)
vsimArgs = re.search(r'^/tools/bin/vsim (.*).+(.*-modelsimini.*.ini)(.*)', logFileContents, flags=re.MULTILINE)

logFileHandle.close()

if voptArgs:
    MODELSIM_ARG = voptArgs.group(2)
    VOPT_ARG = voptArgs.group(1) + voptArgs.group(3)
    VOPT_ARG_FILENAME = "vopt_args_"+TEST_NAME+".f"

    voptArgsFH = open(VOPT_ARG_FILENAME, "w")
    voptArgsFH.write(VOPT_ARG)
    voptArgsFH.close()

    runVopt = open("run_vopt_"+TEST_NAME, "w")
    runVopt.write("vopt -f "+VOPT_ARG_FILENAME+" "+MODELSIM_ARG)
    runVopt.close()
else:
    print("WARNING: No matches for vopt")

if vsimArgs:
    VSIM_ARG = vsimArgs.group(1) + vsimArgs.group(3)
    VSIM_ARG_FILENAME = "vsim_args_"+TEST_NAME+".f"

    vsimArgsFH = open(VSIM_ARG_FILENAME, "w")
    vsimArgsFH.write(VSIM_ARG)
    vsimArgsFH.close()

    runVopt = open("run_vsim_"+TEST_NAME, "w")
    runVopt.write("vsim -f "+VSIM_ARG_FILENAME+" "+MODELSIM_ARG)
    runVopt.close()
else:
    print("WARNING: No matches for vsim")



