import os
import shlex
import utils

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
        print 'Current folder', '%s' % utils.get_safe_value_from_dict(
            self.client.session.current_folder, 'Name', default='')

    def help_session(self):
        #TODO: helptext
        pass

    def do_clear(self, line):
        import platform

        if platform.system() == 'Windows':
            os.system('cls')
        else:
            os.system('clear')

    def help_clear(self):
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

    def do_dir(self, line):
        for folder in utils.get_safe_value_from_dict(self.client.session.folders, 'Items', default=[]):
            print 'DIR'.ljust(3), folder['Name'].ljust(45), folder['Created'].rjust(29)

        for doc in utils.get_safe_value_from_dict(self.client.session.documents, 'Items', default=[]):
            print 'DOC'.ljust(3), doc['Name'].ljust(45), doc['Created'].rjust(29)

    def help_dir(self):
        #TODO: helptext
        pass

    def do_chdir(self, line):
        if self.client.changefolder(line):
            self.prompt = 'foxdox/%s> ' % utils.get_safe_value_from_dict(self.client.session.current_folder, 'Path',
                                                                         default='')
        else:
            print 'folder not found'

    def complete_chdir(self, text, line, begidx, endidx):
        print "debug", text
        folders = []
        for folder in utils.get_safe_value_from_dict(self.client.session.folders, 'Items', default=[]):
            if folder['Name'].startswith(text):
                folders.append(folder['Name'])

        return folders

    def help_chdir(self):
        #TODO: helptext
        pass

    def do_download(self, line):
        pass

    def help_download(self):
        #TODO: helptext
        pass