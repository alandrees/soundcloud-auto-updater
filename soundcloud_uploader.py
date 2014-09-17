import soundcloud
import sys
import subprocess
import os
import wave
import time
import uuid
import math

"""
Soundcloud Auto Uploader

Process a directory and upload the music in it to a soundcloud account, reading the filename to parse metadata (for both the file and soundcloud).

Copyright (C) 2013-2014 Alan Drees

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

"""
Requirements:
soundcloud module (https://github.com/soundcloud/soundcloud-python)
a FLAC encoder (tested with reference flac encoder)

you will need to fill in the information below with information generated from: http://soundcloud.com/you/apps

CLI Arguments:

mp3 - encode the wav into mp3 and upload 

or

flac - encode the wav into flac and upload
"""


#constants

#CLIENTID PROVIDED BY SOUNDCLOUD
CLIENTID     = ""

#CLIENTSECRET PROVIDED BY SOUNDCLOUD
CLIENTSECRET = ""

#USERNAME OF THE USER TO UPLOAD TO
USERNAME     = ""

#PASSWORD OF THAT USER
PASSWORD     = ""

#DIRECTORY TO CHECK FOR NEW UPLOADS IN
DIRECTORY    = ""

#FLAC BINARY
FLACBIN      = "flac"

#MP3BINARY
MP3BIN       = "lame"

#CONSTANT SOUNDCLOUD TAGS
SCTAGS       = ['tag1', 'tag2']

#CONSTANT FILE TAGS (also used to provide information to the soundcloud upload.  Ignores title.)
#Also the fieldname should match (case & spelling) to the predefined vorbis tag fields
#otherwise it gets put in the custom metadata section
FILETAGS     = {'Artist'       : 'Artist Name',
                'Tracknumber'  : '01',
                'Album'        : 'Album Name'}

#MAKE THE UPLOADS DOWNLOADABLE OR NOT
DOWNLOADABLE = True

class SoundcloudAutoUpdater():
    

    def __init__(self, clientid, clientsecret, username, password, directory, encoder, encodedir, tags, downloadable = True):
        """
        Constructor

        @param self object reference
        @param clientid the clientid provided by SoundCloud
        @param clientsecret the client secret provided by SoundCloud
        @param username login username
        @param password login password
        @param directory the directory the PCM files are stored in

        @returns None
        """
        self._client = None
        self._file_queue = list()
        self._time_remaining = 0
        
        self._title = ''
        self._genre = ''
        self._soundcloud_tags = ''
        self._meta_tags = dict()

        for tag in tags[0]:
            self._add_sc_tag_to_list(tag)

        tag = None

        for tag, value in tags[1].iteritems():
            self._meta_tags[tag.strip()] = value.strip()


        self._directory = directory
        self._encoder = encoder
        self._encodedir = encodedir
        self._downloadable = downloadable

        self._client = soundcloud.Client(client_id     = clientid,
                                         client_secret = clientsecret,
                                         username      = username,
                                         password      = password)
        
        self._time_remaining = int(self._client.get('/me').fields()['upload_seconds_left'])

        self._file_queue = self._get_upload_list()

    def _account_has_enough_time(self):
        """
        Gets the length of time of a filename, and compares it 
        with the remaining time on the account.
        
        @param self object reference
        @param filename filename to get the length of

        @returns boolean True on if there is more time left, and False if there
        is less/equal to time remaining
        """

        if self._calculate_file_duration() < self._time_remaining:
            return True
        else:
            return False

    def _get_upload_list(self):
        """
        Gets/generates a list of wav files which need to be encoded, tagged and uploaded
        
        @param self object reference
        @param directory directory to check for, defaults to /mnt/data/sc_upload
        
        @returns list containing all the filenames which need to be uploaded
        """
        file_list = list()

        try:
            filenames = os.listdir(self._directory)
        except OSError:
                print "Unable to open directory: " + self._directory
                return list()

        for pcm_file in filenames:
            
            try:
                wf = wave.open(self._directory + "/" + pcm_file, 'r')
            except:
                pass #print pcm_file + " is not a valid PCM file."
            else:
                file_list.append(pcm_file)
            
        return file_list

    def _upload_file(self, temp_file):
        """
        Uploads a file to the specified soundcloud account
        
        @param self object reference
        @param temp_file the temporary encoded file
    
        @returns Boolean True on success or False on failure
        """

        downloadable = "false"

        if self._downloadable == True:
            downloadable = "true"

        track = self._client.post('/tracks', 
                            track = { 'title'        : self._title,
                                      'genre'        : self._genre,
                                      'tag_list'     : self._soundcloud_tags,
                                      'downloadable' : downloadable,
                                      'sharing'      : 'public',
                                      'asset_data'   : open(temp_file, 'rb')
                                      })

    def _send_upload_notice(self, body, subject, address = "loridcon@mail.lan"):
        """
        Emails a notice when an upload is made successfully, or when there is an error
        
        @param self object reference
        @param reason Explaination of the purpose of the email

        @returns None
        """
        pass

    def _encode_file(self, temp_dir = '/tmp'):
        """
        Encode a file using the selected encoder

        @param self object reference
        @param temp_dir temporary directory to store the encoded file

        @returns The temporary filename
        """

        try:
            artist = self._meta_tags['Artist']
        except KeyError:
            artist = ''
        
        filename = artist + ' - ' + self._title + '.flac'

        #print '"' + temp_dir + '/' + self._file_queue[0] + '"'

        if( self._encoder == "flac" ):

            arg_list = ['flac', 
                        '--output-name='+ temp_dir + '/' + filename]
            
            for tag, value in self._meta_tags.iteritems():
                arg_list.append('--tag='+ tag.strip() + '=' + value.strip() + '')

            #arg_list.append('-8')

            arg_list.append(self._directory + '/' + self._file_queue[0])                    


        if( self._encoder == "mp3" ):
            arg_list = ['lame', 
                        '--silent', 
                        '-output-name="'+ temp_dir + '/' + filename + '"', 
                        '-8']

            for tag, value in self._tags.iteritems():
                arg_list.append('--tag='+ tag + '=' + value + '')

            arg_list.append(self._directory + '/' + self._file_queue[0])

        subprocess.call(arg_list, shell = False)            

        try:
            open(temp_dir + "/" + filename)
        except IOError:
            print "Error: No output file created.  Exiting"
            return ""

        return temp_dir + "/" + filename
        
    def _calculate_file_duration(self):
        """
        Calculates a PCM wav file's length in seconds using the sample rate and number of frames
        
        @param None

        @return Integer representing the length (in seconds) of a PCM WAV file
        """

        try:
            wf = wave.open(self._directory + "/" + self._file_queue[0], 'r')
        except:
            print self._directory + "/" + self._file_queue[0] + " is not a valid PCM file."
        else:
            return int(math.ceil( float( wf.getnframes() ) / float( wf.getframerate() ) ))

    def _update_account_time(self):
        """
        Retreives the account time remaining from soundcloud.  Used between 
        iterations through the queue.

        @param self object reference

        @returns The time remaining (in seconds) remaining on the account
        """
        self._time_remaining = self._time_remaining = int(self._client.get('/me').fields()['upload_seconds_left'])
        return self._time_remaining

    def _parse_filename_data(self):
        """
        Parses the tagging information out of the filename

        @param self object reference

        @returns dictionary of tags to be added to the encoded file
        """

        tagsplit = list()

        filename = os.path.splitext(self._file_queue[0])[0]

        data = filename.split("~-")

        self._title = data[0]

        self._genre = data[1]
        
        tagsplit = data[2].split(',')
        
        for tag in tagsplit:
            self._add_sc_tag_to_list(tag)

        metatag_split = data[3].split(',')

        

        for tag in metatag_split:
            metatag = tag.split(':')
            self._meta_tags[metatag[0].strip()] = metatag[1].strip()

        self._meta_tags['Title'] = self._title.strip()
        self._meta_tags['Genre'] = self._genre.strip()

    def _add_sc_tag_to_list(self, tag):
        """
        Adds a tag, properly quoting it if it has spaces in it

        @param self object refence
        @param tag tag to add to the tag list

        @returns None
        """

        if ' ' in tag.strip():
            tag = '"' + tag + '"'
        

        if self._soundcloud_tags.strip() == '':
            self._soundcloud_tags = self._soundcloud_tags + tag.strip()
        else:
            self._soundcloud_tags = self._soundcloud_tags + ' ' + tag.strip()


    def process_file(self):
        """
        Processes the file queue starting from the top
        
        @param self object instance
        
        @returns None
        """

        if(len(self._file_queue) > 0):
            
            self._update_account_time()
            tags = self._parse_filename_data()
            temp_file = self._encode_file()
                    
            if self._account_has_enough_time():
                self._upload_file(temp_file)
                self._send_upload_notice("File upload completed successfully for " + self._file_queue[0] + " on " + "TODAY" + time.strftime("%D-%M-%y"),
                                         "SoundCloud Upload of " + self._file_queue[0] + " completed.")

                if not temp_file == '':
                    os.remove(self._directory + '/' + self._file_queue[0])
            else:
                    self._send_upload_notice("Soundcloud Uploader Failed", "File upload of " + self._file_queue[0] + " failed on " + "TODAY" + time.strftime("%D-%M-%y") + "\n" +
                                             "Reason: Insufficent soundcloud time remaining: " + str(self.get_remaining_time()),
                                             "Soundcloud upload of " + self._file_queue[0] + " failed.")

            if not temp_file == '':
                os.remove(temp_file)

            self._file_queue.pop(0)

    def has_uploadable_files(self):
        """
        Tests if the file processing queue is empty or not
        
        @param self object reference

        @returns Boolean True if the queue has items in it, otherwise False
        """

        if ( len(self._file_queue) > 0 ):
            return True
        else:
            return False

if __name__ == "__main__":
    
    encoder = ''
    tags = list()

    if ( len(sys.argv) > 1 ):
        
        try:
            sys.argv.index("-mp3")
        except ValueError:
            pass
        else:
            try:
                sys.argv.index("-flac")
            except ValueError:
                encoder = MP3BIN
            else:
                print "Cannot specify both -mp3 and -flac options.  Exiting."
                exit()

        try:
            sys.argv.index("-flac")
        except ValueError:
            pass
        else:
            try:
                sys.argv.index("-mp3")
            except ValueError:
                encoder = FLACBIN
            else:
                print "Cannot specify both -mp3 and -flac options.  Exiting."
                exit()

        try:
           tags_index = sys.argv.index("-tags")
        except ValueError:
            pass
        else:
            try:
                tags = sys.argv[tags_index + 1].split(",")
            except IndexError:
                print "Tags argument given, but no tags supplied"
                tags = list()

    if encoder == '':
        print "No encoder specified.  Use either -mp3 or -flac to specify the encoder.  Now exiting."
        exit()

    if encoder == MP3BIN:
        print "MP3 encoding not yet supported.  Please use the -flac option instead"
        exit()
        
        
    auto_updater = SoundcloudAutoUpdater(CLIENTID, 
                                         CLIENTSECRET, 
                                         USERNAME, 
                                         PASSWORD, 
                                         DIRECTORY,
                                         encoder,
                                         '/tmp',
                                         (SCTAGS, FILETAGS),
                                         DOWNLOADABLE)
    
    if(auto_updater.has_uploadable_files()):
        while(auto_updater.has_uploadable_files()):
            auto_updater.process_file()
        
