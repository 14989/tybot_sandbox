from ..models import Change
from django.utils import timezone
import unicodecsv as csv
import os
from background_task import background
from marketorestpython.client import MarketoClient

@background
def identify_broken_emails():
    munchkin_id = os.getenv('MUNCHKIN_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    api_limit=None
    max_retry_time=None
    mc = MarketoClient(munchkin_id, client_id, client_secret, api_limit, max_retry_time)

    fieldnames = ["email", "id"]
    inputListID = 1038
    outputListID = 1037
    brokenLeads = []
    brokenIDs = []

    # identify invalid emails, i.e. emails with the following errors:
    # missing recipient name, missing @ symbol, missing domain name, missing top level domain
    # Note: ignores blank emails
    for leads in mc.execute(method='get_multiple_leads_by_list_id_yield', listId=inputListID, 
                            fields=fieldnames, batchSize=None, return_full_result=False):
        for lead in leads:
            if lead["email"]:
                if str(lead["email"])[0] == '@':
                    brokenLeads.append(lead)
                    brokenIDs.append(lead["id"])
                elif '@' not in str(lead["email"]):
                    brokenLeads.append(lead)
                    brokenIDs.append(lead["id"])
                else:
                    domain = str(lead["email"]).split('@')[1]
                    if domain[0] == '.':
                        brokenLeads.append(lead)
                        brokenIDs.append(lead["id"])
                    elif '.' not in domain:
                        brokenLeads.append(lead)
                        brokenIDs.append(lead["id"])

    # add broken leads to Change log
    for lead in brokenLeads:
        Change.objects.create(workflow='Identify Broken Emails', timestamp=timezone.now(), 
                                marketo_id=lead["id"], changed_field="N/A", 
                                old_value=lead["email"], new_value=lead["email"])
    # add broken leads to output list
    counter = 0
    while (counter < len(brokenIDs)):
        lead = mc.execute(method="add_leads_to_list", listId=outputListID, 
                            id=brokenIDs[counter:counter+300])
        counter += 300
    # remove broken leads from input list
    counter = 0
    while (counter < len(brokenIDs)):
        lead = mc.execute(method='remove_leads_from_list', listId=inputListID, 
                            id=brokenIDs[counter:counter+300])
        counter += 300
    
    print("[" + str(timezone.now()) + "] COMPLETED WORKFLOW: identify broken emails")