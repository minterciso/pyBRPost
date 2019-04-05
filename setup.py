from setuptools import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='pyBRPost',
    version='1.0.1',
    packages=setuptools.find_packages(),
    url='https://github.com/minterciso/pyBRPost',
    license='MIT License',
    author='Mateus Interciso',
    author_email='minterciso@gmail.com',
    description='Python module to query Brazilian Post Office regarding shipping methods',
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'requests>=2.21.0',
        'xmltodict>=0.12'
        ]
)
