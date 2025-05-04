import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QStatusBar, 
                           QProgressBar, QMessageBox, QTabWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont

# Import Dashboard widget
from ui.dashboard import DashboardWidget

# Simple placeholder for DataProcessor
class SimpleDataProcessor:
    """Simple placeholder for DataProcessor to get the UI working"""
    
    def __init__(self):
        self.scan_data = None
    
    def start_scan(self, path, callbacks=None):
        """Simple placeholder for scanning"""
        print(f"Simulating scan of {path}")
        
        # Simulate scanning
        import time
        import random
        import os
        
        # Generate mock scan results
        results = {
            'total_files': random.randint(100, 500),
            'total_folders': random.randint(20, 50),
            'total_size': random.randint(1000000, 100000000),
            'total_issues': random.randint(10, 50),
            'file_types': {
                '.docx': random.randint(10, 50),
                '.xlsx': random.randint(10, 50),
                '.pdf': random.randint(10, 50),
                '.jpg': random.randint(10, 50),
                '.png': random.randint(10, 50),
                '.txt': random.randint(10, 50),
            },
            'path_length_distribution': {
                50: random.randint(10, 50),
                100: random.randint(10, 50),
                150: random.randint(5, 20),
                200: random.randint(1, 10),
                250: random.randint(0, 5),
                300: random.randint(0, 2),
            },
            'avg_path_length': random.randint(80, 150),
            'max_path_length': random.randint(200, 300),
            'issues': [
                {
                    'type': 'Path Too Long',
                    'count': random.randint(5, 20),
                    'description': 'Files with paths exceeding SharePoint limits',
                    'severity': 'Critical'
                },
                {
                    'type': 'Illegal Characters',
                    'count': random.randint(5, 20),
                    'description': 'Files with illegal characters in their names',
                    'severity': 'Critical'
                },
                {
                    'type': 'Duplicate Files',
                    'count': random.randint(5, 20),
                    'description': 'Files with identical content',
                    'severity': 'Warning'
                }
            ]
        }
        
        # If callbacks are provided, simulate progress and completion
        if callbacks:
            # Simulate progress updates
            if 'progress' in callbacks:
                for i in range(0, 101, 5):
                    callbacks['progress'](i, 100)
                    # Add slight delay to simulate work
                    time.sleep(0.1)
            
            # Simulate completion
            if 'scan_completed' in callbacks:
                callbacks['scan_completed'](results)

class MainWindow(QMainWindow):
    """Main window for SharePoint Data Migration Cleanup Tool."""
    
    def __init__(self):
        super().__init__()
        
        # Set window properties
        self.setWindowTitle("SharePoint Migration Tool")
        self.setMinimumSize(900, 600)
        
        # Create central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        # Create main layout
        self.layout = QVBoxLayout(self.central_widget)
        
        # Initialize data processor with our simple implementation
        self.data_processor = SimpleDataProcessor()
        
        # Add header section
        self.add_header()
        
        # Setup tabs
        self.setup_tabs()
        
        # Add status bar
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedWidth(200)
        self.progress_bar.setVisible(False)
        self.statusBar.addPermanentWidget(self.progress_bar)
        self.statusBar.showMessage("Ready")
        
        # Initialize scan results
        self.scan_results = None
    
    def add_header(self):
        """Add header section with title and controls"""
        header_layout = QHBoxLayout()
        
        # Add title
        title = QLabel("SharePoint Migration Tool")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # Add source selection
        source_label = QLabel("Source:")
        self.source_path = QLabel("Not selected")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_source)
        
        # Add scan button
        self.scan_button = QPushButton("Start Scan")
        self.scan_button.setEnabled(False)
        self.scan_button.clicked.connect(self.start_scan)
        
        # Add widgets to layout
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(source_label)
        header_layout.addWidget(self.source_path)
        header_layout.addWidget(browse_button)
        header_layout.addWidget(self.scan_button)
        
        # Add to main layout
        self.layout.addLayout(header_layout)
    
    def setup_tabs(self):
        """Set up the tab widget with various tabs"""
        self.tabs = QTabWidget()
        
        # Create and add the Dashboard tab
        self.dashboard_tab = DashboardWidget()
        self.tabs.addTab(self.dashboard_tab, "Dashboard")
        
        # Add tabs to main layout
        self.layout.addWidget(self.tabs, 1)  # 1 = stretch factor
    
    def browse_source(self):
        """Browse for source folder"""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Select Source Folder",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.source_path.setText(folder)
            self.scan_button.setEnabled(True)
    
    def start_scan(self):
        """Start scanning process"""
        source = self.source_path.text()
        if source == "Not selected":
            return
        
        # Update UI
        self.scan_button.setEnabled(False)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.statusBar.showMessage(f"Scanning {source}...")
        
        # Define callbacks
        def progress_callback(current, total):
            if total > 0:
                percentage = int((current / total) * 100)
                self.progress_bar.setValue(percentage)
        
        def completion_callback(results):
            self.scan_results = results
            self.progress_bar.setVisible(False)
            self.scan_button.setEnabled(True)
            self.statusBar.showMessage("Scan completed")
            
            # Update dashboard with results
            self.dashboard_tab.update_with_results(results)
            
            # Switch to dashboard tab
            self.tabs.setCurrentIndex(0)
        
        # Start scan with callbacks
        try:
            self.data_processor.start_scan(
                source,
                callbacks={
                    'progress': progress_callback,
                    'scan_completed': completion_callback
                }
            )
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            self.scan_button.setEnabled(True)
            self.statusBar.showMessage("Scan failed")
            QMessageBox.critical(self, "Error", f"Failed to start scan: {str(e)}")