from ..models import Change
from django.utils import timezone
import unicodecsv as csv
import os
from background_task import background
from marketorestpython.client import MarketoClient

@background
def make_emails_all_lowercase():
    munchkin_id = os.getenv('MUNCHKIN_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    api_limit=None
    max_retry_time=None
    mc = MarketoClient(munchkin_id, client_id, client_secret, api_limit, max_retry_time)

    fieldnames = ["email", "id"]
    inputListID = 1038
    outputListID = 1036
    oldEmails = {}
    updatedLeads = []
    updatedIDs = []

    # convert uppercase letters in email addresses into lowercase letters
    for leads in mc.execute(method='get_multiple_leads_by_list_id_yield', listId=inputListID, 
                            fields=fieldnames, batchSize=None, return_full_result=False):
        for lead in leads:
            if not str(lead["email"]).islower() and bool(lead["email"]):
                oldEmails[lead["id"]] = lead["email"]
                lead["email"] = str(lead["email"]).lower()
                updatedLeads.append(lead)
    counter = 0
    while (counter < len(updatedLeads)):
        lead = mc.execute(method="create_update_leads", leads=updatedLeads[counter:counter+300], 
                            action="updateOnly", lookupField="id")
        for response in lead:
            if response["status"] == "updated":
                updatedIDs.append(response["id"])
        counter += 300
    
    # add updated leads to change log and output list
    for lead in updatedLeads:
        if lead["id"] in updatedIDs:
            Change.objects.create(workflow='Make Emails All Lowercase', timestamp=timezone.now(), 
                                    marketo_id=lead["id"], changed_field="email", 
                                    old_value=oldEmails[lead["id"]], new_value=lead["email"])
    counter = 0
    while (counter < len(updatedIDs)):
        lead = mc.execute(method="add_leads_to_list", listId=outputListID, 
                            id=updatedIDs[counter:counter+300])
        counter += 300
    
    print("[" + str(timezone.now()) + "] COMPLETED WORKFLOW: make emails all lowercase")