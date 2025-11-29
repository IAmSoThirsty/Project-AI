from PyQt6.QtWidgets import QFileDialog, QMessageBox, QWidget, QVBoxLayout


class DashboardHandlers:
    def generate_learning_path(self):
        """Generate a learning path based on user input"""
        interest = self.interest_input.text()
        skill_level = self.skill_level.currentText().lower()

        if interest:
            path = self.learning_manager.generate_path(interest, skill_level)
            self.learning_path_display.setText(path)
            self.learning_manager.save_path(self.user_manager.current_user, interest, path)

    def load_data_file(self):
        """Load a data file for analysis"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Data File", "",
            "Data Files (*.csv *.xlsx *.json);;All Files (*.*)")

        if file_path:
            if self.data_analyzer.load_data(file_path):
                self.column_selector.clear()
                self.column_selector.addItems(self.data_analyzer.data.columns)
                self.show_basic_stats()

    def perform_analysis(self):
        """Perform selected data analysis"""
        analysis_type = self.analysis_type.currentText()

        if analysis_type == "Basic Stats":
            self.show_basic_stats()
        elif analysis_type in ["Scatter Plot", "Histogram", "Box Plot"]:
            self.create_visualization(analysis_type.lower().replace(" ", "_"))
        elif analysis_type == "Clustering":
            self.perform_clustering()

    def show_basic_stats(self):
        """Show basic statistical analysis"""
        stats = self.data_analyzer.get_summary_stats()
        self.analysis_display.setText(str(stats))

    def update_security_resources(self):
        """Update the security resources list"""
        category = self.security_category.currentText()
        resources = self.security_manager.get_resources_by_category(category)

        self.resources_list.clear()
        for resource in resources:
            self.resources_list.addItem(f"{resource['name']} ({resource['repo']})")

    def open_security_resource(self, item):
        """Open the selected security resource"""
        import webbrowser
        text = item.text()
        repo = text[text.find("(")+1:text.find(")")]
        webbrowser.open(f"https://github.com/{repo}")

    def add_security_favorite(self):
        """Add current security resource to favorites"""
        if self.resources_list.currentItem():
            text = self.resources_list.currentItem().text()
            repo = text[text.find("(")+1:text.find(")")]
            self.security_manager.save_favorite(self.user_manager.current_user, repo)
            QMessageBox.information(self, "Success", "Added to favorites")

    def toggle_location_tracking(self):
        """Toggle location tracking on/off"""
        if not self.location_tracker.active:
            self.location_tracker.active = True
            self.location_toggle.setText("Stop Location Tracking")
            self.location_timer.start(300000)  # Update every 5 minutes
            self.update_location()
        else:
            self.location_tracker.active = False
            self.location_toggle.setText("Start Location Tracking")
            self.location_timer.stop()

    def update_location(self):
        """Update current location"""
        if self.location_tracker.active:
            location = self.location_tracker.get_location_from_ip()
            if location:
                self.location_tracker.save_location_history(
                    self.user_manager.current_user, location)
                self.update_location_display()
                # Show offline indicator in location display if applicable
                if location.get('offline'):
                    offline_msg = (
                        "📴 Location tracking is in offline mode.\n"
                        "Showing cached/estimated location.\n\n"
                    )
                    self.location_display.setText(
                        offline_msg + self._format_location(location)
                    )
                else:
                    self.location_display.setText(self._format_location(location))

    def _format_location(self, location: dict) -> str:
        """Format location data for display."""
        parts = [
            f"City: {location.get('city', 'Unknown')}",
            f"Region: {location.get('region', 'Unknown')}",
            f"Country: {location.get('country', 'Unknown')}",
        ]
        if location.get('latitude') and location.get('longitude'):
            parts.append(f"Coordinates: {location['latitude']}, {location['longitude']}")
        if location.get('ip'):
            parts.append(f"IP: {location['ip']}")
        parts.append(f"Source: {location.get('source', 'unknown')}")
        parts.append(f"Time: {location.get('timestamp', 'unknown')}")
        return "\n".join(parts)

    def update_location_display(self):
        """Update the location display"""
        history = self.location_tracker.get_location_history(
            self.user_manager.current_user)

        self.location_history.clear()
        for location in history:
            # Add offline indicator if location was cached
            offline_indicator = " 📴" if location.get('offline') else ""
            self.location_history.addItem(
                f"{location['timestamp']}: {location.get('city', 'Unknown')}, "
                f"{location.get('region', 'Unknown')}{offline_indicator}"
            )

    def clear_location_history(self):
        """Clear the location history"""
        if QMessageBox.question(
            self, "Confirm Clear",
            "Are you sure you want to clear your location history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            self.location_tracker.clear_location_history(self.user_manager.current_user)
            self.location_history.clear()

    def save_emergency_contacts(self):
        """Save emergency contact information"""
        contacts = [email.strip() for email in self.contacts_input.text().split(",")]
        self.emergency_alert.add_emergency_contact(
            self.user_manager.current_user, {"emails": contacts})
        QMessageBox.information(self, "Success", "Emergency contacts saved")

    def send_emergency_alert(self):
        """Send emergency alert"""
        if QMessageBox.question(
            self, "Confirm Alert",
            "Are you sure you want to send an emergency alert?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) == QMessageBox.StandardButton.Yes:
            # Get latest location
            history = self.location_tracker.get_location_history(
                self.user_manager.current_user)
            location = history[-1] if history else None

            message = self.emergency_message.toPlainText()

            success, msg = self.emergency_alert.send_alert(
                self.user_manager.current_user, location, message)

            if success:
                QMessageBox.information(self, "Alert Sent", "Emergency alert was sent successfully")
                self.update_alert_history()
            else:
                QMessageBox.warning(self, "Alert Failed", f"Failed to send alert: {msg}")

    def update_alert_history(self):
        """Update the alert history display"""
        history = self.emergency_alert.get_alert_history(self.user_manager.current_user)

        self.alert_history.clear()
        for alert in history:
            self.alert_history.addItem(
                f"{alert['timestamp']}: {alert.get('message', 'No message')}")

    def create_visualization(self, plot_type):
        """Create data visualization"""
        if plot_type in ["scatter", "histogram", "boxplot"]:
            canvas = self.data_analyzer.create_visualization(
                plot_type,
                self.column_selector.currentText())
            if canvas:
                # Create a new window to display the plot
                plot_window = QWidget()
                plot_layout = QVBoxLayout(plot_window)
                plot_layout.addWidget(canvas)
                plot_window.setWindowTitle(f"{plot_type.title()} Plot")
                plot_window.show()

    def perform_clustering(self):
        """Perform clustering analysis"""
        # Get numerical columns
        numeric_cols = self.data_analyzer.data.select_dtypes(include=['float64', 'int64']).columns
        if len(numeric_cols) < 2:
            QMessageBox.warning(self, "Error", "Need at least 2 numeric columns for clustering")
            return

        canvas, clusters = self.data_analyzer.perform_clustering(numeric_cols)
        if canvas:
            plot_window = QWidget()
            plot_layout = QVBoxLayout(plot_window)
            plot_layout.addWidget(canvas)
            plot_window.setWindowTitle("Clustering Results")
            plot_window.show()
