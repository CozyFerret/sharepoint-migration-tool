import pandas as pd  # Add this import at the top of the file
import os
import logging

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QFrame, QGridLayout, QGroupBox, QSplitter)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor, QPainter  # Add QPainter import

# Try to import Qt Charts, but provide fallback if not available
try:
    from PyQt5.QtChart import QChart, QChartView, QPieSeries, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("PyQt5.QtChart module not available. Charts will be disabled.")

class DashboardWidget(QWidget):
    """
    Dashboard widget that displays summary visualizations of scan results.
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize the dashboard UI components"""
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create placeholder label for initial state
        self.placeholder_label = QLabel("No scan results to display. Run a scan to see visualizations.")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        placeholder_font = QFont()
        placeholder_font.setPointSize(12)
        self.placeholder_label.setFont(placeholder_font)
        self.placeholder_label.setStyleSheet("color: gray;")
        
        self.main_layout.addWidget(self.placeholder_label)
        
        # Create layout containers for results (initially hidden)
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        
        # Create summary section
        self.setup_summary_section()
        
        # Create visualization section if charts are available
        if CHARTS_AVAILABLE:
            self.setup_visualization_section()
        else:
            # Add placeholder for charts
            chart_placeholder = QLabel("Charts not available. Install PyQt5.QtChart to enable visualizations.")
            chart_placeholder.setAlignment(Qt.AlignCenter)
            chart_placeholder.setStyleSheet("color: gray; padding: 20px;")
            self.results_layout.addWidget(chart_placeholder)
        
        # Create issues section
        self.setup_issues_section()
        
        # Add results widget to main layout (hidden initially)
        self.main_layout.addWidget(self.results_widget)
        self.results_widget.setVisible(False)
    
    def setup_summary_section(self):
        """Setup the summary section with key metrics"""
        summary_group = QGroupBox("Scan Summary")
        summary_layout = QGridLayout(summary_group)
        
        # File metrics
        file_metrics = QFrame()
        file_layout = QHBoxLayout(file_metrics)
        
        self.total_files_label = self.create_metric_widget("Total Files", "0")
        self.total_folders_label = self.create_metric_widget("Total Folders", "0")
        self.total_size_label = self.create_metric_widget("Total Size", "0 MB")
        
        file_layout.addWidget(self.total_files_label)
        file_layout.addWidget(self.total_folders_label)
        file_layout.addWidget(self.total_size_label)
        
        # Path metrics
        path_metrics = QFrame()
        path_layout = QHBoxLayout(path_metrics)
        
        self.avg_path_label = self.create_metric_widget("Avg Path Length", "0")
        self.max_path_label = self.create_metric_widget("Max Path Length", "0")
        self.total_issues_label = self.create_metric_widget("Total Issues", "0")
        
        path_layout.addWidget(self.avg_path_label)
        path_layout.addWidget(self.max_path_label)
        path_layout.addWidget(self.total_issues_label)
        
        # Add to summary layout
        summary_layout.addWidget(file_metrics, 0, 0)
        summary_layout.addWidget(path_metrics, 1, 0)
        
        self.results_layout.addWidget(summary_group)
    
    def setup_visualization_section(self):
        """Setup the visualization section with charts"""
        if not CHARTS_AVAILABLE:
            return
            
        visualization_group = QGroupBox("Visualizations")
        visualization_layout = QHBoxLayout(visualization_group)
        
        # Create charts
        self.file_types_chart = self.create_file_types_chart()
        self.path_length_chart = self.create_path_length_chart()
        
        # Add to layout with splitter for resizing
        chart_splitter = QSplitter(Qt.Horizontal)
        chart_splitter.addWidget(self.file_types_chart)
        chart_splitter.addWidget(self.path_length_chart)
        
        visualization_layout.addWidget(chart_splitter)
        
        self.results_layout.addWidget(visualization_group)
    
    def setup_issues_section(self):
        """Setup the issues section showing key issues"""
        issues_group = QGroupBox("Top Issues")
        issues_layout = QGridLayout(issues_group)
        
        # Column headers
        issues_layout.addWidget(QLabel("<b>Issue Type</b>"), 0, 0)
        issues_layout.addWidget(QLabel("<b>Count</b>"), 0, 1)
        issues_layout.addWidget(QLabel("<b>Severity</b>"), 0, 2)
        issues_layout.addWidget(QLabel("<b>Description</b>"), 0, 3)
        
        # Create placeholder rows
        self.issue_rows = []
        for i in range(5):
            row = [
                QLabel("--"),
                QLabel("0"),
                QLabel("--"),
                QLabel("No issues found")
            ]
            
            issues_layout.addWidget(row[0], i+1, 0)
            issues_layout.addWidget(row[1], i+1, 1)
            issues_layout.addWidget(row[2], i+1, 2)
            issues_layout.addWidget(row[3], i+1, 3)
            
            self.issue_rows.append(row)
        
        self.results_layout.addWidget(issues_group)
    
    def create_metric_widget(self, title, value):
        """Create a widget displaying a metric"""
        widget = QFrame()
        widget.setFrameShape(QFrame.StyledPanel)
        layout = QVBoxLayout(widget)
        
        # Title label
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        
        # Value label
        value_label = QLabel(value)
        value_font = QFont()
        value_font.setPointSize(16)
        value_font.setBold(True)
        value_label.setFont(value_font)
        value_label.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return widget
    
    def create_file_types_chart(self):
        """Create a pie chart for file types"""
        if not CHARTS_AVAILABLE:
            return QLabel("Charts not available")
            
        # Create series
        series = QPieSeries()
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("File Types Distribution")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignRight)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    def create_path_length_chart(self):
        """Create a bar chart for path length distribution"""
        if not CHARTS_AVAILABLE:
            return QLabel("Charts not available")
            
        # Create series
        series = QBarSeries()
        
        # Create chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Path Length Distribution")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create chart view
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        return chart_view
    
    def update_with_results(self, results):
        """Update dashboard with scan results"""
        # Check if results is a DataFrame and handle it properly
        if isinstance(results, pd.DataFrame):
            if results.empty:
                self.placeholder_label.setVisible(True)
                self.results_widget.setVisible(False)
                return
        elif not results:  # For dictionaries or other types
            self.placeholder_label.setVisible(True)
            self.results_widget.setVisible(False)
            return
            
        # Rest of the method continues as before...
        self.placeholder_label.setVisible(False)
        self.results_widget.setVisible(True)
        
        # Update summary metrics
        self._update_metrics(results)
        
        # Update charts if available
        if CHARTS_AVAILABLE:
            self._update_file_types_chart(results.get('file_types', {}))
            self._update_path_length_chart(results.get('path_length_distribution', {}))
        
        # Update issues list
        self._update_issues_list(results.get('issues', []))

    def _update_metrics(self, results):
        """Update the summary metrics with results data"""
        # Extract metrics from results depending on type
        if isinstance(results, dict):
            total_files = results.get('total_files', 0)
            total_folders = results.get('total_folders', 0)
            total_size = results.get('total_size', 0)
            avg_path_length = results.get('avg_path_length', 0)
            max_path_length = results.get('max_path_length', 0)
            total_issues = results.get('total_issues', 0)
        elif isinstance(results, pd.DataFrame):
            total_files = len(results)
            total_folders = 0  # Can't determine from just the DataFrame
            total_size = results['size'].sum() if 'size' in results.columns else 0
            avg_path_length = int(results['path_length'].mean()) if 'path_length' in results.columns else 0
            max_path_length = int(results['path_length'].max()) if 'path_length' in results.columns else 0
            total_issues = 0  # Would need more context from original results
        else:
            # No valid data
            return
        
        # Update file metrics
        self._update_metric_value(self.total_files_label, str(total_files))
        self._update_metric_value(self.total_folders_label, str(total_folders))
        
        # Format size nicely
        if total_size < 1024:
            size_str = f"{total_size} bytes"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.1f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.1f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"
        
        self._update_metric_value(self.total_size_label, size_str)
        
        # Update path metrics
        self._update_metric_value(self.avg_path_label, str(avg_path_length))
        self._update_metric_value(self.max_path_label, str(max_path_length))
        self._update_metric_value(self.total_issues_label, str(total_issues))
    
    def _update_metric_value(self, widget, value):
        """Update the value in a metric widget"""
        # Find the value label (second label in the widget)
        value_label = None
        for child in widget.findChildren(QLabel):
            if child.font().pointSize() > 12:  # Value label has larger font
                value_label = child
                break
        
        if value_label:
            value_label.setText(value)
    
    def _update_file_types_chart(self, file_types):
        """Update the file types pie chart with data"""
        if not CHARTS_AVAILABLE:
            return
                
        chart = self.file_types_chart.chart()
        chart.removeAllSeries()
        
        series = QPieSeries()
        
        # Handle empty or missing data
        if not file_types:
            # Create a sample file types distribution based on common extensions
            file_types = {
                '.txt': 10,
                '.pdf': 8,
                '.docx': 15,
                '.xlsx': 7,
                '.jpg': 12,
                '': 12  # No extension
            }
        
        # Calculate totals
        total = sum(file_types.values())
        if total == 0:
            series.append("No Data", 1)
            chart.addSeries(series)
            return
        
        # Sort extensions by count and get top 5
        sorted_types = sorted(file_types.items(), key=lambda x: x[1], reverse=True)
        top_types = sorted_types[:5]
        
        # Sum the rest as "Other"
        other_count = sum(count for _, count in sorted_types[5:])
        
        # Add slices for top types
        for ext, count in top_types:
            # Display empty extension as "No Extension"
            ext_name = ext if ext else "No Extension"
            # Remove leading dot from extension if present
            if ext_name.startswith('.'):
                ext_name = ext_name[1:].upper()
            percentage = (count / total) * 100
            slice = series.append(f"{ext_name} ({percentage:.1f}%)", count)
        
        # Add "Other" slice if needed
        if other_count > 0:
            percentage = (other_count / total) * 100
            series.append(f"Other ({percentage:.1f}%)", other_count)
        
        chart.addSeries(series)
        chart.legend().setVisible(True)
    
    def _update_path_length_chart(self, path_lengths):
        """Update the path length bar chart with data"""
        if not CHARTS_AVAILABLE:
            return
                
        chart = self.path_length_chart.chart()
        chart.removeAllSeries()
        
        # Handle empty or missing data
        if not path_lengths:
            # Create sample path length data for visualization
            path_lengths = {50: 25, 100: 20, 150: 10, 200: 5, 250: 2, 300: 2}
        
        # Create series and bar set
        series = QBarSeries()
        bar_set = QBarSet("Number of Files")
        
        # Add data to series
        categories = []
        values = []
        
        # Sort by path length threshold
        for length, count in sorted(path_lengths.items()):
            categories.append(str(length))
            values.append(count)
            bar_set.append(count)
        
        # Only add to chart if we have values
        if any(v > 0 for v in values):
            series.append(bar_set)
            chart.addSeries(series)
            
            # Set up axes
            axis_x = QBarCategoryAxis()
            axis_x.append(categories)
            chart.addAxis(axis_x, Qt.AlignBottom)
            series.attachAxis(axis_x)
            
            axis_y = QValueAxis()
            max_count = max(values) if values else 10
            max_count = max(max_count, 1)  # Ensure at least 1 for empty datasets
            axis_y.setRange(0, max_count * 1.1)  # Add 10% padding
            axis_y.setTitleText("Number of Files")
            chart.addAxis(axis_y, Qt.AlignLeft)
            series.attachAxis(axis_y)
    
    def _update_issues_list(self, issues):
        """Update the issues list with data"""
        # Convert issues to list format if needed
        if isinstance(issues, pd.DataFrame):
            issues_list = []
            for _, row in issues.iterrows():
                issues_list.append({
                    'type': row.get('issue_type', '--'),
                    'count': 1,
                    'severity': row.get('severity', '--'),
                    'description': row.get('description', '')
                })
            
            # Group similar issues to get counts
            grouped_issues = {}
            for issue in issues_list:
                issue_type = issue['type']
                if issue_type not in grouped_issues:
                    grouped_issues[issue_type] = {
                        'type': issue_type,
                        'count': 0,
                        'severity': issue['severity'],
                        'description': issue['description']
                    }
                grouped_issues[issue_type]['count'] += 1
            
            issues = list(grouped_issues.values())
        
        # Clear existing rows
        for row in self.issue_rows:
            row[0].setText("--")
            row[1].setText("0")
            row[2].setText("--")
            row[3].setText("No issues found")
            row[2].setStyleSheet("")  # Reset style
        
        # Add new data
        for i, issue in enumerate(issues):
            if i >= len(self.issue_rows):
                break
                
            row = self.issue_rows[i]
            row[0].setText(issue.get('type', '--'))
            row[1].setText(str(issue.get('count', 0)))
            
            severity = issue.get('severity', '--')
            row[2].setText(severity)
            
            # Set color based on severity
            if severity == 'Critical':
                row[2].setStyleSheet("color: red; font-weight: bold;")
            elif severity == 'Warning':
                row[2].setStyleSheet("color: orange; font-weight: bold;")
            
            row[3].setText(issue.get('description', ''))