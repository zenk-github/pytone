# pytone

pytoneは[Kintone](https://kintone.cybozu.co.jp/index.html)にアクセスするためのPythonライブラリです。

```python
from pytone import kintone

kintone = kintone.Kintone('APIトークン', 'サブドメイン', 'アプリID')
```
# Features

pytoneはKintoneをPythonで操作するためのライブラリです。  
pytoneは[KintoneAPI](https://developer.cybozu.io/hc/ja/articles/360000313406-kintone-REST-API%E4%B8%80%E8%A6%A7)の以下に対応しています
* [GET](https://developer.cybozu.io/hc/ja/articles/202331474)
* [POST](https://developer.cybozu.io/hc/ja/articles/202166160)
* [PUT](https://developer.cybozu.io/hc/ja/articles/201941784)
* [DELETE](https://developer.cybozu.io/hc/ja/articles/201941794)
# Requirement

pytoneはPython3系で動作し、以下のライブラリに依存します。

* [requests](https://pypi.org/project/requests/)

# Installation


```bash
pip install requests
pip install pytone
```
# Usage

* レコードの取得（一括）
```python
#呼び出し方
kintone.select(query=query,order=order,limti=limit,fields=fields)
"""
引数は省略可能です

・queryを省略した場合、アプリの全レコードを取得します
・レコードのソートをする場合はqueryには書かず、orderに記述してください
・limitを指定する場合はqueryには書かず、limitに数値を記述してください
・fieldsを省略した場合、全フィールドを取得します
・idとrevisionは指定していなくても取得します
・対象のレコードをすべて取得します。（offset上限対応）
"""

#例
query    = 'フィールドコート１ = "value"'
order    = 'order by $id asc'
limit    = 500
fields   = ['フィールドコート１','フィールドコート２','サブテーブル']
response = kintone.select(query=query,order=order,limit=limit,fields=fields)

"""
レスポンスの例
[
    {
        '$id':1,
        'revision':1,
        'フィールドコート１':'value',
        'フィールドコート２':'value',
        'サブテーブル':
        [
            {
                'id': '1111111',   #テーブルの行ID
                'フィールドコート１':'value',
                'フィールドコート２':'value',
            },
            {
                'id': '1111112',   #テーブルの行ID
                'フィールドコート１':'value',
                'フィールドコート２':'value',
            }
        ]
    },
    {
        '$id':2,
        'revision':1,
        'フィールドコート１':'value',
        'フィールドコート２':'value',
        'サブテーブル':
        [
            {
                'id': '2222222',   #テーブルの行ID
                'フィールドコート１':'value',
                'フィールドコート２':'value',
            },
            {
                'id': '2222223',   #テーブルの行ID
                'フィールドコート１':'value',
                'フィールドコート２':'value',
            }
        ]
    }
]

"""
```
* レコードの取得（一件）
```python
#呼び出し方
#引数に取得するレコードIDを指定します
kintone.selectRec(recordID)

#例
recordID = 1
response = kintone.selectRec(recordID)

"""
レスポンスの例
{
    '$id':1,
    'revision':1,
    'フィールドコート１':'value',
    'フィールドコート２':'value',
    'サブテーブル':
    [
        {
            'id': '1111111',   #テーブルの行ID
            'フィールドコート１':'value',
            'フィールドコート２':'value',
        },
        {
            'id': '1111112',   #テーブルの行ID
            'フィールドコート１':'value',
            'フィールドコート２':'value',
        }
    ],
}

"""
```
* レコードの登録（一括）
```python
#呼び出し方
#insert関数の引数はリスト型でなくてはいけません
kintone.insert(records)

#例
records = [
    {
        '文字列__1行':'value',
        '文字列__複数行':'value\nvalue2',
        'チェックボックス':
            [
                'sample1',
                'sample2'
            ],
        'ユーザー選択':
            [
                'ログイン名１',
                'ログイン名２'
            ],
        'サブテーブル':
        [
            {
                '文字列__1行':'value',
                '文字列__複数行':'value\nvalue2',
                'チェックボックス':
                    [
                        'sample1',
                        'sample2'
                    ]
            },
            {
                '文字列__1行':'value',
                '文字列__複数行':'value\nvalue2',
                'チェックボックス':
                    [
                        'sample1',
                        'sample2'
                    ]
            }
        ]
    },
    {
        '文字列__1行':'value',
        '文字列__複数行':'value\nvalue2',
        ............
    }
]

response = kintone.insert(records)

"""
レスポンスの例
{
    'ids':['1','2'],
    'revisions':['1','1']
}
"""
```
* レコードの登録（一件）
```python
#呼び出し方
#insertRec関数の引数は辞書型でなくてはいけません
kintone.insertRec(record)

#例
record = {
    '文字列__1行':'value',
    '文字列__複数行':'value\nvalue2',
    'チェックボックス':
        [
            'sample1',
            'sample2'
        ],
    'ユーザー選択':
        [
            'ログイン名１',
            'ログイン名２'
        ],
    'サブテーブル':
        [
            {
                '文字列__1行':'value',
                '文字列__複数行':'value\nvalue2',
                'チェックボックス':
                    [
                        'sample1',
                        'sample2'
                    ]
            },
            {
                '文字列__1行':'value',
                '文字列__複数行':'value\nvalue2',
                'チェックボックス':
                    [
                        'sample1',
                        'sample2'
                    ]
            }
        ]
}

response = kintone.insertRec(record)
"""
レスポンスの例
{
    'id': '1',
    'revision': '1'
}
"""
```
* レコードの更新（一括）
```python
#呼び出し方
#update関数の引数はリスト型でなくてはいけません
kintone.update(records)

"""
登録するレコードにidもしくはupdateKeyを指定する必要があります
"""

#例
records = [
    {
        '$id':'1',
        '文字列__1行':'value',
        '文字列__複数行':'value\nvalue2',
        'チェックボックス':
            [
                'sample1',
                'sample2'
            ],
        'ユーザー選択':
            [
                'ログイン名１',
                'ログイン名２'
            ],
        'サブテーブル':
        [
            {
                '文字列__1行':'value',
                '文字列__複数行':'value\nvalue2',
                'チェックボックス':
                    [
                        'sample1',
                        'sample2'
                    ]
            },
            {
                '文字列__1行':'value',
                '文字列__複数行':'value\nvalue2',
                'チェックボックス':
                    [
                        'sample1',
                        'sample2'
                    ]
            }
        ]
    },
    {
        'updateKey':
        {
            'field':'重複禁止のフィールドコート',
            'value':'value'
        },
        '文字列__1行':'value',
        '文字列__複数行':'value\nvalue2',
        ............
    }
]

response = kintone.update(records)
"""
レスポンスの例
{
    'records':[
        {
            'id':'1',
            'revision':'2'
        },
        {
            'id':'2',
            'revision':'2'
        }
    ]
}
"""
```
* レコードの更新（一件）
```python
#呼び出し方
#updateRec関数の引数は辞書型でなくてはいけません
kintone.updateRec(record)

"""
登録するレコードにidもしくはupdateKeyを指定する必要があります
"""
#例

record = {
    '$id':'1',
    '文字列__1行':'value',
    '文字列__複数行':'value\nvalue2',
    'チェックボックス':
        [
            'sample1',
            'sample2'
        ],
    'ユーザー選択':
        [
            'ログイン名１',
            'ログイン名２'
        ],
    'サブテーブル':
        [
            {
                '文字列__1行':'value',
                '文字列__複数行':'value\nvalue2',
                'チェックボックス':
                    [
                        'sample1',
                        'sample2'
                    ]
            },
            {
                '文字列__1行':'value',
                '文字列__複数行':'value\nvalue2',
                'チェックボックス':
                    [
                        'sample1',
                        'sample2'
                    ]
            }
}

response = kintone.updateRec(record)
"""
レスポンスの例
{
    'revision': '2'
}
"""
```
* レコードの削除
```python
#呼び出し方
#delete関数の引数はリスト型でなくてはいけません
kintone.delete(recordIDs)

#例

recordIDs = ['1','2','3']

response = kintone.delete(recordIDs)
"""
レスポンスの例
{}
"""
#リクエスト成功時は空の辞書が戻ってきます
```

# Author

* Author  
Masashi Tsuruya
* Organization  
[株式会社ゼンク](https://zenk.co.jp/)

# License
"pytone" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).