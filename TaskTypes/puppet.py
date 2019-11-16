from subprocess import check_output, CalledProcessError
import re

PROMETHEUS_TEMPLATE = "COM_example_${func}<${parameters}> ${exit_code}"


def puppet_running():
    (output, exitCode) = runCommand(["/etc/sensu/plugins/check_puppet_agent"])
    output = "COM_puppet<check='puppet_running',value='"+output.strip()+"'> "+str(exitCode)
    return output


def puppet_ssl_expiry():
    (output, exitCode) = runCommand(["/etc/sensu/plugins/check-ssl-cert.rb", "-c", "30",
                                     "-w", "80", "-P", "/etc/puppetlabs/puppet/ssl/certs/tukp-sensuserver-2.papt.to.pem"])
    output = "COM_puppet<check='puppet_ssl_expiry',value='"+output.strip()+"'> "+str(exitCode)
    return output


def puppet_ssl_expiry_autofix():
    (output, exitCode) = runCommand(["/etc/sensu/plugins/check-ssl-cert.rb", "-c", "89",
                                     "-w", "90", "-P", "/etc/puppetlabs/puppet/ssl/certs/tukp-sensuserver-2.papt.to.pem"])
    output = "COM_puppet<check='puppet_ssl_expiry_autofix',value='"+output.strip()+"'> "+str(exitCode)
    return output


FuncList = [puppet_running, puppet_ssl_expiry, puppet_ssl_expiry_autofix]


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
