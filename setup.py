import pathlib
from setuptools import setup
import sys

v = sys.version_info
if sys.version_info < (3, 5):
    v = sys.version_info
    print("FAIL: Requires Python 3.5 or later, but setup.py was run using %s.%s.%s" % (v.major, v.minor, v.micro))
    print("NOTE: Installation failed. Run setup.py using python3")
    sys.exit(1)

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="sgl",
    version="0.9.2",
    description="Structured Grant Language",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/dhh1128/sgl",
    author="Daniel Hardman",
    author_email="daniel.hardman@gmail.com",
    license="Apache 2.0",
    keywords="sgl json dsl authorization authz verifiable credentials did",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Development Status :: 4 - Beta"
    ],
    packages=["sgl"],
    include_package_data=True,
    install_requires=[],
    entry_points={
        "console_scripts": [
            "realpython=reader.__main__:main",
        ]
    },
    download_url='https://github.com/dhh1128/sgl/archive/v0.9.2.tar.gz',
)