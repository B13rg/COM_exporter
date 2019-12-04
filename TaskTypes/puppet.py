import re
from subprocess import CalledProcessError, check_output

PROMETHEUS_TEMPLATE = "COM_puppet<{parameters}> {exit_code}"

def puppet_running():
    """Checks if puppet is running"""

    dataDict = {}
    (output, exitCode) = runCommand(["/etc/sensu/plugins/check_puppet_agent"])
    dataDict['check'] = 'puppet_running'
    dataDict['value'] = output.strip()    
    return generateOutput(dataDict,exitCode)


def puppet_ssl_expiry():
    """Checks if the puppet cert is expiring within the next 80 days"""

    dataDict = {}
    (output, exitCode) = runCommand(["/etc/sensu/plugins/check-ssl-cert.rb", "-c", "30",
                                     "-w", "80", "-P", "/etc/puppetlabs/puppet/ssl/certs/tukp-sensuserver-2.papt.to.pem"])
    dataDict['check'] = 'puppet_ssl_expiry'
    dataDict['value'] = output.strip()    
    return generateOutput(dataDict,exitCode)


def puppet_ssl_expiry_autofix():
    """Copy of the puppet_ssl_expiry definition"""

    dataDict = {}
    (output, exitCode) = runCommand(["/etc/sensu/plugins/check-ssl-cert.rb", "-c", "89",
                                     "-w", "90", "-P", "/etc/puppetlabs/puppet/ssl/certs/tukp-sensuserver-2.papt.to.pem"])
    dataDict['check'] = 'puppet_ssl_expiry_autofix'
    dataDict['value'] = output.strip()    
    return generateOutput(dataDict,exitCode)

# This is used by the WebInterface when the module is loaded to know what scripts are here
FuncList = [puppet_running, puppet_ssl_expiry, puppet_ssl_expiry_autofix]


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
