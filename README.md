# OCI-ResourceLog
Use Auditlog to trace all changes to a resource

## Usage
example:

python resourcelog.py -c your_compartment_OCID -r resource_OCID -maxdays 180

If you are running from Cloud Shell use the parameter -dt

If you are running from an instance and use Dynamic Group as authentication use -ip

In all other cases, make sure you have configured your OCI-CLI so it can authenticate.

