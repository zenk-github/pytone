from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='zenkPytone',
    version='1.0.0',
    description='pytone is a library for operating Kintone with Python.',
    long_description=long_description,
    url='https://github.com/zenk-github/pytone',
    author='Masashi Tsuruya',
    author_email='m_tsuruya@zenk.co.jp',
    license='MIT',
    # 実際に動かす時に依存関係にあるライブラリをinstallしてくれる
    install_requires=['requests'],
    keywords='pytone kintone Kintone KINTONE zenk Zenk ZENK',
    packages=['pytone'],
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)