from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.db import transaction
from django.utils.dateparse import parse_datetime

from ..accounts.models import Project
from .models import commitLog

import os , requests
from urllib.parse import urlparse
@require_POST
def get_user_group_repositories(request):

    group_id = request.POST.get('group_id')
    user_id = request.POST.get('user_id')

    projects = Project.objects.filter(
        group_id=group_id,
        user__user_id=user_id
    ).select_related('user')

    if not projects.exists():
        return JsonResponse({
            'status': False,
            'message': 'No projects found',
            'all_commits': []
        })

    User = projects.first().user

    
    repository_urls = list(
        projects.values_list('projetUrl', flat=True)
    )
    
    print("Repository URLs:", repository_urls)

    for repo_url in repository_urls:
        giveGitdata(repo_url, User)

    all_commits = list(
        commitLog.objects.filter(
            user=User
        ).order_by('-commitdata').values(
            'commitSha',
            'repository',
            'commitdata',
            'autherName',
            'authorEmail',
            'message',
            'addline',
            'deletline',
            'totalChanges',
            'html_url',
            'syncedAt'
        )
    )

    return JsonResponse({
        'status': True,
        'total_commits': len(all_commits),
        'all_commits': all_commits
    })

def giveGitdata(repo_url, User):

    try:
        parsed_url = urlparse(str(repo_url).strip())
        if parsed_url.hostname not in ('github.com', 'www.github.com'):
            return False
        clean_path = parsed_url.path.strip('/').removesuffix('.git')
        parts = clean_path.split('/')
        if len(parts) != 2 or not all(parts):
            return False
        owner, repo_name = parts
        repository = f"{owner}/{repo_name}"

    except Exception as e:
        print("Invalid repository URL:", e)
        return False

    token = os.getenv('GIT_AUTHORIZATION_KAY', '')
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/vnd.github+json'
    }
    session = requests.Session()
    session.headers.update(headers)

    page = 1
    saved_count = 0

    while True:

        commits_api_url = (
            f"https://api.github.com/repos/{owner}/{repo_name}"
            f"/commits?per_page=100&page={page}"
        )

        try:
            response = session.get(
                commits_api_url,
                timeout=20
            )

            if response.status_code != 200:
                print("GitHub API Error:", response.status_code)
                print(response.text[:500])
                break

            commits_json = response.json()
            if not commits_json:
                break
            new_commits = []

            for item in commits_json:
                sha = item.get('sha')
                if commitLog.objects.filter(
                    user=User,
                    repository=repository,
                    commitSha=sha
                ).exists():
                    continue

                commit = item.get('commit', {})
                author = commit.get('author') or {}
                committer = commit.get('committer') or {}
                author_date = (
                    author.get('date')
                    or committer.get('date')
                )
                commit_date = parse_datetime(author_date) if author_date else None
                if not commit_date:
                    continue
                detail_url = (
                    f"https://api.github.com/repos/{owner}/{repo_name}"
                    f"/commits/{sha}"
                )
                additions = 0
                deletions = 0
                total_changes = 0
                try:
                    detail_response = session.get(
                        detail_url,
                        timeout=20
                    )
                    if detail_response.status_code == 200:
                        stats = detail_response.json().get('stats', {})

                        additions = stats.get('additions', 0)
                        deletions = stats.get('deletions', 0)
                        total_changes = stats.get('total', 0)

                except requests.RequestException as e:
                    print("Commit detail error:", e)

                new_commits.append(
                    commitLog(
                        user=User,
                        commitSha=sha,
                        repository=repository,
                        commitdata=commit_date,
                        autherName=author.get('name') or 'Unknown',
                        authorEmail=author.get('email'),
                        message=commit.get('message', ''),
                        addline=additions,
                        deletline=deletions,
                        totalChanges=total_changes,
                        html_url=item.get('html_url')
                    )
                )
            if new_commits:
                with transaction.atomic():
                    commitLog.objects.bulk_create(
                        new_commits,
                        ignore_conflicts=True,
                        batch_size=500
                    )
                saved_count += len(new_commits)
            print(f"Fetched page {page}, saved {len(new_commits)} new commits")
            page += 1

        except requests.RequestException as e:
            print("GitHub request error:", e)
            break

    session.close()
    print(f"Total new commits saved: {saved_count}")

    return True