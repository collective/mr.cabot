from setuptools import setup
import os, sys

version = '1.0'

install_requires = [
  'setuptools',
  'zope.interface',
  'zope.component',
  'ggeocoder',
  'simplekml',
]

setup(name='mr.cabot',
      version=version,
      description="A utility for finding and mapping contributions to open source projects",
      long_description=open("README.rst").read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Matthew Wilkes',
      author_email='matthew@matthewwilkes.co.uk',
      url='http://github.com/collective/mr.cabot',
      license='BSD',
      packages=['mr', 'mr.cabot'],
      package_dir = {'': 'src'},
      namespace_packages=['mr'],
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      test_suite='mr.cabot.tests',
      entry_points="""
      [console_scripts]
      cabot = mr.cabot.sebastian:sebastian
      """,
      )
