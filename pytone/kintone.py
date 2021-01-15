import json
import sys
import requests

class Kintone:

    def __init__(self,apiToken,domain,app):
        self.apiToken = apiToken
        self.rootURL  = 'https://{}.cybozu.com/k/v1/'.format(domain)
        self.app      = app
        self.data_type = ['__ID__', '__REVISION__',
                          'SINGLE_LINE_TEXT', 'CHECK_BOX', 'LINK', 'RICH_TEXT',
                          'RADIO_BUTTON', 'DROP_DOWN', 'MULTI_SELECT', 'MULTI_LINE_TEXT','FILE']
        self.headers   = {
            'X-Cybozu-API-Token': self.apiToken,
            'Content-Type': 'application/json'
        }
        self.property  = self.get_property()

    def get_property(self):
        params = {
            'app': self.app,
            'lang': 'default'
        }
        url = self.rootURL + 'app/form/fields.json'

        resp = requests.get(url, json=params, headers=self.headers)
        result = json.loads(resp.content.decode('utf-8'))
        return result['properties']

    def select(self,where=None,order=None,limit=None,fields=None):
        """
        select is function to get records from Kintone.\n
        Get all fields if "field" is not specified.\n
        If you do not specify "where", get all records.\n
        Always get "id" and "revision".
        """
        params = {
            'app'       : self.app,
            'totalCount': True
        }
        lastRecID = 0
        responses = {
            'records':[]
        }
        if fields is not None:
            params['fields'] = list(set(fields + ['$id', '$revision']))

        url = self.rootURL + 'records.json'
        try:
            while True:
                if where is None:
                    if order is None:
                        params['query'] = '($id > {}) '.format(str(lastRecID)) + 'order by $id asc'
                    else:
                        params['query'] = '($id > {}) '.format(str(lastRecID)) + order
                else:
                    if order is None:
                        params['query'] = '($id > {}) and ('.format(str(lastRecID)) + where + ') order by $id asc'
                    else:
                        params['query'] = '($id > {}) and ('.format(str(lastRecID)) + where + ') ' + order
                if limit is not None:
                    params['query'] = params['query'] + ' limit ' + str(limit)
                resp = requests.get(url, json=params, headers=self.headers)
                resp.raise_for_status()
                response = json.loads(resp.content.decode('utf-8'))
                if response['totalCount'] == '0':
                    break
                #レコードIDの最大値を取得
                response_sorted = sorted(response['records'], key=lambda x:x['$id']['value'])
                lastRecID = int(response_sorted[len(response_sorted) -1]['$id']['value'])
                responses['records'] += response['records']
        except requests.exceptions.RequestException:
            message = ('error： ', json.loads(resp.content.decode('utf-8')))
            return message

        try:
            result = []
            tmp    = responses
            for record in tmp['records']:
                tmp_dic = {}
                for key,value in record.items():
                    if value['type'] in self.data_type:
                        tmp_dic[key] = value['value']
                    #intかfloat型にキャストする(Nonetypeはキャストしない)
                    if value['type'] in ('NUMBER', 'CALC'):
                        if value['value'] == None:
                            tmp_dic[key] = value['value']
                        else:
                            try:
                                tmp_dic[key] = int(value['value'])
                            except:
                                try:
                                    tmp_dic[key] = float(value['value'])
                                except:
                                    tmp_dic[key] = str(value['value'])
                    #日付を文字列にキャストする(Nonetypeはキャストしない)
                    if value['type'] in ('TIME', 'DATE', 'DATETIME', 'CREATED_TIME', 'UPDATED_TIME'):
                        if value['value'] == None:
                            tmp_dic[key] = value['value']
                        else:
                            tmp_dic[key] = str(value['value'])
                    if value['type'] in ('MODIFIER', 'CREATOR'):
                        tmp_dic[key] = value['value']['code']
                    if value['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                        codes = []
                        for val in value['value']:
                            codes.append(val['code'])
                        tmp_dic[key] = codes
                    if value['type'] == 'SUBTABLE':
                        subtable = []
                        sub_dict = {}
                        for sub_rec in value['value']:
                            for sub_keys,sub_values in sub_rec.items():
                                if sub_keys == 'id':
                                    sub_dict['id'] = sub_values
                                    continue
                                for sub_key,sub_value in sub_values.items():
                                    if sub_value['type'] in ('MODIFIER', 'CREATOR'):
                                        sub_dict[sub_key] = sub_value['value']['code']
                                    elif sub_value['type'] in ('NUMBER', 'CALC'):
                                        #Nonetypeはキャストしない
                                        if sub_value['value'] == None:
                                            sub_dict[sub_key] = sub_value['value']
                                        else:
                                            try:
                                                sub_dict[sub_key] = int(sub_value['value'])
                                            except:
                                                try:
                                                    sub_dict[sub_key] = float(sub_value['value'])
                                                except:
                                                    sub_dict[sub_key] = str(sub_value['value'])
                                    elif sub_value['type'] in ('TIME', 'DATE', 'DATETIME', 'CREATED_TIME', 'UPDATED_TIME'):
                                        #Nonetypeはキャストしない
                                        if sub_value['value'] == None:
                                            sub_dict[sub_key] = sub_value['value']
                                        else:
                                            sub_dict[sub_key] = str(sub_value['value'])
                                    elif sub_value['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                                        codes = []
                                        for val in sub_value['value']:
                                            codes.append(val['code'])
                                        sub_dict[sub_key] = codes
                                    else:
                                        sub_dict[sub_key] = sub_value['value']
                                subtable.append(sub_dict)
                                sub_dict = {}
                        tmp_dic[key] = subtable
                result.append(tmp_dic)
            return result
        except:
            return []

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

        try:
            resp = requests.get(url, json=params, headers=self.headers)
            resp.raise_for_status()
        except requests.exceptions.RequestException:
            message = ('error： ', json.loads(resp.content.decode('utf-8')))
            return message

        try:
            tmp = json.loads(resp.content.decode('utf-8'))
            result = {}
            for key,value in tmp['record'].items():
                if key == 'レコード番号':
                    continue
                if value['type'] in self.data_type:
                    result[key] = value['value']
                #intかfloat型にキャストする(Nonetypeはキャストしない)
                if value['type'] in ('NUMBER','CALC'):
                    if value['value'] == None:
                        result[key] = value['value']
                    else:
                        try:
                            result[key] = int(value['value'])
                        except:
                            try:
                                result[key] = float(value['value'])
                            except:
                                result[key] = str(value['value'])
                #日付を文字列にキャストする(Nonetypeはキャストしない)
                if value['type'] in ('TIME', 'DATE', 'DATETIME', 'CREATED_TIME', 'UPDATED_TIME'):
                    if value['value'] == None:
                        result[key] = value['value']
                    else:
                        result[key] = str(value['value'])
                if value['type'] in ('MODIFIER','CREATOR'):
                    result[key] = value['value']['code']
                if value['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                    codes = []
                    for val in value['value']:
                        codes.append(val['code'])
                    result[key] = codes
                if value['type'] == 'SUBTABLE':
                    subtable = []
                    sub_dict = {}
                    for sub_rec in value['value']:
                        for sub_keys, sub_values in sub_rec.items():
                            if sub_keys == 'id':
                                sub_dict['id'] = sub_values
                                continue
                            for sub_key, sub_value in sub_values.items():
                                if sub_value['type'] in ('MODIFIER', 'CREATOR'):
                                    sub_dict[sub_key] = sub_value['value']['code']
                                elif sub_value['type'] in ('NUMBER', 'CALC'):
                                    #Nonetypeはキャストしない
                                    if sub_value['value'] == None:
                                        sub_dict[sub_key] = sub_value['value']
                                    else:
                                        try:
                                            sub_dict[sub_key] = int(sub_value['value'])
                                        except:
                                            try:
                                                sub_dict[sub_key] = float(sub_value['value'])
                                            except:
                                                sub_dict[sub_key] = str(sub_value['value'])
                                elif sub_value['type'] in ('TIME', 'DATE', 'DATETIME', 'CREATED_TIME', 'UPDATED_TIME'):
                                    #Nonetypeはキャストしない
                                    if sub_value['value'] == None:
                                        sub_dict[sub_key] = sub_value['value']
                                    else:
                                        sub_dict[sub_key] = str(sub_value['value'])
                                elif sub_value['type'] in ('USER_SELECT', 'ORGANIZATION_SELECT', 'GROUP_SELECT'):
                                    codes = []
                                    for val in sub_value['value']:
                                        codes.append(val['code'])
                                    sub_dict[sub_key] = codes
                                else:
                                    sub_dict[sub_key] = sub_value['value']
                            subtable.append(sub_dict)
                            sub_dict = {}
                    result[key] = subtable
            return result
        except:
            return []

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

        for record in records:
            #100件づつKintoneに登録する
            if len(params['records']) == 100:
                resp = requests.post(url, json=params, headers=self.headers).json()
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
            resp = requests.post(url, json=params, headers=self.headers).json()

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
        resp = requests.post(url, json=params, headers=self.headers).json()

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

        for record in records:
            #100件づつKintoneに登録する
            if len(params['records']) == 100:
                resp = requests.put(url, json=params, headers=self.headers).json()
            tmp_param['record'] = {}
            for key, value in record.items():
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
            resp = requests.put(url, json=params, headers=self.headers).json()

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
        resp = requests.put(url, json=params, headers=self.headers).json()

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
        url = self.rootURL + 'records.json'

        if revisions is not None:
            params['revisions'] = revisions
        params['ids'] = ids

        resp = requests.delete(url, json=params, headers=self.headers).json()

        return resp

    def postComment(self, recordID, text:str, mentions=None):
        """
        docstring
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

        resp = requests.post(url, json=params, headers=self.headers).json()

        return resp

    def deleteComment(self, recordID, commentID):
        """
        docstring
        """

        params = {
            'app'    : self.app,
            'record' : recordID,
            'comment':commentID
        }
        url = self.rootURL + 'record/comment.json'

        resp = requests.delete(url, json=params, headers=self.headers).json()

        return resp

    def selectComment(self, recordID, order=None, offset=None, limit=None):
        """
        docstring
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

        resp = requests.get(url, json=params, headers=self.headers).json()

        return resp