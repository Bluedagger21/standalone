#!/usr/bin/env python3
import os
import sys
import re
import argparse
class CommandSet:
    args = None
    testName = None
    logPath = None

    def __init__(self, args, type):
        self.args = args
        self.type = type
        self.logPath = os.path.abspath(args.logfile)
        self.cmdList = []

        if self.type == "vlog":
            self.pattern = re.compile(r'^vlog (\-.*)', re.MULTILINE)
        if self.type == "vopt":
            self.pattern = re.compile(r'^vopt (.*).+(.*-modelsimini.*.\.ini)(.*)', re.MULTILINE)
        if self.type == "vsim":
            self.pattern = re.compile(r'^# vsim (.*).+(.*-modelsimini.*.\.ini)(.*)', re.MULTILINE)

        if args.verbose: print("INFO: Parsing for "+self.type+"...")
        with open(self.logPath, "r") as f:
            self.matchedList = self.pattern.findall(f.read())

        for self.match in self.matchedList:
            self.cmdList.append(Command(self.type, self.match))
            if args.verbose: print("INFO: Match found for "+self.type+"!")
        
        if args.testname:
            self.testName = args.testname
        else:
            with open(self.logPath, "r") as f:
                self.testName = re.search(r'^([^.]+)', os.path.basename(f.name), flags=re.MULTILINE).group(1)

    def writeToOutput(self, path):
        self.testNameIndex = ""
        for i, cmd in enumerate(self.cmdList):
            if self.type == "vlog":
                self.testNameIndex = str(i + 1)
            # Create the <type>_arg_<testname>.f and write the args to it
            if self.args.verbose: print("INFO: Writing "+self.type+"_args_"+self.testName+self.testNameIndex+".f")
            cmd.writeArgFile(self.testName+self.testNameIndex, path)

            # Create the run_<type>_<testname> executable, including the .f file and -modelsim arg (if applicable)
            if self.args.verbose: print("INFO: Writing "+self.type+" command to run_"+self.type+"_"+self.testName+self.testNameIndex)
            cmd.writeRunFile(self.testName+self.testNameIndex, path)     
class Command:
    def __init__(self, type, matched):
        self.type = type
        self.matched = matched
        
        if self.type == "vlog":
            self.otherArgs = self.matched.split()
        else:
            self.modelsimArg = self.matched[1] 
            self.otherArgs = (self.matched[0] + self.matched[2]).split()

    def getModelsimArg(self):
        if self.type == "vlog":
            return None
        else:
            return " ".join(self.modelsimArg)

    def getOtherArgs(self):
        return " ".join(self.otherArgs)

    def getArgs(self):
        if self.type == "vlog":
            return " ".join(self.otherArgs)
        else:
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
        if self.type == "vlog":
            self.runFH.write(self.type+" -f "+self.argFileName)
        else:
            self.runFH.write(self.type+" -f "+self.argFileName+" "+ self.modelsimArg)
        self.runFH.close()

def parseForPattern(pattern, content):
    return pattern.findall(content)
    
parser = argparse.ArgumentParser()
parser.add_argument('logfile', help="log file to parse vopt/vsim commands from")
parser.add_argument("--testname", help="user defined name for the test")
parser.add_argument("--outdir", help="relative path directory for generated files")
parser.add_argument("--novlog", help="don't parse vlog commands", action="store_true")
parser.add_argument("--novopt", help="don't parse vopt commands", action="store_true")
parser.add_argument("--novsim", help="don't parse vsim commands", action="store_true")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

# Initialize constants
SCRIPT_DIRECTORY = os.path.dirname(__file__)
CWD = os.getcwd()
REL_OUT_DIR = args.outdir
if REL_OUT_DIR: 
    ABS_OUT_DIR = os.path.abspath(REL_OUT_DIR)
else:
    ABS_OUT_DIR = CWD

# Make target directory if --outdir given
if REL_OUT_DIR:
    try:
        os.mkdir(ABS_OUT_DIR)
        if args.verbose: print("Directory "+ABS_OUT_DIR+" created")
    except FileExistsError:
        if input("INFO: Directory "+ABS_OUT_DIR+" already exists. \nOverwrite contents? (y/n): ") == 'n':
            quit()

# List of CommandSet classes to process
cmdSetList = []
if not args.novlog:
    cmdSetList.append(CommandSet(args, "vlog"))
if not args.novopt:
    cmdSetList.append(CommandSet(args, "vopt"))
if not args.novsim:
    cmdSetList.append(CommandSet(args, "vsim"))

# Write each set of commands out to files
for set in cmdSetList:
    set.writeToOutput(ABS_OUT_DIR)
