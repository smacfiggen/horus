from __future__ import print_function
import httplib2
import io
import os
import sys
import time
import dateutil.parser

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaIoBaseDownload

import pprint

#Change these to the day of the osiris infestation
YEAR_OF_INFECTION=2017
MONTH_OF_INFECTION=01
DAY_OF_INFECTION=01

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/drive'
#YOU NEED TO SET UP AN APPLICATION ON GOOGLE AND GENERATE A KEY AND CREATE THIS FILE
CLIENT_SECRET_FILE = 'revert_osiris.json'
APPLICATION_NAME = 'Revert Osiris'

#copy pasta form gdrive API help examples
def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'drive-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def main():
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)
    pp = pprint.PrettyPrinter()

    #grab first batch of possible infected files
    results = service.files().list(pageSize=1,
                                   fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])
    next_page = results.get('nextPageToken', None)

    bad_files = []
    done = False
    next_page = None
    while True:
        results = service.files().list(pageToken=next_page, pageSize=100,
                fields="nextPageToken, files(id, name)").execute()
        items = results.get('files', [])
        if not items:
            print('No files found.')
            break
        else:
            for item in items:
                #Only act on files with osiris in the name. 
                if 'osiris' in item['name']:
                    bad_files.append(item)
        next_page = results.get('nextPageToken', None)

    print("Found {} bad files".format(len(bad_files)))

    #Download a backup of all files just in case
    for bad_item in bad_files:
        revisions = service.revisions().list(fileId=bad_item['id'], fields='*').execute()
        assert(len(revisions['revisions']) >= 2)
        dt = dateutil.parser.parse(revisions['revisions'][-1]['modifiedTime'])
        if dt.day == DAY_OF_INFECTION and dt.month = MONTH_OF_INFECTION and dt.year == YEAR_OF_INFECTION:
            print("Last revision dates from virus day")
        else:
            print("Skipping {}, datastamp on file isn't from virus day")
            continue
        dt = dateutil.parser.parse(revisions['revisions'][-2]['modifiedTime'])
        print("Date of second to last revision is: {}".format(dt))
    
        request = service.revisions().get_media(fileId=bad_item['id'],
                                               revisionId=revisions['revisions'][-2]['id'])
        #Filenames are not unique in gdrive so append with file ID as well
        new_filename = os.path.join('backup',
                                   revisions['revisions'][-2]['originalFilename'] + '_' + bad_item['id'])
        #If we are re-running script see if we already downloaded this file
        if os.path.isfile(new_filename):
            print("File {} already backed up, skipping".format(new_filename))
            continue

        fh = io.FileIO(new_filename, 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download {}".format(int(status.progress() * 100)) )

    count = 0
    for bad_item in bad_files:
        count = count + 1
        #Do in batches just to be kind of safe. 
        if count > 50:
            break
        file_id = bad_item['id'] 
        revisions = service.revisions().list(fileId=file_id, fields='*').execute()
        if len(revisions['revisions']) < 2:
            print("File has only 1 revision, skipping: {}".format(bad_item))
            continue
        file_meta = service.files().get(fileId=file_id, fields='*').execute()
        dt_last = dateutil.parser.parse(revisions['revisions'][-1]['modifiedTime'])
        dt_2nd_last = dateutil.parser.parse(revisions['revisions'][-2]['modifiedTime'])
        if dt_last.day == DAY_OF_INFECTION and dt_last.month == MONTH_OF_INFECTION and dt_last.year == YEAR_OF_INFECTION:
            print("Last revision dates from virus day")
        else:
            print("Skipping {}, datestamp on file isn't from virus day")
            continue

        orig_file_name = file_meta['originalFilename']
        target_rev_name = revisions['revisions'][-2]['originalFilename']
        #If the 2nd to last revision is also osiris, we can't simply revert
        if 'osiris' in target_rev_name:
            print("2nd to last rev filename has osiris in the name, skipping: ({})".format(target_rev_name))
            #print out some debug info so we can figure out what we have multipe revisions with osiris
            pp.pprint(file_meta)
            print('  ')
            pp.pprint(revisions)
            continue

        print("{}: {} revisions found".format(target_rev_name, len(revisions['revisions'])) )

        #THESE ARE THE REALLY DANGEROUS STEPS, ONLY UNCOMMMENT IF YOU KNOW WHAT YOU ARE DOING!!!
        rev_id_to_delete = revisions['revisions'][-1]['id']
        print("service.revisions().delete(fileId={}, revisionId={}).execute()".format(file_id, rev_id_to_delete))
        #del_rev = service.revisions().delete(fileId=file_id, revisionId=rev_id_to_delete).execute()

        update_body = { 'name': target_rev_name }
        print("service.files().update(fileId={}, body={}).execute()".format(file_id, update_body))
        #update_name = service.files().update(fileId=file_id, body=update_body).execute()

if __name__ == '__main__':
    main()
