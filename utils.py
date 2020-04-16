import os,sys
import datetime
from requests import session

def parse(params):
    try:
        r = {x: params[params.index(x) + 1] for x in params if x[0] == '-' and x[1]=='-'}
        if r['--u']!='':
            return r
        else:
            print("url - обязательный параметр (--u)")
            raise SystemExit
    except:
        print('Неверный формат ввода')
        print('Пример параметров: --u "https://github.com/django/django" --s 2020-03-01 --e 2020-04-02 --b stable/1.0.x' )

def print_commits(_dict):
    if len(_dict)<30:
        count = len(_dict)
    else:
        count=30
    list_d = list(_dict.items())
    list_d.sort(key=lambda i: i[1],reverse=True)
    for i in list_d:
        if count==0:
            break
        else:
            print(i[0], ':', i[1])
        count-=1


def date_str_to_unix_time(s):
    if type(s) is str:
        if len(s) > 10:
            date_unix = datetime.datetime.strptime(s.split('T')[0], '%Y-%m-%d').strftime('%s')
        else:
            date_unix = datetime.datetime.strptime(s, '%Y-%m-%d').strftime('%s')

        return int(date_unix)
    else:
        return s


def login():
    sess = session()
    sess.auth = ('nezaicev', 'wp8db002611')
    return sess


def generate_list(link, params,sess):

    class ResponseApiGithub:
        links = {'next': {'url': link}}

    response = ResponseApiGithub()
    while 'next' in response.links:
        response = sess.get(response.links['next']['url'], params=params)
        for i in response.json():
            yield i


def get_count_page(url,params, sess):
    r = sess.get(url,params=params)
    try:
        parameters = {i.split('=')[0]: i.split('=')[1] for i in r.links['last']['url'].split('?')[1].split('&')}
        return int(parameters['page'])
    except:
        if len(r.json()):
            return 1
        else:
            return 0


def binary_search_page(url,params, value, sess):
    low = 1
    hight = get_count_page(url,params, sess)
    if hight:
        while low <= hight:
            mid = (low + hight) // 2
            params['page']=str(mid)
            r = sess.get(url,params=params).json()
            date_pull_create_start_page = date_str_to_unix_time(r[0]['created_at'])
            date_pull_create_end_page = date_str_to_unix_time(r[len(r) - 1]['created_at'])
            if (date_pull_create_start_page >= value) and (date_pull_create_end_page <= value):
                for index,item in enumerate(r):
                    if (date_str_to_unix_time(item['created_at'])-value)<=0:
                        item=index
                        break
                page=mid
                return page,item
            if date_pull_create_end_page < value:
                hight = mid - 1
            else:
                low = mid + 1
    return None

