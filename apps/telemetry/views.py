from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from ..accounts.models import Project
import os , requests
@require_POST
def get_user_group_repositories(request):

    group_id = request.POST.get('group_id')
    user_id = request.POST.get('user_id')

    projects = Project.objects.filter(
        group_id=group_id,
        user__user_id=user_id
    )

    repository_urls = list(
        projects.values_list('projetUrl', flat=True)
    )

    print("Repository URLs:", repository_urls)
    gitData = giveGitdata(repository_urls)
    return JsonResponse({
        'repository_urls': gitData
    })

def giveGitdata(repo_url):
    print("your url is ",repo_url)
    try:
        if isinstance(repo_url, list):
            if not repo_url:
                raise ValueError("Empty repository URL list")
            repo_url = repo_url[0]
            
        repo_url= str(repo_url).strip()
        clean_path = repo_url.rstrip('/').split('github.com/')[-1]
        print(clean_path)
    except Exception:
        print("Error: Invalid GitHub URL format.")
        return
    headers = {
        'Authorization':os.getenv('GIT_AUTHORIZATION_KAY','')
    }

    all_commits = []
    page = 1
    while True:
        commits_api_url = f"https://api.github.com/repos/{clean_path}/commits?per_page=100&page={page}"
        response = requests.get(commits_api_url, headers=headers)
        if response.status_code != 200:
            print(f"Failed to fetch commits or rate limit reached. Status Code: {response.status_code}")
            break
        commits_json = response.json()
        if not commits_json:
            break
        all_commits.extend(commits_json)
        print(f" Fetched page {page}...")
        page += 1
    return all_commits