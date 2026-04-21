"""
Dashboard event handlers routed through governance pipeline.

Old pattern: Direct core imports and calls
New pattern: Handler → Desktop Adapter → Router → Governance → Systems
"""

import logging

from PyQt6.QtWidgets import QFileDialog, QMessageBox, QVBoxLayout, QWidget

from app.interfaces.desktop.integration import get_desktop_adapter
from app.security.data_validation import sanitize_input, validate_email, validate_length

logger = logging.getLogger(__name__)


# 📚 Documentation Links:
# - [[relationships/gui/03_HANDLER_RELATIONSHIPS.md]]
# - [[source-docs/gui/dashboard_handlers.md]]
#

class DashboardHandlers:
    def generate_learning_path(self):
        """Generate a learning path based on user input (governance-routed)"""
        # Sanitize and validate interest input
        interest = sanitize_input(self.interest_input.text(), max_length=200)
        if not validate_length(interest, min_len=1, max_len=200):
            QMessageBox.warning(
                self,
                "Input Error",
                "Interest must be 1-200 characters"
            )
            return

        skill_level = self.skill_level.currentText().lower()

        if interest:
            try:
                adapter = get_desktop_adapter()
                response = adapter.execute(
                    "learning.generate_path",
                    {
                        "interest": interest,
                        "skill_level": skill_level,
                        "user": self.user_manager.current_user,
                    }
                )

                if response["status"] == "success":
                    path = response["result"]["path"]
                    self.learning_path_display.setText(path)
                else:
                    error_msg = response.get("error", "Unknown error")
                    logger.error(f"Learning path generation failed: {error_msg}")
                    self.learning_path_display.setText(f"Error: {error_msg}")

            except Exception as e:
                logger.error(f"Failed to generate learning path: {e}")
                # Fallback to direct call to preserve functionality
                path = self.learning_manager.generate_path(interest, skill_level)
                self.learning_path_display.setText(path)
                self.learning_manager.save_path(
                    self.user_manager.current_user, interest, path
                )

    def load_data_file(self):
        """Load a data file for analysis (governance-routed)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Data File",
            "",
            "Data Files (*.csv *.xlsx *.json);;All Files (*.*)",
        )

        if file_path:
            try:
                adapter = get_desktop_adapter()
                response = adapter.execute(
                    "data.load_file",
                    {
                        "file_path": file_path,
                        "user": self.user_manager.current_user,
                    }
                )

                if response["status"] == "success":
                    columns = response["result"]["columns"]
                    self.column_selector.clear()
                    self.column_selector.addItems(columns)
                    self.show_basic_stats()
                else:
                    error_msg = response.get("error", "Failed to load file")
                    QMessageBox.warning(self, "Error", error_msg)

            except Exception as e:
                logger.error(f"Failed to load data file through governance: {e}")
                # Fallback to direct call
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
        """Show basic statistical analysis (governance-routed)"""
        try:
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "data.get_stats",
                {
                    "user": self.user_manager.current_user,
                }
            )

            if response["status"] == "success":
                stats = response["result"]["stats"]
                self.analysis_display.setText(str(stats))
            else:
                logger.warning(f"Stats retrieval failed: {response.get('error')}")
                # Fallback to direct call
                stats = self.data_analyzer.get_summary_stats()
                self.analysis_display.setText(str(stats))

        except Exception as e:
            logger.error(f"Failed to get stats through governance: {e}")
            # Fallback to direct call
            stats = self.data_analyzer.get_summary_stats()
            self.analysis_display.setText(str(stats))

    def update_security_resources(self):
        """Update the security resources list (governance-routed)"""
        category = self.security_category.currentText()

        try:
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "security.get_resources",
                {
                    "category": category,
                    "user": self.user_manager.current_user,
                }
            )

            if response["status"] == "success":
                resources = response["result"]["resources"]
                self.resources_list.clear()
                for resource in resources:
                    self.resources_list.addItem(f"{resource['name']} ({resource['repo']})")
            else:
                logger.warning(f"Security resources retrieval failed: {response.get('error')}")
                # Fallback to direct call
                resources = self.security_manager.get_resources_by_category(category)
                self.resources_list.clear()
                for resource in resources:
                    self.resources_list.addItem(f"{resource['name']} ({resource['repo']})")

        except Exception as e:
            logger.error(f"Failed to get security resources through governance: {e}")
            # Fallback to direct call
            resources = self.security_manager.get_resources_by_category(category)
            self.resources_list.clear()
            for resource in resources:
                self.resources_list.addItem(f"{resource['name']} ({resource['repo']})")

    def open_security_resource(self, item):
        """Open the selected security resource"""
        import webbrowser

        text = item.text()
        repo = text[text.find("(") + 1 : text.find(")")]
        webbrowser.open(f"https://github.com/{repo}")

    def add_security_favorite(self):
        """Add current security resource to favorites (governance-routed)"""
        if self.resources_list.currentItem():
            text = self.resources_list.currentItem().text()
            repo = text[text.find("(") + 1 : text.find(")")]

            try:
                adapter = get_desktop_adapter()
                response = adapter.execute(
                    "security.add_favorite",
                    {
                        "repo": repo,
                        "user": self.user_manager.current_user,
                    }
                )

                if response["status"] == "success":
                    QMessageBox.information(self, "Success", "Added to favorites")
                else:
                    error_msg = response.get("error", "Failed to add favorite")
                    QMessageBox.warning(self, "Error", error_msg)

            except Exception as e:
                logger.error(f"Failed to add favorite through governance: {e}")
                # Fallback to direct call
                self.security_manager.save_favorite(self.user_manager.current_user, repo)
                QMessageBox.information(self, "Success", "Added to favorites")

    def toggle_location_tracking(self):
        """Toggle location tracking on/off (governance-routed)"""
        try:
            adapter = get_desktop_adapter()
            action = "location.start" if not self.location_tracker.active else "location.stop"

            response = adapter.execute(
                action,
                {
                    "user": self.user_manager.current_user,
                }
            )

            if response["status"] == "success":
                self.location_tracker.active = response["result"]["active"]
                if self.location_tracker.active:
                    self.location_toggle.setText("Stop Location Tracking")
                    self.location_timer.start(300000)  # Update every 5 minutes
                    self.update_location()
                else:
                    self.location_toggle.setText("Start Location Tracking")
                    self.location_timer.stop()
            else:
                logger.warning(f"Location tracking toggle failed: {response.get('error')}")
                # Fallback to direct control
                self._toggle_location_tracking_direct()

        except Exception as e:
            logger.error(f"Failed to toggle location tracking through governance: {e}")
            # Fallback to direct control
            self._toggle_location_tracking_direct()

    def _toggle_location_tracking_direct(self):
        """Direct location tracking toggle (fallback)"""
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
        """Update current location (governance-routed)"""
        if self.location_tracker.active:
            try:
                adapter = get_desktop_adapter()
                response = adapter.execute(
                    "location.update",
                    {
                        "user": self.user_manager.current_user,
                    }
                )

                if response["status"] == "success":
                    self.update_location_display()
                else:
                    logger.warning(f"Location update failed: {response.get('error')}")
                    # Fallback to direct call
                    self._update_location_direct()

            except Exception as e:
                logger.error(f"Failed to update location through governance: {e}")
                # Fallback to direct call
                self._update_location_direct()

    def _update_location_direct(self):
        """Direct location update (fallback)"""
        location = self.location_tracker.get_location_from_ip()
        if location:
            self.location_tracker.save_location_history(
                self.user_manager.current_user, location
            )
            self.update_location_display()

    def update_location_display(self):
        """Update the location display"""
        history = self.location_tracker.get_location_history(
            self.user_manager.current_user
        )

        self.location_history.clear()
        for location in history:
            self.location_history.addItem(
                f"{location['timestamp']}: {location.get('city', 'Unknown')}, "
                f"{location.get('region', 'Unknown')}"
            )

    def clear_location_history(self):
        """Clear the location history (governance-routed)"""
        if (
            QMessageBox.question(
                self,
                "Confirm Clear",
                "Are you sure you want to clear your location history?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            try:
                adapter = get_desktop_adapter()
                response = adapter.execute(
                    "location.clear_history",
                    {
                        "user": self.user_manager.current_user,
                    }
                )

                if response["status"] == "success":
                    self.location_history.clear()
                else:
                    error_msg = response.get("error", "Failed to clear history")
                    QMessageBox.warning(self, "Error", error_msg)

            except Exception as e:
                logger.error(f"Failed to clear location history through governance: {e}")
                # Fallback to direct call
                self.location_tracker.clear_location_history(self.user_manager.current_user)
                self.location_history.clear()

    def save_emergency_contacts(self):
        """Save emergency contact information (governance-routed)"""
        # Sanitize and validate contact emails
        contacts_raw = sanitize_input(self.contacts_input.text(), max_length=500)
        contacts = [email.strip() for email in contacts_raw.split(",")]

        # Validate each email
        invalid_emails = []
        valid_contacts = []
        for email in contacts:
            if email:  # Skip empty strings
                if validate_email(email):
                    valid_contacts.append(email)
                else:
                    invalid_emails.append(email)

        if invalid_emails:
            QMessageBox.warning(
                self,
                "Invalid Email",
                f"Invalid email addresses: {', '.join(invalid_emails)}"
            )
            return

        if not valid_contacts:
            QMessageBox.warning(
                self,
                "No Contacts",
                "Please enter at least one valid email address"
            )
            return

        try:
            adapter = get_desktop_adapter()
            response = adapter.execute(
                "emergency.save_contacts",
                {
                    "contacts": valid_contacts,
                    "user": self.user_manager.current_user,
                }
            )

            if response["status"] == "success":
                QMessageBox.information(self, "Success", "Emergency contacts saved")
            else:
                error_msg = response.get("error", "Failed to save contacts")
                QMessageBox.warning(self, "Error", error_msg)

        except Exception as e:
            logger.error(f"Failed to save emergency contacts through governance: {e}")
            # Fallback to direct call
            self.emergency_alert.add_emergency_contact(
                self.user_manager.current_user, {"emails": valid_contacts}
            )
            QMessageBox.information(self, "Success", "Emergency contacts saved")

    def send_emergency_alert(self):
        """Send emergency alert (governance-routed)"""
        if (
            QMessageBox.question(
                self,
                "Confirm Alert",
                "Are you sure you want to send an emergency alert?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            == QMessageBox.StandardButton.Yes
        ):
            try:
                # Get latest location
                history = self.location_tracker.get_location_history(
                    self.user_manager.current_user
                )
                location = history[-1] if history else None

                # Sanitize and validate emergency message
                message = sanitize_input(
                    self.emergency_message.toPlainText(),
                    max_length=1000
                )
                if not validate_length(message, min_len=1, max_len=1000):
                    QMessageBox.warning(
                        self,
                        "Input Error",
                        "Emergency message must be 1-1000 characters"
                    )
                    return

                adapter = get_desktop_adapter()
                response = adapter.execute(
                    "emergency.send_alert",
                    {
                        "location": location,
                        "message": message,
                        "user": self.user_manager.current_user,
                    }
                )

                if response["status"] == "success":
                    QMessageBox.information(
                        self, "Alert Sent", "Emergency alert was sent successfully"
                    )
                    self.update_alert_history()
                else:
                    error_msg = response.get("error", "Failed to send alert")
                    QMessageBox.warning(
                        self, "Alert Failed", f"Failed to send alert: {error_msg}"
                    )

            except Exception as e:
                logger.error(f"Failed to send emergency alert through governance: {e}")
                # Fallback to direct call
                self._send_emergency_alert_direct()

    def _send_emergency_alert_direct(self):
        """Direct emergency alert sending (fallback)"""
        # Get latest location
        history = self.location_tracker.get_location_history(
            self.user_manager.current_user
        )
        location = history[-1] if history else None

        # Sanitize and validate emergency message
        message = sanitize_input(
            self.emergency_message.toPlainText(),
            max_length=1000
        )
        if not validate_length(message, min_len=1, max_len=1000):
            QMessageBox.warning(
                self,
                "Input Error",
                "Emergency message must be 1-1000 characters"
            )
            return

        success, msg = self.emergency_alert.send_alert(
            self.user_manager.current_user, location, message
        )

        if success:
            QMessageBox.information(
                self, "Alert Sent", "Emergency alert was sent successfully"
            )
            self.update_alert_history()
        else:
            QMessageBox.warning(
                self, "Alert Failed", f"Failed to send alert: {msg}"
            )

    def update_alert_history(self):
        """Update the alert history display"""
        history = self.emergency_alert.get_alert_history(self.user_manager.current_user)

        self.alert_history.clear()
        for alert in history:
            self.alert_history.addItem(
                f"{alert['timestamp']}: {alert.get('message', 'No message')}"
            )

    def create_visualization(self, plot_type):
        """Create data visualization"""
        if plot_type in ["scatter", "histogram", "boxplot"]:
            canvas = self.data_analyzer.create_visualization(
                plot_type, self.column_selector.currentText()
            )
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
        numeric_cols = self.data_analyzer.data.select_dtypes(
            include=["float64", "int64"]
        ).columns
        if len(numeric_cols) < 2:
            QMessageBox.warning(
                self, "Error", "Need at least 2 numeric columns for clustering"
            )
            return

        canvas, _ = self.data_analyzer.perform_clustering(numeric_cols)
        if canvas:
            plot_window = QWidget()
            plot_layout = QVBoxLayout(plot_window)
            plot_layout.addWidget(canvas)
            plot_window.setWindowTitle("Clustering Results")
            plot_window.show()
