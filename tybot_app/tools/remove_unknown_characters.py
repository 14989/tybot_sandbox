from ..models import Change
from django.utils import timezone
import unicodecsv as csv
import os
from background_task import background
from marketorestpython.client import MarketoClient

@background
def remove_unknown_characters():
    munchkin_id = os.getenv('MUNCHKIN_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    api_limit=None
    max_retry_time=None
    mc = MarketoClient(munchkin_id, client_id, client_secret, api_limit, max_retry_time)

    fieldnames = ['firstName','lastName','email',
                    'city','company','industry','postalCode', 
                    'state', 'country', 'id']
    inputListID = 1038
    outputListID = 1036

    for field in fieldnames:
        oldValues = {}
        updatedLeads = []
        updatedIDs = []
        # remove characters that Windows cannot recognize from field value
        for leads in mc.execute(method='get_multiple_leads_by_list_id_yield', listId=inputListID, 
                                fields=fieldnames, batchSize=None, return_full_result=False):
            for lead in leads:
                if "�" in str(lead[field]):
                    oldValues[lead["id"]] = lead[field]
                    lead[field] = "".join(c for c in str(lead[field]) if c not in "�")
                    updatedLeads.append(lead)
        counter = 0
        while (counter < len(updatedLeads)):
            lead = mc.execute(method="create_update_leads", leads=updatedLeads[counter:counter+300], 
                                action="updateOnly", lookupField="id")
            for response in lead:
                if response["status"] == "updated":
                    updatedIDs.append(response["id"])
                # TODO: write skipped leads to a csv
            counter += 300

        # add updated leads to change log and output list
        for lead in updatedLeads:
            print(lead)
            if lead["id"] in updatedIDs:
                Change.objects.create(workflow='Remove Unknown Characters', timestamp=timezone.now(), 
                                        marketo_id=lead['id'], changed_field=field, 
                                        old_value=oldValues[lead["id"]], new_value=lead[field])
        counter = 0
        while (counter < len(updatedIDs)):
            lead = mc.execute(method="add_leads_to_list", listId=outputListID, 
                                id=updatedIDs[counter:counter+300])
            counter += 300

    print("[" + str(timezone.now()) + "] COMPLETED WORKFLOW: remove unknown characters")