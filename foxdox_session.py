import uuid


class FoxdoxSession(object):
    EMPTY_UUID = uuid.UUID('{00000000-0000-0000-0000-000000000000}')

    def __init__(self):
        self.user_sid = ''
        self.token = ''
        self.current_folder = dict(folder_id=FoxdoxSession.EMPTY_UUID, folder_name='')

    def reset(self):
        self.user_sid = ''
        self.token = ''
        self.current_folder = dict(folder_id=FoxdoxSession.EMPTY_UUID, folder_name='')