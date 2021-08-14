#!/usr/bin/env python3

import shutil
import subprocess
from pathlib import Path

word_sizes = (
    8, 12, 16, 24,
    32, 48, 64, 96,
    128, 192, 256, 273
)


def directories():
    for thing in Path().glob('*'):
        if thing.is_dir() and not thing.name.startswith('.'):
            if thing.name != 'venv':
                yield thing


def removeArchives():
    for thing in Path().glob('*'):
        if thing.is_file() and thing.name.endswith('.7z'):
            print(f'Removing file {thing.name}')
            thing.unlink()


def compress():
    removeArchives()
    _7z_path = shutil.which('7z')
    info = {}
    if _7z_path:
        for w_size in word_sizes:
            for directory in directories():
                cmd = (
                    _7z_path,
                    'a',
                    '-mx9',
                    f'-mfb{w_size}',
                    f'{directory}.7z',
                    directory.name
                )
                subprocess.run(cmd)

            total_size = 0

            for archive in Path().glob('*'):
                if archive.is_file() and archive.name.endswith('.7z'):
                    archive_size = 0
                    archive_size = archive.stat().st_size
                    total_size += archive_size

            info[w_size] = total_size
            total_size = 0
            removeArchives()

        sizes = []

        for wsize, total in info:
            sizes.append(total)

        sizes = tuple(sizes)
        smallest = min(sizes)

        for wsize in info:
            if info[wsize] == smallest:
                print(f'Best word size: {info[wsize]}')
                break


if __name__ == '__main__':
    compress()
