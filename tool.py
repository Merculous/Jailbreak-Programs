#!/usr/bin/env python3

import shutil
import subprocess
import sys
from pathlib import Path

_7z_path = shutil.which('7z')

if not _7z_path:
    sys.exit('7z binary could not be found!')


values = {
    'wordsize': (
        8, 12, 16, 24,
        32, 48, 64, 96,
        128, 192, 256, 273
    ),
    'dictsize': (
        '64k', '1m', '2m', '3m', '4m',
        '6m', '8m', '12m', '16m', '24m',
        '32m', '48m', '64m', '96m', '128m',
        '192m', '256m', '384m', '512m', '768m',
        '1024m', '1536m'
    ),
    'blocksize': (
        'off', 'on', '1m', '2m', '3m',
        '4m', '6m', '8m', '12m', '16m',
        '32m', '64m', '128m', '256m', '512m',
        '1g', '2g', '4g', '8g', '16g',
        '32g', '64g'
    )
}


def directories():
    """
    Yield all directories in the current working directory. Directories that
    contain a '.' at the beginning are ignored, and the directory 'venv' is also ignored.
    Results yielded are Path objects.
    """
    for thing in Path().glob('*'):
        if thing.is_dir() and not thing.name.startswith('.'):
            if thing.name != 'venv':
                yield thing


def removeArchives():
    """
    Remove all archives/files that end with '.7z' within the current working directory.
    """
    for thing in Path().glob('*'):
        if thing.is_file() and thing.name.endswith('.7z'):
            thing.unlink()


def getTotalSizeOfArchives():
    """
    Return the sum of all '.7z' files inside the current working directory.
    """
    total_size = 0
    for archive in Path().glob('*'):
        if archive.is_file() and archive.name.endswith('.7z'):
            archive_size = archive.stat().st_size
            total_size += archive_size

    return total_size


def getLargestDirectorySize():
    """
    Return the largest directory size from 'du'
    """
    sizes = {}

    # TODO Make this all python code

    directory_sizes = subprocess.run(
        'du -sm */',  # 'm' rounds up everything to 1mb+
        capture_output=True,
        universal_newlines=True,
        shell=True  # Need a better way of doing this
    ).stdout.splitlines()

    for size in directory_sizes:
        size = size.split()

        if 'venv' in size[1]:
            continue

        sizes[size[1][:-1]] = int(size[0])

    largest = max(sizes, key=sizes.get)
    return sizes[largest]


def minimumLargestDictSize():
    """
    Return the largest dictionary size given the largest directory size
    """
    largest = getLargestDirectorySize()
    sizes = (s for s in values['dictsize'])

    # Seems like anything under 1mb will be 1 anyway (from du -sm)

    for size in sizes:
        if 'm' in size:
            size = int(size[:-1])
            if size > largest:
                return size


def smallestSize(data):
    """
    Return the smallest size when testing is done.
    """
    smallest = min(data, key=data.get)
    return (smallest, data[smallest])


def runCMD(args):
    """
    Run 7z command for every directory, given the passed arguments.
    """
    dirs = directories()

    for directory in dirs:
        cmd = (
            _7z_path,
            'a',
            '-mx9',
            args,
            '--',
            f'{directory.name}.7z',
            directory.name
        )
        subprocess.run(cmd, stdout=subprocess.DEVNULL)


def testAllDictSizes():
    """
    Compress all directories within the current working directory.
    This function uses 'smart' dictionary sizing to get rid of using
    larger dictionary sizes that will not affect compression or will
    give the same overall size as the minimum largest dictionary size.
    """
    info = {}

    # Using this because even larger sizes than the minimum are redundant
    largestDictSize = minimumLargestDictSize()

    for size in values['dictsize']:
        if int(size[:-1]) > largestDictSize:
            break

        print(f'Dict size: {size}')

        runCMD(f'-md{size}')

        info[size] = getTotalSizeOfArchives()
        removeArchives()

    return info


def testAllWordSizes():
    pass


def testAllBlockSizes():
    pass


def testNumberOfThreads():
    pass


def compress():
    removeArchives()
    dict_best = testAllDictSizes()
    print(f'Best: {smallestSize(dict_best)}')
    # testAllWordSizes()
    # testAllBlockSizes()


def main():
    compress()


if __name__ == '__main__':
    main()
