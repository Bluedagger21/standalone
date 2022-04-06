#!/usr/bin/env python3
import os
import sys
import re
import argparse
class Command:
    def __init__(self, type, matched):
        self.type = type
        self.matched = matched
        
        self.modelsimArg = self.matched.group(2)
        self.otherArgs = (self.matched.group(1) + self.matched.group(3)).split()

    def getModelsimArg(self):
        return self.modelsimArg

    def getOtherArgs(self):
        return " ".join(self.otherArgs)

    def getArgs(self):
        return self.modelsimArg + " ".join(self.otherArgs)

    def writeArgFile(self, testName, path):
        self.argFileName = self.type+"_args_"+testName+".f"
        self.argFilePath = os.path.join(path,self.argFileName)
        self.argsFH = open(self.argFilePath, "w")
        self.argsFH.write(self.getOtherArgs())
        self.argsFH.close()

    def writeRunFile(self, testName, path):
        self.runFileName = "run_"+self.type+"_"+testName
        self.runFilePath = os.path.join(path,self.runFileName)
        self.runFH = open(self.runFilePath, "w")
        self.runFH.write(self.type+" -f "+self.argFileName+" "+self.modelsimArg)
        self.runFH.close()


def parseForPattern(pattern, content):
    return pattern.search(content)
    

parser = argparse.ArgumentParser()
parser.add_argument('logfile', help="log file to parse vopt/vsim commands from")
parser.add_argument("--testname", help="user defined name for the test")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("--outdir", help="relative path directory for generated files")
args = parser.parse_args()

# Open a file handle from the logfile argument
logFileHandle = open(args.logfile)
logFileContents = logFileHandle.read()
logFileHandle.close()

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
VOPT_ARG_FILENAME = ""
VSIM_ARG_FILENAME = ""

# Make target directory if --outdir given
if REL_OUT_DIR:
    try:
        os.mkdir(ABS_OUT_DIR)
        if args.verbose: print("Directory "+ABS_OUT_DIR+" created")
    except FileExistsError:
        if input("INFO: Directory "+ABS_OUT_DIR+" already exists. Overwrite? (y/n): ") == 'n':
            quit()
    

# Search for vopt command while pulling out -modelsimini switch
if args.verbose: print("INFO: Parsing for vopt...")
voptPattern = re.compile(r'vopt (.*).+(.*-modelsimini.*.\.ini)(.*)', re.MULTILINE)
voptArgsMatched = parseForPattern(voptPattern, logFileContents)
if voptArgsMatched:
    voptCmd = Command("vopt", voptArgsMatched)
    if args.verbose: print("INFO: Matches found for vopt!")

    # Create the vopt_arg_<testname>.f and write the args to it
    if args.verbose: print("INFO: Writing vopt_args_"+TEST_NAME+".f")
    voptCmd.writeArgFile(TEST_NAME, ABS_OUT_DIR)

    # Create the run_vopt_<testname> executable, including the .f file and -modelsim arg
    if args.verbose: print("INFO: Writing vopt command to run_vopt_"+TEST_NAME)
    voptCmd.writeRunFile(TEST_NAME, ABS_OUT_DIR)

else:
    print("WARNING: No matches for vopt!")

# Search for vsim command while pulling out -modelsimini switch
if args.verbose: print("INFO: Parsing for vsim...")
vsimPattern = re.compile(r'vsim (.*).+(.*-modelsimini.*.\.ini)(.*)', re.MULTILINE)
vsimArgsMatched = parseForPattern(vsimPattern, logFileContents)
if vsimArgsMatched:
    vsimCmd = Command("vsim", vsimArgsMatched)
    if args.verbose: print("INFO: Matches found for vsim!")

    # Create the vopt_arg_<testname>.f and write the args to it
    if args.verbose: print("INFO: Writing vsim_args_"+TEST_NAME+".f")
    vsimCmd.writeArgFile(TEST_NAME, ABS_OUT_DIR)

    # Create the run_vopt_<testname> executable, including the .f file and -modelsim arg
    if args.verbose: print("INFO: Writing vsim command to run_vsim_"+TEST_NAME)
    vsimCmd.writeRunFile(TEST_NAME, ABS_OUT_DIR)
else:
    print("WARNING: No matches for vsim!")







