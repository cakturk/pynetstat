# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='pynetstat',
    version='0.1.0',
    readme=readme,
    license = license,
    description='netstat implemented in python',
    author='Cihangir Akturk',
    author_email='cakturk@gmail.com',
    url='https://github.com/cakturk/pynetstat',
    packages=find_packages(exclude=('tests', 'docs'))
)
