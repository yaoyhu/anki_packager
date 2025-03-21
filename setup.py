from setuptools import setup, find_packages
from anki_packager import __version__

setup(
    name="apkger",
    version=__version__,
    author="Yaoyao Hu",
    author_email="shady030314@gmail.com",
    description="自动化 Anki 英语单词卡片牌组生成器",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yaoyhu/anki_packager",
    packages=find_packages(
        exclude=["*.pyc", "*.pyo", "__pycache__", "*.__pycache__*"]
    ),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Text Processing :: Linguistic",
        "Development Status :: 4 - Beta",
    ],
    python_requires=">=3.9",
    install_requires=open("requirements.txt").read().splitlines(),
    entry_points={
        "console_scripts": [
            "apkger=anki_packager.__main__:main",
        ],
    },
)
