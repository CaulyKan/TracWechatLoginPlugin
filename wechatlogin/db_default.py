from trac.db import Table, Column

name = 'wechat'
version = 1
tables = [
    Table(name, key=('openid',))[
        Column('openid', type='text'),
        Column('user', type='text'),
        Column('passwd', type='text'),
    ],
]
