from os import path
from setuptools import setup, find_packages

import shopy

here = path.abspath(path.dirname(__file__))

with open('README.md', 'r') as desc:
    long_description = desc.read()

setup(
    name='shopy',
    version=shopy.__version__,
    description='',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/marqetintl/miqshopy',
    author=shopy.__author__,
    author_email=shopy.__email__,
    keywords='Django shop backend',
    # py_modules=[''],
    # package_dir={'': ''},
    packages=find_packages(),
    install_requires=['miqstaff'],
    extras_require={
        "dev": [
            'coverage', 'selenium',
            'pytest', 'pytest-cov', 'pytest-django',
        ]
    },
    python_requires=">=3.5",
    zip_safe=False
)
