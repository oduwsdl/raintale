from setuptools import setup, find_packages
from os import path

# to get pylint to shut up
__appname__ = None
__appversion__ = None

# __appname__, __appversion__, and friends come from here
exec(open("raintale/version.py").read())

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=__appname__.lower(),
    version=__appversion__,
    description='A Python service for publishing a story generated from archived web pages to multiple services.',
    long_description_content_type="text/markdown",
    long_description=long_description,
    url='https://github.com/shawnmjones/raintale',
    author='Shawn M. Jones',
    author_email='jones.shawn.m@gmail.com',
    license='MIT',
    packages=find_packages(),
    package_data={
        'raintale': [ 'templates/*' ]
    },
    scripts=[
        'bin/raintale_cmd',
    ],
    include_package_data=True,
    install_requires=[
        'facebook-sdk',
        'ffmpeg-python',
        'google-api-python-client',
        'google_auth_oauthlib',
        'jinja2',
        'oauth2client',
        'Pillow',
        'pyyaml',
        'python-twitter',
        'requests',
        'requests_cache'
    ],
    test_suite="tests",
    zip_safe=True,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Scientific/Engineering',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='webarchives memento storytelling'
    )
