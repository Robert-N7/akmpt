import setuptools
from setuptools import setup

with open('README.md') as file:
    long_description = file.read()

CLASSIFIERS = [
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    "Operating System :: OS Independent"
 ]


setup(
    name='akmpt',
    description='A tool that helps reverse KMP files.',
    version='v0.0.1',
    entry_points={
        'console_scripts': [
            'akmpt = akmpt.__main__:main'
        ],
    },
    packages=setuptools.find_packages(),
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['colorama'],
    classifiers=CLASSIFIERS,
    url='',
    license='GPLv3',
    author='Robert',
    author_email='robert7.nelson@gmail.com',
)
