#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup

setup(name='clementine_last_export',
      version='0.2',
      description='Tool to import playcounts and loved tracks from your last.fm account into Clementine',
      author='Vincent Verdeil',
      author_email='vincent.verdeil@gmail.com',
      url='http://code.google.com/p/clementine-last-export/',
      scripts=['bin/clementine_last_export'],
      packages=['clementine_last_export'],
      package_data={'clementine_last_export': ['*.png']},
      )
