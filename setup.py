from setuptools import setup

setup(
    name="nmfu_pygments",
    version="0.4.0",
    packages=["nmfu_pygments"],
    install_requires=[
        "pygments"
    ],
    entry_points={
        "pygments.lexers": ["nmfu=nmfu_pygments.nmfu:NmfuLexer"]
    }
)
