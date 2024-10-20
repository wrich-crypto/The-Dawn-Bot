#!/bin/bash

# 脚本名: python_env_init.sh

# 更新系统并安装依赖
sudo apt update
sudo apt install -y wget build-essential zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev libssl-dev libsqlite3-dev libreadline-dev libffi-dev curl libbz2-dev

# 下载Python 3.10.15源码
wget https://www.python.org/ftp/python/3.10.15/Python-3.10.15.tgz

# 解压源码
tar -xzf Python-3.10.15.tgz
cd Python-3.10.15

# 配置和编译Python
./configure --enable-optimizations --prefix=/usr/local/python3.10.15
make -j $(nproc)

# 安装Python
sudo make altinstall

# 创建符号链接
sudo ln -s /usr/local/python3.10.15/bin/python3.10 /usr/local/bin/python3.10
sudo ln -s /usr/local/python3.10.15/bin/pip3.10 /usr/local/bin/pip3.10

# 设置环境变量
echo 'export PATH="/usr/local/python3.10.15/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# 验证安装
python3.10 --version
pip3.10 --version

# 清理下载的文件
cd ..
rm -rf Python-3.10.15 Python-3.10.15.tgz

echo "Python 3.10.15 和 pip 安装完成，环境变量已设置。"
