__author__ = 'CoYe'

from qualipy.common.libs.driver_builder_wrapper import DriverFunction
<<<<<<< HEAD

from cloudshell.networking.cisco.resource_drivers.cisco_generic_resource_dirver import cisco_generic_resource_driver

=======
from cloudshell.networking.cisco.resource_drivers.cisco_generic_resource_dirver import cisco_generic_resource_driver
#from cloudshell.networking.cisco.resource_drivers.cisco_generic_resource_dirver import cisco_generic_resource_driver
>>>>>>> parent of e6a3bf7... Added pkgutil

class cisco_generic_ios_resource_driver(cisco_generic_resource_driver):
    @DriverFunction(extraMatrixRows={"resource": ["ResourceAddress", "User", "Password", "Enable Password", "Console Server IP Address",
                                                  "Console User", "Console Password", "Console Port", "Connection Type",
                                                  "SNMP Version", "SNMP Read Community", "SNMP V3 User", "SNMP V3 Password",
                                                  "SNMP V3 Private Key"]})
    def Init(self, matrixJSON):
        self.handler_name = 'ios'
        cisco_generic_resource_driver.Init(self, matrixJSON)

if __name__ == '__main__':

    data_json = str("""{
            "resource" : {

                    "ResourceAddress": "192.168.42.235",
                    "User": "root",
                    "Password": "Password1",
                    "CLI Connection Type": "ssh",
                    "Console User": "",
                    "Console Password": "",
                    "Console Server IP Address": "",
                    "ResourceName" : "Cisco-2950-Router",
                    "ResourceFullName" : "Cisco-2950-Router",
                    "Enable Password": "",
                    "Console Port": "",
                    "SNMP Read Community": "Cisco",
                    "SNMP Version": "",
                    "SNMP V3 Password": "",
                    "SNMP V3 User": "",
                    "SNMP V3 Private Key": ""
                },
            "reservation" : {
                    "Username" : "admin",
                    "Password" : "admin",
                    "Domain" : "Global",
                    "AdminUsername" : "admin",
                    "AdminPassword" : "admin"}
            }""")
#"ReservationId" : "94e31679-7262-4ad8-977e-cea2dbe2705e",

    #"ResourceAddress": "172.29.128.17",
    #"User": "klop",
    #"Password": "azsxdc",
    #"CLI Connection Type": "ssh ",

    resource_driver = cisco_generic_ios_resource_driver('77', data_json)
    print resource_driver.GetInventory(data_json)

    #import sys; sys.exit()
    print resource_driver.SendCommand(data_json, 'sh ver')
    #print resource_driver.Save(data_json, 'tftp://192.168.65.85', 'startup-config')
    data_json = str("""{
            "resource" : {

                    "ResourceAddress": "192.168.42.235",
                    "User": "root",
                    "Password": "Password1",
                    "CLI Connection Type": "ssh",
                    "Console User": "",
                    "Console Password": "",
                    "Console Server IP Address": "",
                    "ResourceName" : "Cisco-2950-Router",
                    "ResourceFullName" : "Cisco-2950-Router",
                    "Enable Password": "",
                    "Console Port": "",
                    "SNMP Read Community": "Cisco",
                    "SNMP Version": "3",
                    "SNMP V3 Password": "Password1",
                    "SNMP V3 User": "QUALI",
                    "SNMP V3 Private Key": "Live4lol"
                }
            }""")

    #print resource_driver.Save(data_json, 'tftp://192.168.65.85', 'startup-config')
    print resource_driver.SendCommand(data_json, 'sh ver')
    #print resource_driver.GetInventory(data_json)


