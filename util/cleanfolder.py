# Check if local files are older than X days
# If so, then upload files that aren't already in dropbox to dropbox / update out of date files

import dropbox
import os
import datetime
from tabulate import tabulate

import argparse

from dropbox_access import TOKEN
import export_to_dropbox

import scrapelogger

logger = scrapelogger.ScrapeLogger('cleanfolder')

LOCAL_SHELFLIFE = 7   # days to keep files on local computer
logger.log.info("LOCAL_SHELFLIFE set to {}".format(LOCAL_SHELFLIFE))

def get_old_local_files(localfolder):

    current_time = datetime.datetime.now()    
    local_files = dict()

    filelist = [f for f in os.listdir(localfolder) if os.path.isfile(os.path.join(localfolder, f))]

    for f in filelist:
        ts = os.path.getmtime(os.path.join(localfolder, f))
        last_updated =  datetime.datetime.fromtimestamp(ts)
        if (current_time - last_updated) > datetime.timedelta(days=LOCAL_SHELFLIFE):
            local_files[f] = last_updated

    return local_files


def get_dropbox_files(dropboxfolder):

    dbx = dropbox.Dropbox(TOKEN)
    response = dbx.files_list_folder(path=dropboxfolder)

    db_files = dict()
    for f in response.entries:
        if type(f) == dropbox.files.FileMetadata:
            db_files[f.name] = f.server_modified

    return db_files


def compare_files(oldlocalfiles, dropboxfiles):
    missing_files = dict()
    not_updated_files = dict()
    ok_files  = dict()

    # Loop through the local files, check if they were updated more recently than the dropbox files
    for f, updated in oldlocalfiles.items():
        if f not in dropboxfiles:
            missing_files[f] = updated
        elif updated > dropboxfiles[f]:
            not_updated_files[f] = {'local_ts': updated, 'db_ts' : dropboxfiles[f]}
        else:
            ok_files[f] = updated

    return (missing_files, not_updated_files, ok_files)


def summarize_files(missing_files, not_updated_files, ok_files):
    # Print summary statistics
    print("")
    print("Missing in Dropbox")
    print("===========================================")
    missing_data = []
    for f, updated in missing_files.items():
        missing_data.append([f, updated.strftime("%m/%d/%Y, %H:%M:%S")])
    print(tabulate(missing_data, headers = ['File', 'Last Updated']))

    print("")
    print("Not up to date in Dropbox")
    print("==========================================")
    not_updated_data = []
    for f, ts in not_updated_files.items():
        not_updated_data.append([f, ts['local_ts'].strftime("%m/%d/%Y, %H:%M:%S"), ts['db_ts'].strftime("%m/%d/%Y, %H:%M:%S")])
    print(tabulate(not_updated_data, headers = ['File', 'Local Folder Timestamp','Dropbox Timestamp']))

    print("")
    print("OK")
    print("=========================================")
    ok_data = []
    for f, updated in ok_files.items():
        ok_data.append([f, updated.strftime("%m/%d/%Y, %H:%M:%S")])
    print(tabulate(ok_data, headers = ['File', 'Last Updated']))


def clean_folder(localfolder, dropboxfolder, verbose = False, test = False):
    
    oldlocalfiles = get_old_local_files(localfolder)

    if not oldlocalfiles:
        logger.log.info("{} - No files older than shelf life".format(localfolder))
        return

    dropboxfiles = get_dropbox_files(dropboxfolder)
    missing_files, not_updated_files, ok_files = compare_files(oldlocalfiles, dropboxfiles)
    
    if verbose:
        summarize_files(missing_files, not_updated_files, ok_files)

    if not test:

        for f in missing_files:
            logger.log.info("Copying {}".format(f))
            export_to_dropbox.move_to_dropbox(
                os.path.join(localfolder, f), 
                os.path.join(dropboxfolder, f)
            )

        for f in not_updated_files:
            logger.log.info("Updating {}".format(f))
            export_to_dropbox.move_to_dropbox(
                os.path.join(localfolder, f), 
                os.path.join(dropboxfolder, f), 
                overwrite = True
            )

        # Do not overwrite files that are more recent in dropbox

        # Delete old local files
        for f in oldlocalfiles:
            logger.log.info("Deleting on server: {}".format(os.path.join(localfolder, f)))
            os.remove(os.path.join(localfolder, f))


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("local", help="Local folder to clean")
    parser.add_argument("dbx", help="Dropbox folder to save files to")
    parser.add_argument("--verbose", action="store_true", default = False, help="Print details about file status")
    parser.add_argument("--test", action="store_true", default = False, help="Check files without making changes")
    args = parser.parse_args()

    logger.log.info("Local folder: {}".format(args.local))
    logger.log.info("Dropbox folder: {}".format(args.dbx))

    #clean_folder(localfolder, dropboxfolder, verbose = args.verbose, test = args.test)

    # Extract the subfolder names
    # Assumption = dropbox has same folder structure
    alldirs = [x[0] for x in os.walk(args.local)]
    subfolders = [x.split(args.local)[1] for x in alldirs]

    logger.log.info("Subfolders: {}".format(subfolders))
    
    if subfolders:
        for sf in subfolders:
        
            clean_folder(
                os.path.join(args.local, sf), 
                os.path.join(args.dbx, sf), 
                verbose = args.verbose,
                test = args.test
            )

