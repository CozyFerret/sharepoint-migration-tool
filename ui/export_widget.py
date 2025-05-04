#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Export widget for SharePoint Data Migration Cleanup Tool.
Handles exporting analysis results to various formats.
"""

import os
import logging
import json
import pandas as pd
import csv
from datetime import datetime
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QComboBox, QFileDialog, QGroupBox,
                           QCheckBox, QGridLayout, QMessageBox, QTextEdit)
from PyQt5.QtCore import Qt

logger = logging.getLogger('sharepoint_migration_tool')

class ExportWidget(QWidget):
    """Widget for exporting analysis results"""
    
    def __init__(self):
        """Initialize the export widget"""
        super().__init__()
        
        self.analysis_results = None
        
        # Set up the UI
        self.init_ui()
        
    def init_ui(self):
        """Set up the user interface"""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Export format selection
        format_group = QGroupBox("Export Format")
        format_layout = QHBoxLayout()
        
        format_layout.addWidget(QLabel("Format:"))
        
        self.format_combo = QComboBox()
        self.format_combo.addItems(["CSV", "Excel", "JSON", "Text Summary"])
        format_layout.addWidget(self.format_combo)
        
        format_group.setLayout(format_layout)
        main_layout.addWidget(format_group)
        
        # Export content selection
        content_group = QGroupBox("Export Content")
        content_layout = QGridLayout()
        
        self.export_all_check = QCheckBox("All Analysis Results")
        self.export_all_check.setChecked(True)
        self.export_all_check.stateChanged.connect(self._toggle_all_options)
        content_layout.addWidget(self.export_all_check, 0, 0, 1, 2)
        
        self.export_name_check = QCheckBox("Name Issues")
        self.export_name_check.setChecked(True)
        self.export_name_check.setEnabled(False)  # Initially disabled because "All" is checked
        content_layout.addWidget(self.export_name_check, 1, 0)
        
        self.export_path_check = QCheckBox("Path Issues")
        self.export_path_check.setChecked(True)
        self.export_path_check.setEnabled(False)  # Initially disabled because "All" is checked
        content_layout.addWidget(self.export_path_check, 1, 1)
        
        self.export_duplicate_check = QCheckBox("Duplicates")
        self.export_duplicate_check.setChecked(True)
        self.export_duplicate_check.setEnabled(False)  # Initially disabled because "All" is checked
        content_layout.addWidget(self.export_duplicate_check, 2, 0)
        
        self.export_pii_check = QCheckBox("PII (Placeholder)")
        self.export_pii_check.setChecked(True)
        self.export_pii_check.setEnabled(False)  # Initially disabled because "All" is checked
        content_layout.addWidget(self.export_pii_check, 2, 1)
        
        self.export_summary_check = QCheckBox("Summary Statistics")
        self.export_summary_check.setChecked(True)
        content_layout.addWidget(self.export_summary_check, 3, 0)
        
        content_group.setLayout(content_layout)
        main_layout.addWidget(content_group)
        
        # Export action
        export_button_layout = QHBoxLayout()
        
        self.export_button = QPushButton("Export...")
        self.export_button.clicked.connect(self.export_data)
        self.export_button.setEnabled(False)  # Initially disabled until we have data
        export_button_layout.addWidget(self.export_button)
        
        main_layout.addLayout(export_button_layout)
        
        # Preview area
        preview_group = QGroupBox("Export Preview")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setPlaceholderText("Export preview will appear here")
        preview_layout.addWidget(self.preview_text)
        
        preview_group.setLayout(preview_layout)
        main_layout.addWidget(preview_group)
        
        # Status area
        self.status_label = QLabel("No data available for export")
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)
        
    def set_data(self, analysis_results):
        """
        Set the analysis results data for export
        
        Args:
            analysis_results (dict): Dictionary of analysis results
        """
        self.analysis_results = analysis_results
        
        if not analysis_results:
            self.status_label.setText("No data available for export")
            self.export_button.setEnabled(False)
            self.preview_text.clear()
            return
            
        # Enable export button
        self.export_button.setEnabled(True)
        
        # Update status
        total_issues = 0
        if 'name_issues' in analysis_results:
            total_issues += len(analysis_results['name_issues'])
        if 'path_issues' in analysis_results:
            total_issues += len(analysis_results['path_issues'])
        if 'duplicates' in analysis_results:
            total_issues += len(analysis_results['duplicates'])
        if 'pii' in analysis_results:
            total_issues += len(analysis_results['pii'])
            
        self.status_label.setText(f"Ready to export {total_issues} issues")
        
        # Generate preview
        self._update_preview()
        
    def _toggle_all_options(self, state):
        """
        Toggle all export options based on the "All" checkbox
        
        Args:
            state (int): Check state
        """
        enabled = not bool(state)  # True if "All" is unchecked
        
        self.export_name_check.setEnabled(enabled)
        self.export_path_check.setEnabled(enabled)
        self.export_duplicate_check.setEnabled(enabled)
        self.export_pii_check.setEnabled(enabled)
        
        # Update preview
        self._update_preview()
        
    def _update_preview(self):
        """Update the export preview"""
        if not self.analysis_results:
            self.preview_text.clear()
            return
            
        # Get selected format
        export_format = self.format_combo.currentText()
        
        # Generate preview based on format
        if export_format == "Text Summary":
            preview = self._generate_text_summary()
        elif export_format == "JSON":
            preview = self._generate_json_preview()
        elif export_format == "CSV":
            preview = "CSV export preview (headers only):\n\n"
            preview += self._generate_csv_headers()
        elif export_format == "Excel":
            preview = "Excel export will contain the following sheets:\n\n"
            if self.export_all_check.isChecked() or self.export_name_check.isChecked():
                preview += "- Name Issues\n"
            if self.export_all_check.isChecked() or self.export_path_check.isChecked():
                preview += "- Path Issues\n"
            if self.export_all_check.isChecked() or self.export_duplicate_check.isChecked():
                preview += "- Duplicates\n"
            if self.export_all_check.isChecked() or self.export_pii_check.isChecked():
                preview += "- PII Issues (Placeholder)\n"
            if self.export_summary_check.isChecked():
                preview += "- Summary Statistics\n"
                
        self.preview_text.setText(preview)
        
    def _generate_text_summary(self):
        """
        Generate a text summary of the analysis results
        
        Returns:
            str: Text summary
        """
        summary = "SharePoint Data Migration Analysis Summary\n"
        summary += "=" * 40 + "\n\n"
        summary += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Add summary statistics
        total_issues = 0
        name_issues = 0
        path_issues = 0
        duplicate_issues = 0
        pii_issues = 0
        
        if 'name_issues' in self.analysis_results:
            name_issues = len(self.analysis_results['name_issues'])
            total_issues += name_issues
            
        if 'path_issues' in self.analysis_results:
            path_issues = len(self.analysis_results['path_issues'])
            total_issues += path_issues
            
        if 'duplicates' in self.analysis_results:
            # Only count non-original files as issues
            if 'is_original' in self.analysis_results['duplicates'].columns:
                duplicate_issues = (~self.analysis_results['duplicates']['is_original']).sum()
            else:
                duplicate_issues = len(self.analysis_results['duplicates'])
            total_issues += duplicate_issues
            
        if 'pii' in self.analysis_results:
            pii_issues = len(self.analysis_results['pii'])
            total_issues += pii_issues
            
        summary += f"Total Issues Found: {total_issues}\n"
        summary += f"- Name Issues: {name_issues}\n"
        summary += f"- Path Length Issues: {path_issues}\n"
        summary += f"- Duplicate Files: {duplicate_issues}\n"
        summary += f"- Potential PII (Placeholder): {pii_issues}\n\n"
        
        # Add top issues by type
        if self.export_all_check.isChecked() or self.export_name_check.isChecked():
            if 'name_issues' in self.analysis_results and len(self.analysis_results['name_issues']) > 0:
                summary += "Top Name Issues:\n"
                summary += "-" * 15 + "\n"
                for i, (_, row) in enumerate(self.analysis_results['name_issues'].head(5).iterrows()):
                    summary += f"{i+1}. {row['name']} - {row['name_issues']}\n"
                summary += "\n"
                
        if self.export_all_check.isChecked() or self.export_path_check.isChecked():
            if 'path_issues' in self.analysis_results and len(self.analysis_results['path_issues']) > 0:
                summary += "Top Path Length Issues:\n"
                summary += "-" * 20 + "\n"
                for i, (_, row) in enumerate(self.analysis_results['path_issues'].head(5).iterrows()):
                    summary += f"{i+1}. Length: {row['path_length']} - {row['path']}\n"
                summary += "\n"
                
        if self.export_all_check.isChecked() or self.export_duplicate_check.isChecked():
            if 'duplicates' in self.analysis_results and len(self.analysis_results['duplicates']) > 0:
                summary += "Top Duplicates:\n"
                summary += "-" * 15 + "\n"
                # Filter to show only non-original files
                if 'is_original' in self.analysis_results['duplicates'].columns:
                    dupes = self.analysis_results['duplicates'][~self.analysis_results['duplicates']['is_original']]
                else:
                    dupes = self.analysis_results['duplicates']
                    
                for i, (_, row) in enumerate(dupes.head(5).iterrows()):
                    if 'original_path' in row and row['original_path']:
                        summary += f"{i+1}. {row['path']} - Duplicate of {row['original_path']}\n"
                    else:
                        summary += f"{i+1}. {row['path']} - Possible duplicate\n"
                summary += "\n"
                
        if self.export_all_check.isChecked() or self.export_pii_check.isChecked():
            if 'pii' in self.analysis_results and len(self.analysis_results['pii']) > 0:
                summary += "Potential PII (Placeholder Functionality):\n"
                summary += "-" * 35 + "\n"
                for i, (_, row) in enumerate(self.analysis_results['pii'].head(5).iterrows()):
                    if 'pii_types' in row and row['pii_types']:
                        summary += f"{i+1}. {row['path']} - {row['pii_types']}\n"
                    else:
                        summary += f"{i+1}. {row['path']} - Potential PII detected\n"
                summary += "\n"
                
        # Add a note about PII detection being a placeholder
        summary += "\nNote: PII detection is a placeholder in this version and will be fully implemented in future updates.\n"
        
        return summary
        
    def _generate_json_preview(self):
        """
        Generate a JSON preview of the analysis results
        
        Returns:
            str: JSON preview
        """
        # Create a simplified version of the data for preview
        preview_data = {
            "summary": {
                "generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "name_issues_count": len(self.analysis_results.get('name_issues', pd.DataFrame())),
                "path_issues_count": len(self.analysis_results.get('path_issues', pd.DataFrame())),
                "duplicates_count": len(self.analysis_results.get('duplicates', pd.DataFrame())),
                "pii_issues_count": len(self.analysis_results.get('pii', pd.DataFrame())),
            }
        }
        
        # Add sample issues
        if self.export_all_check.isChecked() or self.export_name_check.isChecked():
            if 'name_issues' in self.analysis_results and len(self.analysis_results['name_issues']) > 0:
                preview_data["name_issues_sample"] = self.analysis_results['name_issues'].head(2).to_dict('records')
                
        if self.export_all_check.isChecked() or self.export_path_check.isChecked():
            if 'path_issues' in self.analysis_results and len(self.analysis_results['path_issues']) > 0:
                preview_data["path_issues_sample"] = self.analysis_results['path_issues'].head(2).to_dict('records')
                
        if self.export_all_check.isChecked() or self.export_duplicate_check.isChecked():
            if 'duplicates' in self.analysis_results and len(self.analysis_results['duplicates']) > 0:
                preview_data["duplicates_sample"] = self.analysis_results['duplicates'].head(2).to_dict('records')
                
        if self.export_all_check.isChecked() or self.export_pii_check.isChecked():
            if 'pii' in self.analysis_results and len(self.analysis_results['pii']) > 0:
                preview_data["pii_sample"] = self.analysis_results['pii'].head(2).to_dict('records')
                
        # Convert to JSON for preview
        try:
            return json.dumps(preview_data, indent=2, default=str)
        except Exception as exc:
            logger.error(f"Error generating JSON preview: {exc}")
            return "Error generating JSON preview"
        
    def _generate_csv_headers(self):
        """
        Generate CSV headers for the analysis results
        
        Returns:
            str: CSV headers
        """
        headers = ""
        
        if self.export_all_check.isChecked() or self.export_name_check.isChecked():
            if 'name_issues' in self.analysis_results:
                headers += "Name Issues CSV:\n"
                headers += ",".join(self.analysis_results['name_issues'].columns) + "\n\n"
                
        if self.export_all_check.isChecked() or self.export_path_check.isChecked():
            if 'path_issues' in self.analysis_results:
                headers += "Path Issues CSV:\n"
                headers += ",".join(self.analysis_results['path_issues'].columns) + "\n\n"
                
        if self.export_all_check.isChecked() or self.export_duplicate_check.isChecked():
            if 'duplicates' in self.analysis_results:
                headers += "Duplicates CSV:\n"
                headers += ",".join(self.analysis_results['duplicates'].columns) + "\n\n"
                
        if self.export_all_check.isChecked() or self.export_pii_check.isChecked():
            if 'pii' in self.analysis_results:
                headers += "PII CSV (Placeholder):\n"
                headers += ",".join(self.analysis_results['pii'].columns) + "\n\n"
                
        if not headers:
            headers = "No data selected for export"
            
        return headers
        
    def export_data(self):
        """Export the analysis results"""
        if not self.analysis_results:
            QMessageBox.warning(self, "Error", "No data available for export")
            return
            
        # Get selected format
        export_format = self.format_combo.currentText()
        
        # Ask for save location
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        default_filename = f"sharepoint_analysis_{timestamp}"
        
        if export_format == "CSV":
            file_filter = "CSV Files (*.csv)"
            default_filename += ".csv"
        elif export_format == "Excel":
            file_filter = "Excel Files (*.xlsx)"
            default_filename += ".xlsx"
        elif export_format == "JSON":
            file_filter = "JSON Files (*.json)"
            default_filename += ".json"
        else:  # Text Summary
            file_filter = "Text Files (*.txt)"
            default_filename += ".txt"
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Export", default_filename, file_filter
        )
        
        if not file_path:
            return  # User cancelled
            
        try:
            # Export based on format
            if export_format == "CSV":
                self._export_csv(file_path)
            elif export_format == "Excel":
                self._export_excel(file_path)
            elif export_format == "JSON":
                self._export_json(file_path)
            else:  # Text Summary
                self._export_text(file_path)
                
            QMessageBox.information(self, "Success", f"Data exported successfully to {file_path}")
            
            # Show the exported file in the explorer
            self._show_in_explorer(file_path)
            
        except Exception as exc:
            logger.error(f"Error exporting data: {exc}")
            QMessageBox.critical(self, "Error", f"Error exporting data: {str(exc)}")
            
    def _export_csv(self, file_path):
        """
        Export the analysis results to CSV
        
        Args:
            file_path (str): Path to save the CSV file
        """
        # For CSV, we'll export only one data frame at a time
        # We'll use the filename as the base and add suffixes for each type
        
        file_dir = os.path.dirname(file_path)
        file_base = os.path.splitext(os.path.basename(file_path))[0]
        
        # Export name issues
        if (self.export_all_check.isChecked() or self.export_name_check.isChecked()) and 'name_issues' in self.analysis_results:
            name_issues_path = os.path.join(file_dir, f"{file_base}_name_issues.csv")
            self.analysis_results['name_issues'].to_csv(name_issues_path, index=False)
            
        # Export path issues
        if (self.export_all_check.isChecked() or self.export_path_check.isChecked()) and 'path_issues' in self.analysis_results:
            path_issues_path = os.path.join(file_dir, f"{file_base}_path_issues.csv")
            self.analysis_results['path_issues'].to_csv(path_issues_path, index=False)
            
        # Export duplicates
        if (self.export_all_check.isChecked() or self.export_duplicate_check.isChecked()) and 'duplicates' in self.analysis_results:
            duplicates_path = os.path.join(file_dir, f"{file_base}_duplicates.csv")
            self.analysis_results['duplicates'].to_csv(duplicates_path, index=False)
            
        # Export PII
        if (self.export_all_check.isChecked() or self.export_pii_check.isChecked()) and 'pii' in self.analysis_results:
            pii_path = os.path.join(file_dir, f"{file_base}_pii.csv")
            self.analysis_results['pii'].to_csv(pii_path, index=False)
            
        # Export summary
        if self.export_summary_check.isChecked():
            summary_path = os.path.join(file_dir, f"{file_base}_summary.txt")
            with open(summary_path, 'w') as f:
                f.write(self._generate_text_summary())
                
    def _export_excel(self, file_path):
        """
        Export the analysis results to Excel
        
        Args:
            file_path (str): Path to save the Excel file
        """
        # Create an ExcelWriter object
        try:
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                # Export name issues
                if (self.export_all_check.isChecked() or self.export_name_check.isChecked()) and 'name_issues' in self.analysis_results:
                    self.analysis_results['name_issues'].to_excel(writer, sheet_name='Name Issues', index=False)
                    
                # Export path issues
                if (self.export_all_check.isChecked() or self.export_path_check.isChecked()) and 'path_issues' in self.analysis_results:
                    self.analysis_results['path_issues'].to_excel(writer, sheet_name='Path Issues', index=False)
                    
                # Export duplicates
                if (self.export_all_check.isChecked() or self.export_duplicate_check.isChecked()) and 'duplicates' in self.analysis_results:
                    self.analysis_results['duplicates'].to_excel(writer, sheet_name='Duplicates', index=False)
                    
                # Export PII
                if (self.export_all_check.isChecked() or self.export_pii_check.isChecked()) and 'pii' in self.analysis_results:
                    self.analysis_results['pii'].to_excel(writer, sheet_name='PII', index=False)
                    
                # Export summary as a DataFrame
                if self.export_summary_check.isChecked():
                    # Create a simple DataFrame for the summary
                    summary_text = self._generate_text_summary()
                    summary_lines = summary_text.split('\n')
                    summary_df = pd.DataFrame({'Summary': summary_lines})
                    summary_df.to_excel(writer, sheet_name='Summary', index=False)
        except Exception as exc:
            logger.error(f"Error exporting to Excel: {exc}")
            raise
                
    def _export_json(self, file_path):
        """
        Export the analysis results to JSON
        
        Args:
            file_path (str): Path to save the JSON file
        """
        # Create a dictionary to hold all the data
        export_data = {
            "metadata": {
                "generated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "version": "1.0"
            },
            "summary": {
                "name_issues_count": len(self.analysis_results.get('name_issues', pd.DataFrame())),
                "path_issues_count": len(self.analysis_results.get('path_issues', pd.DataFrame())),
                "duplicates_count": len(self.analysis_results.get('duplicates', pd.DataFrame())),
                "pii_issues_count": len(self.analysis_results.get('pii', pd.DataFrame())),
            }
        }
        
        # Add the detailed data
        if self.export_all_check.isChecked() or self.export_name_check.isChecked():
            if 'name_issues' in self.analysis_results:
                export_data["name_issues"] = self.analysis_results['name_issues'].to_dict('records')
                
        if self.export_all_check.isChecked() or self.export_path_check.isChecked():
            if 'path_issues' in self.analysis_results:
                export_data["path_issues"] = self.analysis_results['path_issues'].to_dict('records')
                
        if self.export_all_check.isChecked() or self.export_duplicate_check.isChecked():
            if 'duplicates' in self.analysis_results:
                export_data["duplicates"] = self.analysis_results['duplicates'].to_dict('records')
                
        if self.export_all_check.isChecked() or self.export_pii_check.isChecked():
            if 'pii' in self.analysis_results:
                export_data["pii"] = self.analysis_results['pii'].to_dict('records')
                
        # Write to file
        try:
            with open(file_path, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)
        except Exception as exc:
            logger.error(f"Error exporting to JSON: {exc}")
            raise
            
    def _export_text(self, file_path):
        """
        Export the analysis results to a text file
        
        Args:
            file_path (str): Path to save the text file
        """
        # Generate the text summary
        summary = self._generate_text_summary()
        
        # Write to file
        try:
            with open(file_path, 'w') as f:
                f.write(summary)
        except Exception as exc:
            logger.error(f"Error exporting to text file: {exc}")
            raise
            
    def _show_in_explorer(self, file_path):
        """
        Show the exported file in the file explorer
        
        Args:
            file_path (str): Path to the exported file
        """
        try:
            if os.name == 'nt':  # Windows
                import subprocess
                subprocess.Popen(f'explorer /select,"{file_path}"')
            elif os.name == 'posix':  # macOS and Linux
                import subprocess
                if os.path.exists('/usr/bin/open'):  # macOS
                    subprocess.Popen(['open', os.path.dirname(file_path)])
                else:  # Linux
                    try:
                        subprocess.Popen(['xdg-open', os.path.dirname(file_path)])
                    except Exception:
                        pass  # Silently fail if unable to open file explorer
        except Exception as exc:
            logger.warning(f"Error showing file in explorer: {exc}")
            # Non-critical error, just log it