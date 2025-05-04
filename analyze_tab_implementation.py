def create_analyze_tab(self):
    """Create the analyze tab with detailed analysis views"""
    try:
        # Create tab widget
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Import analyzer widget
        try:
            from ui.analyzer_widget import AnalyzerWidget
            self.analyzer_widget = AnalyzerWidget()
            layout.addWidget(self.analyzer_widget)
            logger.info("Analyzer widget loaded successfully")
        except ImportError as e:
            logger.error(f"Error importing AnalyzerWidget: {e}")
            # Fallback to simpler implementation if custom widget not available
            self._create_fallback_analyze_tab(layout)
        
        return tab
    except Exception as e:
        logger.error(f"Error creating analyze tab: {e}")
        # Create an error tab
        error_tab = QWidget()
        error_layout = QVBoxLayout(error_tab)
        error_layout.addWidget(QLabel(f"Error creating analyze tab: {str(e)}"))
        return error_tab
    
def _create_fallback_analyze_tab(self, layout):
    """Create a fallback analyze tab if AnalyzerWidget is not available"""
    # Create a splitter for resizable sections
    splitter = QSplitter(Qt.Vertical)
    
    # --- Summary section ---
    summary_group = QGroupBox("Scan Summary")
    summary_layout = QVBoxLayout(summary_group)
    
    # Create data labels
    self.total_files_label = QLabel("Total Files: 0")
    self.total_folders_label = QLabel("Total Folders: 0")
    self.total_size_label = QLabel("Total Size: 0 B")
    self.total_issues_label = QLabel("Total Issues: 0")
    
    # Add to layout
    summary_layout.addWidget(self.total_files_label)
    summary_layout.addWidget(self.total_folders_label)
    summary_layout.addWidget(self.total_size_label)
    summary_layout.addWidget(self.total_issues_label)
    
    splitter.addWidget(summary_group)
    
    # --- Issue details section ---
    issues_group = QGroupBox("Issues Found")
    issues_layout = QVBoxLayout(issues_group)
    
    # Create table for issues
    self.issues_table = QTableView()
    self.issues_model = QStandardItemModel()
    self.issues_model.setHorizontalHeaderLabels(["Issue Type", "Count", "Severity", "Description"])
    self.issues_table.setModel(self.issues_model)
    self.issues_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    self.issues_table.horizontalHeader().setStretchLastSection(True)
    
    issues_layout.addWidget(self.issues_table)
    issues_group.setLayout(issues_layout)
    splitter.addWidget(issues_group)
    
    # --- File issues section ---
    files_group = QGroupBox("Files with Issues")
    files_layout = QVBoxLayout(files_group)
    
    # Create table for files with issues
    self.files_table = QTableView()
    self.files_model = QStandardItemModel()
    self.files_model.setHorizontalHeaderLabels(["Filename", "Path", "Issue Count", "Issue Types"])
    self.files_table.setModel(self.files_model)
    self.files_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
    self.files_table.horizontalHeader().setStretchLastSection(True)
    
    files_layout.addWidget(self.files_table)
    files_group.setLayout(files_layout)
    splitter.addWidget(files_group)
    
    # Add analyze button for running custom analysis
    button_layout = QHBoxLayout()
    
    self.analyze_button = QPushButton("Run Analysis")
    self.analyze_button.clicked.connect(self.run_analysis)
    button_layout.addWidget(self.analyze_button)
    
    self.export_analysis_button = QPushButton("Export Analysis")
    self.export_analysis_button.clicked.connect(self.export_analysis)
    self.export_analysis_button.setEnabled(False)
    button_layout.addWidget(self.export_analysis_button)
    
    # Add splitter to layout
    layout.addWidget(splitter)
    layout.addLayout(button_layout)

def run_analysis(self):
    """Run analysis on the scanned data"""
    try:
        # Check if we have scan data
        scan_data = self.data_processor.get_scan_data()
        if scan_data is None or len(scan_data) == 0:
            QMessageBox.warning(self, "No Data", 
                              "No scan data available. Please scan files first.")
            return
        
        # Enable export button
        self.export_analysis_button.setEnabled(True)
        
        # Get analysis results
        analysis_results = self.data_processor.get_analysis_results()
        
        # Update summary data
        total_files = len(scan_data)
        self.total_files_label.setText(f"Total Files: {total_files}")
        
        # Get folder count from scan_data (approximate)
        total_folders = sum(1 for _, row in scan_data.iterrows() if row.get('is_folder', False))
        self.total_folders_label.setText(f"Total Folders: {total_folders}")
        
        # Get total size from scan_data
        total_size = sum(row.get('size', 0) for _, row in scan_data.iterrows())
        size_text = self._format_size(total_size)
        self.total_size_label.setText(f"Total Size: {size_text}")
        
        # Get total issues
        total_issues = sum(len(issues) for issues in analysis_results.values() if isinstance(issues, (list, dict)))
        self.total_issues_label.setText(f"Total Issues: {total_issues}")
        
        # Update issues table
        self.issues_model.removeRows(0, self.issues_model.rowCount())
        
        issue_counts = {}
        for issue_type, issues in analysis_results.items():
            if not isinstance(issues, (list, dict)) or not issues:
                continue
                
            count = len(issues)
            issue_counts[issue_type] = count
            
            severity = "Critical" if issue_type in ["path_length", "reserved_names"] else "Warning"
            description = self._get_issue_description(issue_type)
            
            row = [
                QStandardItem(issue_type),
                QStandardItem(str(count)),
                QStandardItem(severity),
                QStandardItem(description)
            ]
            
            # Set color based on severity
            if severity == "Critical":
                row[2].setBackground(QColor(255, 200, 200))  # Light red
            else:
                row[2].setBackground(QColor(255, 255, 200))  # Light yellow
                
            self.issues_model.appendRow(row)
        
        # Update files table
        self.files_model.removeRows(0, self.files_model.rowCount())
        
        # Collect files with issues
        files_with_issues = {}
        for issue_type, issues in analysis_results.items():
            if not isinstance(issues, (list, dict)) or not issues:
                continue
                
            # Different issue types have different structures
            if issue_type == 'name_issues':
                for _, row in issues.iterrows():
                    path = row.get('path', '')
                    if path:
                        if path not in files_with_issues:
                            files_with_issues[path] = {'count': 0, 'types': set()}
                        files_with_issues[path]['count'] += 1
                        files_with_issues[path]['types'].add('Name Issue')
            elif issue_type == 'path_issues':
                for _, row in issues.iterrows():
                    path = row.get('path', '')
                    if path:
                        if path not in files_with_issues:
                            files_with_issues[path] = {'count': 0, 'types': set()}
                        files_with_issues[path]['count'] += 1
                        files_with_issues[path]['types'].add('Path Length')
            elif issue_type == 'duplicates':
                for _, row in issues.iterrows():
                    path = row.get('path', '')
                    if path:
                        if path not in files_with_issues:
                            files_with_issues[path] = {'count': 0, 'types': set()}
                        files_with_issues[path]['count'] += 1
                        files_with_issues[path]['types'].add('Duplicate')
            elif issue_type == 'pii':
                for _, row in issues.iterrows():
                    path = row.get('path', '')
                    if path:
                        if path not in files_with_issues:
                            files_with_issues[path] = {'count': 0, 'types': set()}
                        files_with_issues[path]['count'] += 1
                        files_with_issues[path]['types'].add('PII')
        
        # Add files to table
        for path, info in files_with_issues.items():
            filename = os.path.basename(path)
            count = info['count']
            types = ', '.join(info['types'])
            
            row = [
                QStandardItem(filename),
                QStandardItem(path),
                QStandardItem(str(count)),
                QStandardItem(types)
            ]
            
            # Highlight row based on issue count
            if count > 1:
                for item in row:
                    item.setBackground(QColor(255, 240, 240))  # Very light red
            
            self.files_model.appendRow(row)
        
        # If analyzer_widget exists, update it too
        if hasattr(self, 'analyzer_widget'):
            self.analyzer_widget.update_with_results(analysis_results)
        
    except Exception as e:
        logger.error(f"Error running analysis: {e}")
        QMessageBox.critical(self, "Analysis Error", 
                           f"Error running analysis: {str(e)}")

def _format_size(self, size_bytes):
    """Format size in bytes to human-readable string"""
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024*1024:
        return f"{size_bytes/1024:.1f} KB"
    elif size_bytes < 1024*1024*1024:
        return f"{size_bytes/(1024*1024):.1f} MB"
    else:
        return f"{size_bytes/(1024*1024*1024):.2f} GB"

def _get_issue_description(self, issue_type):
    """Get a description for an issue type"""
    descriptions = {
        'name_issues': 'Files with names that violate SharePoint naming rules',
        'path_issues': 'Files with paths exceeding SharePoint\'s 256 character limit',
        'duplicates': 'Files with identical content found in multiple locations',
        'pii': 'Files potentially containing personally identifiable information',
        'path_length': 'Files with paths exceeding SharePoint\'s 256 character limit',
        'illegal_chars': 'Files with names containing characters not allowed in SharePoint',
        'reserved_names': 'Files with names that match SharePoint reserved names',
        'illegal_prefix': 'Files with names starting with illegal prefixes',
        'illegal_suffix': 'Files with names ending with illegal suffixes'
    }
    
    return descriptions.get(issue_type, 'General issue')

def export_analysis(self):
    """Export analysis results to a file"""
    try:
        # Check if we have analysis data
        analysis_results = self.data_processor.get_analysis_results()
        if not analysis_results:
            QMessageBox.warning(self, "No Data", 
                              "No analysis results available. Please run analysis first.")
            return
        
        # Ask for save location
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Analysis Results",
            "",
            "CSV Files (*.csv);;Excel Files (*.xlsx);;HTML Files (*.html);;Text Files (*.txt)"
        )
        
        if not file_path:
            return
            
        # Determine export format based on extension
        export_format = os.path.splitext(file_path)[1].lower()
        
        # Create a report from analysis results
        report_data = []
        
        # Add summary data
        scan_data = self.data_processor.get_scan_data()
        total_files = len(scan_data) if scan_data is not None else 0
        
        # Get folder count from scan_data (approximate)
        total_folders = sum(1 for _, row in scan_data.iterrows() if row.get('is_folder', False)) if scan_data is not None else 0
        
        # Get total size from scan_data
        total_size = sum(row.get('size', 0) for _, row in scan_data.iterrows()) if scan_data is not None else 0
        size_text = self._format_size(total_size)
        
        # Get total issues
        total_issues = sum(len(issues) for issues in analysis_results.values() if isinstance(issues, (list, dict)))
        
        # Add summary to report
        report_data.append(["Summary", "", "", ""])
        report_data.append(["Total Files", str(total_files), "", ""])
        report_data.append(["Total Folders", str(total_folders), "", ""])
        report_data.append(["Total Size", size_text, "", ""])
        report_data.append(["Total Issues", str(total_issues), "", ""])
        report_data.append(["", "", "", ""])  # Empty row
        
        # Add issue summary
        report_data.append(["Issue Summary", "", "", ""])
        report_data.append(["Issue Type", "Count", "Severity", "Description"])
        
        for issue_type, issues in analysis_results.items():
            if not isinstance(issues, (list, dict)) or not issues:
                continue
                
            count = len(issues)
            severity = "Critical" if issue_type in ["path_length", "reserved_names"] else "Warning"
            description = self._get_issue_description(issue_type)
            
            report_data.append([issue_type, str(count), severity, description])
        
        report_data.append(["", "", "", ""])  # Empty row
        
        # Add files with issues
        report_data.append(["Files with Issues", "", "", ""])
        report_data.append(["Filename", "Path", "Issue Count", "Issue Types"])
        
        # Collect files with issues
        files_with_issues = {}
        for issue_type, issues in analysis_results.items():
            if not isinstance(issues, (list, dict)) or not issues:
                continue
                
            # Different issue types have different structures
            if issue_type == 'name_issues':
                for _, row in issues.iterrows():
                    path = row.get('path', '')
                    if path:
                        if path not in files_with_issues:
                            files_with_issues[path] = {'count': 0, 'types': set()}
                        files_with_issues[path]['count'] += 1
                        files_with_issues[path]['types'].add('Name Issue')
            elif issue_type == 'path_issues':
                for _, row in issues.iterrows():
                    path = row.get('path', '')
                    if path:
                        if path not in files_with_issues:
                            files_with_issues[path] = {'count': 0, 'types': set()}
                        files_with_issues[path]['count'] += 1
                        files_with_issues[path]['types'].add('Path Length')
            elif issue_type == 'duplicates':
                for _, row in issues.iterrows():
                    path = row.get('path', '')
                    if path:
                        if path not in files_with_issues:
                            files_with_issues[path] = {'count': 0, 'types': set()}
                        files_with_issues[path]['count'] += 1
                        files_with_issues[path]['types'].add('Duplicate')
            elif issue_type == 'pii':
                for _, row in issues.iterrows():
                    path = row.get('path', '')
                    if path:
                        if path not in files_with_issues:
                            files_with_issues[path] = {'count': 0, 'types': set()}
                        files_with_issues[path]['count'] += 1
                        files_with_issues[path]['types'].add('PII')
        
        # Add files to report
        for path, info in files_with_issues.items():
            filename = os.path.basename(path)
            count = info['count']
            types = ', '.join(info['types'])
            
            report_data.append([filename, path, str(count), types])
        
        # Export data based on format
        if export_format == '.csv':
            import csv
            with open(file_path, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerows(report_data)
        elif export_format == '.xlsx':
            import pandas as pd
            # Convert to DataFrame
            df = pd.DataFrame(report_data)
            df.to_excel(file_path, index=False, header=False)
        elif export_format == '.html':
            html = "<html><head><title>Analysis Report</title></head><body>"
            html += "<h1>SharePoint Migration Analysis Report</h1>"
            
            # Add tables for each section
            for i, row in enumerate(report_data):
                if len(row) == 4 and row[0] and row[1] == "" and row[2] == "" and row[3] == "":
                    # Section header
                    html += f"<h2>{row[0]}</h2>"
                    html += "<table border='1'>"
                    # Next row is table header
                    if i + 1 < len(report_data):
                        html += "<tr>"
                        for cell in report_data[i+1]:
                            html += f"<th>{cell}</th>"
                        html += "</tr>"
                    # Subsequent rows until empty row
                    for j in range(i+2, len(report_data)):
                        if report_data[j][0] == "":
                            break
                        html += "<tr>"
                        for cell in report_data[j]:
                            html += f"<td>{cell}</td>"
                        html += "</tr>"
                    html += "</table>"
            
            html += "</body></html>"
            
            with open(file_path, 'w') as f:
                f.write(html)
        else:  # Text format
            with open(file_path, 'w') as f:
                for row in report_data:
                    f.write('\t'.join(row) + '\n')
        
        QMessageBox.information(self, "Export Complete", 
                              f"Analysis results exported to {file_path}")
        
    except Exception as e:
        logger.error(f"Error exporting analysis: {e}")
        QMessageBox.critical(self, "Export Error", 
                           f"Error exporting analysis: {str(e)}")