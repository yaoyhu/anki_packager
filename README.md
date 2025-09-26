<!-- LOGO -->
<h1>
<p align="center">
  <img src="./images/apkg.png" alt="Logo" width="200">
  <br>anki_packager
</h1>
  <p align="center">
    自动化 Anki 英语单词高质量卡片牌组生成工具
    <br />
    <a href="#关于项目">关于项目</a>
    ·
    <a href="#使用">使用指南</a>
    ·
    <a href="#todo">开发计划</a>
    ·
    <a href="#thanks">致谢</a>
  </p>
</p>

## 关于项目

`anki_packager` 是一款自动化的 Anki 单词卡片生成工具，能够自动创建高质量的 `.apkg` 牌组。本项目致力于为英语学习者提供一个高效、智能的记忆辅助工具。

### 核心特性

- 多源精选词典整合：[ECDICT](https://github.com/skywind3000/ECDICT)、[《有道词语辨析》加强版](https://skywind.me/blog/archives/2941)、[单词释义比例词典](https://skywind.me/blog/archives/2938)
- 智能化学习体验：
  - 自动抓取有道词典优质例句和常用短语
  - 支持谷歌 TTS 发音、中英双解、考纲标记等功能
  - 支持流行 AI 模型（需要 API-KEY）对单词进行总结、助记及和情境故事生成
- 便捷的数据导入：支持欧路词典生词本一键导入并批量处理单词列表，自动生成卡片
- 优良的命令行体验：显示处理进度，支持记录错误、支持丰富的命令行参数
- 支持 Docker 运行、支持 PyPI 安装

### 卡片预览

每张单词卡片包含丰富的学习资源，结构清晰，内容全面：

- 正面：词头、发音、音标 + 考试大纲标签（如 中高考、CET4、CET6、GRE 等）
- 背面：
  - 释义：中文（ECDICT）、时态（AI）、释义和词性比例（[《有道词语辨析》加强版](https://skywind.me/blog/archives/2941)）
  - AI 生成词根 + 辅助记忆（联想记忆 + 谐音记忆）
  - 短语 + 例句（有道爬虫）
  - 单词辨析（[单词释义比例词典](https://skywind.me/blog/archives/2938)）
  - 英文释义（目前来自 ECDICT）+ AI 生成故事

<img src="./images/卡片预览.png" alt="背面 " style="zoom:50%;" />

## 使用

### 快速开始

```bash
# 直接使用 pip 安装
pip install apkger
```

在使用 apkger 之前，你需要先在 `config/config.toml` 文件中填写相关配置信息：

本项目使用 [litellm](https://github.com/BerriAI/litellm) 统一调用 LLM 服务。关于 `MODEL_PARAM` 的详细配置方法，请参考 [LiteLLM Providers 文档](https://docs.litellm.ai/docs/providers)。

```toml
PROXY = ""
EUDIC_TOKEN = ""
EUDIC_ID = "0"
DECK_NAME = "anki_packager"

[[MODEL_PARAM]]
model = "gemini/gemini-2.5-flash"
api_key = "GEMINI_API_KEY"
rpm = 10                          # 每分钟请求次数

### OpenAI-Compatible Endpoints 示例
# [[MODEL_PARAM]]
# model = "openai/gpt-4o"
# api_key = "OPENAI_API_KEY"
# api_base = "YOUR_API_BASE"
# rpm = 200
```

下面是关于配置文件中各参数的详细说明：

- `MODEL_PARAM`:
  - `model`: Provider Route on LiteLLM + Model ID
  - `api_key`: 对应模型的 API 密钥。
  - `api_base`: (可选) 仅在模型为 OpenAI-Compatible Endpoints 时需要填写
  - `rpm`: (可选) 每分钟的请求次数限制，用于控制 API 调用频率。
- `PROXY`: 如果你无法直接连接到 AI 服务提供商，可以在这里设置代理服务器地址

- 如果需要使用欧路词典生词本：先按照[欧陆官方获取](https://my.eudic.net/OpenAPI/Authorization) TOKEN，然后使用`apkger --eudicid` 选择 ID 写入配置文件

### 下载字典

下载字典到配置目录中（注意名称不要错）:

- Linux/MacOS: `~/.config/anki_packager/dicts/`
- Windows: `C:\Users\<用户名>\AppData\Roaming\anki_packager\dicts\`

字典数据（感谢 [skywind）](https://github.com/skywind3000)下载地址:

- [stardict.7z](https://github.com/skywind3000/ECDICT/raw/refs/heads/master/stardict.7z)
- [单词释义比例](https://pan.baidu.com/s/1kUItx8j)
- [有道词语辨析](https://pan.baidu.com/s/1gff2tdp)

字典下载完毕后，解压和处理交给 anki_packager 即可。

### 运行

目前软件没有 UI 界面，只支持命令行运行，下面给出一些参考：

```bash
# 查看帮助信息
apkger -h

# 从默认生词本读词生成卡片
apkger

### 关闭 AI 功能
apkger --disable_ai

### 从欧路词典生词本导出单词，生成卡片（需要先配置)
## 先查看 ID 写入配置文件
apkger --eudicid
## 生成卡片
apkger --eudic
```

<details>
<summary>方式一：Conda 环境</summary>

```bash
# 创建并激活一个名为 apkg 的 Python 3.9 虚拟环境
conda create -n apkg python=3.9
conda activate apkg

# 安装项目依赖
pip install -r requirements.txt

# 查看帮助信息
python -m anki_packager -h

# 从欧路词典生词本导出单词，生成卡片（需要先配置)
python -m anki_packager --eudic

# 关闭 AI 功能
python -m anki_packager --disable_ai

# 从生词本读词生成卡片
python -m anki_packager
```

</details>

<details>
<summary>方式二：Docker 容器</summary>

如果你希望避免污染本地环境，可以使用 Docker 运行 anki_packager，可以配合 `Makefile` 使用：

```shell
# 构建 Docker 镜像 和 创建持久化卷
make build

# 第一次运行容器下载词典（需要一点时间）
make run

# 进入容器（注意！需要在主机先配置 config/config.toml）
# 在容器中运行 anki_packager，生成的牌组会保存在当前目录中
make shell
```

</details>

## TODO

- [x] ~~集成单词释义比例词典~~
- [x] ~~近一步优化单词卡片 UI~~
- [x] ~~从欧路词典导入生词~~
- [x] ~~支持 SiliconFlow、Gemini~~
- [x] ~~重新支持 Docker~~
- [x] ~~发布到 PyPI~~
- [x] ~~训练现成的数据包发布 release~~ @Initsnow
- [ ] 支持更多软件生词导出
- [ ] 支持 Longman 词典
- [ ] 开发 GUI

## Thanks

本项目得到了众多开源项目和社区的支持：

- 感谢 [skywind](https://github.com/skywind3000) 开源的 [ECDICT](https://github.com/skywind3000/ECDICT) 以及其他词典项目，为本项目提供了丰富的词典资源。
- 感谢 [yihong0618](https://github.com/yihong0618) 开源的众多优秀 Python 项目，从中获益良多。

---

<p align="center">如果这个项目对你有帮助，欢迎 Star ⭐️</p>
