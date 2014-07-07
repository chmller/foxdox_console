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
        self._developerId = 'LI8JRbcZxXWFJ3aqdnPN'
        self._applicationId = 't8qIrYMtpJcZ4jYsY3Ul'
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

            try:
                result2 = self._post_request('https://api.foxdox.de/folder/rootfolder', {}, self.session.token)
                if result2['Status'] == 200:
                    self.session.current_folder = dict(folder_id=result2['Id'], folder_name=result2['Name'])
                else:
                    self.session.current_folder = dict(folder_id='<UUID>', folder_name='Root')
            except Exception:
                self.session.current_folder = dict(folder_id='<UUID>', folder_name='Root')

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
        values = {'folderid': str(self.session.current_folder['folder_id'])}

        try:
            result = self._post_request(url, values, self.session.token)
        except:
            result = self._default_result

        return result

    def folder_listdocuments(self):
        url = 'https://api.foxdox.de/folder/listdocuments'
        values = {'folderid': str(self.session.current_folder['folder_id'])}

        try:
            result = self._post_request(url, values, self.session.token)
        except Exception as ex:
            result = self._default_result

        return result

    def changefolder(self, folder_name):
        folders = self.folder_listfolders()
        for folder in folders['Items']:
            if folder['Name'] == folder_name:
                self.session.current_folder['folder_id'] = folder['Id']
                self.session.current_folder['folder_name'] = folder['Name']
                return True

        return False

    def _post_request(self, url, values, token):
        headers = {'X-DEVID': self._developerId,
                   'X-APPID': self._applicationId,
                   'X-APPVER': self._appVersion,
                   'X-LANG': self._language,
                   'X-TOKEN': token}

        data = urllib.urlencode(values)
        req = urllib2.Request(url, data.encode('utf-8'), headers)
        res = urllib2.urlopen(req)
        result = json.loads(res.read().decode('utf-8'))

        return result

    def _get_binary(self, url, values, token):
        headers = {'X-DEVID': self._developerId,
                   'X-APPID': self._applicationId,
                   'X-APPVER': self._appVersion,
                   'X-LANG': self._language,
                   'X-TOKEN': token}

        data = urllib.urlencode(values)
        req = urllib2.Request(url+'?'+data, data=None, headers=headers)
        res = urllib2.urlopen(req)
        result = res.read()

        return result

    def _get_secure_binary(self, url, values, key, token):
        headers = {'X-DEVID': self._developerId,
                   'X-APPID': self._applicationId,
                   'X-APPVER': self._appVersion,
                   'X-LANG': self._language,
                   'X-KEYPASS': key,
                   'X-TOKEN': token}

        data = urllib.urlencode(values)
        req = urllib2.Request(url+'?'+data, data=None, headers=headers)
        res = urllib2.urlopen(req)
        result = res.read()

        return result

    def _post_binary(self, url, file_name, values, token):
        headers = {'X-DEVID': self._developerId,
                   'X-APPID': self._applicationId,
                   'X-APPVER': self._appVersion,
                   'X-LANG': self._language,
                   'X-TOKEN': token}

        url_parts = urlparse.urlparse(url)
        host = url_parts.netloc
        selector = url_parts.path
        result = self._post_multipart(host,
                                      selector,
                                      values.items(),
                                      [('file', file_name, open(file_name, 'rb'))],
                                      headers,
                                      'FOXDOXpy1337')
        return result

    def _post_multipart(self, host, selector, fields, files, headers, boundary):
        headers['Content-type'] = 'multipart/form-data; boundary=' + boundary
        body = self._encode_multipart_formdata(fields, files, boundary)
        client = httplib.HTTPSConnection(host)
        client.request('POST', selector, body, headers)
        res = client.getresponse()
        return json.loads(res.read().decode('utf-8'))

    def _encode_multipart_formdata(self, fields, files, boundary):
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
            ctype = 'Content-Type: %s\r\n' % self._get_content_type(filename)
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

    def _get_content_type(self, filename):
        return mimetypes.guess_type(filename)[0] or 'application/octet-stream'
