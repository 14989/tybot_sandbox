from ..models import Change
from django.utils import timezone
import unicodecsv as csv
import os
from background_task import background
from .common_email_domains import domains
from marketorestpython.client import MarketoClient


@background
def add_company_by_email_domain():
    munchkin_id = os.getenv('MUNCHKIN_ID')
    client_id = os.getenv('CLIENT_ID')
    client_secret = os.getenv('CLIENT_SECRET')
    api_limit=None
    max_retry_time=None
    mc = MarketoClient(munchkin_id, client_id, client_secret, api_limit, max_retry_time)

    fieldnames = ["email", "company", "id"]
    inputListID = 1038
    outputListID = 1035
    oldCompanies = {}
    updatedLeads = []
    updatedIDs = []
    excludedDomains = domains
    companiesByDomain = {"None": None}

    # exclude popular email domains
    for domain in excludedDomains:
        companiesByDomain[domain] = None

    # associate email domains with companies 
    # collision priority given to company with most associations with each email domain
    for leads in mc.execute(method="get_multiple_leads_by_list_id_yield", listId=inputListID, 
                            fields=fieldnames, batchSize=None, return_full_result=False):
        for lead in leads:
            if '@' in str(lead["email"]):
                domain = str(lead["email"]).split("@")[1]
            else:
                domain = "None"
            if lead["company"]:
                # add email domain to outer dictionary
                if domain not in companiesByDomain:
                    companiesByDomain[domain] = {}
                if companiesByDomain[domain] != None:
                    # add company name to inner dictionary
                    if lead["company"] not in companiesByDomain[domain]:
                        companiesByDomain[domain][lead["company"]] = 1
                    # increase count of company name in inner dictionary
                    else:
                        companiesByDomain[domain][lead["company"]] += 1

    # update leads that are missing company but have a known email domain
    for leads in mc.execute(method="get_multiple_leads_by_list_id_yield", listId=inputListID, 
                            fields=fieldnames, batchSize=None, return_full_result=False):
        for lead in leads:
            if not lead["company"]:
                if '@' in str(lead["email"]):
                    domain = str(lead["email"]).split("@")[1]
                else:
                    domain = "None"
                if domain in companiesByDomain and companiesByDomain[domain]:
                    oldCompanies[lead["id"]] = lead["company"]
                    lead["company"] = max(companiesByDomain[domain], 
                                          key = lambda k : companiesByDomain[domain][k])
                    updatedLeads.append(lead)
    counter = 0
    while (counter < len(updatedLeads)):
        lead = mc.execute(method="create_update_leads", leads=updatedLeads[counter:counter+300], 
                            action="updateOnly", lookupField="id")
        for response in lead:
            if response["status"] == "updated":
                updatedIDs.append(response["id"])
        counter += 300

    # add updated leads to change log
    for lead in updatedLeads:
        if lead["id"] in updatedIDs:
            Change.objects.create(workflow='Add Company By Email Domain', timestamp=timezone.now(), 
                                    marketo_id=lead["id"], changed_field="company", 
                                    old_value=oldCompanies[lead["id"]], new_value=lead["company"])
    # add updated leads to output list
    counter = 0
    while (counter < len(updatedIDs)):
        lead = mc.execute(method="add_leads_to_list", listId=outputListID, 
                            id=updatedIDs[counter:counter+300])
        counter += 300

    print("[" + str(timezone.now()) + "] COMPLETED WORKFLOW: add company by email domain")