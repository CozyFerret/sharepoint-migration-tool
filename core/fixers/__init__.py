#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fixers package for SharePoint Data Migration Cleanup Tool.
Contains fixers for resolving various issues in files.
"""

# Import all fixers for easy access
from core.fixers.name_fixer import NameFixer
from core.fixers.path_shortener import PathShortener
from core.fixers.deduplicator import Deduplicator