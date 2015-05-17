#!/usr/bin/env python

"""
config.py
Allen Guo <allenguo@berkeley.edu>
Specifies configurable settings for publish.py.
"""

github_url = 'https://github.com/berkeley-cs61as/markdown-courseware/tree/master/'

output_directory = '../berkeley-cs61as.github.io/'

# List of tuples. Each tuple represents a unit.
# The first item in the tuple is the name of the unit.
# The second item is a range of numbers indicating the chapters
# in that tuple. The range must be something like this: "1, 2-4, 6, 7."
# Note that ranges indicated with a dash are inclusive-inclusive.
# Also, make sure every comma is followed by a space.
units = [('Setup', '1-3'),
         ('Unit 0', '4, 6-7'),
         ('Unit 1', '8-9, 11-12'),
         ('Unit 2', '13-16'),
         ('Unit 3', '17-21'),
         ('Unit 4', '22,23,25-27')]

# List of tuples. Each tuple represents a (non-textbook) page.
# The first item in the tuple is the name of the page.
# The second item is the file path (relative to publish.py).
# This can either be a Markdown file or HTML file.
# The third item is the template to use with page.
pages = [('Home', 'pages/index.html', 'index'),
         ('Textbook', 'pages/textbook.html', 'page-no-toc'),
         ('Syllabus', 'pages/syllabus.md', 'page-toc'),
         ('FAQ', 'pages/faq.html', 'page-toc'),
         ('Staff', 'pages/staff.html', 'page-no-toc'),
         ('Resources', 'pages/resources.html', 'page-no-toc')]

# publish.py generates a warning if a section title exceeds this
section_title_max_length = 48
