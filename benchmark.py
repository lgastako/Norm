import time

from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.sql import select

from norm import SELECT

metadata = MetaData()
users = Table(
    'users', metadata,
    Column('id', Integer, primary_key=True),
    Column('name', String),
    Column('fullname', String))

addresses = Table(
    'addresses', metadata,
    Column('id', Integer, primary_key=True),
    Column('user_id', None, ForeignKey('users.id')),
    Column('email_address', String, nullable=False))


def sqlalchemy_bench():
    s = select([users, addresses], users.c.id == addresses.c.user_id)
    s = s.where(users.c.id > 1)
    s = s.where(users.c.name.startswith('Justin'))
    return str(s)


def norm_bench():
    s = (SELECT('users.name',
                'users.fullname',
                'addresses.email_address')
         .FROM('users')
         .JOIN('addresses', ON='users.id = addresses.user_id'))

    s = s.WHERE('users.id > %(id)s').bind(id=1)
    s = s.WHERE("users.name LIKE %(name)s").bind(name='Justin%')

    return s.query


def raw_bench():
    s = """SELECT users.name,
       users.fullname,
       addresses.email_address
  FROM users
  JOIN addresses
       ON users.id = addresses.user_id
 WHERE users.id > %(id)s AND
       users.name LIKE %(name)s;"""
    return s


def time_it(f, last=None):
    #print f()
    start = time.time()
    for x in xrange(10000):
        f()

    elapsed = time.time() - start
    faster = ''
    if last is not None:
        faster = '%.1f' % (last / elapsed)
    print '%s %.4f, %s' % (f.__name__, elapsed, faster)
    return elapsed


def run_benchmark():
    sqla_time = time_it(sqlalchemy_bench)
    norm_time = time_it(norm_bench, sqla_time)
    time_it(raw_bench, norm_time)


if __name__ == '__main__':
    run_benchmark()
