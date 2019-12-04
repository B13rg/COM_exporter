import common as COM

COM.PROMETHEUS_TEMPLATE = "COM_example<{parameters}> {exit_code}"   # <--- Customize this based on your TaskType name

def Whoami():
    datadict = {}
    (output,exitCode) = COM.runCommand(["whoami"])
    datadict["check"] = "Whoami"
    datadict["user"] = output.strip()
    return COM.generateOutput(datadict,exitCode)

def Pwd():
    datadict = {}
    (output,exitCode) = COM.runCommand(["pwd"])
    datadict["check"] = "Pwd"
    datadict["pwd"] = output.strip()
    return COM.generateOutput(datadict,exitCode)

def Tree():
    datadict = {}
    (output,exitCode) = COM.runCommand(["tree","./","--charset=ascii"])
    datadict["check"] = "Tree"
    datadict["data"] = output.strip()
    return COM.generateOutput(datadict,exitCode)

#
##
## Example Function, use it as a template
##
#
def FunctionName():
    datadict = {}
    (output, exitCode) = COM.runCommand(["<command>","<param 1>","<param 2>"])  # <--- Notice how each parameter is a comma separated string
    datadict["check"] = "FunctionName"
    datadict["label_name1"] = output.strip()
    datadict["label_name2"] = "Thing to record"
    # Secondary command example
    (output2, exitCode2) = COM.runCommand(["<supp. Command>", "<param3>", "<param4>"])
    datadict["label_name3"] = output2.strip()
    return COM.generateOutput(datadict,exitCode)

#
##
## Once you create your functions, add the function names here:
##
#
FuncList = [Whoami,Pwd,Tree,FunctionName]
