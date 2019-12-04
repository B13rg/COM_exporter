import re
from subprocess import CalledProcessError, check_output

PROMETHEUS_TEMPLATE =  "COM_example<{parameters}> {exit_code}"

def generateOutput(dataDict, exitCode):
    """Uses the prometheus template to create metric string
    
    The data dict is used to create the metric labels, with the key as the label name and the value as the label value.
    The exit code usually communicates the outcome of a script.
    """
    # First create a list of parameters by combining key value pairs from the datadict
    params = [','.join([key+"=\""+value+"\""]) for key,value in dataDict.items]
    # Here we use the prometheus metric template and fill in our stuff
    return PROMETHEUS_TEMPLATE.format(
        parameters= ','.join(params),   # Now join each parameter with a comma
        exit_code=str(exitCode)
    )


def runCommand(command):
    """Returns a tuple of (output text, exit code)"""

    try:
        output = check_output(command)
    except CalledProcessError, err:  # Exception of the script being ran
        # Hit if error code is anything except 0
        # Pass error info to calling function for it to handle
        return (err.output, err.returncode)
    except Exception as err:    # Exception from anything above the script (such as not being able to find it)
        return (err.message, 1)
    # Remove any terminal ansi text left over from running the script
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    output = ansi_escape.sub('', output)
    return (output, 0)