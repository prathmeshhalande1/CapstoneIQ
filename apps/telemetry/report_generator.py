import os
import re
from urllib.parse import urlparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import requests
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from ..accounts.models import Project, projectGroup, userProfile
from .models import commitLog
from .utils import get_github_headers, process_commit_data

UPPERCASE_TOKENS = {"MCA", "BCA", "BBA", "API", "UI", "UX", "SQL", "LOC", "IQR"}


def format_display_title(raw_text):
    words = str(raw_text or "").strip().split()
    formatted = []
    for word in words:
        clean_upper = re.sub(r"[^A-Za-z0-9]", "", word).upper()
        if clean_upper in UPPERCASE_TOKENS:
            formatted.append(word.upper())
        else:
            formatted.append(word.capitalize())
    return " ".join(formatted)


def extract_repo_slug(repo_url):
    try:
        parsed = urlparse(str(repo_url).strip())
        if parsed.hostname not in ("github.com", "www.github.com"):
            return None
        path = parsed.path.strip("/").removesuffix(".git")
        parts = path.split("/")
        if len(parts) == 2 and all(parts):
            return f"{parts[0]}/{parts[1]}"
    except Exception:
        pass
    return None


def fetch_language_percentages(repo_slugs):
    """Fetches GitHub language byte counts across synced repos and computes %."""
    totals = {}
    headers = get_github_headers()
    for slug in repo_slugs:
        try:
            resp = requests.get(
                f"https://api.github.com/repos/{slug}/languages",
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                for lang, byte_count in resp.json().items():
                    totals[lang] = totals.get(lang, 0) + byte_count
        except requests.RequestException:
            continue

    total_bytes = sum(totals.values())
    if total_bytes <= 0:
        return {}
    return {
        lang: round((count / total_bytes) * 100, 2)
        for lang, count in sorted(totals.items(), key=lambda x: x[1], reverse=True)
    }


def format_date_range(commits_list):
    if not commits_list:
        return "No Commit Dates"
    dates = pd.to_datetime(
        [c["commitdata"] for c in commits_list if c.get("commitdata")]
    ).dropna()
    if dates.empty:
        return "No Commit Dates"
    start_str = dates.min().strftime("%b %d, %Y")
    end_str = dates.max().strftime("%b %d, %Y")
    if start_str == end_str:
        return start_str
    return f"{start_str} – {end_str}"


def build_repo_summary_rows(commits_list):
    """Builds compact repository breakdown rows from commitLog records."""
    if not commits_list:
        return [["Repository", "Commits", "Net LOC"]]

    df = pd.DataFrame(commits_list)
    df["repository"] = df["repository"].fillna("Unknown Repo")
    df["addline"] = pd.to_numeric(df["addline"], errors="coerce").fillna(0)
    df["deletline"] = pd.to_numeric(df["deletline"], errors="coerce").fillna(0)
    df["net_loc"] = df["addline"] - df["deletline"]

    grouped = (
        df.groupby("repository", as_index=False)
        .agg(commits=("commitSha", "count"), net_loc=("net_loc", "sum"))
        .sort_values("commits", ascending=False)
        .head(5)
    )

    rows = [["Repository", "Commits", "Net LOC"]]
    for _, row in grouped.iterrows():
        repo_name = str(row["repository"]).split("/")[-1][:22]
        net_val = int(row["net_loc"])
        net_str = f"+{net_val:,}" if net_val >= 0 else f"{net_val:,}"
        rows.append([repo_name, str(int(row["commits"])), net_str])
    return rows


def make_language_chart(lang_pct, out_path="_lang_chart.png"):
    if not lang_pct:
        lang_pct = {"No Data": 100.0}

    top_items = list(lang_pct.items())[:4]
    labels = [k for k, _ in top_items][::-1]
    values = [v for _, v in top_items][::-1]
    palette = ["#2563eb", "#10b981", "#f59e0b", "#64748b"][: len(labels)]

    fig, ax = plt.subplots(figsize=(4.6, 2.5), dpi=220)
    bars = ax.barh(labels, values, color=palette[::-1], height=0.52)
    max_val = max(values) if values else 100
    ax.set_xlim(0, max_val * 1.28 + 4)
    ax.set_xlabel("Share of Repo Bytes (%)", fontsize=8, color="#475569")
    ax.set_title(
        "Language Mix (GitHub Bytes)",
        fontsize=10,
        fontweight="bold",
        color="#0f172a",
        loc="left",
    )
    ax.tick_params(axis="both", labelsize=8, colors="#334155")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="x", linestyle="--", alpha=0.35)

    for bar, val in zip(bars, values):
        ax.text(
            bar.get_width() + (max_val * 0.02),
            bar.get_y() + bar.get_height() / 2,
            f"{val:.2f}%",
            va="center",
            fontsize=8,
            fontweight="bold",
            color="#1e293b",
        )

    plt.tight_layout()
    plt.savefig(out_path, dpi=220)
    plt.close(fig)


def make_growth_chart(commits_list, out_path="_growth_chart.png"):
    fig, ax = plt.subplots(figsize=(8.6, 3.1), dpi=220)

    if not commits_list:
        ax.text(
            0.5,
            0.5,
            "No commit history available",
            ha="center",
            va="center",
            color="#64748b",
        )
        ax.set_axis_off()
        plt.tight_layout()
        plt.savefig(out_path, dpi=220)
        plt.close(fig)
        return

    df = pd.DataFrame(commits_list)
    df["commit_dt"] = pd.to_datetime(df["commitdata"])
    df["addline"] = pd.to_numeric(df["addline"], errors="coerce").fillna(0)
    df["deletline"] = pd.to_numeric(df["deletline"], errors="coerce").fillna(0)

    daily = (
        df.groupby(df["commit_dt"].dt.normalize(), as_index=False)[
            ["addline", "deletline"]
        ]
        .sum()
        .sort_values("commit_dt")
    )

    x_dates = daily["commit_dt"].tolist()
    added = daily["addline"].tolist()
    deleted = daily["deletline"].tolist()

    ax.plot(
        x_dates,
        added,
        color="#16a34a",
        linewidth=2,
        marker="o",
        markersize=3,
        label="Lines Added",
    )
    ax.plot(
        x_dates,
        deleted,
        color="#dc2626",
        linewidth=1.8,
        marker="o",
        markersize=3,
        label="Lines Deleted",
    )
    ax.fill_between(x_dates, added, color="#16a34a", alpha=0.08)
    ax.fill_between(x_dates, deleted, color="#dc2626", alpha=0.08)

    ax.set_title(
        "Lines of Code Growth",
        fontsize=10.5,
        fontweight="bold",
        color="#0f172a",
        loc="left",
        pad=22,
    )
    ax.set_ylabel("Lines", fontsize=8.5, color="#475569")
    max_y = max(added + deleted + [50])
    ax.set_ylim(0, max_y * 1.2)

    # Fixed 5-day interval ticks across the date axis
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=5))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))

    ax.tick_params(axis="x", labelsize=8, colors="#334155", pad=5)
    ax.tick_params(axis="y", labelsize=8, colors="#334155")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(axis="y", linestyle="--", alpha=0.35)

    # Place legend cleanly above the chart area so high peaks never overlap it
    ax.legend(
        frameon=False,
        fontsize=8.5,
        loc="lower left",
        bbox_to_anchor=(0.0, 1.01),
        ncol=2,
    )

    plt.subplots_adjust(left=0.08, right=0.98, top=0.80, bottom=0.18)
    plt.savefig(out_path, dpi=220)
    plt.close(fig)


def generate_user_group_pdf(
    user_id, group_id, output_pdf="analytics_report.pdf", fetch_live_langs=True
):
    profile = userProfile.objects.select_related("user").get(user_id=user_id)
    group = projectGroup.objects.get(id=group_id)

    projects = Project.objects.filter(user=profile, group=group)
    repo_slugs = [
        slug for slug in (extract_repo_slug(p.projetUrl) for p in projects) if slug
    ]

    commits_qs = commitLog.objects.filter(user=profile)
    if repo_slugs:
        commits_qs = commits_qs.filter(repository__in=repo_slugs)

    commits_list = list(
        commits_qs.order_by("commitdata").values(
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
            "syncedAt",
        )
    )

    processed = process_commit_data(commits_list)
    summary = processed["summary"]
    lang_pct = fetch_language_percentages(repo_slugs) if fetch_live_langs else {}
    date_range_str = format_date_range(commits_list)

    lang_img = f"_lang_{user_id}_{group_id}.png"
    growth_img = f"_growth_{user_id}_{group_id}.png"
    make_language_chart(lang_pct, lang_img)
    make_growth_chart(commits_list, growth_img)

    doc = SimpleDocTemplate(
        output_pdf,
        pagesize=A4,
        leftMargin=36,
        rightMargin=36,
        topMargin=34,
        bottomMargin=42,
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "Title",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontSize=9.5,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=14,
    )
    section_style = ParagraphStyle(
        "Section",
        parent=styles["Heading2"],
        fontSize=11.5,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=8,
        spaceAfter=6,
    )

    raw_member_name = profile.user.get_full_name() or profile.user.username
    member_title = format_display_title(raw_member_name)
    group_title = format_display_title(group.groupName)

    net_loc = int(summary["total_added"]) - int(summary["total_deleted"])
    net_loc_str = f"+{net_loc:,} Net LOC" if net_loc >= 0 else f"{net_loc:,} Net LOC"

    story = [
        Paragraph("Repository & Code Analytics Report", title_style),
        Paragraph(
            f"Member: {member_title} • Group: {group_title} ({group.groupCode}) • Period: {date_range_str}",
            subtitle_style,
        ),
    ]

    kpi_table = Table(
        [
            [
                "Commit Size Spread (IQR)",
                "Total Lines Added",
                "Net Code & Commits",
            ],
            [
                str(summary["iqr"]),
                f"+{summary['total_added']:,} LOC",
                f"{summary['total_commits']} Commits",
            ],
            [
                f"50% between Q1 ({summary['q1']}) & Q3 ({summary['q3']}) • Outliers: {summary['iqr_outliers']}",
                f"Avg Total/Commit: {summary['average_lines']}",
                f"{net_loc_str} (Del: {summary['total_deleted']:,})",
            ],
        ],
        colWidths=[184, 169, 169],
    )
    kpi_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f172a")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 8.5),
                ("BACKGROUND", (0, 1), (-1, 1), colors.HexColor("#f8fafc")),
                ("TEXTCOLOR", (0, 1), (-1, 1), colors.HexColor("#0f172a")),
                ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
                ("FONTSIZE", (0, 1), (-1, 1), 13.5),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#f1f5f9")),
                ("TEXTCOLOR", (0, 2), (-1, 2), colors.HexColor("#475569")),
                ("FONTSIZE", (0, 2), (-1, 2), 8),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("GRID", (0, 0), (-1, -1), 0.6, colors.HexColor("#cbd5e1")),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(kpi_table)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Language Mix & Repository Activity", section_style))
    repo_rows = build_repo_summary_rows(commits_list)
    repo_table = Table(repo_rows, colWidths=[112, 48, 55])
    repo_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1e293b")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f8fafc")],
                ),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
                ("ALIGN", (1, 0), (-1, -1), "RIGHT"),
                ("PADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    mid_row = Table(
        [[Image(lang_img, width=295, height=165), repo_table]],
        colWidths=[302, 220],
    )
    mid_row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
    story.append(mid_row)
    story.append(Spacer(1, 14))

    story.append(Paragraph("Code Growth Trend", section_style))
    story.append(Image(growth_img, width=522, height=188))

    doc.build(story)

    for temp_file in (lang_img, growth_img):
        if os.path.exists(temp_file):
            os.remove(temp_file)

    return output_pdf