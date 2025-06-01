# ファイルのマジックナンバーを取得するスクリプト
import os
import sys

def get_magic_number(file_path):
    """
    ファイルのマジックナンバーを取得する関数
    :param file_path: ファイルのパス
    :return: マジックナンバーの文字列
    """
    try:
        with open(file_path, 'rb') as f:
            magic_number = f.read(4).hex()
        return magic_number
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None

def main():
    # 対象のファイルパスを指定
    file_path = sys.argv[1] if len(sys.argv) > 1 else 'example.bin'

    # マジックナンバーを取得
    magic_number = get_magic_number(file_path)
    
    if magic_number:
        print(f"Magic number for {file_path}: {magic_number}")
    else:
        print("Could not retrieve magic number.")

if __name__ == "__main__":
    main()
