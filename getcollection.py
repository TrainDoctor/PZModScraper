# cli options need to collect:
##  Steam WebAPI Key, Collection ID, Excluded Mod IDs

import argparse
import difflib
import os
import re
import io

import yaml
from requests import exceptions
from steam.webapi import WebAPI

class splitargs(argparse.Action):
    def __call__(self, parser, namespace, values: str, option_string=None):
        setattr(namespace, self.dest, [v for v in values.split(',') if v])

def handle_argv(count: int, args: list):
    ## if len 0, return 1
    if len(args) == 0:
        return 1
    ## if len > count, return 2
    elif len(args) > count:
        print("More arguements given than allowed.")
        return 2
    ## lol how'd you get here
    elif len(args) < 0:
        raise ValueError("Negative argv count, impossible scenario.")
    ## if len == count, return 0
    else:
        return 0

## yield values by looking recursively
## looking through json data via yield (coroutine)
def item_generator(json_input: dict, lookup_key,):
    if isinstance(json_input, dict):
        for k, v in json_input.items():
            if k == lookup_key:
                yield v
            else:
                yield from item_generator(v, lookup_key) 
    elif isinstance(json_input, list):
        for item in json_input:
                yield from item_generator(item, lookup_key)

## gather raw json data of desired mod/collection
def request_ugc(amount: int, workshopidlist: list, *argv) -> dict:
    argsvalid = handle_argv(1, argv)
    try:
        if argsvalid == 2:
            if "collection" or "mod" in argv[0]:
                print("Multiple arguments in single argument.\n"+\
                    "Specify only: \"collection\" or \"mod\".")
                exit()
        else:
            if "collection" in str(argv[0]):
                return api.call(method_path='ISteamRemoteStorage.GetCollectionDetails',\
                collectioncount=amount, publishedfileids=workshopidlist)
            if "mod" in str(argv[0]):
                return api.call(method_path='ISteamRemoteStorage.GetPublishedFileDetails',\
                itemcount=amount, publishedfileids=workshopidlist)
    except exceptions.HTTPError as e:
        print("HTTP Error encountered, exiting." + e.with_traceback())
        exit()

def update_collection(collection: dict, workshopid: str, modids: list):
    if workshopid in collection:
        collection.update({str(workshopid): modids})
    else:
        print("Could not find Workshop ID " + workshopid + " in " + str(collection))
            
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

###########################################
### \|/ Section 0, Preliminary Work \|/ ###
###########################################

defaultfilepath = str(os.path.realpath(__file__))
defaultfilepath = defaultfilepath.replace("getcollection.py",\
    "config.yaml")

parser = argparse.ArgumentParser(\
    description='Script to pull Workshop IDs and Mod IDs for Steam Workshop collections.')
parser.add_argument('-k', '--key', metavar='QQQQWWWWEEEERRRRTTTTYYYYUUUUIIII',\
    type=str, nargs="*",\
    help="Steam WebAPI key as found at https://steamcommunity.com/dev/apikey")
parser.add_argument('-c', '--collections', metavar='2736394657,7564936372,6374732965',\
    type=str, nargs="?", default="", action=splitargs,\
    help="id of a workshop collection:\
    https://steamcommunity.com/sharedfiles/filedetails/?id=2736394657")
parser.add_argument('-e', '--exclude', metavar='abc,def,ghi',\
    type=str, nargs="?", default="", action=splitargs,\
    help="List of Mod IDs to be excluded from output.")
parser.add_argument('--configpath', metavar='/path/to/config',\
    type=str, nargs="?", default=defaultfilepath, action=splitargs,\
    help="Path to and name of config file. Defaults to \"config.yaml\" in local dir.")
parser.add_argument('config', metavar='default',\
    type=str, nargs="?", default="none",\
    help="Config preset within configuration file to use. Files support multi-config.")

## create apikey placeholder
apikey = ""
## get collection id and amount of collections
collectionids = []
## get list of strings to exclude from output
excluded = []

cli_args = parser.parse_args()

usingconfig = False

if cli_args.config == "none": 
    print("No config specified.")
elif cli_args.config != None:
    usingconfig = True
else:
    print("How did I get here?\nhttps://www.youtube.com/watch?v=djT_hBVbmGc")

if usingconfig:
    configfile = yaml.load(stream=open(cli_args.configpath, 'r'),\
        Loader=yaml.FullLoader)
    conf = configfile.get(str(cli_args.config))
    for k,v in conf.items():
        if k == "apikey":
            # print("apikey")
            if len(v) > 0:
                apikey = str(v)
            else:
                print("API Key from config not present. "+\
                    "Run \'python getcollection.py --help\'"+\
                    " for more info.")
                exit()
            continue
        if k == "collections":
            # print("collections")
            if len(v) > 0:
                for id in v:
                    collectionids.append(id)
            else:
                print("Collection ID from config not present. "+\
                    "Run \'python getcollection.py --help\'"+\
                    " for more info.")
                exit()
            continue
        if k == "exclusions":
            # print("exclusions")
            for exclusion in v:
                excluded.append(str(exclusion))
            continue
else:
    ## get api key
    apikey = cli_args.key
    ## get collection ID(s)
    for id in cli_args.collections:
        collectionids.append(id)
    ## get excluded Mod ID(s)
    for exclusion in cli_args.exclude:
        excluded.append(str(exclusion))

#############################################
### \|/ Section 1, Connection Testing \|/ ###
#############################################

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
    exit()
except exceptions.HTTPError as e:
    print("WebAPI not working or WebAPI key invalid.")
    reachedSteam = False
    exit()
if not reachedSteam:
    print("No errors encountered but Steam could not be reached.")
    exit()
else:
    api = WebAPI(apikey, format="json", https=True)

## dictionary of workshop IDs as the key
## and an array of Mod IDs as corresponding value
# collectiondict = dict([("workshopid", ["modid"])])
wscollection = {}
wscollectionsize = 0
      
###############################################
### \|/ Section 2, Workshop ID Scraping \|/ ###
###############################################

## print a newline to seperate 
## input from Workshop ID output
print("")

## request raw json data
collectionjson = request_ugc(len(collectionids), collectionids,\
    "collection")

## add keys (WSIDs) to wscollection
for workshopid in item_generator(collectionjson, "publishedfileid"):
    ## in case the collection id(s) aren't yielded, use try except
    try:
        ## make sure that we're not grabbing the extra
        ## collection description, even if it won't have any Mod IDs.
        for collectionid in collectionids:
            if str(workshopid) == str(collectionid):
                break
            else:
                wscollection.update({str(workshopid): ['']})
    except ValueError:
        print("Handled ID not in list error.")

## print out workshop ids in config file format
for wsid,modid in wscollection.items():
    print(wsid, end=";")
print("")

## adjust size of collection to correspond to collectiondict's size
wscollectionsize = len(wscollection)

##########################################
### \|/ Section 3, Mod ID Scraping \|/ ###
##########################################

## print a newline to put a space
## between WSID output and MID output
print("")

## instead of iterating through WSIDs to get MIDs,
## collect all raw mod json in a single call
modjson = request_ugc(len(wscollection),\
    list(wscollection.keys()), "mod")

## use zip to join the two generator's output for good sorting
joinedinfo = zip(item_generator(modjson, "publishedfileid"),\
    item_generator(modjson, "description"))

spacerneeded = False
for wsid,description in joinedinfo:
    ## mod ids in description
    ids = re.findall\
        ("(?:Mod(?:\s?)ID)(?:\:)(?:[\s+])([\w._&-]+)", description)
    update_collection(wscollection, wsid, ids)
    for id in ids:
        for exclude in excluded:
            ratio = difflib.SequenceMatcher(lambda x: x in " \t", exclude, id).ratio()
            if ratio >= 0.5 and ratio < 0.636:
                spacerneeded = True
                print("One of your exclusions is miss-spelled or similair to another ID.")
                print("\tExcluded ID: " + str(exclude) + "\n\tMod ID: " + str(id))
        
if spacerneeded:
    print("")

## print out list of Mod IDs
## which correspond to Workshop IDs
for workshopdids,modids in wscollection.items():
    for modid in modids:
        if str(modid) not in excluded:
            print(modid, end=";")
print("\n")
