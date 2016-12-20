# -*- coding: utf-8 -*-
from setuptools import setup

setup(name='xmldestroyer',
      version='0.2',
      description='Bottom-up transformation of XML into python generators, XML, JSON or text.',
      long_description=open('README.rst').read(),
      classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Topic :: Text Processing :: Markup :: XML',
          'License :: OSI Approved',
          'License :: OSI Approved :: MIT License',
          'Intended Audience :: Developers',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 3',
      ],
      keywords='xml bottom up bottom-up transformation syb scrap your boilerplate scrap-your-boilerplate uniplate geniplate',
      url='http://github.com/danr/xmldestroyer',
      author='Dan Rosén',
      author_email='dan.rosen@gu.se',
      license='MIT',
      packages=['xmldestroyer'],
      install_requires=['six'],
      zip_safe=True,
      test_suite='nose.collector',
      tests_require=['nose', 'xmltodict'])
