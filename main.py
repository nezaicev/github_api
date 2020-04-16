import requests
import sys
import os
import datetime
from utils import login, generate_list, date_str_to_unix_time, print_commits, get_count_page, binary_search_page, parse

BASE_URL = 'https://api.github.com'

WEEK_UNIX_TIME = 604800
MONTH_UNIX_TIME = 2629743
DAY_UNIX_TIME = 86400


def get_commits(params, sess):
    total_commits = {}
    url = os.path.join(params.url, 'commits')
    parameters_url = {'sha': params.branch,
                      'since': date_str_to_unix_time(params.date_start),
                      'until': date_str_to_unix_time(params.date_end),
                      }

    if (parameters_url['until'] - parameters_url['since']) < WEEK_UNIX_TIME:
        for commit in generate_list(url, parameters_url):
            if commit['author'] and commit['author']['login'] not in total_commits:
                total_commits[commit['author']['login']] = 1
            elif commit['author']:
                total_commits[commit['author']['login']] += 1

    else:
        url = os.path.join(params.url, 'stats', 'contributors')
        list_contributors = sess.get(url).json()
        for author in list_contributors:
            count_commits = 0
            for w in author['weeks']:
                if (w['w'] >= parameters_url['since']) and (w['w'] <= parameters_url['until']):
                    count_commits += int(w['c'])
            if count_commits:
                total_commits[author['author']['login']] = count_commits
    print_commits(total_commits)


def get_count_item(params, sess, name_section_api_github):
    url = os.path.join(params.url, name_section_api_github)
    parameters_url = {'base': params.branch,
                      'state': params.state,
                      'per_page': 100,
                      'page': ''
                      }
    count_page = get_count_page(url, parameters_url, sess)

    if count_page:
        start_page = binary_search_page(url, parameters_url, date_str_to_unix_time(params.date_start), sess)
        if start_page is None:
            params.page = count_page
            start_page = (count_page, len(sess.get(url, params=parameters_url).json()))

        end_page = binary_search_page(url, parameters_url, date_str_to_unix_time(params.date_end), sess)
        if end_page is None:
            params.page = count_page
            end_page = (0, 0)
        if start_page[0]==1:
            return start_page[1]
        else:
            count_pull_requests = (100 * ((start_page[0] - end_page[0]) - 1)) + (100 - end_page[1]) + start_page[1]
            return count_pull_requests
    else:
        return 0


class Parameters:
    def __init__(self, params):
        params_dict=parse(params)

        owner, repo = params_dict['--u'].split('github.com/')[1].split('/')
        self.url = os.path.join(BASE_URL, 'repos', owner, repo)

        self.date_start = params_dict.get('--s') if params_dict.get('--s') else '1970-01-01'
        self.date_end = params_dict.get('--e') if params_dict.get('--e') else datetime.date.today().strftime('%Y-%m-%d')
        self.branch = params_dict.get('--b') if params_dict.get('--b') else 'master'
        self.state = ''


def main():
    sess = login()
    base_parameters_script = Parameters(sys.argv)
    print('Commits', '...')
    get_commits(base_parameters_script, sess)
    print('Pull Requests:', '...')
    parameters_url_pulls = Parameters(sys.argv)
    parameters_url_pulls.state = 'open'
    count_open_pull_requests = get_count_item(parameters_url_pulls, sess, 'pulls')
    parameters_url_pulls.state = 'closed'
    count_closed_pull_requests = get_count_item(parameters_url_pulls, sess, 'pulls')
    parameters_url_pulls.date_end = date_str_to_unix_time(parameters_url_pulls.date_end) - MONTH_UNIX_TIME
    parameters_url_pulls.state = 'open'
    count_old_pull_requests = get_count_item(parameters_url_pulls, sess, 'pulls')
    print('open_pr:', count_open_pull_requests,
          'closed_pr:', count_closed_pull_requests,
          'old_pr:',count_old_pull_requests)
    print('Issues:', '...')
    parameters_url_issues = Parameters(sys.argv)
    parameters_url_issues.state = 'open'
    count_open_issues = get_count_item(parameters_url_issues, sess, 'issues')
    parameters_url_issues.state = 'closed'
    count_closed_issues = get_count_item(parameters_url_issues, sess, 'issues')
    parameters_url_issues.date_end = date_str_to_unix_time(parameters_url_issues.date_end) - WEEK_UNIX_TIME * 2
    parameters_url_issues.state = 'open'
    count_old_issues = get_count_item(parameters_url_issues, sess, 'issues')
    print('open_iss:', count_open_issues,
          'closed_iss:', count_closed_issues,
          'old_issue:', count_old_issues)


if __name__ == "__main__":
    main()
