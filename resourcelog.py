import oci.audit
import json
from functions import *
from oci import audit
from oci import pagination
from oci import exceptions

configProfile = "DEFAULT"
cmd = input_command_line()
configProfile = cmd.config_profile if cmd.config_profile else configProfile
config, signer = create_signer(cmd.config_profile, cmd.is_instance_principals, cmd.is_delegation_token)

fulllog = open("fulllog.txt", "w")

audit = oci.audit.AuditClient(config= config, signer=signer)

startdate = "2023-06-06T00:00:00Z"
enddate = "2023-06-06T23:59:00Z"

try:
    retention = audit.get_configuration(compartment_id=cmd.compartment).data
except oci.exceptions.ServiceError as response:
    print("error: {} - Likely incorrect compartmentID or permission problem".format(response.code))
    exit()

print ("Retention days: {}".format(retention.retention_period_days))
print ("Search in compartment: {}".format(cmd.compartment))
print ("Search resource: {}".format(cmd.resource))

try:
    events = oci.pagination.list_call_get_all_results(audit.list_events, compartment_id=cmd.compartment, start_time=startdate, end_time=enddate)
except oci.exceptions.ServiceError as response:
    print("error: {}".format(response.code))
    exit()

for e in events:
    if e.data.request.action != "GET" and e.data.request.action and e.data.resource_id == cmd.resource:
        print ("{}: {} - {} - {} ({}) ".format(e.event_time, e.source, e.event_type, e.data.identity.principal_name, e.data.identity.ip_address))
        fulllog.writelines(str(e))

fulllog.close()





