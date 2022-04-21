#!/usr/bin/env python3
import os
import sys
import re
import argparse

class Command:
    def __init__(self, type, matched):
        self.type = type
        self.matched = matched
        self.argFileName = None
        self.argFilePath = None
        self.libName = None
        self.modelsimArg = None
        self.otherArgs = None
        
        # Find -modelsimini argument if it exists
        self.modelsimMatch = re.findall(r"-modelsimini .*\.ini", self.matched)
        if self.modelsimMatch[0]:
            self.modelsimArg = self.modelsimMatch[0]
        else:
            if args.verbose: print("INFO: -modelsimini option not found for this "+self.type+" command. Continuing...")    

        # Find -work argument if it exists (for vlog only)
        if self.type == "vlog":
            self.vlogMatch = re.findall(r"-work (\w+)", self.matched)
            if len(self.vlogMatch) > 0:
                self.libName = self.vlogMatch[0]
            else:
                self.vlogMatch = re.findall(r"(\w+).libmap", self.matched)
                if len(self.vlogMatch) > 0:
                    self.libName = self.vlogMatch[0]
                else:
                    if args.verbose: print("INFO: -libmap nor -work options not found for this "+self.type+" command. Moving on...")
     
        # Save all args besides -modelsimini
        self.otherArgs = (re.sub(self.modelsimArg, "", self.matched)).split()

    # Returns -modelsimini argument
    def getModelsimArg(self):
        return self.modelsimArg

    # Returns joined arguments other than -modelsimini
    def getOtherArgs(self):
        return " ".join(self.otherArgs)

    # Returns all arguments
    def getArgs(self):
        return self.modelsimArg + " ".join(self.otherArgs)

    # Write .f file, returns file path
    def writeArgFile(self, testName, path):
        if self.type == "vlog" and self.libName: 
            self.argFileName = self.type+"_args_"+self.libName+".f"
        else:
            self.argFileName = self.type+"_args_"+testName+".f"
        self.argFilePath = os.path.join(path,self.argFileName)
        if args.verbose: print("INFO: Writing "+self.argFileName)
        self.argsFH = open(self.argFilePath, "w")
        self.argsFH.write(self.getOtherArgs())
        self.argsFH.close()
        return self.argFilePath

    # Write single line script with command utilizing .f file, returns file path
    def writeRunFile(self, testName, path):
        if self.type == "vlog" and self.libName: 
            self.runFileName = "run_"+self.type+"_"+self.libName
        else:
            self.runFileName = "run_"+self.type+"_"+testName
        self.runFilePath = os.path.join(path,self.runFileName)
        if args.verbose: print("INFO: Writing "+self.runFileName)
        self.runFH = open(self.runFilePath, "w")
        self.runFH.write(self.type+" -f "+self.argFilePath+" "+ self.modelsimArg)
        self.runFH.close()
        return self.runFilePath
class CommandSet:
    testName = None
    logPath = None

    def __init__(self, type):
        self.type = type
        self.logPath = os.path.abspath(args.logfile)
        self.cmdList = []

        # Tool allows 0 or more non-whitespace characters after beginning of new line to start parsing for cmd
        # There may be duplicates, but files created should get overwritten
        self.pattern = re.compile(r"^\S{0,}"+self.type+" (.*)", re.MULTILINE)
                                    
        if args.verbose: print("INFO: Parsing for "+self.type+"...")
        # Open logfile and return all matches of set pattern
        with open(self.logPath, "r") as f:
            self.matchedList = self.pattern.findall(f.read())
        
        # For each match, append a new Command class
        for self.match in self.matchedList:
            self.cmdList.append(Command(self.type, self.match))
            if args.verbose: print("INFO: Match found for "+self.type+"!")
        
        # Use user defined testname or derive from logfile name (default)
        if args.testname:
            self.testName = args.testname
        else:
            with open(self.logPath, "r") as f:
                self.testName = re.search(r'^([^.]+)', os.path.basename(f.name), flags=re.MULTILINE).group(1)

    def writeToOutput(self, path):
        self.testNameIndex = ""
        self.runFileList = []
        # Iterate through commands in command list
        for i, cmd in enumerate(self.cmdList):
            if self.type == "vlog":
                self.testNameIndex = str(i + 1)
            # Create the <type>_arg_<testname>.f and write the args to it
            cmd.writeArgFile(self.testName+self.testNameIndex, path)
            # Create the run_<type>_<testname> executable, including the .f file and -modelsim arg (if applicable)
            self.runFileList.append(cmd.writeRunFile(self.testName+self.testNameIndex, path))
        if self.type == "vlog":
            # Remove duplicates
            self.runFileList = list(dict.fromkeys(self.runFileList))
            # Create executable to run all vlog commands
            if args.verbose: print("INFO: Writing run_all_vlog")
            with open(os.path.join(path,"run_all_vlog"), "w") as f:
                for self.cmd in self.runFileList:
                    f.write("source " + self.cmd + "\n")

    
parser = argparse.ArgumentParser()
parser.add_argument('logfile', help="log file to parse vopt/vsim commands from")
parser.add_argument("--testname", help="user defined name for the test")
parser.add_argument("--outdir", help="relative path directory for generated files")
parser.add_argument("--novlog", help="don't parse vlog commands", action="store_true")
parser.add_argument("--novopt", help="don't parse vopt commands", action="store_true")
parser.add_argument("--novsim", help="don't parse vsim commands", action="store_true")
parser.add_argument("--nolibraryname", help="forces iteration numbering only for file names", action="store_true")
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
args = parser.parse_args()

# Initialize global constants
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
        if args.verbose: print("INFO: Directory "+ABS_OUT_DIR+" created")
    except FileExistsError:
        if input("INFO: Directory "+ABS_OUT_DIR+" already exists. \nOverwrite contents? (y/n): ") == 'n':
            quit()

# List of CommandSet classes to process
cmdSetList = []
if not args.novlog:
    cmdSetList.append(CommandSet("vlog"))
if not args.novopt:
    cmdSetList.append(CommandSet("vopt"))
if not args.novsim:
    cmdSetList.append(CommandSet("vsim"))

# Write each set of commands out to files
for set in cmdSetList:
    set.writeToOutput(ABS_OUT_DIR)
