"""
Settings Widget for SharePoint Migration Tool

This module provides a widget for configuring application settings,
including upload destination and operation mode.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QGroupBox, QRadioButton, 
                             QButtonGroup, QHBoxLayout, QLabel, QCheckBox,
                             QPushButton, QFrame, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal, QSettings


class SettingsWidget(QWidget):
    """
    Widget for configuring application settings, particularly related to
    file operations and SharePoint integration.
    """
    
    # Define signals
    settings_changed = pyqtSignal(dict)  # Signal when settings are changed
    
    def __init__(self, parent=None):
        super(SettingsWidget, self).__init__(parent)
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize the UI components."""
        main_layout = QVBoxLayout(self)
        
        # Create destination group
        destination_group = QGroupBox("Destination Mode")
        destination_layout = QVBoxLayout(destination_group)
        
        self.upload_radio = QRadioButton("Upload directly to SharePoint")
        self.upload_radio.setToolTip("Clean files and upload directly to SharePoint")
        
        self.local_radio = QRadioButton("Save to local directory")
        self.local_radio.setToolTip("Clean files and save to a local directory")
        
        # Set default
        self.local_radio.setChecked(True)
        
        # Group radio buttons
        self.destination_group = QButtonGroup(self)
        self.destination_group.addButton(self.upload_radio, 1)
        self.destination_group.addButton(self.local_radio, 2)
        self.destination_group.buttonClicked.connect(self.on_setting_changed)
        
        destination_layout.addWidget(self.upload_radio)
        destination_layout.addWidget(self.local_radio)
        
        # Create operation mode group
        operation_group = QGroupBox("Operation Mode")
        operation_layout = QVBoxLayout(operation_group)
        
        self.non_destructive_radio = QRadioButton("Non-destructive (copy files)")
        self.non_destructive_radio.setToolTip("Create copies of files with issues fixed")
        
        self.destructive_radio = QRadioButton("Destructive (modify original files)")
        self.destructive_radio.setToolTip("WARNING: This will modify the original files")
        
        # Set default
        self.non_destructive_radio.setChecked(True)
        
        # Group radio buttons
        self.operation_group = QButtonGroup(self)
        self.operation_group.addButton(self.non_destructive_radio, 1)
        self.operation_group.addButton(self.destructive_radio, 2)
        self.operation_group.buttonClicked.connect(self.on_setting_changed)
        
        operation_layout.addWidget(self.non_destructive_radio)
        operation_layout.addWidget(self.destructive_radio)
        
        # Add warning for destructive mode
        self.warning_frame = QFrame()
        self.warning_frame.setFrameShape(QFrame.StyledPanel)
        self.warning_frame.setStyleSheet("background-color: #FFEEEE; border: 1px solid #FF0000;")
        warning_layout = QHBoxLayout(self.warning_frame)
        
        warning_label = QLabel("⚠️ Warning: Destructive mode will modify your original files. Make backups first!")
        warning_label.setStyleSheet("color: #CC0000; font-weight: bold;")
        warning_layout.addWidget(warning_label)
        
        # Hide warning initially
        self.warning_frame.setVisible(False)
        
        # Add advanced options
        advanced_group = QGroupBox("Advanced Options")
        advanced_layout = QVBoxLayout(advanced_group)
        
        self.preserve_timestamps_check = QCheckBox("Preserve original timestamps")
        self.preserve_timestamps_check.setChecked(True)
        self.preserve_timestamps_check.stateChanged.connect(self.on_setting_changed)
        
        self.ignore_hidden_check = QCheckBox("Ignore hidden files and folders")
        self.ignore_hidden_check.setChecked(True)
        self.ignore_hidden_check.stateChanged.connect(self.on_setting_changed)
        
        advanced_layout.addWidget(self.preserve_timestamps_check)
        advanced_layout.addWidget(self.ignore_hidden_check)
        
        # Add save/reset buttons
        buttons_layout = QHBoxLayout()
        
        self.save_button = QPushButton("Save as Default")
        self.save_button.clicked.connect(self.save_settings)
        
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self.reset_settings)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.save_button)
        buttons_layout.addWidget(self.reset_button)
        
        # Add all widgets to main layout
        main_layout.addWidget(destination_group)
        main_layout.addWidget(operation_group)
        main_layout.addWidget(self.warning_frame)
        main_layout.addWidget(advanced_group)
        main_layout.addLayout(buttons_layout)
        main_layout.addStretch()
        
        # Connect signals for destructive mode warning
        self.destructive_radio.toggled.connect(self.toggle_warning)
    
    def toggle_warning(self, checked):
        """Show or hide the warning frame based on destructive mode selection"""
        self.warning_frame.setVisible(checked)
    
    def on_setting_changed(self, *args):
        """Handle setting changes and emit signal with new settings"""
        settings = self.get_current_settings()
        self.settings_changed.emit(settings)
    
    def get_current_settings(self):
        """Get the current settings as a dictionary"""
        return {
            'upload_to_sharepoint': self.upload_radio.isChecked(),
            'destructive_mode': self.destructive_radio.isChecked(),
            'preserve_timestamps': self.preserve_timestamps_check.isChecked(),
            'ignore_hidden': self.ignore_hidden_check.isChecked()
        }
    
    def save_settings(self):
        """Save current settings as default"""
        settings = QSettings()
        current = self.get_current_settings()
        
        settings.setValue("Settings/upload_to_sharepoint", current['upload_to_sharepoint'])
        settings.setValue("Settings/destructive_mode", current['destructive_mode'])
        settings.setValue("Settings/preserve_timestamps", current['preserve_timestamps'])
        settings.setValue("Settings/ignore_hidden", current['ignore_hidden'])
    
    def load_settings(self):
        """Load settings from saved defaults"""
        settings = QSettings()
        
        # Load destination mode
        upload_to_sharepoint = settings.value("Settings/upload_to_sharepoint", False, type=bool)
        if upload_to_sharepoint:
            self.upload_radio.setChecked(True)
        else:
            self.local_radio.setChecked(True)
        
        # Load operation mode
        destructive_mode = settings.value("Settings/destructive_mode", False, type=bool)
        if destructive_mode:
            self.destructive_radio.setChecked(True)
        else:
            self.non_destructive_radio.setChecked(True)
        
        # Update warning visibility
        self.warning_frame.setVisible(destructive_mode)
        
        # Load advanced options
        preserve_timestamps = settings.value("Settings/preserve_timestamps", True, type=bool)
        self.preserve_timestamps_check.setChecked(preserve_timestamps)
        
        ignore_hidden = settings.value("Settings/ignore_hidden", True, type=bool)
        self.ignore_hidden_check.setChecked(ignore_hidden)
    
    def reset_settings(self):
        """Reset settings to default values"""
        # Set defaults
        self.local_radio.setChecked(True)
        self.non_destructive_radio.setChecked(True)
        self.preserve_timestamps_check.setChecked(True)
        self.ignore_hidden_check.setChecked(True)
        
        # Update warning visibility
        self.warning_frame.setVisible(False)
        
        # Emit signal with new settings
        self.on_setting_changed()