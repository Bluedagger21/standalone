#!/bin/csh
set logpath = $1
set logname = `echo "$logpath" | sed -n 's/^.*logs.//p' | sed -n 's/\..*//p'`
echo "Log Path: $logpath"
echo "Test Name: $logname"
#echo 'Checking if log file exists...'
if (-e "$logpath") then
	#echo 'Extracting -modelsimini switch...'
	set modelsimini = `grep "vopt.**-modelsimini" $1 | sed -n 's/.*\(-modelsimini.*ini \).*/\1/p'`
	#echo "Extracting vopt args..."
	set vopt_args = `grep "vopt.**-modelsimini" $1 | sed 's/\/tools\/bin\/vopt //' | sed 's/-modelsimini.*ini //'`
	echo "$vopt_args" >! vopt_args.f.$logname
	echo "# VOPT ARGS #"
	echo "vopt_args.f.$logname"
	#echo "Extracting vsim args..."
	set vsim_args = `grep "tools/bin/vsim.**-modelsimini" $1 | sed 's/\/tools\/bin\/vsim //' | sed 's/-modelsimini.*ini //'`
	echo "$vsim_args" >! vsim_args.f.$logname
	echo "# VSIM ARGS #"
	echo "vsim_args.f.$logname"
	echo "/tools/bin/vopt $modelsimini -f vopt_args.f.$logname" >! run_vopt_$logname.sh
	chmod +x run_vopt_$logname.sh
	echo "/tools/bin/vsim $modelsimini -f vsim_args.f.$logname" >! run_vsim_$logname.sh
	chmod +x run_vsim_$logname.sh
	echo "### TO RUN VOPT ###"
	echo "source run_vopt_$logname.sh"
	echo "### TO RUN VSIM ###"
	echo "source run_vsim_$logname.sh"
else
	echo "Error: Log file does not exist: $1"
endif