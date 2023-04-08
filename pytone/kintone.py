import json
import sys
import requests

class Kintone:

    def __init__(self,api_token,domain,app):
        self.api_token = api_token
        self.rootURL   = 'https://{}.cybozu.com/k/v1/'.format(domain)
        self.app       = app
        self.headers   = {
            "X-Cybozu-API-Token": self.api_token,
            'Content-Type': 'application/json'
        }
        self.property  = self.get_property()

    def requestKintone(self, method, url, json):
        if method == 'GET':
            try:
                response = requests.get(url, json=json, headers=self.headers)
                #ステータスコードチェック
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException:
                raise Exception(response.json())

        if method == 'POST':
            try:
                response = requests.post(url, json=json, headers=self.headers)
                #ステータスコードチェック
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException:
                raise Exception(response.json())

        if method == 'PUT':
            try:
                response = requests.put(url, json=json, headers=self.headers)
                #ステータスコードチェック
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException:
                raise Exception(response.json())

        if method == 'DELETE':
            try:
                response = requests.delete(url, json=json, headers=self.headers)
                #ステータスコードチェック
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException:
                raise Exception(response.json())


    def get_property(self):
        params = {
            'app': self.app,
            'lang': 'default'
        }
        url = self.rootURL + 'app/form/fields.json'

        response   = self.requestKintone(method='GET', url=url, json=params)
        properties = response['properties']
        return properties

    def selectAll(self,where=None, fields=None):
        """
        selectAll is function to get records from Kintone.\n
        Get all fields if "field" is not specified.\n
        If you do not specify "where", get all records.\n
        Always get "id" and "revision".
        """
        params = {
            'app'       : self.app,
            'query'     : '',
            'totalCount': True,
        }
        if fields is not None:
            params['fields'] = list(set(fields + ['$id', '$revision']))

        url       = self.rootURL + 'records.json'

        lastRecID = '0'
        records   = []

        while True:
            if where is None:
                params['query'] = '($id > ' + lastRecID + ' ) order by $id asc limit 500'
            else:
                params['query'] = '($id > ' + lastRecID + ' ) and (' + where + ') order by $id asc limit 500'

            response   = self.requestKintone(method='GET', url=url, json=params)
            totalCount = int(response['totalCount'])

            if totalCount == 0:
                break
            #レコードIDの最大値を取得
            lastRecID = response['records'][-1]['$id']['value']
            records.extend(response['records'])

            if totalCount <= 500:
                break

        result = []
        for record in records:
            tmp_record = {}
            for field_code, value in record.items():
                field_type  = value['type' ]
                field_value = value['value']

                if field_type == 'NUMBER' and field_value is not None and field_value != "":
                    #intかfloatにキャスト
                    try:
                        field_value = int(field_value)
                    except ValueError:
                        field_value = float(field_value)

                if field_type == 'SUBTABLE':
                    subtable        = []
                    for sub_rec in field_value:
                        subtable_record = {}
                        subtable_record['id'] = sub_rec['id']
                        for sub_field_code, sub_value in sub_rec['value'].items():
                            if sub_value['type'] == 'NUMBER' and field_value is not None:
                                #intかfloatにキャスト
                                try:
                                    sub_value['value'] = int(sub_value['value'])
                                except ValueError:
                                    sub_value['value'] = float(sub_value['value'])

                            subtable_record[sub_field_code] = sub_value['value']
                        subtable.append(subtable_record)
                    field_value = subtable

                tmp_record[field_code] = field_value
            result.append(tmp_record)

        return result

    def select(self,where=None, order=None , limit=None, fields=None):
        """
        select is function to get records from Kintone.\n
        Get all fields if "field" is not specified.\n
        If you do not specify "where", get all records.\n
        Always get "id" and "revision".
        """
        params = {
            'app'       : self.app,
            'query'     : '($id > 0)',
            'totalCount': True,
        }
        if fields is not None:
            params['fields'] = list(set(fields + ['$id', '$revision']))

        url       = self.rootURL + 'records.json'

        if where is not None:
            params['query'] += ' and (' + where + ')'

        if order is not None:
            params['query'] += ' ' + order

        if limit is not None:
            params['query'] += ' limit ' + str(limit)

        response = self.requestKintone(method='GET', url=url, json=params)
        records  = response['records']

        result = []
        for record in records:
            tmp_record = {}
            for field_code, value in record.items():
                field_type  = value['type' ]
                field_value = value['value']

                if field_type == 'NUMBER' and field_value is not None and field_value != "":
                    #intかfloatにキャスト
                    try:
                        field_value = int(field_value)
                    except ValueError:
                        field_value = float(field_value)

                if field_type == 'SUBTABLE':
                    subtable        = []
                    for sub_rec in field_value:
                        subtable_record = {}
                        subtable_record['id'] = sub_rec['id']
                        for sub_field_code, sub_value in sub_rec['value'].items():
                            if sub_value['type'] == 'NUMBER' and field_value is not None:
                                #intかfloatにキャスト
                                try:
                                    sub_value['value'] = int(sub_value['value'])
                                except ValueError:
                                    sub_value['value'] = float(sub_value['value'])

                            subtable_record[sub_field_code] = sub_value['value']
                        subtable.append(subtable_record)
                    field_value = subtable

                tmp_record[field_code] = field_value
            result.append(tmp_record)

        return result

    def selectRec(self,recordID):
        """
        selectRec is function to get 1 record of Kintone.\n
        recordID = Specify the record ID.
        """
        params = {
            'app': self.app,
            'id' : recordID
        }
        url = self.rootURL + 'record.json'

        record = self.requestKintone(method='GET', url=url, json=params)
        result = {}

        for field_code, value in record['record'].items():
            field_type  = value['type' ]
            field_value = value['value']

            if field_type == 'NUMBER' and field_value is not None and field_value != "":
                #intかfloatにキャスト
                try:
                    field_value = int(field_value)
                except ValueError:
                    field_value = float(field_value)

            if field_type == 'SUBTABLE':
                subtable        = []
                for sub_rec in field_value:
                    subtable_record = {}
                    subtable_record['id'] = sub_rec['id']
                    for sub_field_code, sub_value in sub_rec['value'].items():
                        if sub_value['type'] == 'NUMBER' and field_value is not None:
                            #intかfloatにキャスト
                            try:
                                sub_value['value'] = int(sub_value['value'])
                            except ValueError:
                                sub_value['value'] = float(sub_value['value'])

                        subtable_record[sub_field_code] = sub_value['value']
                    subtable.append(subtable_record)
                field_value = subtable

            result[field_code] = field_value

        return result

    def insert(self,records:list):
        """
        insert is Function for inserting records in kintone.\n
        records = Specify the record information (field code and field value) in the list.\n
        records = [
            {
                'field_code': 'value'
            }
        ]
        """
        if type(records) != list:
            raise Exception('Argument is not a list')
        params = {
            'app': self.app,
            "records": [

            ]
        }
        tmp_param = {}
        url       = self.rootURL + 'records.json'
        parameter = self.property
        resp      = []

        for record in records:
            #100件づつKintoneに登録する
            if len(params['records']) == 100:
                resp = self.requestKintone(method='POST', url=url, json=params)
                params['records'] = []
            for key, value in record.items():
                if key not in parameter:
                    continue
                if parameter[key]['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                    codes = []
                    for val in value:
                        codes.append({'code':val})
                    tmp_param[key] = {
                        'value': codes
                    }
                    continue
                elif parameter[key]['type'] == 'FILE':
                    fileKeys = []
                    for val in value:
                        fileKeys.append({'fileKey': val})
                    tmp_param[key] = {
                        'value': fileKeys
                    }
                    continue
                elif parameter[key]['type'] == 'SUBTABLE':
                    tmp_param[key] = {
                        'value': []
                    }
                    for sub_rec in value:
                        sub_dict = {}
                        for sub_key, sub_value in sub_rec.items():
                            if parameter[key]['fields'][sub_key]['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                                codes = []
                                for val in sub_value:
                                    codes.append({'code': val})
                                sub_dict[sub_key] = {
                                    'value':codes
                                }
                            elif parameter[key]['fields'][sub_key]['type'] == 'FILE':
                                fileKeys = []
                                for val in sub_value:
                                    fileKeys.append({'fileKey': val})
                                sub_dict[sub_key] = {
                                    'value': fileKeys
                                }
                            else:
                                sub_dict[sub_key] = {
                                    'value':sub_value
                                }
                        tmp_param[key]['value'].append({
                                'value':sub_dict
                        })
                    continue
                else:
                    tmp_param[key] = {
                        'value': value
                    }
                    continue
            params['records'].append(tmp_param)
            tmp_param = {}
        #最後に残りを追加する
        if params['records']:
            resp = self.requestKintone(method='POST', url=url, json=params)

        return resp
    def insertRec(self,record:dict):
        """
        insertRec is Function for inserting 1 record in kintone.\n
        record = Specify the record information (field code and field value) in the dict.\n
        record = {
            'field_code': 'value'
        }
        """
        #引数の型チェック
        if type(record) != dict:
            raise Exception('Argument is not a dict')
        params = {
            'app': self.app,
            "record": {

            }
        }
        url = self.rootURL + 'record.json'
        parameter = self.property

        for key, value in record.items():
            if key not in parameter:
                continue
            if parameter[key]['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                codes = []
                for val in value:
                    codes.append({'code': val})
                params['record'][key] = {
                    'value': codes
                }
                continue
            elif parameter[key]['type'] == 'FILE':
                fileKeys = []
                for val in value:
                    fileKeys.append({'fileKey': val})
                params['record'][key] = {
                    'value': fileKeys
                }
                continue
            elif parameter[key]['type'] == 'SUBTABLE':
                params['record'][key] = {
                    'value': []
                }
                for sub_rec in value:
                    sub_dict = {}
                    for sub_key, sub_value in sub_rec.items():
                        if parameter[key]['fields'][sub_key]['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                            codes = []
                            for val in sub_value:
                                codes.append({'code': val})
                            sub_dict[sub_key] = {
                                'value': codes
                            }
                        elif parameter[key]['fields'][sub_key]['type'] == 'FILE':
                            fileKeys = []
                            for val in sub_value:
                                fileKeys.append({'fileKey': val})
                            sub_dict[sub_key] = {
                                'value': fileKeys
                            }
                        else:
                            sub_dict[sub_key] = {
                                'value': sub_value
                            }
                    params['record'][key]['value'].append({
                            'value': sub_dict
                        })
                continue
            else:
                params['record'][key] = {
                    'value': value
                }
                continue
        resp = self.requestKintone(method='POST', url=url, json=params)

        return resp

    def update(self, records:list):
        """
        update is function for updating records in kintone.\n
        records = data to update in kintone.\n
        records = [
            {
                '$id':'1'
                   or
                'updateKey': {
                    'field':'No duplication field code',
                    'value':'value'
                }
                'field_code': 'value'
            }
        ]
        """
        if type(records) != list:
            raise Exception('Argument is not a list')
        params = {
            'app': self.app,
            "records": [

            ]
        }
        tmp_param = {}
        url       = self.rootURL + 'records.json'
        parameter = self.property
        resp      = []

        for record in records:
            #100件づつKintoneに登録する
            if len(params['records']) == 100:
                resp = self.requestKintone(method='PUT', url=url, json=params)
                params['records'] = []
            tmp_param['record'] = {}
            for key, value in record.items():
                if key == '$revision':
                    continue
                #レコードIDを取得する
                if key in ('id','$id'):
                    tmp_param['id'] = value
                    continue
                elif key == 'updateKey':
                    tmp_param['updateKey'] = {
                        'field':value['field'],
                        'value':value['value']
                    }
                    continue
                elif parameter[key]['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                    codes = []
                    for val in value:
                        codes.append({'code': val})
                    tmp_param['record'][key] = {
                        'value': codes
                    }
                    continue
                elif parameter[key]['type'] == 'FILE':
                    fileKeys = []
                    for val in value:
                        fileKeys.append({'fileKey': val})
                    tmp_param['record'][key] = {
                        'value': fileKeys
                    }
                    continue
                elif parameter[key]['type'] == 'SUBTABLE':
                    tmp_param['record'][key] = {
                        'value': []
                    }
                    for sub_rec in value:
                        sub_dict = {}
                        sub_id   = ''
                        for sub_key, sub_value in sub_rec.items():
                            if sub_key == 'id':
                                sub_id = sub_value
                                continue
                            elif parameter[key]['fields'][sub_key]['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                                codes = []
                                for val in sub_value:
                                    codes.append({'code': val})
                                sub_dict[sub_key] = {
                                    'value': codes
                                }
                            elif parameter[key]['fields'][sub_key]['type'] == 'FILE':
                                fileKeys = []
                                for val in sub_value:
                                    fileKeys.append({'fileKey': val})
                                sub_dict[sub_key] = {
                                    'value': fileKeys
                                }
                            else:
                                sub_dict[sub_key] = {
                                    'value': sub_value
                                }
                        if sub_id:
                            tmp_param['record'][key]['value'].append({
                                'id'   : sub_id,
                                'value': sub_dict
                            })
                        else:
                            tmp_param['record'][key]['value'].append({
                                'value': sub_dict
                            })
                    continue
                else:
                    tmp_param['record'][key] = {
                        'value': value
                    }
                    continue
            params['records'].append(tmp_param)
            tmp_param = {}
        #最後に残りを追加する
        if params['records']:
            resp = self.requestKintone(method='PUT', url=url, json=params)

        return resp

    def updateRec(self,record:dict):
        """
        updateRec is function for updating 1 record in kintone.\n
        record = data to update in kintone.\n
        record = {
            '$id':'1'
               or
            'updateKey': {
                'field':'No duplication field code',
                'value':'value'
            }
            'field_code': 'value'
        }
        """
        if type(record) != dict:
            raise Exception('Argument is not a dict')
        params = {
            'app': self.app,
            "record": {

            }
        }
        url = self.rootURL + 'record.json'
        parameter = self.property

        for key, value in record.items():
            if key == '$revision':
                continue
            #レコードIDを取得する
            if key in ('id', '$id'):
                params['id'] = value
                continue
            elif key == 'updateKey':
                params['updateKey'] = {
                    'field': value['field'],
                    'value': value['value']
                }
                continue
            elif parameter[key]['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                codes = []
                for val in value:
                    codes.append({'code': val})
                params['record'][key] = {
                    'value': codes
                }
                continue
            elif parameter[key]['type'] == 'FILE':
                fileKeys = []
                for val in value:
                    fileKeys.append({'fileKey': val})
                params['record'][key] = {
                    'value': fileKeys
                }
                continue
            elif parameter[key]['type'] == 'SUBTABLE':
                params['record'][key] = {
                    'value': []
                }
                for sub_rec in value:
                    sub_dict = {}
                    sub_id = ''
                    for sub_key, sub_value in sub_rec.items():
                        if sub_key == 'id':
                            sub_id = sub_value
                            continue
                        elif parameter[key]['fields'][sub_key]['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                            codes = []
                            for val in sub_value:
                                codes.append({'code': val})
                            sub_dict[sub_key] = {
                                'value': codes
                            }
                        elif parameter[key]['fields'][sub_key]['type'] == 'FILE':
                            fileKeys = []
                            for val in sub_value:
                                fileKeys.append({'fileKey': val})
                            sub_dict[sub_key] = {
                                'value': fileKeys
                            }
                        else:
                            sub_dict[sub_key] = {
                                'value': sub_value
                            }
                    if sub_id:
                        params['record'][key]['value'].append({
                            'id': sub_id,
                            'value': sub_dict
                        })
                    else:
                        params['record'][key]['value'].append({
                            'value': sub_dict
                        })
                    continue
            else:
                params['record'][key] = {
                    'value': value
                }
                continue
        resp = self.requestKintone(method='PUT', url=url, json=params)

        return resp

    def delete(self,ids:list,revisions=None):
        """
        delete is function for deleting records in kintone.\n
        ids = Specify the record ID of the record to be deleted as a list.\n
        revisions = The expected revision number.
        The order is the same as ids (the revision number expected in the first record of ids is the first number of revisions).
        If it does not match the actual revision number, an error will occur (no record will be deleted).
        However, if the value is -1 or not specified, the revision number will not be verified.
        """
        if type(ids) != list:
            raise Exception('Argument is not a list')

        params = {
            'app': self.app,
            'ids': [

            ]
        }
        response = {}

        url = self.rootURL + 'records.json'

        if revisions is not None:
            params['revisions'] = revisions

        while len(ids) > 100:
            params['ids'] = ids[0:100]
            response = self.requestKintone(method='DELETE', url=url, json=params)
            del ids[0:100]

        if ids:
            params['ids'] = ids[0:100]
            response = self.requestKintone(method='DELETE', url=url, json=params)

        return response

    def postComment(self, recordID, text:str, mentions=None):
        """
        postComment is function for posting comments to kintone.
        """
        if type(text) != str:
            raise Exception('Argument is not a str')
        if mentions is not None and type(mentions) != list:
            raise Exception('Argument is not a list')

        params = {
            'app'    : self.app,
            'record' : recordID,
            'comment': {
                'text'    : text,
                'mentions': mentions if mentions is not None else []
            }
        }
        url = self.rootURL + 'record/comment.json'

        resp = self.requestKintone(method='POST', url=url, json=params)

        return resp

    def deleteComment(self, recordID, commentID):
        """
        deleteComment is function to delete the comment of kintone.
        """

        params = {
            'app'    : self.app,
            'record' : recordID,
            'comment':commentID
        }
        url = self.rootURL + 'record/comment.json'

        resp = self.requestKintone(method='DELETE', url=url, json=params)

        return resp

    def selectComment(self, recordID, order=None, offset=None, limit=None):
        """
        selectComment function to get the comments of kintone records at once.
        """

        params = {
            'app'    : self.app,
            'record' : recordID
        }
        url = self.rootURL + 'record/comments.json'

        if order is not None:
            params['order'] = order
        if offset is not None:
            params['offset'] = offset
        if limit is not None:
            params['limit'] = limit

        resp = self.requestKintone(method='GET', url=url, json=params)

        return resp