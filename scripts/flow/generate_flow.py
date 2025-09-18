#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Flow chart generator for TripLog (crawler version)

This script crawls a running UI starting from a base URL, discovers links
within the same origin, and emits a Mermaid (.mmd) flowchart by default.
Optionally, it can output Graphviz DOT and render SVG/PNG if the corresponding
CLI tools are available (`mmdc` for Mermaid or `dot` for Graphviz).

Usage examples:
  python scripts/flow/generate_flow.py --base-url http://127.0.0.1:8000/
  python scripts/flow/generate_flow.py --base-url http://127.0.0.1:8000/ --format svg
  python scripts/flow/generate_flow.py --base-url http://127.0.0.1:8000/ --max-pages 100 \
      --exclude "^/admin|^/static|^/media"

No Python package dependency on graphviz/bs4 is required; we use stdlib
HTMLParser and shell out to `mmdc`/`dot` when available.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Set, Optional
from urllib.parse import urljoin, urlparse, urlunparse
import requests


class _LinkParser(HTMLParser):
    """Minimal HTML parser to extract <title>, <a href>, and anchor text."""

    def __init__(self) -> None:
        super().__init__()
        self.title_parts: List[str] = []
        self.in_title: bool = False
        self.current_anchor_href: Optional[str] = None
        self.current_anchor_text_parts: List[str] = []
        self.links: List[Tuple[str, str]] = []  # (href, text)

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() == "title":
            self.in_title = True
        elif tag.lower() == "a":
            href = None
            for k, v in attrs:
                if k.lower() == "href":
                    href = v
                    break
            self.current_anchor_href = href
            self.current_anchor_text_parts = []

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self.in_title = False
        elif tag.lower() == "a":
            if self.current_anchor_href:
                text = "".join(self.current_anchor_text_parts).strip()
                self.links.append((self.current_anchor_href, text))
            self.current_anchor_href = None
            self.current_anchor_text_parts = []

    def handle_data(self, data: str) -> None:
        if self.in_title:
            self.title_parts.append(data)
        if self.current_anchor_href is not None:
            self.current_anchor_text_parts.append(data)

    @property
    def title(self) -> str:
        t = "".join(self.title_parts).strip()
        return t


def _normalize_url(base: str, href: str) -> Optional[str]:
    if not href:
        return None
    href = href.strip()
    # Ignore anchors, mailto, tel, javascript
    if href.startswith("#") or href.startswith("mailto:") or href.startswith("tel:") or href.lower().startswith("javascript:"):
        return None
    abs_url = urljoin(base, href)
    # Remove fragments
    parts = urlparse(abs_url)
    parts = parts._replace(fragment="")
    return urlunparse(parts)


def crawl(base_url: str, max_pages: int, include_pattern: Optional[str], exclude_pattern: Optional[str]) -> Tuple[Dict[str, str], List[Tuple[str, str, str]]]:
    """BFS crawl within same origin and return (url->title, edges).

    edges are tuples of (src_url, dst_url, anchor_text)
    """
    base = urlparse(base_url)
    origin = (base.scheme, base.netloc)

    include_re = re.compile(include_pattern) if include_pattern else None
    exclude_re = re.compile(exclude_pattern) if exclude_pattern else None

    session = requests.Session()
    headers = {"User-Agent": "TripLogFlowCrawler/1.0"}

    to_visit: deque[str] = deque([base_url])
    visited: Set[str] = set()
    titles: Dict[str, str] = {}
    edges: List[Tuple[str, str, str]] = []

    while to_visit and len(visited) < max_pages:
        url = to_visit.popleft()
        if url in visited:
            continue
        visited.add(url)

        try:
            resp = session.get(url, headers=headers, timeout=10)
        except Exception:
            continue

        if resp.status_code >= 400:
            continue

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type:
            continue

        parser = _LinkParser()
        try:
            parser.feed(resp.text)
        except Exception:
            # Best-effort parsing; skip on fatal HTML errors
            continue

        title = parser.title or urlparse(url).path or url
        titles[url] = title

        for href, text in parser.links:
            nurl = _normalize_url(url, href)
            if not nurl:
                continue
            p = urlparse(nurl)
            if (p.scheme, p.netloc) != origin:
                continue
            path = p.path or "/"
            if exclude_re and exclude_re.search(path):
                continue
            if include_re and not include_re.search(path):
                # If include is specified, only include matching paths
                continue

            edges.append((url, nurl, text))
            if nurl not in visited and nurl not in to_visit:
                to_visit.append(nurl)

    return titles, edges


_UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")


def canonical_path(path: str) -> str:
    """Normalize dynamic path segments to improve node aggregation.

    - Remove trailing slash (except root)
    - Replace UUID-like and purely numeric segments with :id
    """
    if not path:
        return "/"
    if path != "/" and path.endswith("/"):
        path = path[:-1]
    parts = [p for p in path.split("/") if p]
    norm: List[str] = []
    for p in parts:
        if p.isdigit() or _UUID_RE.fullmatch(p):
            norm.append(":id")
        else:
            norm.append(p)
    return "/" + "/".join(norm)


def word_wrap(text: str, width: int) -> str:
    if width <= 0:
        return text
    words = re.findall(r"\S+", text)
    lines: List[str] = []
    cur: List[str] = []
    cur_len = 0
    for w in words:
        add = len(w) + (1 if cur else 0)
        if cur_len + add > width:
            lines.append(" ".join(cur))
            cur = [w]
            cur_len = len(w)
        else:
            cur.append(w)
            cur_len += add
    if cur:
        lines.append(" ".join(cur))
    return "\\n".join(lines)


def dot_id(label: str) -> str:
    """Create a stable DOT node identifier from a label/url."""
    return "n_" + str(abs(hash(label)))


def render_mermaid(nodes: Iterable[str], edges: Iterable[Tuple[str, str, str]]) -> str:
    """Emit Mermaid flowchart with grouping and de-duplicated edges.

    - Left-to-right layout
    - Group by first path segment using subgraph-like sections (Mermaid: subgraph)
    - Merge parallel edges; show up to 3 labels, rest as (+N)
    - Suppress self-loops
    """
    # Build groups and ids
    id_map: Dict[str, str] = {}
    groups: Dict[str, List[str]] = {}
    for label in nodes:
        nid = "n" + str(abs(hash(label)))
        id_map[label] = nid
        path = label.split("\n", 1)[0]
        seg = path.strip("/").split("/", 1)[0] or "root"
        groups.setdefault(seg, []).append(label)

    lines: List[str] = []
    lines.append("flowchart LR")

    # Nodes inside subgraphs
    for seg, labels in sorted(groups.items()):
        lines.append(f"  subgraph {seg}")
        for label in labels:
            nid = id_map[label]
            disp = label.replace("\"", "\\\"")
            if "\n" in disp:
                path_part, title_part = disp.split("\n", 1)
                title_part = word_wrap(title_part, 26)
                disp = path_part + "\\n" + title_part
            lines.append(f"    {nid}[\"{disp}\"]")
        lines.append("  end")

    # Merge edges
    grouped: Dict[Tuple[str, str], Set[str]] = {}
    for src, dst, label in edges:
        s = id_map[src]
        d = id_map[dst]
        if s == d:
            continue
        grouped.setdefault((s, d), set()).add((label or "").strip())

    for (s, d), labels in grouped.items():
        clean = sorted({l for l in labels if l})
        if clean:
            shown = clean[:3]
            extra = len(clean) - len(shown)
            txt = ", ".join(shown)
            if extra > 0:
                txt += f" (+{extra})"
            txt = word_wrap(txt, 24).replace("\"", "\\\"")
            lines.append(f"  {s} -- \"{txt}\" --> {d}")
        else:
            lines.append(f"  {s} --> {d}")

    return "\n".join(lines) + "\n"


def render_dot(nodes: Iterable[str], edges: Iterable[Tuple[str, str, str]]) -> str:
    """Build a DOT string with better readability.

    Improvements:
    - rankdir=LR, increased node separation
    - rounded boxes, subtle colors
    - cluster subgraphs by first path segment
    - deduplicate edges and wrap labels
    """
    lines: List[str] = []
    lines.append("digraph AppFlow {")
    lines.append("  rankdir=LR;")
    lines.append("  nodesep=0.4; ranksep=0.6; pad=0.3;")
    lines.append("  graph [fontname=\"Helvetica\"]; ")
    lines.append("  node [shape=box, style=\"rounded,filled\", fillcolor=\"#FFF8D9\", color=\"#C8B36B\", fontname=\"Helvetica\", fontsize=11]; ")
    lines.append("  edge [color=\"#8A8A8A\", arrowsize=0.7, fontname=\"Helvetica\", fontsize=10]; ")

    id_map: Dict[str, str] = {}
    clusters: Dict[str, List[str]] = {}
    for label in nodes:
        nid = dot_id(label)
        id_map[label] = nid
        # derive group from first path segment
        path = label.split("\n", 1)[0]
        seg = path.strip("/").split("/", 1)[0] or "root"
        clusters.setdefault(seg, []).append(label)

    # Emit clusters
    cluster_index = 0
    for seg, labels in sorted(clusters.items()):
        lines.append(f"  subgraph cluster_{cluster_index} {{")
        lines.append(f"    label=\"/{seg}\";")
        lines.append("    color=\"#E6DFAE\"; fontsize=12; fontname=\"Helvetica\";")
        for label in labels:
            nid = id_map[label]
            # compact label: wrap at 26 chars per line for title part
            if "\n" in label:
                path_part, title_part = label.split("\n", 1)
                disp = path_part + "\\n" + word_wrap(title_part, 26)
            else:
                disp = label
            disp = disp.replace("\"", "\\\"")
            lines.append(f"    {nid} [label=\"{disp}\"];")
        lines.append("  }")
        cluster_index += 1

    # Deduplicate edges (src,dst,label)
    seen_edges: Set[Tuple[str, str, str]] = set()
    for src, dst, elabel in edges:
        s = id_map[src]
        d = id_map[dst]
        lbl = word_wrap(elabel.strip(), 24) if elabel else ""
        key = (s, d, lbl)
        if key in seen_edges:
            continue
        seen_edges.add(key)
        if lbl:
            lines.append(f"  {s} -> {d} [label=\"{lbl}\"];")
        else:
            lines.append(f"  {s} -> {d};")

    lines.append("}")
    return "\n".join(lines) + "\n"


def write_outputs_mermaid(mmd_text: str, outdir: Path, filename: str, fmt: str) -> Path:
    """Write .mmd, and if `mmdc` exists, render to image (svg/png)."""
    outdir.mkdir(parents=True, exist_ok=True)
    mmd_path = outdir / f"{filename}.mmd"
    mmd_path.write_text(mmd_text, encoding="utf-8")

    mmdc_bin = shutil.which("mmdc")  # Mermaid CLI (node @mermaid-js/mermaid-cli)
    if not mmdc_bin:
        return mmd_path

    out_path = outdir / f"{filename}.{fmt}"
    cmd = [mmdc_bin, "-i", str(mmd_path), "-o", str(out_path), "-t", "default"]
    subprocess.run(cmd, check=False)
    return mmd_path


def write_outputs_dot(dot_text: str, outdir: Path, filename: str, fmt: str) -> Path:
    outdir.mkdir(parents=True, exist_ok=True)
    dot_path = outdir / f"{filename}.dot"
    dot_path.write_text(dot_text, encoding="utf-8")

    dot_bin = shutil.which("dot")
    if not dot_bin:
        return dot_path

    out_path = outdir / f"{filename}.{fmt}"
    cmd = [dot_bin, f"-T{fmt}", str(dot_path), "-o", str(out_path)]
    subprocess.run(cmd, check=False)
    return dot_path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Crawl UI and generate TripLog app flow chart (Mermaid by default)")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000/", help="Start URL to crawl (same-origin only)")
    parser.add_argument("--max-pages", type=int, default=60, help="Maximum number of pages to crawl")
    parser.add_argument("--include", default=None, help="Regex to include paths (optional)")
    parser.add_argument("--exclude", default=r"^/(admin|static|media)", help="Regex to exclude paths")
    parser.add_argument("--outdir", default="scripts/flow/out", help="Output directory for generated files")
    parser.add_argument("--filename", default="app_flow", help="Base filename without extension")
    parser.add_argument("--engine", choices=["mermaid", "dot"], default="mermaid", help="Output engine")
    parser.add_argument("--format", choices=["svg", "png"], default="svg", help="Image format when rendering (mermaid: mmdc, dot: graphviz)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    titles, edges = crawl(args.base_url, args.max_pages, args.include, args.exclude)
    # Build nodes list using page titles for labels, but use URLs as identities
    # For readability, show path + title when available
    labeled_nodes: List[str] = []
    url_to_label: Dict[str, str] = {}
    for url, title in titles.items():
        raw_path = urlparse(url).path or "/"
        path = canonical_path(raw_path)
        label = f"{path}\n{title}" if title and title != path else path
        url_to_label[url] = label
        labeled_nodes.append(label)

    # Remap edges to use node labels
    remapped_edges: List[Tuple[str, str, str]] = []
    for src, dst, text in edges:
        if src in url_to_label and dst in url_to_label:
            remapped_edges.append((url_to_label[src], url_to_label[dst], text))

    if args.engine == "mermaid":
        mmd = render_mermaid(labeled_nodes, remapped_edges)
        mmd_path = write_outputs_mermaid(mmd, Path(args.outdir), args.filename, args.format)
        has_mmdc = shutil.which("mmdc") is not None
        if has_mmdc:
            print(f"Wrote MMD: {mmd_path}")
            print(f"Rendered: {Path(args.outdir) / (args.filename + '.' + args.format)}")
        else:
            print(f"Wrote MMD only (install mmdc to render): {mmd_path}")
            print("Install Mermaid CLI: npm i -g @mermaid-js/mermaid-cli")
    else:
        dot_text = render_dot(labeled_nodes, remapped_edges)
        dot_path = write_outputs_dot(dot_text, Path(args.outdir), args.filename, args.format)
        has_dot = shutil.which("dot") is not None
        if has_dot:
            print(f"Wrote DOT: {dot_path}")
            print(f"Rendered: {Path(args.outdir) / (args.filename + '.' + args.format)}")
        else:
            print(f"Wrote DOT only (Graphviz 'dot' not found): {dot_path}")
            print("Install Graphviz to render: brew install graphviz  または  apt-get install graphviz")


if __name__ == "__main__":
    main()


