from setuptools import setup, find_packages

try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = ""

setup(
    name="redu-config-manager",
    version="1.0.0",
    author="Ridwan Hossain Abid",
    author_email="ridwan0110@hotmail.com",
    url="https://github.com/Ridwan0110/redu_config_manager",
    license="MIT",
    description="A simple configuration manager that reads a configuration file and provides methods to access configuration values programmatically.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0.0,<7.0.0",
        "redu-logger @ https://python.ridwanabid.com/repository/simple/redu-logger/redu_logger-1.0.5.tar.gz"
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6',
    keywords="configuration manager, config manager, yaml, config, settings, application configuration, python config manager",
)
