# PZModScraper
Script to pull Workshop IDs and Mod IDs for Steam Workshop collections.
```
usage: getcollection.py [-h] [-k [QQQQWWWWEEEERRRRTTTTYYYYUUUUIIII ...]] [-c 2736394657 [2736394657 ...]]

Script to pull Workshop IDs and Mod IDs for Steam Workshop collections.

options:
  -h, --help            show this help message and exit
  -k [QQQQWWWWEEEERRRRTTTTYYYYUUUUIIII ...], --key [QQQQWWWWEEEERRRRTTTTYYYYUUUUIIII ...]
                        your Steam WebAPI key as found at https://steamcommunity.com/dev/apikey
  -c 2736394657 [2736394657 ...], --collection 2736394657 [2736394657 ...]
                        the id of your workshop collection, found at the end of a collection like this:
                        https://steamcommunity.com/sharedfiles/filedetails/?id=2736394657
```

You can then put these output of this script into the ``WorkshopIDs=`` and ``ModIDs=`` fields in your server config.

Desired features if I ever get around to adding them:
- [x] Config files for usage based on yaml
- [x] Allow for excluding mod ids
