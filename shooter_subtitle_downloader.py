# -*- coding: utf-8 -*-
import os
import glob
import hashlib
import math
import urllib2
import re

extensions = (".avi", ".mp4", ".mkv", ".mpg", ".mpeg", ".mov", ".rm", ".vob", ".wmv", ".flv", ".3gp")
dir_path = '/var/lib/transmission/Downloads/'


# dir_path = 'D:\\video\\movies\\test'


def get_hash(name):
    hash_val = list()
    with open(name, 'rb') as f:
        e = 4096
        f.seek(0, os.SEEK_END)
        size = f.tell()

        # first 4k
        start = min(size, 4096)
        end = min(start + e, size)
        f.seek(int(start))
        data = f.read(int(end - start))
        digest = hashlib.md5(data).hexdigest()
        hash_val.append(digest)

        # second 4k
        start = math.floor(size / 3 * 2)
        end = min(start + e, size)
        f.seek(int(start))
        data = f.read(int(end - start))
        digest = hashlib.md5(data).hexdigest()
        hash_val.append(digest)

        # third 4k
        start = math.floor(size / 3)
        end = min(start + e, size)
        f.seek(int(start))
        data = f.read(int(end - start))
        digest = hashlib.md5(data).hexdigest()
        hash_val.append(digest)

        # fourth 4k
        start = max(0, size - 8192)
        end = min(start + e, size)
        f.seek(int(start))
        data = f.read(int(end - start))
        digest = hashlib.md5(data).hexdigest()
        hash_val.append(digest)

    return hash_val


def sub_downloader(path):
    hash_val = get_hash(path)
    name = path.split('\\')[-1]
    replace = extensions
    for content in replace:
        path = path.replace(content, "")
    headers = {'User-Agent': 'SubDB/1.0 (subtitle-downloader/1.0; http://github.com/manojmj92/subtitle-downloader)'}

    # step 1. find subtitle list
    filehash = hash_val[0] + '%3B' + hash_val[1] + '%3B' + hash_val[2] + '%3B' + hash_val[3]
    url = 'http://www.shooter.cn/api/subapi.php?filehash=' + filehash + '&format=json&pathinfo=' + name + '&lang=Chn'
    print 'list url:', url
    req = urllib2.Request(url, '', headers)
    done = False
    response = None
    while not done:
        try:
            response = urllib2.urlopen(req).read()
            done = True
        except:
            done = False
    # step 2. get first 5 subtitle from subtitle list
    for index, res in enumerate(eval(response)):
        if index < 5:
            subtitle = res['Files']
            url = subtitle[0]['Link'].replace('\u0026', '&')
            print 'download url:', url
            req = urllib2.Request(url, '', headers)
            done = False
            while not done:
                try:
                    response = urllib2.urlopen(req).read()
                    done = True
                except:
                    done = False
        with open(path + '-' + str(index) + ".zh.srt", "wb") as subtitle_file:
            subtitle_file.write(response)


# 重新命名資料夾，避免出現[]及()，glob會抓不到內容
for filename in os.listdir(dir_path):
    if re.match('^[A-Za-z0-9_.]+$', filename) is None:  # 只可包含英文大小寫及dot
        print 'rename from', filename, 'to', re.sub('[^0-9a-zA-Z]+', '.', filename)
        os.rename(os.path.join(dir_path, filename), os.path.join(dir_path, re.sub('[^0-9a-zA-Z]+', '.', filename)))

for root, subFolders, files in os.walk(dir_path):
    print 'in folder:', root
    print 'num of srt files:', len(glob.glob(os.path.join(root, '*.srt')))
    if len(glob.glob(os.path.join(root, '*.srt'))) <= 1:
        for ext in extensions:
            for f in glob.glob(os.path.join(root, '*' + ext)):
                print 'file:', f
                sub_downloader(f)
