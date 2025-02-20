FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    ruby \
    ruby-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 必要に応じて、PythonとRubyのバージョンを指定することも可能です。
# 例：
# python3.9
# python3.9-pip
# ruby3.0
# ruby3.0-dev

# pipを使用してPythonパッケージをインストールする場合（例：requests）
# RUN pip3 install requests

# gemを使用してRubyパッケージをインストールする場合（例：bundler）
# RUN gem install bundler

# 必要に応じて、作業ディレクトリを設定します。
# WORKDIR /app

# 必要に応じて、デフォルトのコマンドを設定します。
# CMD ["bash"]
