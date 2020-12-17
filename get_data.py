import pickle
import requests
from datetime import datetime


def get_cached_agent(auth, agency_id, agent_name):
  recache = False
  t, agencies = pickle.load(open("agents_cache.pkl", "rb"))
  if agencies == None:
    agencies = {}
    recache = True

  if agency_id not in agencies:
    agencies[agency_id] = get_new_agent_data(auth, agency_id)
    recache = True
  
  agency = agencies[agency_id]

  diff = agency.get("time_fetched", datetime.now()) - datetime.now()
  if diff.days > 1:
    agencies[agency_id] = get_new_agent_data(auth, agency_id)
    recache = True

  agent_names = {f'{x["firstName"]} {x["lastName"]}'.lower().strip(): x["id"] for x in agency["agents"]}
  agents = {x["id"]: x for x in agency["agents"]}

  if agent_name not in agent_names:
    agencies[agency_id] = get_new_agent_data(auth, agency_id)
    recache = True
  
  # No more fetches so can recache here
  if recache == True:
      cache_agent_data(agencies)

  if agent_name not in agent_names:
    print(agent_name, agent_names)
    return ("No agent data", "", "")
  
  agent_id = agent_names[agent_name]

  agent = agents[agent_id]

  return (f'{agent.get("firstName", "")} {agent.get("lastName", "")}', agent.get("email", ""), agent.get("phone", ""))

def cache_agent_data(all_agents):
  pickle.dump((datetime.now(), all_agents) , open("agents_cache.pkl", "wb"))

def get_new_agent_data(auth, agency_id):
  agency_url = "https://api.domain.com.au/v1/agencies/" + str(agency_id)
  agency_response = requests.get(agency_url,headers=auth)
  agency_data = agency_response.json()
  agency_data["time_fetched"] = datetime.now()
  return agency_data

def api_data():

  # this guy did it
  # https://colab.research.google.com/drive/16wg0VWPim1-dwt7W8jZuJrqFRMrW8iQ0#scrollTo=tlwYltsjF3DO

  # importing the requests library 
   

  ### query data
  # data to be sent to api 

  data = """
  {
    "listingType":"Rent",
    "maxprice":450,
    "pageSize": 100,
    "locations":[
      {
        "state":"NSW",
        "region":"",
        "area":"",
        "suburb":"Coffs Harbour", 
        "postCode":"2450",
        "includeSurroundingSuburbs":true
      },
      {
        "state":"NSW",
        "region":"",
        "area":"",
        "suburb":"Toormina", 
        "postCode":"2542",
        "includeSurroundingSuburbs":true
      } 
    ]
  }
  """
 
  ### Authorisation yvette.maree api keys
 # client_id =    "client_2956ea033588bab24b1288e267c3f20f"
  
 # client_secret = "secret_3daacd10fadc1ba0a7771dadc4b61946"

#coffs nc
          
  client_id =    "client_8af75bde18ec7930d9664346b69e0b28"
  
  client_secret = "secret_fb8d5ec7029c36bc0231d4cb046651b4"         
          

 # student mq email alt id

 # client_id =    "client_0e9c75f4b6483cb84ddd7eb1e76cb857"
 
 # client_secret = "secret_6ce93f4260eb92e8d9cb3a72177c7f13"





  # POST request for token
  response = requests.post('https://auth.domain.com.au/v1/connect/token', data = {'client_id':client_id, "client_secret": client_secret,"grant_type":"client_credentials","scope":"api_listings_read api_agencies_read api_properties_read","Content-Type":"text/json"
  })
  token=response.json()
  access_token=token["access_token"]

  auth = {"Authorization":"Bearer " + access_token}

  ### Make query

  # defining the api-endpoint  
  API_ENDPOINT = "https://api.domain.com.au/v1/listings/residential/_search"

  # sending post request and saving response as response object 
  r = requests.post(url = API_ENDPOINT, headers=auth, data = data) 
    
  # extracting response text  
  response = r.text 
  import json
  response_data = json.loads(response)

  properties = []

  for i in response_data:
    listing = i['listing']
    prop = {}
    slug = listing["listingSlug"]
    prop["link"] = "https://domain.com.au/" + slug
    
    agency = listing["advertiser"]
    agency_id = agency["id"]
    if len(agency["contacts"]) > 0:
      agent_name = agency["contacts"][0]["name"].lower().strip()
    else:
      agent_name = ""

    name, email, phone = get_cached_agent(auth, agency_id, agent_name)
    prop['agent_name'] = name
    prop['agent_email'] = email
    prop['agent_phone'] = phone

    property_details = listing['propertyDetails']
    prop["type"] = property_details['propertyType']

    if prop["type"].lower() == "apartmentunitflat":
      prop["type"] = "Apartment / Unit" 
    elif prop["type"] == "house":
      prop["type"] = "House" 
    elif prop["type"] == "studio":
      prop["type"] = "Studio" 
    elif prop["type"] == "townhouse":
      prop["type"] = "Townhouse" 

    prop["headline"] = listing.get("headline", "")


    prop['description'] = listing.get("summaryDescription", "")[13:]

    prop["suburb"] = property_details.get("suburb", "").title()
    prop["unitNumber"] = property_details.get("unitNumber", "")
    prop["streetNumber"] = property_details.get("streetNumber", "")
    prop["street"] = property_details.get("street", "")
    
    prop["datelisted"] = listing.get("dateListed", "")
    prop["dateavailable"] = listing.get("dateAvailable", "")

    cost_details =  listing.get("priceDetails", "")
    if cost_details:
      prop["cost"] =  cost_details["displayPrice"]
    else:
      prop["cost"] = ""

    advertiser_details = listing['advertiser']
    prop['agency'] = advertiser_details['name']


    properties.append(prop)
          
  properties_sorted = sorted(properties, key=lambda x: x["cost"])
 
  return properties_sorted

  
