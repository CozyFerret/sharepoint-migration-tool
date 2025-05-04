import sys
import os
import logging
import pandas as pd
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, 
                           QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QFileDialog, QStatusBar, 
                           QProgressBar, QMessageBox, QTabWidget,
                           QAction, QMenu, QMenuBar, QLineEdit)
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtGui import QFont, QIcon

# Import Dashboard widget
from ui.dashboard import DashboardWidget

# Import Enhanced Data View
from ui.enhanced_data_view import EnhancedDataView

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


class AnalysisTab(QWidget):
    """Tab for data analysis and enhanced viewing."""
    
    def __init__(self, parent=None):
        super(AnalysisTab, self).__init__(parent)
        
        # Main layout
        self.layout = QVBoxLayout(self)
        
        # Source selection
        source_layout = QHBoxLayout()
        source_label = QLabel("Source Directory:")
        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.select_source)
        
        scan_btn = QPushButton("Start Scan")
        scan_btn.clicked.connect(self.start_scan)
        
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_edit)
        source_layout.addWidget(browse_btn)
        source_layout.addWidget(scan_btn)
        self.layout.addLayout(source_layout)
        
        # Add enhanced data view
        self.enhanced_view = EnhancedDataView()
        self.layout.addWidget(self.enhanced_view)
        
        # Status bar for progress updates
        status_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.status_label = QLabel("Ready")
        
        status_layout.addWidget(self.progress_bar)
        status_layout.addWidget(self.status_label)
        self.layout.addLayout(status_layout)
        
    def select_source(self):
        """Select source directory for analysis"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Source Directory", "", QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.source_edit.setText(folder)
            
    def start_scan(self):
        """Start scanning the selected directory"""
        source_dir = self.source_edit.text()
        if not source_dir or source_dir == "Not selected":
            QMessageBox.warning(self, "Error", "Please select a valid source directory.")
            return
            
        # Show progress
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        self.status_label.setText("Scanning...")
        
        # Find the main window to access data processor
        main_window = self.window()
        if hasattr(main_window, 'data_processor'):
            # Define callbacks
            def progress_callback(current, total):
                if total > 0:
                    percentage = int((current / total) * 100)
                    self.progress_bar.setValue(percentage)
            
            def completion_callback(results):
                self.progress_bar.setVisible(False)
                self.status_label.setText("Scan completed")
                
                # Update the enhanced data view with results
                self.update_data_view(results)
            
            # Start scan
            try:
                main_window.data_processor.start_scan(
                    source_dir,
                    callbacks={
                        'progress': progress_callback,
                        'scan_completed': completion_callback
                    }
                )
            except Exception as e:
                self.progress_bar.setVisible(False)
                self.status_label.setText("Scan failed")
                QMessageBox.critical(self, "Error", f"Failed to start scan: {str(e)}")
    
    def update_data_view(self, results):
        """Update the enhanced data view with scan results"""
        if not results:
            return
            
        try:
            # Convert the results dictionary to a DataFrame
            if 'issues' in results and isinstance(results['issues'], list) and results['issues']:
                # If we have detailed issues, use those
                df = pd.DataFrame(results['issues'])
            else:
                # Otherwise create a simple summary
                summary_data = []
                for key, value in results.items():
                    if isinstance(value, (int, float, str, bool)):
                        summary_data.append({'Metric': key, 'Value': value})
                
                df = pd.DataFrame(summary_data)
            
            # Update the enhanced data view
            self.enhanced_view.set_data(df)
        except Exception as e:
            logging.error(f"Error updating enhanced data view: {str(e)}")
            QMessageBox.warning(self, "Error", f"Failed to update data view: {str(e)}")


# Simple placeholder for the Migration Tab
class MigrationTab(QWidget):
    """Tab for migration options."""
    
    def __init__(self, parent=None):
        super(MigrationTab, self).__init__(parent)
        
        # Simple placeholder layout
        layout = QVBoxLayout(self)
        
        # Source selection
        source_layout = QHBoxLayout()
        source_label = QLabel("Source Directory:")
        self.source_edit = QLineEdit()
        self.source_edit.setReadOnly(True)
        
        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self.select_source)
        
        source_layout.addWidget(source_label)
        source_layout.addWidget(self.source_edit)
        source_layout.addWidget(browse_btn)
        layout.addLayout(source_layout)
        
        # Add placeholder message
        message = QLabel("Migration functionality will be implemented in a future version.")
        message.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setItalic(True)
        message.setFont(font)
        layout.addWidget(message)
        
    def select_source(self):
        """Select source directory"""
        folder = QFileDialog.getExistingDirectory(
            self, "Select Source Directory", "", QFileDialog.ShowDirsOnly
        )
        
        if folder:
            self.source_edit.setText(folder)


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
        
        # Initialize data processor - use simple version for now to avoid errors
        self.data_processor = SimpleDataProcessor()
        
        # Try to load the real DataProcessor, but handle any errors
        try:
            # Try importing the real DataProcessor
            from core.data_processor import DataProcessor
            # Check if it can be instantiated without errors
            test_instance = DataProcessor()
            # If successful, use it instead of the placeholder
            self.data_processor = test_instance
            logging.info("Using real DataProcessor")
        except Exception as e:
            logging.warning(f"Could not initialize real DataProcessor, using placeholder: {str(e)}")
        
        # Create menus
        self.create_menus()
        
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
        
        # Load settings
        self.load_settings()
    
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
        
        # Add Analysis tab with enhanced data view
        self.analysis_tab = AnalysisTab()
        self.tabs.addTab(self.analysis_tab, "Analysis")
        
        # Add Migration tab (placeholder)
        self.migration_tab = MigrationTab()
        self.tabs.addTab(self.migration_tab, "Migration")
        
        # Add tabs to main layout
        self.layout.addWidget(self.tabs, 1)  # 1 = stretch factor
    
    def create_menus(self):
        """Create application menus"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        open_action = QAction("&Open Source Folder...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.browse_source)
        file_menu.addAction(open_action)
        
        export_action = QAction("&Export Report...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_report)
        file_menu.addAction(export_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menu_bar.addMenu("&Tools")
        
        scan_action = QAction("&Scan Files", self)
        scan_action.triggered.connect(self.start_scan)
        tools_menu.addAction(scan_action)
        
        analyze_action = QAction("&Analyze Data", self)
        analyze_action.triggered.connect(self.go_to_analysis)
        tools_menu.addAction(analyze_action)
        
        # Help menu
        help_menu = menu_bar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
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
            
            # Update source in other tabs
            if hasattr(self.analysis_tab, 'source_edit') and hasattr(self.analysis_tab.source_edit, 'setText'):
                self.analysis_tab.source_edit.setText(folder)
            
            if hasattr(self.migration_tab, 'source_edit') and hasattr(self.migration_tab.source_edit, 'setText'):
                self.migration_tab.source_edit.setText(folder)
    
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
            
            # Update Analysis tab with enhanced data view
            if hasattr(self.analysis_tab, 'update_data_view'):
                self.analysis_tab.update_data_view(results)
            
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
    
    def export_report(self):
        """Export the current scan results"""
        if hasattr(self.analysis_tab, 'enhanced_view') and hasattr(self.analysis_tab.enhanced_view, 'show_export_menu'):
            # Switch to Analysis tab
            self.tabs.setCurrentIndex(1)  # Assuming Analysis is the second tab
            
            # Show export menu
            self.analysis_tab.enhanced_view.show_export_menu()
        else:
            QMessageBox.information(self, "Export", "No data available to export.")
    
    def go_to_analysis(self):
        """Switch to the Analysis tab"""
        self.tabs.setCurrentIndex(1)  # Assuming Analysis is the second tab
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About SharePoint Migration Tool",
            "<h2>SharePoint Migration Tool</h2>"
            "<p>Version 1.1.0</p>"
            "<p>A tool for cleaning and preparing file systems for SharePoint migration.</p>"
            "<p>© 2025 CozyFerret</p>"
            "<p><a href='https://github.com/CozyFerret/sharepoint-migration-tool'>"
            "https://github.com/CozyFerret/sharepoint-migration-tool</a></p>"
        )
    
    def load_settings(self):
        """Load application settings"""
        settings = QSettings()
        geometry = settings.value("MainWindow/geometry")
        if geometry:
            self.restoreGeometry(geometry)
    
    def save_settings(self):
        """Save application settings"""
        settings = QSettings()
        settings.setValue("MainWindow/geometry", self.saveGeometry())
    
    def closeEvent(self, event):
        """Handle window close event"""
        reply = QMessageBox.question(
            self, "Exit Confirmation",
            "Are you sure you want to exit?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Save settings
            self.save_settings()
            event.accept()
        else:
            event.ignore()