from setuptools import setup, find_packages

setup(
    name="heimdallr",
    version="1.0.0",
    description="Advanced facial recognition search tool across social media and web",
    author="Heimdallr Team",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.7",
        "face-recognition>=1.3.0",
        "opencv-python>=4.8.1.78",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.2",
        "selenium>=4.15.2",
        "pandas>=2.1.4",
        "rich>=13.7.0",
        "tqdm>=4.66.1",
    ],
    entry_points={
        "console_scripts": [
            "heimdallr=heimdallr.cli:main",
        ],
        "gui_scripts": [
            "heimdallr-gui=heimdallr.gui:main",
        ]
    },
    python_requires=">=3.8",
)