#!/usr/bin/env python3
"""
orcid_pub_sync.py
=================
从 ORCID 同步出版物列表，查询 Crossref 补全元数据，
将作者 "S. Liu" / "Shuai Liu" 自动加粗，
并支持直接替换 index.md 中的 publications 部分。

不在 ORCID 上的中文文章已内置在 EXTRA_PUBS 中，会自动保留。

用法
----
    # 仅生成 publicationlist.md + publications.bib
    python orcid_pub_sync.py --orcid 0000-0002-6256-6208 --outdir ./pubs

    # 同时更新 index.md 中的 publications Markdown 区块
    python orcid_pub_sync.py --orcid 0000-0002-6256-6208 --index ./index.md

    # 全部都要
    python orcid_pub_sync.py --orcid 0000-0002-6256-6208 --outdir ./pubs --index ./index.md

依赖
----
    pip install requests

作者
----
    S.Liu 工作室
"""

import argparse
import json
import os
import re
import sys
import time
from collections import OrderedDict
from typing import Any

import requests

# ---------------------------------------------------------------------------
# 配置
# ---------------------------------------------------------------------------
ORCID_API = "https://pub.orcid.org/v3.0/{orcid}/works"
CROSSREF_API = "https://api.crossref.org/works/{doi}"
USER_AGENT = "orcid-pub-sync/1.0 (mailto:shliu@stu.xmu.edu.cn)"
REQUEST_DELAY = 1.0          # 秒，防止 Crossref 限流
TIMEOUT = 30

# 不在 ORCID 上的文章（中文期刊等），每次同步自动保留
EXTRA_PUBS = [
    {
        "year": "2018",
        "authors": ["L. Chen", "**S. Liu**", "M. Li", "J. Su", "J. Yan", "B. Mao"],
        "title": "An Investigation on the Structure of Au(111)/Imidazolium-Based Ionic Liquid Interface: Effect of Alkyl Side Chain Length",
        "journal": "J. Electrochem.",
        "journal_year": "2018",
        "volume": "24(05)",
        "page": "511–516",
        "doi": "10.13208/j.electrochem.180148",
        "url": "http://electrochem.xmu.edu.cn/CN/10.13208/j.electrochem.180148",
    },
    {
        "year": "2018",
        "authors": ["Z. Li", "H. Deng", "Z. Gong", "**S. Liu**", "Y. Yang"],
        "title": "Washing efficiency of Cd from contaminated Lou soil by saponin and low-molecular-weight organic acid",
        "journal": "J. Northwest A & F Univ. (Nat. Sci. Ed.)",
        "journal_year": "2018",
        "volume": "05",
        "page": "85–93",
        "doi": "10.13207/j.cnki.jnwafu.2018.05.012",
        "url": "http://doi.org/10.13207/j.cnki.jnwafu.2018.05.012",
    },
    {
        "year": "2016",
        "authors": ["**S. Liu**", "H. Yan", "Z. Li", "Y. Yang", "H. Deng"],
        "title": "Study on the leaching remediation of phenol from contaminated Lou soil by two biosurfactants",
        "journal": "Environ. Pollut. Control",
        "journal_year": "2016",
        "volume": "38(04)",
        "page": "70–77",
        "doi": "10.15985/j.cnki.1001-3865.2016.04.014",
        "url": "http://doi.org/10.15985/j.cnki.1001-3865.2016.04.014",
    },
]

# 用于匹配 "自己" 的正则（大小写不敏感）
SELF_PATTERNS = [
    re.compile(r"\bShuai\s+Liu\b", re.I),
    re.compile(r"\bS\.\s*Liu\b", re.I),
    re.compile(r"\bLiu,\s*S\.\b", re.I),
    re.compile(r"\bLiu,\s*Shuai\b", re.I),
]


def is_self(name: str) -> bool:
    """判断作者名是否是自己。"""
    for pat in SELF_PATTERNS:
        if pat.search(name):
            return True
    return False


def bold_self(name: str) -> str:
    """将作者名中的自己加粗（保持原有格式）。"""
    for pat in SELF_PATTERNS:
        if pat.search(name):
            return f"**{name}**"
    return name


# ---------------------------------------------------------------------------
# ORCID / Crossref 拉取
# ---------------------------------------------------------------------------
def fetch_orcid_works(orcid: str) -> list[dict[str, Any]]:
    """从 ORCID 公开 API 获取作品列表。"""
    url = ORCID_API.format(orcid=orcid)
    headers = {
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }
    resp = requests.get(url, headers=headers, timeout=TIMEOUT)
    resp.raise_for_status()
    data = resp.json()

    articles = []
    for work in data.get("group", []):
        summary = (work.get("work-summary") or [{}])[0]
        if not summary:
            continue

        title = summary.get("title", {}).get("title", {}).get("value", "")
        journal = summary.get("journal-title", {}).get("value", "")
        pub_date = summary.get("publication-date", {})
        year = pub_date.get("year", {}).get("value", "")

        doi = ""
        for ext_id in summary.get("external-ids", {}).get("external-id", []):
            if ext_id.get("external-id-type") == "doi":
                doi = ext_id.get("external-id-value", "")
                break

        authors = []
        for c in work.get("contributors", {}).get("contributor", []):
            name = c.get("credit-name", {}).get("value", "")
            if name:
                authors.append(name)
        if not authors:
            cn = summary.get("credit-name", {}).get("value", "")
            if cn:
                authors.append(cn)

        articles.append({
            "title": title,
            "journal": journal,
            "year": year,
            "doi": doi,
            "authors": authors,
        })

    print(f"[ORCID] 获取到 {len(articles)} 条作品记录")
    return articles


def fetch_crossref(doi: str) -> dict[str, Any] | None:
    """通过 Crossref API 补全单条 DOI 的元数据。"""
    url = CROSSREF_API.format(doi=doi)
    headers = {"User-Agent": USER_AGENT}
    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()
        msg = resp.json().get("message", {})
        return {
            "title": msg.get("title", [""])[0] if msg.get("title") else "",
            "authors": msg.get("author", []),
            "journal": msg.get("container-title", [""])[0] if msg.get("container-title") else "",
            "year": str(
                msg.get("published-print", {}).get("date-parts", [[""]])[0][0]
                or msg.get("published-online", {}).get("date-parts", [[""]])[0][0]
                or ""
            ),
            "volume": msg.get("volume", ""),
            "issue": msg.get("issue", ""),
            "page": msg.get("page", ""),
            "article_number": msg.get("article-number", ""),
        }
    except Exception as exc:
        print(f"  [WARN] Crossref 查询失败 DOI={doi}: {exc}")
        return None


# ---------------------------------------------------------------------------
# 作者格式化
# ---------------------------------------------------------------------------
def short_initials(given: str, family: str) -> str:
    """将 given name 转成首字母缩写，如 'Shuai' -> 'S.'。"""
    parts = given.replace("-", " ").split()
    initials = ".".join(p[0].upper() for p in parts if p)
    return f"{initials}. {family}"


def format_author(author: dict[str, str]) -> str:
    """格式化单条作者为 'X.-Y. Zhang' 或 'S. Liu'。"""
    given = author.get("given", "").strip()
    family = author.get("family", "").strip()
    if not given or not family:
        return author.get("name", "")
    name = short_initials(given, family)
    return bold_self(name)


def authors_from_orcid_names(names: list[str]) -> list[str]:
    """将 ORCID 返回的纯字符串作者列表做加粗处理。"""
    out = []
    for n in names:
        n = n.strip()
        if not n:
            continue
        if " " in n and "," not in n:
            parts = n.rsplit(" ", 1)
            initials = ".".join(p[0].upper() for p in parts[0].split("-") if p)
            short = f"{initials}. {parts[1]}"
            out.append(bold_self(short))
        else:
            out.append(bold_self(n))
    return out


# ---------------------------------------------------------------------------
# 数据补全主流程
# ---------------------------------------------------------------------------
def enrich_entries(orcid_entries: list[dict], delay: float, skip_crossref: bool) -> list[dict[str, Any]]:
    enriched = []
    for item in orcid_entries:
        doi = item.get("doi", "")
        display_authors = authors_from_orcid_names(item.get("authors", []))

        if doi and not skip_crossref:
            print(f"[Crossref] 查询 {doi} ...")
            cr = fetch_crossref(doi)
            time.sleep(delay)
            if cr:
                if cr.get("authors"):
                    display_authors = [format_author(a) for a in cr["authors"]]
                enriched.append({
                    "title": cr.get("title") or item.get("title", ""),
                    "journal": cr.get("journal") or item.get("journal", ""),
                    "year": cr.get("year") or item.get("year", ""),
                    "journal_year": cr.get("year") or item.get("year", ""),
                    "volume": cr.get("volume", ""),
                    "issue": cr.get("issue", ""),
                    "page": cr.get("page", ""),
                    "doi": doi,
                    "_display_authors": display_authors,
                })
                continue

        # 回退到 ORCID 原始数据
        enriched.append({
            "title": item.get("title", ""),
            "journal": item.get("journal", ""),
            "year": item.get("year", ""),
            "journal_year": item.get("year", ""),
            "volume": "",
            "issue": "",
            "page": "",
            "doi": doi,
            "_display_authors": display_authors,
        })

    # 合并不在 ORCID 上的手动文章
    for extra in EXTRA_PUBS:
        enriched.append({
            **extra,
            "_display_authors": extra["authors"],
        })
    return enriched


# ---------------------------------------------------------------------------
# Markdown 输出
# ---------------------------------------------------------------------------
def build_markdown(entries: list[dict[str, Any]], out_path: str) -> None:
    """生成 Markdown 文件。"""
    groups: OrderedDict[str, list[str]] = OrderedDict()
    for e in entries:
        y = e.get("year", "????")
        groups.setdefault(y, [])

        author_str = ", ".join(e.get("_display_authors", []))
        journal = e.get("journal", "")
        jyear = e.get("journal_year", y)
        volume = e.get("volume", "")
        page = e.get("page", "")
        doi = e.get("doi", "")
        url = e.get("url", "")
        link = url if url else (f"https://doi.org/{doi.lower()}" if doi else "")

        line = f'{author_str}. *{journal}* **{jyear}**, *{volume}*, {page}.'
        if doi and link:
            line += f' DOI: [{doi}]({link})'
        groups[y].append(line)

    sorted_years = sorted(groups.keys(), key=lambda x: int(x) if x.isdigit() else 0, reverse=True)

    lines = ["## Selected Publications", "", "<!-- Auto-generated by orcid_pub_sync.py -->", ""]
    for year in sorted_years:
        lines.append(f"`{year}`")
        lines.append("")
        for entry in groups[year]:
            lines.append(entry)
            lines.append("")

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[MD] 已保存 {out_path}")


# ---------------------------------------------------------------------------
# BibTeX 输出
# ---------------------------------------------------------------------------
def make_bibkey(authors: list[str], year: str, idx: int) -> str:
    """生成 BibTeX cite key，如 'Liu2025_1'。"""
    first = authors[0].replace("**", "").replace("†", "").strip()
    last_name = first.split()[-1] if " " in first else first
    return f"{last_name}{year}_{idx}"


def build_bibtex(entries: list[dict[str, Any]], out_path: str) -> None:
    """生成 BibTeX 文件。"""
    bib_lines = []
    for idx, e in enumerate(entries, 1):
        year = e.get("year", "????")
        authors = e.get("_display_authors", [])
        key = make_bibkey(authors, year, idx)

        clean_authors = [a.replace("**", "").replace("†", "").strip() for a in authors]
        author_bib = " and ".join(clean_authors)

        title = e.get("title", "")
        journal = e.get("journal", "")
        volume = e.get("volume", "")
        issue = e.get("issue", "")
        page = e.get("page", "")
        doi = e.get("doi", "")

        entry_str = f"@article{{{key},\n"
        entry_str += f"  title = {{{title}}},\n"
        entry_str += f"  author = {{{author_bib}}},\n"
        entry_str += f"  journal = {{{journal}}},\n"
        entry_str += f"  year = {{{year}}},\n"
        if volume:
            entry_str += f"  volume = {{{volume}}},\n"
        if issue:
            entry_str += f"  number = {{{issue}}},\n"
        if page:
            entry_str += f"  pages = {{{page}}},\n"
        if doi:
            entry_str += f"  doi = {{{doi}}},\n"
        entry_str += "}\n"
        bib_lines.append(entry_str)

    with open(out_path, "w", encoding="utf-8") as f:
        f.write("\n".join(bib_lines))
    print(f"[BIB] 已保存 {out_path}")


# ---------------------------------------------------------------------------
# index.md 出版物区块替换（纯 Markdown）
# ---------------------------------------------------------------------------
def build_index_markdown(entries: list[dict[str, Any]]) -> str:
    """生成 index.md 中 `## Selected Publications` 的 Markdown 内容。"""
    groups: OrderedDict[str, list[str]] = OrderedDict()
    for e in entries:
        y = e.get("year", "????")
        groups.setdefault(y, [])

        author_str = ", ".join(e.get("_display_authors", []))
        journal = e.get("journal", "")
        jyear = e.get("journal_year", y)
        volume = e.get("volume", "")
        page = e.get("page", "")
        doi = e.get("doi", "")
        url = e.get("url", "")
        link = url if url else (f"https://doi.org/{doi.lower()}" if doi else "")

        line = f'{author_str}. *{journal}* **{jyear}**, *{volume}*, {page}.'
        if doi and link:
            line += f' DOI: [{doi}]({link})'
        groups[y].append(line)

    sorted_years = sorted(groups.keys(), key=lambda x: int(x) if x.isdigit() else 0, reverse=True)

    lines = ["## Selected Publications", ""]
    for year in sorted_years:
        lines.append(f"`{year}`")
        lines.append("")
        for entry in groups[year]:
            lines.append(entry)
            lines.append("")
    return "\n".join(lines)


def update_index_md(index_path: str, entries: list[dict[str, Any]]) -> None:
    """读取 index.md，替换 `## Selected Publications` 与下一个 `## ` 之间的区块。"""
    with open(index_path, "r", encoding="utf-8") as f:
        content = f.read()

    pattern = re.compile(
        r'(## Selected Publications\n\n)'
        r'.*?'
        r'(?=\n## |\Z)',
        re.DOTALL
    )

    if not pattern.search(content):
        print(f"[WARN] 未在 {index_path} 中找到 `## Selected Publications` 区块，跳过替换")
        return

    new_section = build_index_markdown(entries) + "\n"

    new_content = pattern.sub(r'\1' + new_section.split('\n\n', 1)[1], content)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"[INDEX] 已更新 {index_path} 中的 `## Selected Publications` 区块")


# ---------------------------------------------------------------------------
# 主入口
# ---------------------------------------------------------------------------
def main() -> int:
    parser = argparse.ArgumentParser(description="从 ORCID 同步出版物并生成 MD / BibTeX / 更新 index.md")
    parser.add_argument("--orcid", required=True, help="ORCID ID，如 0000-0002-6256-6208")
    parser.add_argument("--outdir", default=".", help="输出目录（默认当前目录）")
    parser.add_argument("--index", default="", help="index.md 路径，提供则直接替换其中的 publications 区块")
    parser.add_argument("--delay", type=float, default=REQUEST_DELAY, help="Crossref 请求间隔（秒）")
    parser.add_argument("--skip-crossref", action="store_true", help="跳过 Crossref，仅用 ORCID 数据")
    args = parser.parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    # 1. 获取 ORCID 数据
    orcid_entries = fetch_orcid_works(args.orcid)

    # 2. 补全 Crossref 元数据 + 合并手动文章
    enriched = enrich_entries(orcid_entries, args.delay, args.skip_crossref)

    # 3. 生成文件
    md_path = os.path.join(args.outdir, "publicationlist.md")
    bib_path = os.path.join(args.outdir, "publications.bib")
    build_markdown(enriched, md_path)
    build_bibtex(enriched, bib_path)

    # 4. 可选：更新 index.md
    if args.index:
        if not os.path.isfile(args.index):
            print(f"[ERROR] 找不到 {args.index}")
            return 1
        update_index_md(args.index, enriched)

    print(f"\n✅ 全部完成！共 {len(enriched)} 篇文章（ORCID {len(orcid_entries)} 条 + 手动 {len(EXTRA_PUBS)} 条）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
