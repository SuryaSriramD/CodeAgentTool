import requests
import json
import os
import ipdb
from tqdm import tqdm  
from datetime import datetime

# 读取配置
with open('config.json') as config_file:
    config = json.load(config_file)
GITHUB_TOKEN = config['GITHUB_TOKEN']

# headers = {'Authorization': f'token {GITHUB_TOKEN}'}
headers = {
    'Authorization': f'token {GITHUB_TOKEN}',
    'Accept': 'application/vnd.github.v3+json'
}
response = requests.get('https://api.github.com/some_endpoint', headers=headers)
# limit = response.headers.get('X-RateLimit-Limit')
# remaining = response.headers.get('X-RateLimit-Remaining')
# reset_time = response.headers.get('X-RateLimit-Reset')


# 函数定义
def get_top_language_repos(lan="python"):
    GITHUB_API_URL = 'https://api.github.com/search/repositories'
    query_params = {
        'q': f'language:{lan} created:>2023-01-01 created:<2024-01-01',
        'sort': 'stars',
        'order': 'desc',
        'per_page': 20
    }
    response = requests.get(GITHUB_API_URL, headers=headers, params=query_params)
    if response.status_code == 200:
        repos = response.json()['items']
        return [{'owner': repo['owner']['login'], 'name': repo['name'], 'url': repo['html_url']} for repo in repos]
    else:
        print('Failed to retrieve repositories')
        return []
""" 
def get_pull_requests(owner, repo_name, state):
    GITHUB_API_URL = f'https://api.github.com/repos/{owner}/{repo_name}/pulls'
    pull_requests = []
    page = 1
    params = {'state': state, 'page': page, 'per_page': 100}
    
    while len(pull_requests) < 15:  # 确保不超过20个PR
        params = {'state': state, 'page': page, 'per_page': 15}
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        # 过滤掉2023年之前的PR
        filtered_data = [pr for pr in data if datetime.fromisoformat(pr['created_at'][:-1]) > datetime(2023, 1, 1)]
        pull_requests.extend(filtered_data)
        page += 1
    return pull_requests

"""      
def get_pull_requests(owner, repo_name, state):
    GITHUB_API_URL = f'https://api.github.com/repos/{owner}/{repo_name}/pulls'
    pull_requests = []
    page = 1
    while len(pull_requests) < 15:
        params = {'state': state, 'page': page, 'per_page': 15}
        response = requests.get(GITHUB_API_URL, headers=headers, params=params)
        if response.status_code != 200:
            break
        data = response.json()
        if not data:
            break
        pull_requests.extend(data)
        page += 1
    return pull_requests



def get_commit_files(commit_url, token):
    headers = {'Authorization': f'token {token}'}
    response = requests.get(commit_url, headers=headers)
    if response.status_code == 200:
        return response.json().get('files', [])
    else:
        return []
    
def write_commit_data(repo_folder, commit_sha, files, token):
    for i, file_info in enumerate(files):
        patch = file_info.get('patch', 'No changes available')
        with open(f'{repo_folder}/{commit_sha}-commit.txt', 'w') as patch_file:
            patch_file.write(patch)

        raw_url = file_info.get('raw_url')  # 使用 get 方法获取 raw_url
        if raw_url:  # 检查 raw_url 是否存在
            file_response = requests.get(raw_url, headers={'Authorization': f'token {token}'})
            if file_response.status_code == 200:
                with open(f'{repo_folder}/{commit_sha}-context.txt', 'w') as content_file:
                    content_file.write(file_response.text)

def write_commit_datas(repo_folder, commit_sha, files, token):
    for i, file_info in enumerate(files):
        patch = file_info.get('patch', 'No changes available')
        with open(f'{repo_folder}/{commit_sha}-commit-{i}.txt', 'w') as patch_file:
            patch_file.write(patch)

        raw_url = file_info.get('raw_url')  # 使用 get 方法获取 raw_url
        if raw_url:  # 检查 raw_url 是否存在
            file_response = requests.get(raw_url, headers={'Authorization': f'token {token}'})
            if file_response.status_code == 200:
                with open(f'{repo_folder}/{commit_sha}-context-{i}.txt', 'w') as content_file:
                    content_file.write(file_response.text)

"""
def write_commit_data(repo_folder, commit_sha, files, token):
    for i, file_info in enumerate(files):
        patch = file_info.get('patch', 'No changes available')
        with open(f'{repo_folder}/{commit_sha}-commit-{i}.txt', 'w') as patch_file:
            patch_file.write(patch)
        if 'raw_url' in file_info:
            file_response = requests.get(file_info['raw_url'], headers={'Authorization': f'token {token}'})
            if file_response.status_code == 200:
                with open(f'{repo_folder}/{commit_sha}-context-{i}.txt', 'w') as content_file:
                    content_file.write(file_response.text)
"""
def get_pull_request_commits(repo, pull_number, token):
    api_url = f"https://api.github.com/repos/{repo}/pulls/{pull_number}/commits"
    headers = {'Authorization': f'token {token}'}
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        print('Failed to retrieve commits')
        return []


def process_pr_files(pr_file, pr_type):
    with open(pr_file, 'r') as file:
        pr_links = file.readlines()
    repo_folder = f"{pr_type}"
    
    if not os.path.exists(repo_folder):
        os.makedirs(repo_folder)
    else:
        for existing_file in os.listdir(repo_folder):
            continue
            # os.remove(os.path.join(repo_folder, existing_file))
    print(len(pr_links),pr_file)
    if pr_links != []:
        print(len(pr_links))
        for pr_link in pr_links:
            pr_link = pr_link.strip()
            repo, pull_number = "/".join(pr_link.split('/')[3:5]), pr_link.split('/')[-1]
            commits = get_pull_request_commits(repo, pull_number, GITHUB_TOKEN)
            # ipdb.set_trace()
            for commit in commits:
                sha = commit['sha']
                message = commit['commit']['message']
                commit_files = get_commit_files(commit['url'], GITHUB_TOKEN)
                if len(commit_files)>1: #超过1的文件太多, 会拖慢项目进度, 超过1的请write_commit_datas
                    continue
                else:
                    with open(f'{repo_folder}/{sha}-message.txt', 'w') as msg_file:
                        msg_file.write(message)
                    write_commit_data(repo_folder, sha, commit_files, GITHUB_TOKEN)

def check_and_prepare_directory(directory_name):
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
    else:
        for file in os.listdir(directory_name):
            file_path = os.path.join(directory_name, file)
            if os.path.isfile(file_path):
                os.remove(file_path)


def main(lan="python"):
    # 第一步：获取 top Python 项目
    top_lan_repos = get_top_language_repos(lan)
    lan_directory = f'LAN{lan}'

    # 第二步: 获取每个项目的PR list
    check_and_prepare_directory(lan_directory)

    # 保存 Python 项目信息到 JSON 文件
    with open(f'top_{lan}_repos.json', 'w') as file:
        json.dump(top_lan_repos, file, indent=4)

        
    
    for repo in tqdm(top_lan_repos, desc=f"Processing repositories for {lan}"):
        owner = repo['owner']
        repo_name = repo['name']
        merged_prs = get_pull_requests(owner, repo_name, 'closed')
        closed_prs = []
        with open(f'{lan_directory}/{lan}-merged-{owner}-{repo_name}.txt', 'w') as merged_file, \
             open(f'{lan_directory}/{lan}-closed-{owner}-{repo_name}.txt', 'w') as closed_file:
            for pr in merged_prs:
                if pr['merged_at'] is not None:
                    merged_file.write(f"{pr['html_url']}\n")
                else:
                    closed_prs.append(pr['html_url'])
            
            for pr in closed_prs:
                closed_file.write(f"{pr}\n")
    
    # 第三步：处理每个 PR 的提交
    for repo in tqdm(top_lan_repos, desc=f"Processing commits for {lan}"):
        owner = repo['owner']
        repo_name = repo['name']
        process_pr_files(f'{lan_directory}/{lan}-merged-{owner}-{repo_name}.txt', 'merged')
        process_pr_files(f'{lan_directory}/{lan}-closed-{owner}-{repo_name}.txt', 'closed')

if __name__ == '__main__':
    main("Perl")
