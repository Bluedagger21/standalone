#!/usr/bin/env python3
import os
import sys
import re
import argparse

class Command:
    def __init__(self, type, matched):
        self.type = type
        self.matched = matched
        
        self.modelsimArg = re.search(r"-modelsimini .*\.ini", self.matched).group(0)
        self.otherArgs = (re.sub(self.modelsimArg, "", self.matched)).split()

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
        self.runFH.write(self.type+" -f "+self.argFileName+" "+ self.modelsimArg)
        self.runFH.close()
class CommandSet:
    args = None
    testName = None
    logPath = None

    def __init__(self, args, type):
        self.args = args
        self.type = type
        self.logPath = os.path.abspath(args.logfile)
        self.cmdList = []

        # For some reason, vsim has a "# " before it to pattern match
        self.pattern = re.compile(r'^.{0,2}'+self.type+' (-.*)', re.MULTILINE)

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
