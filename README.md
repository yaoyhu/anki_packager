# anki_packager

anki_package 是一个生成 Anki apkg 文件的工具，专注于生成单词卡片。卡片内容包括：正面：词头、发音、音标、考试大纲范围，背面：中英文释义、短语例句、AI 助记、近义词反义词。

# Usage

## conda

建议使用虚拟环境，这里使用 conda 作为例子：

```shell
# 生成一个名为 apkg 的虚拟环境并启动
conda create -n apkg python=3.9
conda activate apkg
# 安装依赖
pip install -r requirements.txt
# 运行 help 查看具体用法
python -m anki_packager -h
```

## Docker

如果你不想弄脏你的环境，可以使用 Docker 运行：

```shell
docker build --tag apkg .

# windows powershell
$folder=yourfolderpath # $folder_path="C:\Users\user\mybook\"
# linux
export folder=yourfolderpath # export folder_path="/home/user/mybook/"

docker run --rm --name apkg --mount type=bind,source=$folder,target=/app/
```

如果你不想每次都输入这么多命令，可以使用 makefile 脚本：

```shell
make build
```

# TODO

- [ ] 单词释义比例词典
- [ ] 近一步优化 UI
- [ ] Longman 词典
- [ ] 获取欧陆词典生词
- [ ] 图形界面

# Thanks
- 感谢 [yihong0618](https://github.com/yihong0618) 大佬开源的那么多 Python 项目，受益匪浅
- 感谢 [skywind](https://github.com/skywind3000) 开源的 [ECDICT](https://github.com/skywind3000/ECDICT)