import os
import shlex

from cmd import Cmd
from foxdox_client import FoxdoxClient


class FoxdoxCli(Cmd):
    def preloop(self):
        print 'Starting FOXDOX interactive shell...'
        self.client = FoxdoxClient()

    def postloop(self):
        print 'Bye!'

    def emptyline(self):
        pass

    def do_shell(self, line):
        print "running shell command:", line
        output = os.popen(line).read()
        print output

    def help_shell(self):
        print 'Executes a shell command'

    def do_exit(self, line):
        print 'exiting the interactive shell...'

        if self.client.session.token:
            self.client.auth_deletetoken()

        return True

    def help_exit(self):
        #TODO: helptext
        pass

    def do_session(self, line):
        print 'SID', self.client.session.user_sid
        print 'Token', self.client.session.token
        print 'Current folder', '%s' % self.client.session.current_folder['folder_name']

    def help_session(self):
        #TODO: helptext
        pass

    def do_requesttoken(self, line):
        s = shlex.split(line)
        if len(s) != 2:
            print 'Invalid argument count'
            return False

        response = self.client.auth_requesttoken(s[0], s[1])

        if response['Status'] == 200:
            print 'OK'
        else:
            print response['Error'], response['StatusMsg']

    def help_requesttoken(self):
        print 'Obtain a token for accessing the FOXDOX-Client-API'
        print 'Usage: requesttoken <username> <password>'

    def do_deletetoken(self, line):
        response = self.client.auth_deletetoken()
        if response['Status'] == 200:
            print 'OK'
        else:
            print response['Error'], response['StatusMsg']

    def help_deletetoken(self):
        #TODO: helptext
        pass

    def do_listfolders(self, line):
        response = self.client.folder_listfolders()
        if response['Status'] == 200:
            folders = []
            for folder in response['Items']:
                folders.append(folder['Name'].encode('utf-8'))
            self.columnize(folders)
        else:
            print response['Error'], response['StatusMsg']

    def help_listfolders(self):
        #TODO: helptext
        pass

    def do_listdocuments(self, line):
        response = self.client.folder_listdocuments()
        if response['Status'] == 200:
            documents = []
            for doc in response['Items']:
                documents.append(doc['Name'].encode('utf-8'))
            self.columnize(documents)
        else:
            print response['Error'], response['StatusMsg']

    def help_listdocuments(self):
        #TODO: helptext
        pass

    def do_tree(self, line):
        response = self.client.folder_foldertree()

        if response['Status'] == 200:
            for folder in response['Items']:
                print folder['Path']
        else:
            print response['Error'], response['StatusMsg']
            self.session.reset()

    def help_tree(self):
        #TODO: helptext
        pass

    def do_cd(self, line):
        if self.client.changefolder(line):
            print 'OK'
        else:
            print 'folder not found'

    def help_cd(self):
        #TODO: helptext
        pass

    def do_download(self, line):
        pass

    def help_download(self):
        #TODO: helptext
        pass