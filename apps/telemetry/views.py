from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from django.db import transaction
from django.utils.dateparse import parse_datetime
from django.utils import timezone

from ..accounts.models import Project
from .models import commitLog,RepositorySync

import os , requests
from urllib.parse import urlparse
from django.views.decorators.http import require_POST,require_GET

import pandas as pd

def process_commit_data(all_commits):
    df = pd.DataFrame(all_commits)

    if df.empty:
        return {
        "summary": {
            "total_commits": 0,
            "total_added": 0,
            "total_deleted": 0,
            "total_lines": 0,
            "average_lines": 0,
            "z_score_outliers": 0,
            "iqr_outliers": 0,
            "q1": 0,
            "q3": 0,
            "iqr": 0,
            "lower_limit": 0,
            "upper_limit": 0
        },
        "commits": []
        }

    #Line data 
    #=============

    df["addline"] = pd.to_numeric(
        df["addline"], errors="coerce"
    ).fillna(0)

    df["deletline"] = pd.to_numeric(
        df["deletline"], errors="coerce"
    ).fillna(0)

    df["total_lines"] = df["addline"] + df["deletline"]

    #z_score data 
    #===============
    mean = df["total_lines"].mean()
    std = df["total_lines"].std(ddof=0)
    if std == 0:
        df["z_score"] = 0
    else:
        df["z_score"] = (
            df["total_lines"] - mean
        ) / std
    df["z_outlier"] = df["z_score"].abs() > 3

    #IQR data
    #===============
    q1 = df["total_lines"].quantile(0.25)
    q3 = df["total_lines"].quantile(0.75)
    iqr = q3 - q1
    lower_limit = q1 - (1.5 * iqr)
    upper_limit = q3 + (1.5 * iqr)
    df["iqr_outlier"] = (
        (df["total_lines"] < lower_limit) |
        (df["total_lines"] > upper_limit)
    )

    #add all to one obj
    #===============
    summary = {
        "total_commits": int(len(df)),
        "total_added": int(df["addline"].sum()),
        "total_deleted": int(df["deletline"].sum()),
        "total_lines": int(df["total_lines"].sum()),
        "average_lines": round(float(mean), 2),
        "z_score_outliers": int(df["z_outlier"].sum()),
        "iqr_outliers": int(df["iqr_outlier"].sum()),
        "q1": round(float(q1), 2),
        "q3": round(float(q3), 2),
        "iqr": round(float(iqr), 2),
        "lower_limit": round(float(lower_limit), 2),
        "upper_limit": round(float(upper_limit), 2)
    }

    df["z_score"] = df["z_score"].round(2)
    df["commitdata"] = df["commitdata"].astype(str)
    df["syncedAt"] = df["syncedAt"].astype(str)
    
    return {
        "summary": summary,
        "commits": df.to_dict(orient="records")
    }

#AUTHORIZATION is by this frindly funcation
#==========================================
def get_github_headers():
    token = os.getenv("GIT_AUTHORIZATION_KAY", "")

    return {
        "Authorization": (
            token if token.startswith("Bearer ")
            else f"Bearer {token}"
        ),
        "Accept": "application/vnd.github+json"
    }

#sync git hub repository to local sqlLigtht DB
#==========================================
def sync_repository(repo_url, user):
    parsed_url = urlparse(str(repo_url).strip())
    if parsed_url.hostname not in ("github.com", "www.github.com"):
        raise ValueError("Invalid GitHub URL")
    path = parsed_url.path.strip("/").removesuffix(".git")
    parts = path.split("/")
    if len(parts) != 2 or not all(parts):
        raise ValueError("Invalid repository path")
    owner, repo_name = parts
    repository = f"{owner}/{repo_name}"
    sync_record, created = RepositorySync.objects.get_or_create(
        user=user,
        repository=repository
    )
    last_sha = sync_record.last_commit_sha
    session = requests.Session()
    session.headers.update(get_github_headers())
    new_commits = []
    page = 1
    checkpoint_found = False
    while True:
        api_url = (
            f"https://api.github.com/repos/{owner}/{repo_name}"
            f"/commits?per_page=100&page={page}"
        )
        response = session.get(api_url, timeout=20)
        response.raise_for_status()
        commits = response.json()
        if not commits:
            break
        for item in commits:
            sha = item["sha"]
            if last_sha and sha == last_sha:
                checkpoint_found = True
                break
            new_commits.append(item)
        if checkpoint_found:
            break
        page += 1
    records = []
    for item in new_commits:
        sha = item["sha"]
        commit = item.get("commit", {})
        author = commit.get("author") or {}
        committer = commit.get("committer") or {}
        commit_date = (author.get("date") or committer.get("date"))
        commit_date = (parse_datetime(commit_date) if commit_date else None)
        if not commit_date:
            continue
        detail_url = (
            f"https://api.github.com/repos/{owner}/{repo_name}"
            f"/commits/{sha}"
        )

        additions = 0
        deletions = 0
        total = 0

        detail_response = session.get(detail_url, timeout=20)

        if detail_response.status_code == 200:
            stats = detail_response.json().get("stats", {})

            additions = stats.get("additions", 0)
            deletions = stats.get("deletions", 0)
            total = stats.get("total", 0)

        records.append(
            commitLog(
                user=user,
                commitSha=sha,
                repository=repository,
                commitdata=commit_date,
                autherName=author.get("name") or "Unknown",
                authorEmail=author.get("email"),
                message=commit.get("message", ""),
                addline=additions,
                deletline=deletions,
                totalChanges=total,
                html_url=item.get("html_url")
            )
        )
    with transaction.atomic():
        commitLog.objects.bulk_create(
            records,
            ignore_conflicts=True,
            batch_size=500
        )
        if new_commits:
            latest_commit = new_commits[0]
            latest_author = latest_commit.get("commit", {})
            latest_author = latest_author.get("author") or {}
            latest_date = latest_author.get("date")
            sync_record.last_commit_sha = latest_commit["sha"]
            sync_record.last_commit_date = (parse_datetime(latest_date) if latest_date else None)
        sync_record.last_synced_at = timezone.now()
        sync_record.save()
    session.close()
    return {
        "repository": repository,
        "new_commits": len(records),
        "status": "success"
    }


#facth and updata data base by github repo data
#==============================================
@require_POST
def get_user_group_repositories(request):

    group_id = request.POST.get("group_id")
    user_id = request.POST.get("user_id")

    projects = Project.objects.filter(
        group_id=group_id,
        user__user_id=user_id
    ).select_related("user")

    if not projects.exists():
        return JsonResponse({
            "status": False,
            "message": "No projects found"
        }, status=404)

    user = projects.first().user

    results = []

    for repo_url in projects.values_list("projetUrl", flat=True):

        try:
            result = sync_repository(repo_url, user)
            results.append(result)

        except (requests.RequestException, ValueError) as e:

            results.append({
                "repository": str(repo_url),
                "status": "failed",
                "error": str(e)
            })

    repository_names = [
        item["repository"]
        for item in results
        if item["status"] == "success"
    ]

    all_commits = list(
        commitLog.objects.filter(
            user=user,
            repository__in=repository_names
        ).order_by("-commitdata").values(
            "commitSha",
            "repository",
            "commitdata",
            "autherName",
            "authorEmail",
            "message",
            "addline",
            "deletline",
            "totalChanges",
            "html_url",
            "syncedAt"
        )
    )
    processed_data = process_commit_data(all_commits)
    return JsonResponse({
        "status": True,
        "repositories": results,

        "total_commits": len(all_commits),
        "all_commits": all_commits,

        "analytics": processed_data["summary"],
        "processed_commits": processed_data["commits"]
    })

#use if data inside local Store age
#=======================================
@require_GET
def get_group_commits(request):

    group_id = request.GET.get("group_id")
    user_id = request.GET.get("user_id")
    projects = Project.objects.filter(group_id=group_id,user__user_id=user_id)

    if not projects.exists():
        return JsonResponse({"status": False,"all_commits": []}, status=404)
    
    user = projects.first().user
    repositories = []
    for url in projects.values_list("projetUrl", flat=True):
        try:
            parsed = urlparse(str(url).strip())
            if parsed.hostname not in ("github.com", "www.github.com"):
                continue
            path = parsed.path.strip("/").removesuffix(".git")
            if len(path.split("/")) == 2:
                repositories.append(path)
        except Exception:
            continue
    all_commits = list(
        commitLog.objects.filter(
            user=user,
            repository__in=repositories
        ).order_by("-commitdata").values("commitSha","repository","commitdata","autherName","authorEmail","message","addline","deletline","totalChanges","html_url","syncedAt")
    )
    processed_data = process_commit_data(all_commits)
    return JsonResponse({
        "status": True,
        "total_commits": len(all_commits),
        "all_commits": all_commits,

        "analytics": processed_data["summary"],
        "processed_commits": processed_data["commits"]
        })
