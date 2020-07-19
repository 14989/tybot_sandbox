from ..models import Change
from django.utils import timezone
import unicodecsv as csv
import os
from background_task import background
from marketorestpython.client import MarketoClient

@background
def update_country_by_state():
    munchkin_id = os.getenv('MUNCHKIN_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    api_limit=None
    max_retry_time=None
    mc = MarketoClient(munchkin_id, client_id, client_secret, api_limit, max_retry_time)

    fieldnames = ["state", "country", "id"]
    inputListID = 1038
    outputListID = 1035
    oldCountries = {}
    updatedLeads = []
    updatedIDs = []

    # if state field is filled in, update country to "United States"
    # if country field is "US", update country to "United States"
    for leads in mc.execute(method='get_multiple_leads_by_list_id_yield', listId=inputListID, 
                            fields=fieldnames, batchSize=None, return_full_result=False):
        for lead in leads:
            if not lead["country"]:
                if lead["state"]:
                    oldCountries[lead["id"]] = lead["country"]
                    lead["country"] = "United States"
                    updatedLeads.append(lead)
            elif str(lead["country"]) == "US":
                oldCountries[lead["id"]] = lead["country"]
                lead["country"] = "United States"
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
            Change.objects.create(workflow='Update Country By State', timestamp=timezone.now(), 
                                    marketo_id=lead['id'], changed_field='country', 
                                    old_value=oldCountries[lead["id"]], new_value=lead['country'])
    counter = 0
    while (counter < len(updatedIDs)):
        lead = mc.execute(method="add_leads_to_list", listId=outputListID, 
                            id=updatedIDs[counter:counter+300])
        counter += 300

    print("[" + str(timezone.now()) + "] COMPLETED WORKFLOW: update country by state")