import oci.audit
import json
from functions import *
from oci import audit
from oci import pagination
from oci import exceptions
import datetime

configProfile = "DEFAULT"
cmd = input_command_line()
configProfile = cmd.config_profile if cmd.config_profile else configProfile
config, signer = create_signer(cmd.config_profile, cmd.is_instance_principals, cmd.is_delegation_token)

fulllog = open(cmd.log_file, "w")

audit = oci.audit.AuditClient(config= config, signer=signer)

try:
    retention = audit.get_configuration(compartment_id=cmd.compartment).data
except oci.exceptions.ServiceError as response:
    print("error: {} - Likely incorrect compartmentID or permission problem".format(response.code))
    exit()

print ("Retention days: {}".format(retention.retention_period_days))
if cmd.max_days:
    print ("Max days: {}".format(cmd.max_days))
else:
    print ("Max Days: ALL")
    cmd.max_days = retention.retention_period_days
print ("Search in compartment: {}".format(cmd.compartment))
print ("Search resource: {}".format(cmd.resource))

days = retention.retention_period_days
if cmd.max_days < retention.retention_period_days:
    days = cmd.max_days

today = datetime.datetime.now()
for d in range(days):
    today = datetime.datetime.now() - datetime.timedelta(days=d)
    startdate = "{:04d}-{:02d}-{:02d}T00:00:00Z".format(today.year, today.month, today.day)
    enddate = "{:04d}-{:02d}-{:02d}T23:59:59Z".format(today.year, today.month, today.day)
    print ("{} - {}".format(startdate, enddate))

    try:
        events = oci.pagination.list_call_get_all_results(audit.list_events, compartment_id=cmd.compartment, start_time=startdate, end_time=enddate).data
    except oci.exceptions.ServiceError as response:
        print("error: {}".format(response.code))
        exit()

    for e in events:
        if e.data.request.action != "GET" and e.data.request.action and e.data.resource_id == cmd.resource:
            print ("{}: {} - {} - {} ({}) ".format(e.event_time, e.source, e.event_type, e.data.identity.principal_name, e.data.identity.ip_address))
            fulllog.writelines(str(e))


fulllog.close()





