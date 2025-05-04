from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QGridLayout, QGroupBox, QPushButton,
                           QRadioButton, QCheckBox, QButtonGroup, 
                           QFileDialog, QComboBox, QSpinBox,
                           QLineEdit, QTabWidget, QTextEdit, QScrollArea)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QIcon

class ExportWidget(QWidget):
    """
    Widget for exporting scan results in various formats.
    Provides configuration options for exports and preview functionality.
    """
    
    # Define signals
    export_requested = pyqtSignal(dict)  # Signal for export request with options
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.scan_results = None
        
    def init_ui(self):
        """Initialize the export widget UI components"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create tabs for different export options
        self.tabs = QTabWidget()
        
        # Create tabs for each export format
        self.report_tab = QWidget()
        self.data_tab = QWidget()
        self.summary_tab = QWidget()
        self.custom_tab = QWidget()
        
        # Setup tab contents
        self.setup_report_tab()
        self.setup_data_tab()
        self.setup_summary_tab()
        self.setup_custom_tab()
        
        # Add tabs to tab widget
        self.tabs.addTab(self.report_tab, "Report Export")
        self.tabs.addTab(self.data_tab, "Data Export")
        self.tabs.addTab(self.summary_tab, "Summary Export")
        self.tabs.addTab(self.custom_tab, "Custom Export")
        
        # Add tabs to main layout
        self.main_layout.addWidget(self.tabs)
        
        # Create preview panel
        self.preview_group = QGroupBox("Export Preview")
        preview_layout = QVBoxLayout(self.preview_group)
        
        # Add preview text box
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Export preview will appear here")
        preview_layout.addWidget(self.preview_text)
        
        # Add actions row
        actions_layout = QHBoxLayout()
        
        self.generate_preview_button = QPushButton("Generate Preview")
        self.generate_preview_button.clicked.connect(self.generate_preview)
        
        self.export_button = QPushButton("Export Now")
        self.export_button.clicked.connect(self.perform_export)
        self.export_button.setEnabled(False)
        
        actions_layout.addWidget(self.generate_preview_button)
        actions_layout.addStretch()
        actions_layout.addWidget(self.export_button)
        
        preview_layout.addLayout(actions_layout)
        
        # Add preview group to main layout
        self.main_layout.addWidget(self.preview_group)
        
    def setup_report_tab(self):
        """Setup the comprehensive report export tab"""
        layout = QVBoxLayout(self.report_tab)
        
        # Create description
        description = QLabel("Generate a comprehensive report of all scan results and issues")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create format options
        format_group = QGroupBox("Report Format")
        format_layout = QVBoxLayout(format_group)
        
        self.pdf_radio = QRadioButton("PDF Document")
        self.html_radio = QRadioButton("HTML Document")
        self.doc_radio = QRadioButton("Word Document")
        self.text_radio = QRadioButton("Text Document")
        
        self.pdf_radio.setChecked(True)
        
        format_layout.addWidget(self.pdf_radio)
        format_layout.addWidget(self.html_radio)
        format_layout.addWidget(self.doc_radio)
        format_layout.addWidget(self.text_radio)
        
        # Group radio buttons
        self.report_format_group = QButtonGroup(self)
        self.report_format_group.addButton(self.pdf_radio)
        self.report_format_group.addButton(self.html_radio)
        self.report_format_group.addButton(self.doc_radio)
        self.report_format_group.addButton(self.text_radio)
        
        layout.addWidget(format_group)
        
        # Create content options
        content_group = QGroupBox("Report Content")
        content_layout = QVBoxLayout(content_group)
        
        self.include_summary_check = QCheckBox("Include Summary Statistics")
        self.include_summary_check.setChecked(True)
        
        self.include_issues_check = QCheckBox("Include Detailed Issue Lists")
        self.include_issues_check.setChecked(True)
        
        self.include_charts_check = QCheckBox("Include Charts and Visualizations")
        self.include_charts_check.setChecked(True)
        
        self.include_recommendations_check = QCheckBox("Include Recommendations")
        self.include_recommendations_check.setChecked(True)
        
        content_layout.addWidget(self.include_summary_check)
        content_layout.addWidget(self.include_issues_check)
        content_layout.addWidget(self.include_charts_check)
        content_layout.addWidget(self.include_recommendations_check)
        
        layout.addWidget(content_group)
        
        # Add destination selector
        dest_group = QGroupBox("Destination")
        dest_layout = QHBoxLayout(dest_group)
        
        self.report_path_label = QLabel("Not selected")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_report_destination)
        
        dest_layout.addWidget(QLabel("Save to:"))
        dest_layout.addWidget(self.report_path_label, 1)
        dest_layout.addWidget(browse_button)
        
        layout.addWidget(dest_group)
        
        layout.addStretch()
    
    def setup_data_tab(self):
        """Setup the data export tab for raw data export"""
        layout = QVBoxLayout(self.data_tab)
        
        # Create description
        description = QLabel("Export raw scan data for use in other applications")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create format options
        format_group = QGroupBox("Data Format")
        format_layout = QVBoxLayout(format_group)
        
        self.csv_radio = QRadioButton("CSV File")
        self.excel_radio = QRadioButton("Excel Spreadsheet")
        self.json_radio = QRadioButton("JSON File")
        self.xml_radio = QRadioButton("XML File")
        
        self.csv_radio.setChecked(True)
        
        format_layout.addWidget(self.csv_radio)
        format_layout.addWidget(self.excel_radio)
        format_layout.addWidget(self.json_radio)
        format_layout.addWidget(self.xml_radio)
        
        # Group radio buttons
        self.data_format_group = QButtonGroup(self)
        self.data_format_group.addButton(self.csv_radio)
        self.data_format_group.addButton(self.excel_radio)
        self.data_format_group.addButton(self.json_radio)
        self.data_format_group.addButton(self.xml_radio)
        
        layout.addWidget(format_group)
        
        # Create content options
        content_group = QGroupBox("Data Content")
        content_layout = QVBoxLayout(content_group)
        
        self.export_all_files_check = QCheckBox("Export All Files")
        self.export_all_files_check.setChecked(True)
        
        self.export_only_issues_check = QCheckBox("Export Only Files With Issues")
        
        self.include_paths_check = QCheckBox("Include Full Paths")
        self.include_paths_check.setChecked(True)
        
        self.include_file_details_check = QCheckBox("Include File Details (size, type)")
        self.include_file_details_check.setChecked(True)
        
        content_layout.addWidget(self.export_all_files_check)
        content_layout.addWidget(self.export_only_issues_check)
        content_layout.addWidget(self.include_paths_check)
        content_layout.addWidget(self.include_file_details_check)
        
        # Connect checkboxes to handle mutual exclusion
        self.export_all_files_check.stateChanged.connect(self.handle_data_export_options)
        self.export_only_issues_check.stateChanged.connect(self.handle_data_export_options)
        
        layout.addWidget(content_group)
        
        # Add destination selector
        dest_group = QGroupBox("Destination")
        dest_layout = QHBoxLayout(dest_group)
        
        self.data_path_label = QLabel("Not selected")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_data_destination)
        
        dest_layout.addWidget(QLabel("Save to:"))
        dest_layout.addWidget(self.data_path_label, 1)
        dest_layout.addWidget(browse_button)
        
        layout.addWidget(dest_group)
        
        layout.addStretch()
    
    def setup_summary_tab(self):
        """Setup the summary export tab for executive summary"""
        layout = QVBoxLayout(self.summary_tab)
        
        # Create description
        description = QLabel("Generate a concise summary report of key findings")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create format options
        format_group = QGroupBox("Summary Format")
        format_layout = QVBoxLayout(format_group)
        
        self.summary_pdf_radio = QRadioButton("PDF Document")
        self.summary_text_radio = QRadioButton("Text Document")
        self.summary_email_radio = QRadioButton("Email Format")
        
        self.summary_pdf_radio.setChecked(True)
        
        format_layout.addWidget(self.summary_pdf_radio)
        format_layout.addWidget(self.summary_text_radio)
        format_layout.addWidget(self.summary_email_radio)
        
        # Group radio buttons
        self.summary_format_group = QButtonGroup(self)
        self.summary_format_group.addButton(self.summary_pdf_radio)
        self.summary_format_group.addButton(self.summary_text_radio)
        self.summary_format_group.addButton(self.summary_email_radio)
        
        layout.addWidget(format_group)
        
        # Create content options
        content_group = QGroupBox("Summary Content")
        content_layout = QVBoxLayout(content_group)
        
        self.summary_include_stats_check = QCheckBox("Include Statistics")
        self.summary_include_stats_check.setChecked(True)
        
        self.summary_include_chart_check = QCheckBox("Include Overview Chart")
        self.summary_include_chart_check.setChecked(True)
        
        self.summary_include_critical_check = QCheckBox("Include Critical Issues Only")
        self.summary_include_critical_check.setChecked(True)
        
        self.summary_include_timeline_check = QCheckBox("Include Estimated Fix Timeline")
        self.summary_include_timeline_check.setChecked(True)
        
        content_layout.addWidget(self.summary_include_stats_check)
        content_layout.addWidget(self.summary_include_chart_check)
        content_layout.addWidget(self.summary_include_critical_check)
        content_layout.addWidget(self.summary_include_timeline_check)
        
        layout.addWidget(content_group)
        
        # Add destination selector
        dest_group = QGroupBox("Destination")
        dest_layout = QHBoxLayout(dest_group)
        
        self.summary_path_label = QLabel("Not selected")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_summary_destination)
        
        dest_layout.addWidget(QLabel("Save to:"))
        dest_layout.addWidget(self.summary_path_label, 1)
        dest_layout.addWidget(browse_button)
        
        layout.addWidget(dest_group)
        
        layout.addStretch()
    
    def setup_custom_tab(self):
        """Setup the custom export tab for advanced options"""
        layout = QVBoxLayout(self.custom_tab)
        
        # Create description
        description = QLabel("Create a custom export with specific fields and formatting")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Create scroll area for many options
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        # Output format
        format_group = QGroupBox("Output Format")
        format_layout = QGridLayout(format_group)
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "Excel", "JSON", "XML", "Text", "HTML", "PDF"])
        
        self.delimiter_combo = QComboBox()
        self.delimiter_combo.addItems([",", ";", "Tab", "|", "Space"])
        
        self.encoding_combo = QComboBox()
        self.encoding_combo.addItems(["UTF-8", "ASCII", "ISO-8859-1", "Windows-1252"])
        
        # Add to layout
        format_layout.addWidget(QLabel("Format:"), 0, 0)
        format_layout.addWidget(self.format_combo, 0, 1)
        format_layout.addWidget(QLabel("Delimiter:"), 1, 0)
        format_layout.addWidget(self.delimiter_combo, 1, 1)
        format_layout.addWidget(QLabel("Encoding:"), 2, 0)
        format_layout.addWidget(self.encoding_combo, 2, 1)
        
        scroll_layout.addWidget(format_group)
        
        # Fields to include
        fields_group = QGroupBox("Fields to Include")
        fields_layout = QVBoxLayout(fields_group)
        
        self.include_field_filename = QCheckBox("Filename")
        self.include_field_path = QCheckBox("Full Path")
        self.include_field_size = QCheckBox("File Size")
        self.include_field_modified = QCheckBox("Modified Date")
        self.include_field_path_length = QCheckBox("Path Length")
        self.include_field_issue_count = QCheckBox("Issue Count")
        self.include_field_issue_types = QCheckBox("Issue Types")
        self.include_field_severity = QCheckBox("Severity")
        self.include_field_recommendations = QCheckBox("Recommendations")
        
        # Check all by default
        for field in [self.include_field_filename, self.include_field_path,
                     self.include_field_size, self.include_field_modified,
                     self.include_field_path_length, self.include_field_issue_count,
                     self.include_field_issue_types, self.include_field_severity,
                     self.include_field_recommendations]:
            field.setChecked(True)
            fields_layout.addWidget(field)
        
        scroll_layout.addWidget(fields_group)
        
        # Filtering options
        filter_group = QGroupBox("Filter Options")
        filter_layout = QVBoxLayout(filter_group)
        
        self.filter_only_issues = QCheckBox("Only Items with Issues")
        self.filter_min_severity = QCheckBox("Minimum Severity:")
        
        severity_layout = QHBoxLayout()
        self.severity_combo = QComboBox()
        self.severity_combo.addItems(["Critical", "Warning", "Info"])
        severity_layout.addWidget(self.severity_combo)
        severity_layout.addStretch()
        
        self.filter_issue_types = QCheckBox("Specific Issue Types:")
        
        issue_types_layout = QVBoxLayout()
        self.issue_type_path_length = QCheckBox("Path Length")
        self.issue_type_illegal_chars = QCheckBox("Illegal Characters")
        self.issue_type_reserved_names = QCheckBox("Reserved Names")
        self.issue_type_duplicates = QCheckBox("Duplicates")
        
        for issue_type in [self.issue_type_path_length, self.issue_type_illegal_chars,
                         self.issue_type_reserved_names, self.issue_type_duplicates]:
            issue_type.setChecked(True)
            issue_types_layout.addWidget(issue_type)
        
        filter_layout.addWidget(self.filter_only_issues)
        filter_layout.addWidget(self.filter_min_severity)
        filter_layout.addLayout(severity_layout)
        filter_layout.addWidget(self.filter_issue_types)
        filter_layout.addLayout(issue_types_layout)
        
        # Connect checkboxes to enable/disable options
        self.filter_min_severity.stateChanged.connect(
            lambda state: self.severity_combo.setEnabled(state == Qt.Checked))
        self.filter_issue_types.stateChanged.connect(
            lambda state: self.toggle_issue_type_checks(state == Qt.Checked))
        
        # Initial state
        self.severity_combo.setEnabled(False)
        
        scroll_layout.addWidget(filter_group)
        
        # Output options
        output_group = QGroupBox("Output Options")
        output_layout = QVBoxLayout(output_group)
        
        self.include_header_check = QCheckBox("Include Header Row")
        self.include_header_check.setChecked(True)
        
        self.pretty_format_check = QCheckBox("Pretty Format (JSON/XML)")
        self.pretty_format_check.setChecked(True)
        
        self.generate_stats_check = QCheckBox("Generate Statistics Page")
        self.generate_stats_check.setChecked(True)
        
        output_layout.addWidget(self.include_header_check)
        output_layout.addWidget(self.pretty_format_check)
        output_layout.addWidget(self.generate_stats_check)
        
        scroll_layout.addWidget(output_group)
        
        # Add destination selector
        dest_group = QGroupBox("Destination")
        dest_layout = QHBoxLayout(dest_group)
        
        self.custom_path_label = QLabel("Not selected")
        browse_button = QPushButton("Browse...")
        browse_button.clicked.connect(self.browse_custom_destination)
        
        dest_layout.addWidget(QLabel("Save to:"))
        dest_layout.addWidget(self.custom_path_label, 1)
        dest_layout.addWidget(browse_button)
        
        scroll_layout.addWidget(dest_group)
        scroll_layout.addStretch()
        
        # Set the scroll widget
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
    
    def toggle_issue_type_checks(self, enabled):
        """Enable or disable issue type checkboxes"""
        for issue_type in [self.issue_type_path_length, self.issue_type_illegal_chars,
                         self.issue_type_reserved_names, self.issue_type_duplicates]:
            issue_type.setEnabled(enabled)
    
    def handle_data_export_options(self, state):
        """Handle mutual exclusion between data export options"""
        sender = self.sender()
        
        if sender == self.export_all_files_check and state == Qt.Checked:
            self.export_only_issues_check.setChecked(False)
        elif sender == self.export_only_issues_check and state == Qt.Checked:
            self.export_all_files_check.setChecked(False)
    
    def browse_report_destination(self):
        """Open file dialog to select report destination"""
        # Determine file filter based on selected format
        if self.pdf_radio.isChecked():
            file_filter = "PDF Files (*.pdf)"
            default_ext = ".pdf"
        elif self.html_radio.isChecked():
            file_filter = "HTML Files (*.html)"
            default_ext = ".html"
        elif self.doc_radio.isChecked():
            file_filter = "Word Documents (*.docx)"
            default_ext = ".docx"
        else:  # Text
            file_filter = "Text Files (*.txt)"
            default_ext = ".txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Report As",
            "",
            file_filter
        )
        
        if file_path:
            # Ensure file has correct extension
            if not file_path.endswith(default_ext):
                file_path += default_ext
                
            self.report_path_label.setText(file_path)
    
    def browse_data_destination(self):
        """Open file dialog to select data export destination"""
        # Determine file filter based on selected format
        if self.csv_radio.isChecked():
            file_filter = "CSV Files (*.csv)"
            default_ext = ".csv"
        elif self.excel_radio.isChecked():
            file_filter = "Excel Files (*.xlsx)"
            default_ext = ".xlsx"
        elif self.json_radio.isChecked():
            file_filter = "JSON Files (*.json)"
            default_ext = ".json"
        else:  # XML
            file_filter = "XML Files (*.xml)"
            default_ext = ".xml"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Data Export As",
            "",
            file_filter
        )
        
        if file_path:
            # Ensure file has correct extension
            if not file_path.endswith(default_ext):
                file_path += default_ext
                
            self.data_path_label.setText(file_path)
    
    def browse_summary_destination(self):
        """Open file dialog to select summary destination"""
        # Determine file filter based on selected format
        if self.summary_pdf_radio.isChecked():
            file_filter = "PDF Files (*.pdf)"
            default_ext = ".pdf"
        elif self.summary_text_radio.isChecked():
            file_filter = "Text Files (*.txt)"
            default_ext = ".txt"
        else:  # Email
            file_filter = "HTML Files (*.html)"
            default_ext = ".html"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Summary As",
            "",
            file_filter
        )
        
        if file_path:
            # Ensure file has correct extension
            if not file_path.endswith(default_ext):
                file_path += default_ext
                
            self.summary_path_label.setText(file_path)
    
    def browse_custom_destination(self):
        """Open file dialog to select custom export destination"""
        # Determine file filter based on selected format
        format_text = self.format_combo.currentText().lower()
        
        if format_text == "csv":
            file_filter = "CSV Files (*.csv)"
            default_ext = ".csv"
        elif format_text == "excel":
            file_filter = "Excel Files (*.xlsx)"
            default_ext = ".xlsx"
        elif format_text == "json":
            file_filter = "JSON Files (*.json)"
            default_ext = ".json"
        elif format_text == "xml":
            file_filter = "XML Files (*.xml)"
            default_ext = ".xml"
        elif format_text == "text":
            file_filter = "Text Files (*.txt)"
            default_ext = ".txt"
        elif format_text == "html":
            file_filter = "HTML Files (*.html)"
            default_ext = ".html"
        else:  # PDF
            file_filter = "PDF Files (*.pdf)"
            default_ext = ".pdf"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Custom Export As",
            "",
            file_filter
        )
        
        if file_path:
            # Ensure file has correct extension
            if not file_path.endswith(default_ext):
                file_path += default_ext
                
            self.custom_path_label.setText(file_path)
    
    def generate_preview(self):
        """Generate a preview of the export"""
        if not self.scan_results:
            self.preview_text.setText("No scan results available for preview")
            return
        
        # Get the current tab to determine export type
        current_tab_index = self.tabs.currentIndex()
        tab_text = self.tabs.tabText(current_tab_index)
        
        preview_text = f"Preview of {tab_text}\n\n"
        
        if tab_text == "Report Export":
            preview_text += self.generate_report_preview()
        elif tab_text == "Data Export":
            preview_text += self.generate_data_preview()
        elif tab_text == "Summary Export":
            preview_text += self.generate_summary_preview()
        else:  # Custom Export
            preview_text += self.generate_custom_preview()
        
        # Set preview text
        self.preview_text.setText(preview_text)
        
        # Enable export button
        self.export_button.setEnabled(True)
    
    def generate_report_preview(self):
        """Generate a preview of the report export"""
        preview = "=== SHAREPOINT MIGRATION SCAN REPORT ===\n\n"
        
        # Add summary if selected
        if self.include_summary_check.isChecked():
            preview += "--- Summary Statistics ---\n"
            preview += f"Total Files: {self.scan_results.get('total_files', 0)}\n"
            preview += f"Total Folders: {self.scan_results.get('total_folders', 0)}\n"
            preview += f"Total Size: {self.format_size(self.scan_results.get('total_size', 0))}\n"
            preview += f"Total Issues: {self.scan_results.get('total_issues', 0)}\n\n"
        
        # Add issues if selected
        if self.include_issues_check.isChecked():
            preview += "--- Issue Summary ---\n"
            
            # Path length issues
            path_length_issues = self.scan_results.get('path_length_issues', {})
            total_path_issues = sum(len(files) for files in path_length_issues.values())
            preview += f"Path Length Issues: {total_path_issues}\n"
            
            # Illegal character issues
            illegal_chars = self.scan_results.get('illegal_characters', {})
            total_illegal_chars = sum(len(files) for files in illegal_chars.values())
            preview += f"Illegal Character Issues: {total_illegal_chars}\n"
            
            # Reserved name issues
            reserved_names = self.scan_results.get('reserved_names', {})
            total_reserved = sum(len(files) for files in reserved_names.values())
            preview += f"Reserved Name Issues: {total_reserved}\n"
            
            # Duplicate issues
            duplicates = self.scan_results.get('duplicates', {})
            total_duplicates = sum(max(0, len(files) - 1) for files in duplicates.values())
            preview += f"Duplicate Files: {total_duplicates}\n\n"
        
        # Add charts placeholder if selected
        if self.include_charts_check.isChecked():
            preview += "--- Charts and Visualizations ---\n"
            preview += "[Chart: Issue Type Distribution]\n"
            preview += "[Chart: Path Length Distribution]\n"
            preview += "[Chart: File Type Distribution]\n\n"
        
        # Add recommendations if selected
        if self.include_recommendations_check.isChecked():
            preview += "--- Recommendations ---\n"
            preview += "1. Fix path length issues by relocating deep folder structures\n"
            preview += "2. Rename files with illegal characters\n"
            preview += "3. Address reserved name conflicts\n"
            preview += "4. Consolidate duplicate files\n\n"
        
        # Add file format info
        if self.pdf_radio.isChecked():
            preview += "[This report will be exported as a PDF document]\n"
        elif self.html_radio.isChecked():
            preview += "[This report will be exported as an HTML document]\n"
        elif self.doc_radio.isChecked():
            preview += "[This report will be exported as a Word document]\n"
        else:
            preview += "[This report will be exported as a Text document]\n"
        
        # Add destination info if selected
        destination = self.report_path_label.text()
        if destination and destination != "Not selected":
            preview += f"Export destination: {destination}\n"
        
        return preview
    
    def generate_data_preview(self):
        """Generate a preview of the data export"""
        preview = "=== DATA EXPORT PREVIEW ===\n\n"
        
        # Determine format
        if self.csv_radio.isChecked():
            format_str = "CSV"
            delimiter = ","
        elif self.excel_radio.isChecked():
            format_str = "Excel"
            delimiter = "\t"  # For preview purposes
        elif self.json_radio.isChecked():
            format_str = "JSON"
            delimiter = None
        else:  # XML
            format_str = "XML"
            delimiter = None
        
        # Generate header row for tabular formats
        if format_str in ["CSV", "Excel"]:
            headers = []
            
            if self.include_paths_check.isChecked():
                headers.append("Path")
            
            headers.append("Filename")
            
            if self.include_file_details_check.isChecked():
                headers.append("Size")
                headers.append("Type")
            
            headers.append("Has Issues")
            headers.append("Issue Count")
            headers.append("Issue Types")
            
            # Add header row
            preview += delimiter.join(headers) + "\n"
            
            # Add sample data rows (limit to 5 for preview)
            file_structure = self.scan_results.get('file_structure', {})
            
            # Collect all files
            all_files = []
            for parent_path, children in file_structure.items():
                if 'files' in children:
                    for file_info in children['files']:
                        # Include only files with issues if that option is selected
                        if (self.export_only_issues_check.isChecked() and 
                            ('issues' not in file_info or not file_info['issues'])):
                            continue
                        
                        all_files.append(file_info)
            
            # Add sample rows (limit to 5)
            for i, file_info in enumerate(all_files[:5]):
                row = []
                
                if self.include_paths_check.isChecked():
                    row.append(file_info.get('path', ''))
                
                row.append(file_info.get('name', ''))
                
                if self.include_file_details_check.isChecked():
                    row.append(self.format_size(file_info.get('size', 0)))
                    row.append(file_info.get('type', ''))
                
                has_issues = 'issues' in file_info and file_info['issues']
                row.append("Yes" if has_issues else "No")
                
                issue_count = len(file_info.get('issues', []))
                row.append(str(issue_count))
                
                issue_types = ", ".join([issue['type'] for issue in file_info.get('issues', [])])
                row.append(issue_types)
                
                preview += delimiter.join(row) + "\n"
            
            # Add note if more files exist
            if len(all_files) > 5:
                preview += f"... and {len(all_files) - 5} more files\n"
            
        elif format_str == "JSON":
            # Generate JSON preview
            preview += "{\n"
            preview += '  "scan_results": {\n'
            preview += f'    "total_files": {self.scan_results.get("total_files", 0)},\n'
            preview += f'    "total_folders": {self.scan_results.get("total_folders", 0)},\n'
            preview += f'    "total_issues": {self.scan_results.get("total_issues", 0)},\n'
            preview += '    "files": [\n'
            preview += '      { "file1": "details..." },\n'
            preview += '      { "file2": "details..." },\n'
            preview += '      ...\n'
            preview += '    ]\n'
            preview += '  }\n'
            preview += '}\n'
        else:  # XML
            # Generate XML preview
            preview += '<?xml version="1.0" encoding="UTF-8"?>\n'
            preview += '<scan_results>\n'
            preview += f'  <total_files>{self.scan_results.get("total_files", 0)}</total_files>\n'
            preview += f'  <total_folders>{self.scan_results.get("total_folders", 0)}</total_folders>\n'
            preview += f'  <total_issues>{self.scan_results.get("total_issues", 0)}</total_issues>\n'
            preview += '  <files>\n'
            preview += '    <file path="...">\n'
            preview += '      <name>...</name>\n'
            preview += '      <size>...</size>\n'
            preview += '      <issues>...</issues>\n'
            preview += '    </file>\n'
            preview += '    ...\n'
            preview += '  </files>\n'
            preview += '</scan_results>\n'
        
        # Add export info
        preview += f"\n[This data will be exported as a {format_str} file"
        
        # Add destination info if selected
        destination = self.data_path_label.text()
        if destination and destination != "Not selected":
            preview += f" to: {destination}"
        
        preview += "]\n"
        
        return preview
    
    def generate_summary_preview(self):
        """Generate a preview of the summary export"""
        preview = "=== EXECUTIVE SUMMARY ===\n\n"
        
        # Add title and date
        from datetime import datetime
        today = datetime.now().strftime("%B %d, %Y")
        preview += f"SharePoint Migration Scan Summary - {today}\n\n"
        
        # Add statistics if selected
        if self.summary_include_stats_check.isChecked():
            preview += "--- Key Statistics ---\n"
            preview += f"Total Files: {self.scan_results.get('total_files', 0)}\n"
            preview += f"Total Size: {self.format_size(self.scan_results.get('total_size', 0))}\n"
            preview += f"Total Issues: {self.scan_results.get('total_issues', 0)}\n\n"
        
        # Add chart placeholder if selected
        if self.summary_include_chart_check.isChecked():
            preview += "--- Overview Chart ---\n"
            preview += "[Chart: Issue Distribution by Type]\n\n"
        
        # Add critical issues if selected
        if self.summary_include_critical_check.isChecked():
            preview += "--- Critical Issues ---\n"
            
            # Get critical issues
            critical_issues = []
            
            # Path length issues over 250 characters
            path_length_issues = self.scan_results.get('path_length_issues', {})
            for length, files in path_length_issues.items():
                if int(length) > 250:
                    critical_issues.append(
                        f"Path Length > 250 chars: {len(files)} files"
                    )
            
            # Reserved names
            reserved_names = self.scan_results.get('reserved_names', {})
            total_reserved = sum(len(files) for files in reserved_names.values())
            if total_reserved > 0:
                critical_issues.append(
                    f"Reserved Names: {total_reserved} files"
                )
            
            # Illegal chars (* ? : etc.)
            critical_chars = ['*', '?', ':', '\\', '/', '|', '<', '>', '"']
            illegal_chars = self.scan_results.get('illegal_characters', {})
            critical_char_count = sum(
                len(files) for char, files in illegal_chars.items() 
                if char in critical_chars
            )
            if critical_char_count > 0:
                critical_issues.append(
                    f"Critical Illegal Characters: {critical_char_count} files"
                )
            
            # Add issues to preview
            if critical_issues:
                for issue in critical_issues:
                    preview += f"• {issue}\n"
            else:
                preview += "No critical issues found.\n"
            
            preview += "\n"
        
        # Add timeline if selected
        if self.summary_include_timeline_check.isChecked():
            preview += "--- Estimated Fix Timeline ---\n"
            
            # Calculate estimated time
            total_issues = self.scan_results.get('total_issues', 0)
            
            # Rough estimate: 5 minutes per issue
            total_minutes = total_issues * 5
            
            if total_minutes < 60:
                timeline = f"Less than 1 hour"
            elif total_minutes < 480:  # 8 hours
                hours = total_minutes // 60
                timeline = f"Approximately {hours} hour{'s' if hours > 1 else ''}"
            else:
                days = total_minutes // 480  # 8-hour work days
                timeline = f"Approximately {days} day{'s' if days > 1 else ''}"
            
            preview += f"Estimated fix time: {timeline}\n\n"
        
        # Add format info
        if self.summary_pdf_radio.isChecked():
            format_str = "PDF"
        elif self.summary_text_radio.isChecked():
            format_str = "Text"
        else:
            format_str = "Email-compatible HTML"
        
        preview += f"[This summary will be exported as a {format_str} document"
        
        # Add destination info if selected
        destination = self.summary_path_label.text()
        if destination and destination != "Not selected":
            preview += f" to: {destination}"
        
        preview += "]\n"
        
        return preview
    
    def generate_custom_preview(self):
        """Generate a preview of the custom export"""
        preview = "=== CUSTOM EXPORT PREVIEW ===\n\n"
        
        # Get selected format
        format_str = self.format_combo.currentText()
        
        # Add format-specific preview
        if format_str in ["CSV", "Excel"]:
            # Determine which fields to include
            fields = []
            
            if self.include_field_filename.isChecked():
                fields.append("Filename")
            
            if self.include_field_path.isChecked():
                fields.append("Full Path")
            
            if self.include_field_size.isChecked():
                fields.append("File Size")
            
            if self.include_field_modified.isChecked():
                fields.append("Modified Date")
            
            if self.include_field_path_length.isChecked():
                fields.append("Path Length")
            
            if self.include_field_issue_count.isChecked():
                fields.append("Issue Count")
            
            if self.include_field_issue_types.isChecked():
                fields.append("Issue Types")
            
            if self.include_field_severity.isChecked():
                fields.append("Severity")
            
            if self.include_field_recommendations.isChecked():
                fields.append("Recommendations")
            
            # Get delimiter
            delimiter_text = self.delimiter_combo.currentText()
            if delimiter_text == "Tab":
                delimiter = "\t"
            elif delimiter_text == "Space":
                delimiter = " "
            else:
                delimiter = delimiter_text
            
            # Add header if selected
            if self.include_header_check.isChecked():
                preview += delimiter.join(fields) + "\n"
            
            # Add sample rows
            preview += f"file1.docx{delimiter}C:\\path\\to\\file1.docx{delimiter}..."
            if len(fields) > 2:
                preview += f"{delimiter}..." * (len(fields) - 2)
            preview += "\n"
            
            preview += f"file2.xlsx{delimiter}C:\\path\\to\\file2.xlsx{delimiter}..."
            if len(fields) > 2:
                preview += f"{delimiter}..." * (len(fields) - 2)
            preview += "\n"
        
        elif format_str == "JSON":
            # Add JSON preview
            preview += "{\n"
            
            # Add pretty formatting if selected
            if self.pretty_format_check.isChecked():
                indent = "  "
                preview += f"{indent}\"export_data\": [\n"
                preview += f"{indent}{indent}{{\n"
                
                # Add fields based on selection
                if self.include_field_filename.isChecked():
                    preview += f"{indent}{indent}{indent}\"filename\": \"file1.docx\",\n"
                
                if self.include_field_path.isChecked():
                    preview += f"{indent}{indent}{indent}\"path\": \"C:\\\\path\\\\to\\\\file1.docx\",\n"
                
                # Add more fields with ellipsis
                preview += f"{indent}{indent}{indent}...\n"
                
                preview += f"{indent}{indent}}},\n"
                preview += f"{indent}{indent}...\n"
                preview += f"{indent}]\n"
            else:
                preview += "  \"export_data\":[{\"filename\":\"file1.docx\",\"path\":\"C:\\\\path\\\\to\\\\file1.docx\",...},...]"
            
            preview += "}\n"
        
        elif format_str == "XML":
            # Add XML preview
            preview += '<?xml version="1.0" encoding="UTF-8"?>\n'
            
            # Add pretty formatting if selected
            if self.pretty_format_check.isChecked():
                preview += '<export_data>\n'
                preview += '  <file>\n'
                
                # Add fields based on selection
                if self.include_field_filename.isChecked():
                    preview += '    <filename>file1.docx</filename>\n'
                
                if self.include_field_path.isChecked():
                    preview += '    <path>C:\\path\\to\\file1.docx</path>\n'
                
                # Add more fields with ellipsis
                preview += '    ...\n'
                
                preview += '  </file>\n'
                preview += '  ...\n'
                preview += '</export_data>\n'
            else:
                preview += '<export_data><file><filename>file1.docx</filename>...</file>...</export_data>\n'
        
        else:
            # Text, HTML, PDF
            preview += f"Custom {format_str} export preview\n"
            preview += "This would include:\n"
            
            # List selected fields
            if self.include_field_filename.isChecked():
                preview += "- Filename\n"
            
            if self.include_field_path.isChecked():
                preview += "- Full Path\n"
            
            # List more fields with ellipsis
            preview += "- ...\n"
        
        # Add filter info
        preview += "\nFilters applied:\n"
        
        if self.filter_only_issues.isChecked():
            preview += "- Only items with issues\n"
        
        if self.filter_min_severity.isChecked():
            severity = self.severity_combo.currentText()
            preview += f"- Minimum severity: {severity}\n"
        
        if self.filter_issue_types.isChecked():
            preview += "- Specific issue types:\n"
            
            if self.issue_type_path_length.isChecked():
                preview += "  • Path Length\n"
            
            if self.issue_type_illegal_chars.isChecked():
                preview += "  • Illegal Characters\n"
            
            if self.issue_type_reserved_names.isChecked():
                preview += "  • Reserved Names\n"
            
            if self.issue_type_duplicates.isChecked():
                preview += "  • Duplicates\n"
        
        # Add format info
        preview += f"\n[This data will be exported as a {format_str} file"
        
        # Add destination info if selected
        destination = self.custom_path_label.text()
        if destination and destination != "Not selected":
            preview += f" to: {destination}"
        
        preview += "]\n"
        
        return preview
    
    def perform_export(self):
        """Perform the actual export operation"""
        # Get the current tab to determine export type
        current_tab_index = self.tabs.currentIndex()
        tab_text = self.tabs.tabText(current_tab_index)
        
        # Create options dictionary to pass to backend
        export_options = {
            'type': tab_text.replace(' Export', '').lower(),
            'destination': '',
            'format': '',
            'options': {}
        }
        
        # Set destination and format based on tab
        if tab_text == "Report Export":
            export_options['destination'] = self.report_path_label.text()
            
            if self.pdf_radio.isChecked():
                export_options['format'] = 'pdf'
            elif self.html_radio.isChecked():
                export_options['format'] = 'html'
            elif self.doc_radio.isChecked():
                export_options['format'] = 'docx'
            else:  # Text
                export_options['format'] = 'txt'
            
            # Add report-specific options
            export_options['options'] = {
                'include_summary': self.include_summary_check.isChecked(),
                'include_issues': self.include_issues_check.isChecked(),
                'include_charts': self.include_charts_check.isChecked(),
                'include_recommendations': self.include_recommendations_check.isChecked()
            }
            
        elif tab_text == "Data Export":
            export_options['destination'] = self.data_path_label.text()
            
            if self.csv_radio.isChecked():
                export_options['format'] = 'csv'
            elif self.excel_radio.isChecked():
                export_options['format'] = 'xlsx'
            elif self.json_radio.isChecked():
                export_options['format'] = 'json'
            else:  # XML
                export_options['format'] = 'xml'
            
            # Add data-specific options
            export_options['options'] = {
                'export_all_files': self.export_all_files_check.isChecked(),
                'export_only_issues': self.export_only_issues_check.isChecked(),
                'include_paths': self.include_paths_check.isChecked(),
                'include_file_details': self.include_file_details_check.isChecked()
            }
            
        elif tab_text == "Summary Export":
            export_options['destination'] = self.summary_path_label.text()
            
            if self.summary_pdf_radio.isChecked():
                export_options['format'] = 'pdf'
            elif self.summary_text_radio.isChecked():
                export_options['format'] = 'txt'
            else:  # Email
                export_options['format'] = 'html'
            
            # Add summary-specific options
            export_options['options'] = {
                'include_stats': self.summary_include_stats_check.isChecked(),
                'include_chart': self.summary_include_chart_check.isChecked(),
                'include_critical': self.summary_include_critical_check.isChecked(),
                'include_timeline': self.summary_include_timeline_check.isChecked()
            }
            
        else:  # Custom Export
            export_options['destination'] = self.custom_path_label.text()
            export_options['format'] = self.format_combo.currentText().lower()
            
            # Add custom-specific options
            field_options = {}
            if self.include_field_filename.isChecked():
                field_options['filename'] = True
            if self.include_field_path.isChecked():
                field_options['path'] = True
            if self.include_field_size.isChecked():
                field_options['size'] = True
            if self.include_field_modified.isChecked():
                field_options['modified'] = True
            if self.include_field_path_length.isChecked():
                field_options['path_length'] = True
            if self.include_field_issue_count.isChecked():
                field_options['issue_count'] = True
            if self.include_field_issue_types.isChecked():
                field_options['issue_types'] = True
            if self.include_field_severity.isChecked():
                field_options['severity'] = True
            if self.include_field_recommendations.isChecked():
                field_options['recommendations'] = True
            
            filter_options = {}
            if self.filter_only_issues.isChecked():
                filter_options['only_issues'] = True
            if self.filter_min_severity.isChecked():
                filter_options['min_severity'] = self.severity_combo.currentText()
            if self.filter_issue_types.isChecked():
                issue_types = []
                if self.issue_type_path_length.isChecked():
                    issue_types.append('path_length')
                if self.issue_type_illegal_chars.isChecked():
                    issue_types.append('illegal_chars')
                if self.issue_type_reserved_names.isChecked():
                    issue_types.append('reserved_names')
                if self.issue_type_duplicates.isChecked():
                    issue_types.append('duplicates')
                filter_options['issue_types'] = issue_types
            
            format_options = {
                'delimiter': self.delimiter_combo.currentText(),
                'encoding': self.encoding_combo.currentText(),
                'include_header': self.include_header_check.isChecked(),
                'pretty_format': self.pretty_format_check.isChecked(),
                'generate_stats': self.generate_stats_check.isChecked()
            }
            
            export_options['options'] = {
                'fields': field_options,
                'filters': filter_options,
                'format_options': format_options
            }
        
        # Validate destination
        if not export_options['destination'] or export_options['destination'] == "Not selected":
            self.preview_text.setText("Please select a destination file before exporting")
            return
        
        # Emit signal to perform export
        self.export_requested.emit(export_options)
        
        # Show confirmation
        self.preview_text.setText(f"Export initiated.\nExporting to: {export_options['destination']}")
    
    def update_with_results(self, results):
        """Update the export widget with scan results"""
        self.scan_results = results
        
        # Clear preview
        self.preview_text.setText("Scan results loaded. Generate a preview to see export format.")
        
        # Disable export button until preview is generated
        self.export_button.setEnabled(False)
    
    def format_size(self, size_bytes):
        """Format size in bytes to human-readable string"""
        if size_bytes < 1024:
            return f"{size_bytes} bytes"
        elif size_bytes < 1024*1024:
            return f"{size_bytes/1024:.1f} KB"
        elif size_bytes < 1024*1024*1024:
            return f"{size_bytes/(1024*1024):.1f} MB"
        else:
            return f"{size_bytes/(1024*1024*1024):.2f} GB"