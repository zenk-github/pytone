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

    def select(self,query=None,order=None,limit=None,fields=None):
        #フィールドを指定しない場合はすべてのフィールドを取得
        #クエリを指定しない場合、すべてのレコードを取得
        #idとrevisionは常に取得する
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
                if query is None:
                    if order is None:
                        params['query'] = '($id > {}) '.format(str(lastRecID)) + 'order by $id asc'
                    else:
                        params['query'] = '($id > {}) '.format(str(lastRecID)) + order
                else:
                    if order is None:
                        params['query'] = '($id > {}) and ('.format(str(lastRecID)) + query + ') order by $id asc'
                    else:
                        params['query'] = '($id > {}) and ('.format(str(lastRecID)) + query + ') ' + order
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
                    #intかfloat型にキャストする
                    if value['type'] in ('NUMBER', 'CALC'):
                        try:
                            tmp_dic[key] = int(value['value'])
                        except:
                            try:
                                tmp_dic[key] = float(value['value'])
                            except:
                                tmp_dic[key] = str(value['value'])
                    #日付を文字列にキャストする
                    if value['type'] in ('TIME', 'DATE', 'DATETIME', 'CREATED_TIME', 'UPDATED_TIME'):
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
                                        try:
                                            sub_dict[sub_key] = int(sub_value['value'])
                                        except:
                                            try:
                                                sub_dict[sub_key] = float(sub_value['value'])
                                            except:
                                                sub_dict[sub_key] = str(sub_value['value'])
                                    elif sub_value['type'] in ('TIME', 'DATE', 'DATETIME', 'CREATED_TIME', 'UPDATED_TIME'):
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
                #intかfloat型にキャストする
                if value['type'] in ('NUMBER','CALC'):
                    try:
                        result[key] = int(value['value'])
                    except:
                        try:
                            result[key] = float(value['value'])
                        except:
                            result[key] = str(value['value'])
                #日付を文字列にキャストする
                if value['type'] in ('TIME', 'DATE', 'DATETIME', 'CREATED_TIME', 'UPDATED_TIME'):
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
                                    try:
                                        sub_dict[sub_key] = int(sub_value['value'])
                                    except:
                                        try:
                                            sub_dict[sub_key] = float(sub_value['value'])
                                        except:
                                            sub_dict[sub_key] = str(sub_value['value'])
                                elif sub_value['type'] in ('TIME', 'DATE', 'DATETIME', 'CREATED_TIME', 'UPDATED_TIME'):
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
        if type(records) != list:
            print('引数にはリスト型を指定してください')
            sys.exit()
        params = {
            'app': self.app,
            "records": [

            ]
        }
        tmp_param = {}
        url       = self.rootURL + 'records.json'
        parameter = self.property

        for record in records:
            #100件づつkintoneに登録する
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
        #引数の型チェック
        if type(record) != dict:
            print('引数には辞書型を指定してください')
            sys.exit()
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
        if type(records) != list:
            print('引数にはリスト型を指定してください')
            sys.exit()
        params = {
            'app': self.app,
            "records": [

            ]
        }
        tmp_param = {}
        url       = self.rootURL + 'records.json'
        parameter = self.property

        for record in records:
            #100件づつkintoneに登録する
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
        if type(record) != dict:
            print('引数には辞書型を指定してください')
            sys.exit()
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
        if type(ids) != list:
            print('引数にはリスト型を指定してください')
            sys.exit()

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

