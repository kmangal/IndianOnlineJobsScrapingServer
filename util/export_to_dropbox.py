import dropbox
import os
import datetime
import sys

TOKEN = 'lCdHJDySKOIAAAAAAAAAAQiX2-M6qRcEqnrOUAFDRlE5_J-f5uAx9bokaHYpRUWa'
CHUNK_SIZE = 2 ** 20


def move_to_dropbox(localpath, dropboxpath, overwrite = False):
    dbx = dropbox.Dropbox(TOKEN)
    with open(localpath, 'rb') as f:
        if overwrite:
            dbx.files_upload(f.read(), dropboxpath, mode=dropbox.files.WriteMode.overwrite)
        else:
            dbx.files_upload(f.read(), dropboxpath)


def upload_to_dropbox(localpath, dropboxpath):
    dbx = dropbox.Dropbox(TOKEN)
    with open(localpath, 'rb') as f:
        chunk = f.read(CHUNK_SIZE)
        offset = len(chunk)

        upload_session = dbx.files_upload_session_start(chunk)

        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            dbx.files_upload_session_append_v2(
                chunk,
                dropbox.files.UploadSessionCursor(
                    upload_session.session_id,
                    offset,
                ),
            )
            offset += len(chunk)

        file_metadata = dbx.files_upload_session_finish(
            b'',
            dropbox.files.UploadSessionCursor(
                upload_session.session_id,
                offset=offset,
            ),
            dropbox.files.CommitInfo(
                dropboxpath,
                # When writing the file it won't overwrite an existing file, just add
                # another file like "filename (2).txt"
                dropbox.files.WriteMode('add'),
            ),
        )

if __name__ == '__main__':

    if len(sys.argv) != 3:
        print("Usage: python export_to_dropbox [localfile] [dropboxfile]")
        raise Exception

    localpath = sys.argv[1]
    dropboxpath = sys.argv[2]
    print('Local path', localpath)
    print('Dropbox path', dropboxpath)
    upload_to_dropbox(localpath, dropboxpath)

