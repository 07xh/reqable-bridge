#!/usr/bin/env python3
"""Disable the Reqable receiver's 4-second whole-page refresh safely.

Applies a minimal change to a matching FastAPI server.py. Preserves the
SQLite database and HAR endpoints. Makes a timestamped backup before writing.
"""

import argparse
import ast
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone

MARKER = '<meta http-equiv="refresh" content="4">'
TITLE = '<h2>Reqable 上报记录</h2>'
REPLACEMENT_TITLE = TITLE + '<p><a href="/">手动刷新列表</a> · 空闲时不自动刷新</p>'
SERVICE = 'reqable-receiver'
NAMES = {'server.py', 'reqable_receiver.py', 'server.py.new'}


def change_source(source: str) -> str:
    if MARKER not in source:
        raise ValueError('没有找到4秒整页刷新标记；文件可能已修复或不是目标版本')
    if source.count(MARKER) != 1:
        raise ValueError('刷新标记出现多次，停止以避免误修改')
    if TITLE not in source:
        raise ValueError('不是预期的 Reqable 管理页面，停止修改')
    result = source.replace(MARKER, '').replace(TITLE, REPLACEMENT_TITLE, 1)
    ast.parse(result)
    return result


def service_info() -> tuple[str, str]:
    try:
        wd = subprocess.run(['systemctl', 'show', SERVICE, '-p', 'WorkingDirectory', '--value'],
                            text=True, capture_output=True, timeout=5).stdout.strip()
        unit = subprocess.run(['systemctl', 'cat', SERVICE],
                              text=True, capture_output=True, timeout=5).stdout
        return wd, unit
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return '', ''


def candidates() -> list[Path]:
    wd, unit = service_info()
    dirs = [Path.cwd()]
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        import pwd
        try:
            dirs.append(Path(pwd.getpwnam(sudo_user).pw_dir))
        except KeyError:
            pass
    dirs += [Path.home(), Path('/opt/reqable-bridge'), Path('/opt/reqable-receiver'),
             Path('/srv/reqable-bridge'), Path('/srv/reqable-receiver')]
    if wd.startswith('/'):
        dirs.insert(0, Path(wd))
    for path in re.findall(r'(/[A-Za-z0-9_./-]+\.(?:py|new))\b', unit):
        p = Path(path)
        dirs.insert(0, p.parent)
    out = []
    for folder in dirs:
        for location in (folder, folder / 'reqable-bridge', folder / 'reqable-receiver'):
            for name in NAMES:
                p = location / name
                if p.is_file() and p.resolve() not in out:
                    out.append(p.resolve())
    return out


def active_service() -> bool:
    try:
        r = subprocess.run(['systemctl', 'is-active', '--quiet', SERVICE], timeout=5)
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--file', type=Path, help='指定当前运行的 server.py 文件')
    parser.add_argument('--no-restart', action='store_true', help='仅修改文件，不重启 systemd 服务')
    args = parser.parse_args()
    paths = [args.file.resolve()] if args.file else candidates()
    matches = []
    already_patched = []
    for path in paths:
        try:
            data = path.read_text(encoding='utf-8')
        except (OSError, UnicodeError):
            continue
        if MARKER in data and TITLE in data:
            matches.append((path, data))
        elif REPLACEMENT_TITLE in data:
            already_patched.append(path)
    if not matches:
        if len(already_patched) == 1:
            print(f'无需修改：{already_patched[0]} 已取消整页刷新')
            return 0
        print('未找到对应的 server.py，未修改任何文件。', file=sys.stderr)
        print('请查看: sudo systemctl cat reqable-receiver', file=sys.stderr)
        print('然后使用: sudo python3 fix_dashboard_refresh.py --file /实际路径/server.py', file=sys.stderr)
        return 1
    if len(matches) != 1:
        print('发现多个旧版文件，为避免修改错误服务而停止。请用 --file 指定：', file=sys.stderr)
        for path, _ in matches:
            print(f'  {path}', file=sys.stderr)
        return 1
    path, source = matches[0]
    try:
        updated = change_source(source)
    except (ValueError, SyntaxError) as exc:
        print(f'校验失败：{exc}', file=sys.stderr)
        return 1
    stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    backup = path.with_name(f'{path.name}.bak-{stamp}')
    if backup.exists():
        print(f'备份文件已存在：{backup}，停止', file=sys.stderr)
        return 1
    shutil.copy2(path, backup)
    tmp = path.with_name(f'.{path.name}.new-{os.getpid()}')
    try:
        tmp.write_text(updated, encoding='utf-8')
        shutil.copymode(path, tmp)
        os.replace(tmp, path)
        if not args.no_restart and active_service():
            result = subprocess.run(['systemctl', 'restart', SERVICE], timeout=25)
            if result.returncode != 0 or not active_service():
                shutil.copy2(backup, path)
                subprocess.run(['systemctl', 'restart', SERVICE], timeout=25)
                raise RuntimeError('重启失败，已恢复原文件并尝试恢复服务')
            print(f'{SERVICE} 已重启且运行中')
        else:
            print('没有重启服务（服务未运行或指定了 --no-restart）')
    except Exception as exc:
        if tmp.exists():
            tmp.unlink()
        print(f'部署失败：{exc}；备份：{backup}', file=sys.stderr)
        return 1
    print(f'修复成功：{path}')
    print(f'备份位置：{backup}')
    print('现在刷新网页一次，之后不会再每4秒重载；可以点“手动刷新列表”。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
