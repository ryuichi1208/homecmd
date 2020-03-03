#!/usr/bin/python3

import glob
import hashlib
import os
import sys

def get_file_list(path: str, ext: str) -> list:
    L = []
    for f in glob.glob(f"{path}/**/*.{ext}", recursive=True):
        print(os.stat(f).st_ctime)
        L.append(f[len(path)+1:])
    return L


def hash_check(dst_files, dst_dir, src_dir):
    cnt = 0
    for f in dst_files:
        try:
            f1 = open(f"{dst_dir}/{f}", "rb")
            f2 = open(f"{src_dir}/{f}", "rb")
            if hashlib.md5(f1.read()).hexdigest() != hashlib.md5(f2.read()).hexdigest():
                print(f"{dst_dir}/{f}")
                cnt+=1
        except FileNotFoundError:
            print("Not Found file {src_dir}/{f}")
            continue
        f1.close()
        f2.close()
    print(f"=====\nFILE NUMS: {len(dst_files)}\nDIFFER FILES: {cnt}")

def main(argv):
    dst_dir = argv[1]
    src_dir = argv[2]
    dst_files = get_file_list(argv[1], "inc")

    hash_check(dst_files, dst_dir, src_dir)

if __name__ == "__main__":
    main(sys.argv)
