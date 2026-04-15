"""
patent_fetch.py — Google Patents PDF 下载
=======================================

从 Google Patents 页面提取 PDF 下载链接并下载到本地 inbox-patent 目录。

用法::

    from scholaraio.patent_fetch import download_patent_pdf
    path = download_patent_pdf("https://patents.google.com/patent/US20240176406A1")
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import requests

from scholaraio.log import ui

if TYPE_CHECKING:
    from scholaraio.config import Config

_log = logging.getLogger(__name__)

GOOGLE_PATENTS_HOST = "patents.google.com"
PDF_URL_PATTERN = re.compile(
    r"https?://patentimages\.storage\.googleapis\.com/[^\s\"'<>]+\.pdf"
)


class PatentFetchError(Exception):
    """专利下载异常。"""

    pass


def _resolve_url(id_or_url: str) -> str:
    """将专利 ID 或 URL 解析为完整的 Google Patents URL。"""
    raw = id_or_url.strip()
    if raw.startswith(("http://", "https://")):
        return raw
    # 纯 ID，构造默认 URL
    return f"https://patents.google.com/patent/{raw}"


def _extract_patent_id(url: str) -> str:
    """从 URL 中提取专利 ID（如 US20240176406A1）。"""
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]
    # 期望路径: /patent/<ID>
    if len(path_parts) >= 2 and path_parts[0] == "patent":
        return path_parts[1]
    # 兜底：取最后一段
    if path_parts:
        return path_parts[-1]
    return "unknown"


def extract_pdf_url(
    id_or_url: str,
    *,
    timeout: float = 30.0,
) -> str | None:
    """从 Google Patents 页面提取 PDF 下载链接。

    Args:
        id_or_url: Google Patents 页面 URL 或专利 ID（如 US20240176406A1）。
        timeout: 请求超时（秒）。

    Returns:
        PDF 下载链接，未找到则返回 None。

    Raises:
        PatentFetchError: 页面获取失败。
    """
    url = _resolve_url(id_or_url)

    try:
        _log.info("Fetching patent page: %s", url)
        resp = requests.get(url, timeout=timeout)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        raise PatentFetchError(f"请求超时（{timeout}秒）")
    except requests.exceptions.RequestException as e:
        raise PatentFetchError(f"页面获取失败: {e}")

    html = resp.text
    matches = PDF_URL_PATTERN.findall(html)

    if not matches:
        return None

    # 去重并保持顺序
    seen = set()
    for candidate in matches:
        if candidate not in seen:
            seen.add(candidate)
            _log.info("Found PDF URL: %s", candidate)
            return candidate

    return None


def download_patent_pdf(
    id_or_url: str,
    *,
    output_dir: str | Path = "data/inbox-patent",
    filename: str | None = None,
    timeout: float = 120.0,
    cfg: Config | None = None,
) -> Path | None:
    """从 Google Patents 下载专利 PDF。

    Args:
        id_or_url: Google Patents 页面 URL 或专利 ID（如 US20240176406A1）。
        output_dir: 保存目录（默认 data/inbox-patent）。
        filename: 自定义文件名（不含 .pdf，默认从 URL/ID 提取专利 ID）。
        timeout: 下载超时（秒）。
        cfg: 配置对象（用于解析路径）。

    Returns:
        下载文件的 Path，失败返回 None。

    Example:
        >>> path = download_patent_pdf("US20240176406A1")
        >>> path = download_patent_pdf("https://patents.google.com/patent/US20240176406A1")
    """
    url = _resolve_url(id_or_url)

    # 解析路径
    if cfg is not None:
        output_path = cfg._root / "data" / "inbox-patent"
    else:
        output_path = Path(output_dir)

    output_path.mkdir(parents=True, exist_ok=True)

    # 提取 PDF 链接
    try:
        pdf_url = extract_pdf_url(id_or_url, timeout=30.0)
    except PatentFetchError as e:
        ui(f"错误: {e}")
        return None

    if not pdf_url:
        ui("未在该页面找到 PDF 下载链接")
        return None

    # 文件名
    patent_id = _extract_patent_id(url)
    if filename:
        out_file = output_path / f"{filename}.pdf"
    else:
        out_file = output_path / f"{patent_id}.pdf"

    # 检查是否已存在
    if out_file.exists():
        ui(f"文件已存在: {out_file}")
        return out_file

    # 下载 PDF
    headers = {
        "User-Agent": "ScholarAIO/1.0 (https://github.com/ZimoLiao/scholaraio)"
    }

    try:
        _log.info("Downloading PDF: %s", pdf_url)
        resp = requests.get(pdf_url, headers=headers, timeout=timeout)
        resp.raise_for_status()
        out_file.write_bytes(resp.content)
        ui(f"已下载: {out_file} ({len(resp.content)} bytes)")
        return out_file
    except requests.exceptions.Timeout:
        ui(f"下载超时（{timeout}秒）")
        return None
    except requests.exceptions.RequestException as e:
        ui(f"下载失败: {e}")
        return None
