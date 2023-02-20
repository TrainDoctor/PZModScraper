# PZModScraper
Script to pull Workshop IDs and Mod IDs for Steam Workshop collections.

Required to run: PyYAML, steam, requests

``pip install PyYAML steam requests``

```
usage: getcollection.py [-h] [-k [QQQQWWWWEEEERRRRTTTTYYYYUUUUIIII ...]] [-c [2736394657,7564936372,6374732965]] [-e [abc,def,ghi]] [--configpath [/path/to/config]] [default]

Script to pull Workshop IDs and Mod IDs for Steam Workshop collections.

positional arguments:
  default               Config preset within configuration file to use. Files support multi-config.

options:
  -h, --help            show this help message and exit
  -k [QQQQWWWWEEEERRRRTTTTYYYYUUUUIIII ...], --key [QQQQWWWWEEEERRRRTTTTYYYYUUUUIIII ...]
                        Steam WebAPI key as found at https://steamcommunity.com/dev/apikey
  -c [2736394657,7564936372,6374732965], --collections [2736394657,7564936372,6374732965]
                        id of a workshop collection: https://steamcommunity.com/sharedfiles/filedetails/?id=2736394657
  -e [abc,def,ghi], --exclude [abc,def,ghi]
                        List of Mod IDs to be excluded from output.
  --configpath [/path/to/config]
                        Path to and name of config file. Defaults to "config.yaml" in local dir.
```

Example:
``python getcollection.py default``
```
2609849923;1919438901;2071347174;2621259304;2313387159;1902468232;2478768005;2696083206;2619072426;2392709985;2688151429;2366717227;2728300240;2696147945;2704811006;2048544858;2685168362;2186592938;2327276448;2613596656;854848547;503640135;2529746725;2631149521;2617575303;2593268632;2341974040;566115016;2659216714;2544353492;2616986064;2553593324;2734705913;2710167561;2613871263;2725216703;2169435993;2694448564;2701170568;2487022075;2461082856;2714198296;2690908199;2650547917;2699828474;2687842971;1946782371;2503622437;2454057677;2763647806;2392676812;

AdvancedVolumeEnabler;alwaysfavorite;LitSortOGSN_gold;LitSortOGSN_diamond;LitSortOGSN_readOnePage;LitSortOGSN;LitSortOGSN_chocolate;LitSortOGSN_rice;BasicCrafting;BetterSortCC;BetterSoap;TMC_Trolley;wringclothes;TheStar;tsarslib;TearUnderwear;SwapIt;Skateboard;Skateboard;RIPKnife;snowiswater;snowiswaterbeta;NRK_Accountant;MoreDescriptionForTraits;CraftHelper41;CCItemTweak;CoolBag;BookCollection;bcUtils;EasyConfigChucked;eggonsHaveIFoundThisBook;eggonsModdingUtils;EliazBetterBagsBackpacks;fix_xp_view_41;ItemTweakerAPI;OutTheWindow;P4HasBeenRead;fuelsideindicator;HowMuchFuel;MapSymbolSizeSlider;MapLegendUI;MetalSpear;ModManagerServer;modoptions;ModManager;ExtraMapSymbols;ExtraMapSymbolsUI;TMC_TrueActions;SREmptyTrashMod;NoLighterNeeded;NoLighterNeeded;CatsReadMod;manageContainers;RebalancedPropMoving;Respawn;SimpleAddInventoryPages20191226;SkillRecoveryJournal;SmarterMechanics;SmarterMechanics;MoreCLR_desc4mood;lgd_antibodies;
```

You can then put these output of this script into the ``WorkshopIDs=`` and ``ModIDs=`` fields in your server config.
