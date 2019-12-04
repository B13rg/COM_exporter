import common as COM

COM.PROMETHEUS_TEMPLATE = "COM_puppet<{parameters}> {exit_code}"

def puppet_running():
    """Checks if puppet is running"""

    dataDict = {}
    (output, exitCode) = COM.runCommand(["/etc/sensu/plugins/check_puppet_agent"])
    dataDict['check'] = 'puppet_running'
    dataDict['value'] = output.strip()    
    return COM.generateOutput(dataDict,exitCode)


def puppet_ssl_expiry():
    """Checks if the puppet cert is expiring within the next 80 days"""

    dataDict = {}
    (output, exitCode) = COM.runCommand(["/etc/sensu/plugins/check-ssl-cert.rb", "-c", "30",
                                     "-w", "80", "-P", "/etc/puppetlabs/puppet/ssl/certs/tukp-sensuserver-2.papt.to.pem"])
    dataDict['check'] = 'puppet_ssl_expiry'
    dataDict['value'] = output.strip()    
    return COM.generateOutput(dataDict,exitCode)


def puppet_ssl_expiry_autofix():
    """Copy of the puppet_ssl_expiry definition"""

    dataDict = {}
    (output, exitCode) = COM.runCommand(["/etc/sensu/plugins/check-ssl-cert.rb", "-c", "89",
                                     "-w", "90", "-P", "/etc/puppetlabs/puppet/ssl/certs/tukp-sensuserver-2.papt.to.pem"])
    dataDict['check'] = 'puppet_ssl_expiry_autofix'
    dataDict['value'] = output.strip()    
    return COM.generateOutput(dataDict,exitCode)

# This is used by the WebInterface when the module is loaded to know what scripts are here
FuncList = [puppet_running, puppet_ssl_expiry, puppet_ssl_expiry_autofix]
