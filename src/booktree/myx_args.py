import argparse
import json
from pprint import pprint

#Module Variables
params:any

def importArgs():
    appDescription = """Reorganize your audiobooks using ID3 or Audbile metadata.\nThe originals are untouched and will be hardlinked to their destination"""
    parser = argparse.ArgumentParser(prog="booktree", description=appDescription)
    parser.add_argument ("config_file", help="Your Config File")
    #Debug flags
    parser.add_argument ("--dry-run", default=None, action="store_true", help="If provided, will override dryRun in config")
    parser.add_argument("--verbose", default=None, action="store_true", help="If provided, will print additional info")
    #Advanced flags
    parser.add_argument("--no-opf", default=None, action="store_true", help="If provided, skips OPF file")
    parser.add_argument("--no-cache", default=None, action="store_true", help="If provided, processes books that have been processed/cached before")
    parser.add_argument("--multibook", default=None, action="store_true", help="If provided, will process books at file level")
    parser.add_argument("--fixid3", default=None, action="store_true", help="If provided, will attempt to fix id3 metadata")
    parser.add_argument("--ebooks", default=None, action="store_true", help="If provided, will look for ebooks and skip audible")
    parser.add_argument("--add-narrators", default=None, action="store_true", help="If provided,include the narrators in the path")

    # #you want a specific file or pattern
    # parser.add_argument("--file", default="", help="The file or files(s) you want to process.  Accepts * and ?. Defaults to *.m4b/*.mp3")
    # #path to source files, e.g. /data/torrents/downloads
    # parser.add_argument("--source_path", default=".", help="Where your unorganized files are")
    # #path to media files, e.g. /data/media/abs
    # parser.add_argument("--media_path", help="Where your organized files will be, i.e. your Audiobookshelf library", required=True)
    # #path to log files, e.g. /data/media/abs
    # parser.add_argument("--log_path", default="", help="Where your log files will be")
    # #medata source (audible|mam|mam-audible|id3|log)
    # parser.add_argument("metadata", choices=["audible","mam","mam-audible","log"], default="mam-audible", help="Source of the metada: (audible, mam, mam-audible)")
    # parser.add_argument("--session", default="", help="Your session cookie")
    # parser.add_argument("--matchrate", default=60, help="Minimum acceptable fuzzy match rate. Defaults to 60")
    # #debug flags
    # parser.add_argument("--dry-run", default=False, action="store_true", help="If provided, will only create log and not actually build the tree")
    # parser.add_argument("--verbose", default=False, action="store_true", help="If provided, will print additional info")

    #get all arguments
    args = parser.parse_args()

    # if (len(args.log_path)==0):
    #     args.log_path=os.path.join(os.getcwd(),"logs")    

    #set module variable to args
    return args

def merge_dictionaries_recursively (dict1, dict2):
    """ Update two config dictionaries recursively.
        Args:
            dict1 (dict): first dictionary to be updated
            dict2 (dict): second dictionary which entries should be preferred
    """
    if dict2 is None: return

    for k, v in dict2.items():
        if k not in dict1:
            dict1[k] = dict()
        if isinstance(v, dict):
            merge_dictionaries_recursively (dict1[k], v)
        else:
            dict1[k] = v    

class Config(object):  
    """ Simple dict wrapper that adds a thin API allowing for slash-based retrieval of
        nested elements, e.g. cfg.get_config("meta/dataset_name")
    """
    def __init__(self, params):
        try:
            with open(params.config_file) as cf_file:
                cfg = json.loads (cf_file.read())

                #override config/flags with command line param
                if params.dry_run is not None:
                    cfg["Config"]["flags"]["dry_run"] = bool(params.dry_run)            

                if params.verbose is not None:
                    cfg["Config"]["flags"]["verbose"] = bool(params.verbose)            

                if params.no_cache is not None:
                    cfg["Config"]["flags"]["no_cache"] = bool(params.no_cache)            

                if params.no_opf is not None:
                    cfg["Config"]["flags"]["no_opf"] = bool(params.no_opf)            

                if params.multibook is not None:
                    cfg["Config"]["flags"]["multibook"] = bool(params.multibook)            

                if params.ebooks is not None:
                    cfg["Config"]["flags"]["ebooks"] = bool(params.ebooks)            

                if params.fixid3 is not None:
                    cfg["Config"]["flags"]["fixid3"] = bool(params.fixid3)            

                if params.add_narrators is not None:
                    cfg["Config"]["flags"]["add_narrators"] = bool(params.add_narrators)   

            self._data = cfg            
        except Exception as e:
            raise Exception(e)

    def get(self, path=None, default=None):
        # we need to deep-copy self._data to avoid over-writing its data
        sub_dict = dict(self._data)

        if path is None:
            return sub_dict

        path_items = path.split("/")[:-1]
        data_item = path.split("/")[-1]

        try:
            for path_item in path_items:
                sub_dict = sub_dict.get(path_item)

            value = sub_dict.get(data_item, default)

            return value
        except (TypeError, AttributeError):
            return default
