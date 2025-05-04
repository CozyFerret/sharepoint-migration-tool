#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Core package for SharePoint Data Migration Cleanup Tool.
Contains the main functionality for scanning, analyzing, and cleaning files.
"""

# Import main components for easy access
from core.scanner import FileSystemScanner
from core.data_cleaner import DataCleaner
from core.data_processor import DataProcessor

# Import analyzers
from core.analyzers.name_validator import SharePointNameValidator
from core.analyzers.path_analyzer import PathAnalyzer
from core.analyzers.duplicate_finder import DuplicateFinder
from core.analyzers.pii_detector import PIIDetector

# Import fixers
from core.fixers.name_fixer import NameFixer
from core.fixers.path_shortener import PathShortener
from core.fixers.deduplicator import Deduplicator