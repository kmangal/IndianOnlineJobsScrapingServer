import dropbox
import os
import datetime
import sys

TOKEN = 'lCdHJDySKOIAAAAAAAAAAQiX2-M6qRcEqnrOUAFDRlE5_J-f5uAx9bokaHYpRUWa'

def move_to_dropbox(localpath, dropboxpath, overwrite = False):
    dbx = dropbox.Dropbox(TOKEN)
    with open(localpath, 'rb') as f:
        if overwrite:
            dbx.files_upload(f.read(), dropboxpath, mode=dropbox.files.WriteMode.overwrite)
        else:
            dbx.files_upload(f.read(), dropboxpath)

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Usage: python3 export_to_dropbox [localfile] [dropboxfile]")
        raise Exception

    localpath = sys.argv[1]
    dropboxpath = sys.argv[2]
    move_to_dropbox(localpath, dropboxpath)

