# cli options need to collect:
##  Steam WebAPI Key, Collection ID

# import yaml
import argparse
import json
import re

from requests import exceptions
from steam.webapi import WebAPI

def handle_argv(count: int, args: list):
    ## if len 0, return 1
    if len(args) == 0:
        return 1
    ## if len > 1, return 2
    elif len(args) > count:
        return 2
    ## lol how'd you get here
    elif len(args) < 0:
        raise ValueError("Negative argv count, impossible scenario.")
    ## if len == count, return 0
    return 0

## gather raw json data of desired collection
def request_collection(collectionids: list, collectionamount: int):
    try:
        return api.call(method_path='ISteamRemoteStorage.GetCollectionDetails',\
            collectioncount=collectionamount, publishedfileids=collectionids)
    except exceptions.HTTPError as e:
        print("Collection ID is invalid, please try again.")
        exit()
    # print(collectioninfo)
    
## gather raw json data of desired mod/collection
def request_ugc(collectionamount: int, workshopidlist: list, *argv):
    argsvalid = handle_argv(1, argv)
    try:
        if argsvalid == 1:
            if "collection" or "mod" in argv[0]:
                print("Invalid invocation, must be \"collection\" or \"mod\".")
                exit()
            else:
                print("Multiple arguments in single argument.\n"+\
                    "Specify only: \"collection\" or \"mod\".")
                exit()
        else:
            if "collection" in str(argv[0]):
                return api.call(method_path='ISteamRemoteStorage.GetCollectionDetails',\
                collectioncount=collectionamount, publishedfileids=workshopidlist)
            if "mod" in str(argv[0]):
                return api.call(method_path='ISteamRemoteStorage.GetPublishedFileDetails',\
                itemcount=collectionamount, publishedfileids=workshopidlist)
    except exceptions.HTTPError as e:
        print("HTTP Error encountered, exiting." + e.with_traceback())
        exit()
    # print(modinfo)

## convert str json to usable Mod ID(s)
def process_modjson(modjson: str):
    for fulldescription in item_generator(modjson, "description"):
        slimdescription = re.findall("(?:Mod(?:\s?)ID)(?:\:)(?:[\s+])([\w._-]+)",\
            fulldescription)
    # print(slimdescription.groups())
    if slimdescription == None:
        print("Mod ID not found!")
        print("Check page for Mod ID", end=" ")
        print("and please alert the maintainer of this script!")
    else:
        buffer = []
        for modid in slimdescription:
            if modid in buffer:
                pass
            else:
                yield modid
            buffer.append(modid)
    
## gather raw json from a Workshop ID
def get_modjson(workshopid: str):
    out = []
    rawjson = request_ugc(1, [workshopid], "mod")
    modjson = json.loads(json.dumps(rawjson))
    for modid in process_modjson(modjson):
        out.append(str(modid))
    return out

def update_collection(collection: dict, workshopid: str, modids: list):
    if workshopid in collection:
        collection.update({str(workshopid): modids})
    else:
        print("Could not find Workshop ID " + workshopid + " in " + str(collection))
        
def item_generator(json_input, lookup_key):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from item_generator(v, lookup_key)
    elif isinstance(json_input, list):
        for item in json_input:
            yield from item_generator(item, lookup_key)
            
def get_ids(collection: dict, *argv):
    tocollect= ""
    out = []
    argsvalid = handle_argv(1, argv)
    if argsvalid == 1:
        print("No ID type specified. Defaulting to Workshop ID.")
        out = []
        for wsid,modid in collection.items():
            out.append(workshopid)
        return out
    elif argsvalid == 2:
        print("Specify only one id to yield!")
        exit()
    else:
        for arg in argv:
            if arg == "workshop":
                tocollect="workshop"
            elif arg == "mod":
                tocollect="mod"
            else:
                print("No ID type specified. Defaulting to Workshop ID.")
        if tocollect == "workshop":
            for wsid,modids in collection.items():
                out.append(wsid)
            return out
        elif tocollect == "mod":
            for wsid,modids in collection.items():
                for modid in modids:
                    out.append(modid)
        else:
            print("How'd you manage to end up here?")
            return    
          
parser = argparse.ArgumentParser(\
    description='Script to pull Workshop IDs and Mod IDs for Steam Workshop collections.')
parser.add_argument('-k', '--key', metavar='QQQQWWWWEEEERRRRTTTTYYYYUUUUIIII', type=str, nargs="*",\
    help="your Steam WebAPI key as found at https://steamcommunity.com/dev/apikey")
parser.add_argument('-c', '--collection', metavar='2736394657', type=str, nargs="+",\
    help="the id of your workshop collection, found at the end of a collection like this:\
        https://steamcommunity.com/sharedfiles/filedetails/?id=2736394657",\
        default="0")

cli_args = parser.parse_args()

###########################################
### \|/ Section 0, Preliminary Work \|/ ###
###########################################

## get api key
apikey = cli_args.key

## get collection id and amount of collections
collectionidlist = []

for arg in cli_args.collection:
    collectionidlist.append(arg)

## dictionary of workshop IDs as the key
## and an array of Mod IDs as corresponding value
# collectiondict = dict([("workshopid", ["modid"])])
collectiondict = {}
collectionsize = 0

reachedSteam = True

# key must be valid/non-empty
if apikey is None or len(apikey) <= 0:
    # print("Key must not be empty!")
    parser.print_help()
    exit()
    # raise ValueError("Key cannot be empty!")

# check that WebAPI is avaliable and key is working
try:
    test = WebAPI(apikey)
except (exceptions.ConnectionError, exceptions.ConnectTimeout) as e:
    print("WebAPI appears to not be responding.\n\
          Check your internet connection and or http://steamstat.us")
    reachedSteam = False
except exceptions.HTTPError as e:
    print("WebAPI not working or WebAPI key invalid.")
    reachedSteam = False
finally:
    if not reachedSteam:
        exit()
    api = WebAPI(apikey, format="json", https=True)
       
###############################################
### \|/ Section 1, Workshop ID Scraping \|/ ###
###############################################

## request raw json data
collectionraw = request_collection(collectionidlist, len(collectionidlist))

## make python happy with json data
collectionjson = json.loads(json.dumps(collectionraw))
# print(collectionjson)

## add keys (workshop IDs) to collectiondict
for workshopid in item_generator(collectionjson, "publishedfileid"):
    ## in case the collection id(s) aren't yielded, use try except
    try:
        ## make sure that we're not grabbing the extra
        ## collection description, even if it won't have any Mod IDs.
        for collectionid in collectionidlist:
            if str(workshopid) == str(collectionid):
                break
            else:
                collectiondict.update({str(workshopid): [""]})
    except ValueError:
        print("Handled ID not in list error.")
print("")
## print out workshop ids in config file format
for wsid, modids in collectiondict.items():
    print(wsid, end=";")
print("")
# for modid in modids:
#     print(wsid, modid)

## adjust size of collection to correspond to collectiondict's size
collectionsize = len(collectiondict)

##########################################
### \|/ Section 2, Mod ID Scraping \|/ ###
##########################################

print("")

workshopidlist = get_ids(collectiondict, "workshop")

## parse Mod ID(s) from
## a list of Workshop IDs
for id in workshopidlist:
    modids = get_modjson(id)
    update_collection(collectiondict, id, modids)

for workshopdids,modids in collectiondict.items():
    for modid in modids:
        print(modid, end=";")
print("")

## gather json data of desired mods
try:
    modinfo = api.call(method_path='ISteamRemoteStorage.GetPublishedFileDetails',\
        itemcount=collectionsize, publishedfileids=workshopidlist)
except exceptions.HTTPError as e:
    print("HTTP Error encountered, exiting." + e.with_traceback())
    exit()
# print(modinfo)

### TODO: Add config support (yaml)
### TODO: Add support for excluding Mod IDs from output via a config.
