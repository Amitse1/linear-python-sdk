from setuptools import setup, find_packages

setup(
    name="linear-python-sdk",
    version="0.1.0",
    packages=find_packages(exclude=["tests*", "examples*"]),
    install_requires=[
        "requests>=2.25.0",
        "python-dotenv>=0.15.0",
    ],
    author="Amit Segev",
    author_email="amit@avon-ai.com",
    url="https://github.com/AmitSe1/linear-python-sdk",
) 