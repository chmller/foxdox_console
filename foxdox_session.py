class FoxdoxSession(object):
    def __init__(self):
        self.user_sid = ''
        self.token = ''
        self.current_folder = None
        self.root_folder = None
        self.folders = []
        self.documents = []

    def reset(self):
        self.user_sid = ''
        self.token = ''
        self.current_folder = None
        self.root_folder = None
        self.folders = []
        self.documents = []