# pytone

pytoneは[Kintone](https://kintone.cybozu.co.jp/index.html)にアクセスするためのPythonライブラリです。

```python
from pytone import kintone, kintone_file

kintone      = kintone.Kintone('認証情報', 'サブドメイン', 'アプリID')
kintone_file = kintone_file.KintoneFile('認証情報', 'サブドメイン')
```
# Features

pytoneはKintoneをPythonで操作するためのライブラリです。  
pytoneは[Kintone REST API](https://developer.cybozu.io/hc/ja/articles/360000313406-kintone-REST-API%E4%B8%80%E8%A6%A7)の以下に対応しています
* [レコードの取得](https://developer.cybozu.io/hc/ja/articles/202331474)
* [レコードの一括取得](https://developer.cybozu.io/hc/ja/articles/360029152012)
* [レコードの登録](https://developer.cybozu.io/hc/ja/articles/202166160)
* [レコードの更新](https://developer.cybozu.io/hc/ja/articles/201941784)
* [レコードの削除](https://developer.cybozu.io/hc/ja/articles/201941794)
* [レコードコメントの投稿](https://developer.cybozu.io/hc/ja/articles/209758903)
* [レコードコメントの削除](https://developer.cybozu.io/hc/ja/articles/209758703)
* [レコードコメントの一括取得](https://developer.cybozu.io/hc/ja/articles/208242326)
* [ファイルアップロード](https://developer.cybozu.io/hc/ja/articles/201941824)
* [ファイルダウンロード](https://developer.cybozu.io/hc/ja/articles/202166180)
# Requirement

pytoneはPython3系で動作し、以下のライブラリに依存します。

* [requests](https://pypi.org/project/requests/)

# Installation


```bash
pip install requests
pip install zenkPytone
```
[![Downloads](https://pepy.tech/badge/zenkpytone)](https://pepy.tech/project/zenkpytone)
# Usage

* レコードの取得（複数）
```python
#呼び出し方
kintone.select(where,order,limit,fields)
"""
引数は省略可能です

・レコードのソートをする場合はwhereには書かず、orderに記述してください
・limitを指定する場合はwhereには書かず、limitに数値を記述してください
・fieldsを省略した場合、全フィールドを取得します
・idとrevisionは指定していなくても取得します
・500件より多いレコードを取得することは出来ません
"""

#例
where    = 'フィールドコート１ = "value"'
order    = 'order by $id asc'
limit    = 500
fields   = ['フィールドコート１','フィールドコート２','サブテーブル']
response = kintone.select(where=where,order=order,limit=limit,fields=fields)

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
* レコードの取得（全件）
```python
#呼び出し方
kintone.selectAll(where,fields)
"""
引数は省略可能です

・order byを指定することはできません
・limitを指定することはできません
・fieldsを省略した場合、全フィールドを取得します
・idとrevisionは指定していなくても取得します
・対象のレコードをすべて取得します（offset上限対応）
"""

#例
where    = 'フィールドコート１ = "value"'
fields   = ['フィールドコート１','フィールドコート２','サブテーブル']
response = kintone.select(where=where, fields=fields)

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
* レコードコメントの投稿
```python
#呼び出し方
kintone.postComment(recordID, text, mentions)

#例

text      = "システムからのコメントです。\nご確認をお願いします。"
mentions  = [
    {
        "code": "takahashi",
        "type": "USER"
    },
    {
        // メンション先のユーザーにゲストユーザーを指定する場合
        "code": "guest/yamada@test.jp",
        "type": "USER"
    },
]

response = kintone.postComment(recordID=1, text=text, mentions=mentions)
"""
レスポンスの例
{
    "id": 1
}
"""
#投稿したコメントのIDが返されます
```

* レコードコメントの削除
```python
#呼び出し方
kintone.deleteComment(recordID, commentID)

#例
response = kintone.deleteComment(recordID=1, comment=1)

"""
レスポンスの例
{}
"""
#リクエスト成功時は空の辞書が戻ってきます
```

* レコードコメントの一括取得
```python
#呼び出し方
kintone.selectComment(recordID, order, offset, limit)
"""
order,offset,limitは省略可能です
"""

#例
response = kintone.selectComment(recordID=1, order='desc', offset=0, limit=10)

"""
レスポンスの例
{
    "comments": [
        {
            "id": "2",
            "text": "佐藤　昇 \nありがとうございます。内容を確認しました。\n引き続きよろしくお願いします！",
            "createdAt": "2016-04-12T23:49:00Z",
            "creator": {
                "code": "kato",
                "name": "加藤　美咲"
            },
            "mentions": [
                {
                    "code": "sato",
                    "type": "USER"
                }
            ]
        },
        {
            "id": "1",
            "text": "加藤　美咲   営業本部 管理部受付 \n\n本日の作業レポートです。\n高橋　しおり さん、ご確認をお願いします。",
            "createdAt": "2016-04-12T23:46:00Z",
            "creator": {
                "code": "sato",
                "name": "佐藤　昇"
            },
            "mentions": [
                {
                    "code": "kato",
                    "type": "USER"
                },
                {
                    "code": "営業本部_OZKQWZ",
                    "type": "ORGANIZATION"
                },
                {
                    "code": "管理部受付_zX6C6r",
                    "type": "GROUP"
                },
                {
                    "code": "takahashi",
                    "type": "USER"
                }
            ]
        }
    ],
    "older": false,
    "newer": false
}
"""
```

* ファイルのアップロード
```python
#呼び出し方
kintone_file.uploadFile(file)

#例
with open('ファイルのパス', mode='rb') as f:
    response = kintone_file.uploadFile(f)

"""
レスポンスの例
{
    "fileKey": "c15b3870-7505-4ab6-9d8d-b9bdbc74f5d6"
}
"""
```

* ファイルのダウンロード
```python
#呼び出し方
kintone_file.downloadFile(fileKey)

#例
fileKey  = 'c15b3870-7505-4ab6-9d8d-b9bdbc74f5d6'
response = kintone_file.downloadFile(fileKey=fileKey)

"""
バイナリデータがレスポンスされます
"""
```

# Author

* Author  
Masashi Tsuruya
* Organization  
[株式会社ゼンク](https://zenk.co.jp/)

# License
"pytone" is under [MIT license](https://en.wikipedia.org/wiki/MIT_License).