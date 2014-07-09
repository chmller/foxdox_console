import utils
import urllib
import urlparse
import urllib2
import io
import httplib
import mimetypes
import json

from foxdox_session import FoxdoxSession


class FoxdoxClient:
    def __init__(self):
        self._developerId = 'zp1xwCn976mX4kd5j2VM'
        self._applicationId = 'bPEcEdEYqg68ryWBcct2'
        self._appVersion = '0.1'
        self._language = 'en'
        self._default_result = {'Status': 0, 'Error': 0, 'StatusMsg': ''}
        self.session = FoxdoxSession()

    def auth_requesttoken(self, username, password):
        url = 'https://api.foxdox.de/auth/requesttoken'
        values = {'username': username, 'password': password}

        try:
            result = self._post_request(url, values, None)

            self.session.user_sid = result['SID']
            self.session.token = result['Token']
            self.session.root_folder = self.folder_rootfolder()
            self.session.current_folder = self.folder_details(
                folder_id=utils.get_safe_value_from_dict(self.session.root_folder, 'Id', default=''))
            self.session.folders = self.folder_listfolders()
            self.session.documents = self.folder_listdocuments()

        except Exception:
            result = self._default_result

        return result

    def auth_deletetoken(self):
        url = 'https://api.foxdox.de/auth/deletetoken'
        values = {}

        try:
            result = self._post_request(url, values, self.session.token)
            self.session.reset()
        except:
            result = self._default_result

        return result

    def folder_rootfolder(self):
        url = 'https://api.foxdox.de/folder/rootfolder'
        values = {}

        try:
            result = self._post_request(url, values, self.session.token)
        except Exception as ex:
            result = self._default_result

        return result

    def folder_foldertree(self):
        url = 'https://api.foxdox.de/folder/foldertree'
        values = {'rootfoldername': 'Root', 'flat': 'true'}

        try:
            result = self._post_request(url, values, self.session.token)
        except:
            result = self._default_result

        return result

    def folder_listfolders(self):
        url = 'https://api.foxdox.de/folder/listfolders'
        values = {'folderid': str(utils.get_safe_value_from_dict(self.session.current_folder, 'Id'))}

        try:
            result = self._post_request(url, values, self.session.token)
        except:
            result = self._default_result

        return result

    def folder_listdocuments(self):
        url = 'https://api.foxdox.de/folder/listdocuments'
        values = {'folderid': utils.get_safe_value_from_dict(self.session.current_folder, 'Id')}

        try:
            result = self._post_request(url, values, self.session.token)
        except Exception as ex:
            result = self._default_result

        return result

    def folder_details(self, folder_id=None):
        url = 'https://api.foxdox.de/folder/details'
        fid = utils.get_safe_value_from_dict(self.session.current_folder, 'Id') if folder_id is None else folder_id
        values = {'folderid': fid}

        try:
            result = self._post_request(url, values, self.session.token)
        except Exception as ex:
            result = self._default_result

        return result

    def changefolder(self, folder_name):
        if folder_name == '..':
            if self.session.current_folder['ParentFolderId'] == str(utils.EMPTY_UUID):
                return True
            else:
                self.session.current_folder = self.folder_details(folder_id=self.session.current_folder['ParentFolderId'])
                self.session.folders = self.folder_listfolders()
                self.session.documents = self.folder_listdocuments()
                return True
        elif folder_name == '/':
            self.session.current_folder = self.folder_details(folder_id=self.session.root_folder['Id'])
            self.session.folders = self.folder_listfolders()
            self.session.documents = self.folder_listdocuments()
            return True
        else:
            folders = self.folder_listfolders()
            for folder in folders['Items']:
                if folder['Name'] == folder_name:
                    self.session.current_folder = self.folder_details(folder_id=folder['Id'])
                    self.session.folders = self.folder_listfolders()
                    self.session.documents = self.folder_listdocuments()
                    return True

            return False

    def _post_request(self, url, values, token):
        headers = {
            'X-DEVID': self._developerId,
            'X-APPID': self._applicationId,
            'X-APPVER': self._appVersion,
            'X-LANG': self._language,
            'X-TOKEN': token
        }

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data.encode('utf-8'), headers)
        res = urllib2.urlopen(req)
        result = json.loads(res.read().decode('utf-8'))

        return result

    def _get_binary(self, url, values, token):
        headers = {
            'X-DEVID': self._developerId,
            'X-APPID': self._applicationId,
            'X-APPVER': self._appVersion,
            'X-LANG': self._language,
            'X-TOKEN': token
        }

        data = urllib.urlencode(values)
        req = urllib2.Request(url + '?' + data, data=None, headers=headers)
        res = urllib2.urlopen(req)
        result = res.read()

        return result

    def _get_secure_binary(self, url, values, key, token):
        headers = {
            'X-DEVID': self._developerId,
            'X-APPID': self._applicationId,
            'X-APPVER': self._appVersion,
            'X-LANG': self._language,
            'X-KEYPASS': key,
            'X-TOKEN': token
        }

        data = urllib.urlencode(values)
        req = urllib2.Request(url + '?' + data, data=None, headers=headers)
        res = urllib2.urlopen(req)
        result = res.read()

        return result

    def _post_binary(self, url, file_name, values, token):
        headers = {
            'X-DEVID': self._developerId,
            'X-APPID': self._applicationId,
            'X-APPVER': self._appVersion,
            'X-LANG': self._language,
            'X-TOKEN': token
        }

        url_parts = urlparse.urlparse(url)
        host = url_parts.netloc
        selector = url_parts.path
        result = FoxdoxClient.post_multipart(host, selector, values.items(),
                                             [('file', file_name, open(file_name, 'rb'))], headers, 'FOXDOXpy1337')
        return result

    @staticmethod
    def post_multipart(host, selector, fields, files, headers, boundary):
        headers['Content-type'] = 'multipart/form-data; boundary=' + boundary
        body = FoxdoxClient.encode_multipart_formdata(fields, files, boundary)
        client = httplib.HTTPSConnection(host)
        client.request('POST', selector, body, headers)
        res = client.getresponse()
        return json.loads(res.read().decode('utf-8'))

    @staticmethod
    def encode_multipart_formdata(fields, files, boundary):
        body = io.BytesIO()
        mime_boundary = boundary

        for (key, value) in fields:
            title = 'Content-Disposition: form-data; name="%s"\r\n' % key
            body.write(str('--' + mime_boundary + '\r\n').encode('utf-8'))
            body.write(str(title).encode('utf-8'))
            body.write(b'\r\n')
            body.write(str(value).encode('utf-8') + b'\r\n')

        for (key, filename, value) in files:
            title = 'Content-Disposition: form-data; name="%s"; filename="%s"\r\n' % (key, filename)
            ctype = 'Content-Type: %s\r\n' % FoxdoxClient.get_content_type(filename)
            body.write(str('--' + mime_boundary + '\r\n').encode('utf-8'))
            body.write(str(title).encode('utf-8'))
            body.write(str(ctype).encode('utf-8'))
            body.write(b'\r\n')
            body.write(value.read())
            body.write(b'\r\n')

            value.close()

        body.write(str('--' + mime_boundary + '--\r\n').encode('utf-8'))
        body.write(b'\r\n')

        return body.getvalue()

    @staticmethod
    def get_content_type(filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
