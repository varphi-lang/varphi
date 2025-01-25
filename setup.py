from setuptools import setup, find_packages

setup(
    name="varphi",
    version="0.0.0",
    author="Hassan El-Sheikha",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    install_requires=[
        "antlr4-python3-runtime==4.13.2"
    ],
)
