import os
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
