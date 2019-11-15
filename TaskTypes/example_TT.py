from subprocess import check_output, CalledProcessError
import re

PROMETHEUS_TEMPLATE = "COM_example_${func}<${parameters}> ${exit_code}"

def Whoami():
    (output,exitCode) = runCommand(["whoami"])
    output = "COM_example_whoami<value='"+output.strip()+"'> "+str(exitCode)
    return output
def Pwd():
    (output,exitCode) = runCommand(["pwd"])
    output = "COM_example_pwd<value='"+output.strip()+"'> "+str(exitCode)
    return output
def Ddate():
    (output,exitCode) = runCommand(["ddate"])
    output = "COM_example_ddate<value='"+output.strip()+"'> "+str(exitCode)
    return output
def Date():
    (output,exitCode) = runCommand(["date"])
    output = "COM_example_date<value='"+output.strip()+"'> "+str(exitCode)
    return output
def Tree():
    (output,exitCode) = runCommand(["tree --charset=ascii"])
    output = "COM_example_date<value='"+output.strip()+"'> "+str(exitCode)
    return output

FuncList = [Whoami,Pwd,Ddate,Date,Tree]

def runCommand(command):
    """
    Returns a tuple of (output text, exit code)
    """
    try:
        output = check_output(command)
    except CalledProcessError, err:  # Hit if error code is anything except 0
        # Pass error info to calling function for it to handle
        return (err.output, err.returncode)
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    return (output, 0)




