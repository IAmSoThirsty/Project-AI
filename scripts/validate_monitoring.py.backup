#!/usr/bin/env python3
"""
Monitoring Infrastructure Validation Script
Tests Prometheus, Grafana, AlertManager, and all exporters
"""

import sys
from datetime import datetime

import requests

# Color codes for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


class MonitoringValidator:
    def __init__(self):
        self.prometheus_url = "http://localhost:9090"
        self.grafana_url = "http://localhost:3000"
        self.alertmanager_url = "http://localhost:9093"
        self.results = []

    def print_header(self, text: str):
        print(f"\n{BLUE}{'='*60}{RESET}")
        print(f"{BLUE}{text.center(60)}{RESET}")
        print(f"{BLUE}{'='*60}{RESET}\n")

    def print_success(self, text: str):
        print(f"{GREEN}✓{RESET} {text}")

    def print_error(self, text: str):
        print(f"{RED}✗{RESET} {text}")

    def print_warning(self, text: str):
        print(f"{YELLOW}⚠{RESET} {text}")

    def test_prometheus_health(self) -> bool:
        """Test Prometheus health endpoint"""
        self.print_header("Testing Prometheus")

        try:
            response = requests.get(f"{self.prometheus_url}/-/healthy", timeout=5)
            if response.status_code == 200:
                self.print_success("Prometheus is healthy")
                self.results.append(("Prometheus Health", True))
                return True
            else:
                self.print_error(f"Prometheus health check failed: {response.status_code}")
                self.results.append(("Prometheus Health", False))
                return False
        except Exception as e:
            self.print_error(f"Cannot connect to Prometheus: {e}")
            self.results.append(("Prometheus Health", False))
            return False

    def test_prometheus_targets(self) -> bool:
        """Test Prometheus scrape targets"""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/targets", timeout=5)
            data = response.json()

            if data["status"] != "success":
                self.print_error("Failed to fetch Prometheus targets")
                return False

            targets = data["data"]["activeTargets"]
            up_count = sum(1 for t in targets if t["health"] == "up")
            total_count = len(targets)

            self.print_success(f"Scrape targets: {up_count}/{total_count} UP")

            # List targets
            for target in targets:
                job = target["labels"].get("job", "unknown")
                health = target["health"]
                if health == "up":
                    self.print_success(f"  {job}: {health}")
                else:
                    error = target.get("lastError", "unknown error")
                    self.print_error(f"  {job}: {health} - {error}")

            self.results.append(("Prometheus Targets", up_count == total_count))
            return up_count == total_count

        except Exception as e:
            self.print_error(f"Error checking targets: {e}")
            self.results.append(("Prometheus Targets", False))
            return False

    def test_prometheus_rules(self) -> bool:
        """Test Prometheus alerting and recording rules"""
        try:
            response = requests.get(f"{self.prometheus_url}/api/v1/rules", timeout=5)
            data = response.json()

            if data["status"] != "success":
                self.print_error("Failed to fetch Prometheus rules")
                return False

            groups = data["data"]["groups"]
            total_rules = sum(len(g["rules"]) for g in groups)
            alert_rules = sum(1 for g in groups for r in g["rules"] if r["type"] == "alerting")
            recording_rules = sum(1 for g in groups for r in g["rules"] if r["type"] == "recording")

            self.print_success(f"Total rules: {total_rules}")
            self.print_success(f"  Alert rules: {alert_rules}")
            self.print_success(f"  Recording rules: {recording_rules}")

            # Check for firing alerts
            firing_alerts = [
                r
                for g in groups
                for r in g["rules"]
                if r["type"] == "alerting" and r["state"] == "firing"
            ]

            if firing_alerts:
                self.print_warning(f"  {len(firing_alerts)} alerts currently firing")
                for alert in firing_alerts[:5]:  # Show first 5
                    self.print_warning(f"    - {alert['name']}")
            else:
                self.print_success("  No alerts firing")

            self.results.append(("Prometheus Rules", True))
            return True

        except Exception as e:
            self.print_error(f"Error checking rules: {e}")
            self.results.append(("Prometheus Rules", False))
            return False

    def test_prometheus_metrics(self) -> bool:
        """Test that key metrics exist"""
        self.print_header("Testing Prometheus Metrics")

        expected_metrics = [
            "project_ai_api_requests_total",
            "project_ai_four_laws_validations_total",
            "project_ai_security_incidents_total",
            "node_cpu_seconds_total",
            "container_memory_usage_bytes",
            "pg_stat_database_numbackends",
        ]

        all_found = True
        for metric in expected_metrics:
            try:
                response = requests.get(
                    f"{self.prometheus_url}/api/v1/query",
                    params={"query": f"count({metric})"},
                    timeout=5,
                )
                data = response.json()

                if data["status"] == "success" and data["data"]["result"]:
                    count = int(data["data"]["result"][0]["value"][1])
                    self.print_success(f"{metric}: {count} time series")
                else:
                    self.print_warning(f"{metric}: NOT FOUND")
                    all_found = False

            except Exception as e:
                self.print_error(f"{metric}: Error - {e}")
                all_found = False

        self.results.append(("Prometheus Metrics", all_found))
        return all_found

    def test_grafana_health(self) -> bool:
        """Test Grafana health"""
        self.print_header("Testing Grafana")

        try:
            response = requests.get(f"{self.grafana_url}/api/health", timeout=5)
            data = response.json()

            if data.get("database") == "ok":
                self.print_success("Grafana is healthy")
                self.results.append(("Grafana Health", True))
                return True
            else:
                self.print_error(f"Grafana health check failed: {data}")
                self.results.append(("Grafana Health", False))
                return False

        except Exception as e:
            self.print_error(f"Cannot connect to Grafana: {e}")
            self.results.append(("Grafana Health", False))
            return False

    def test_grafana_datasources(self) -> bool:
        """Test Grafana datasources"""
        try:
            # Note: This requires authentication
            # For now, we'll just test connectivity
            response = requests.get(
                f"{self.grafana_url}/api/datasources", auth=("admin", "admin"), timeout=5
            )

            if response.status_code == 200:
                datasources = response.json()
                self.print_success(f"Grafana datasources: {len(datasources)}")
                for ds in datasources:
                    self.print_success(f"  {ds['name']} ({ds['type']})")
                self.results.append(("Grafana Datasources", True))
                return True
            else:
                self.print_warning("Could not fetch datasources (may need login)")
                self.results.append(("Grafana Datasources", False))
                return False

        except Exception as e:
            self.print_warning(f"Error checking datasources: {e}")
            self.results.append(("Grafana Datasources", False))
            return False

    def test_alertmanager_health(self) -> bool:
        """Test AlertManager health"""
        self.print_header("Testing AlertManager")

        try:
            response = requests.get(f"{self.alertmanager_url}/-/healthy", timeout=5)
            if response.status_code == 200:
                self.print_success("AlertManager is healthy")
                self.results.append(("AlertManager Health", True))
                return True
            else:
                self.print_error(f"AlertManager health check failed: {response.status_code}")
                self.results.append(("AlertManager Health", False))
                return False
        except Exception as e:
            self.print_error(f"Cannot connect to AlertManager: {e}")
            self.results.append(("AlertManager Health", False))
            return False

    def test_alertmanager_status(self) -> bool:
        """Test AlertManager status and alerts"""
        try:
            response = requests.get(f"{self.alertmanager_url}/api/v2/status", timeout=5)
            data = response.json()

            cluster = data.get("cluster", {})
            peers = cluster.get("peers", [])

            self.print_success(f"AlertManager cluster: {cluster.get('status', 'unknown')}")
            self.print_success(f"  Peers: {len(peers)}")

            # Check for active alerts
            alerts_response = requests.get(f"{self.alertmanager_url}/api/v2/alerts", timeout=5)
            alerts = alerts_response.json()

            if alerts:
                self.print_warning(f"  {len(alerts)} active alerts")
                for alert in alerts[:5]:  # Show first 5
                    labels = alert.get("labels", {})
                    self.print_warning(f"    - {labels.get('alertname', 'unknown')}")
            else:
                self.print_success("  No active alerts")

            self.results.append(("AlertManager Status", True))
            return True

        except Exception as e:
            self.print_error(f"Error checking AlertManager status: {e}")
            self.results.append(("AlertManager Status", False))
            return False

    def print_summary(self):
        """Print test summary"""
        self.print_header("Test Summary")

        total = len(self.results)
        passed = sum(1 for _, result in self.results if result)
        failed = total - passed

        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {passed}{RESET}")
        print(f"{RED}Failed: {failed}{RESET}")
        print(f"Success Rate: {(passed/total*100):.1f}%\n")

        if failed > 0:
            print(f"{RED}Failed Tests:{RESET}")
            for name, result in self.results:
                if not result:
                    print(f"  {RED}✗{RESET} {name}")

        print()
        return failed == 0

    def run_all_tests(self) -> bool:
        """Run all validation tests"""
        print(f"\n{BLUE}╔{'═'*58}╗{RESET}")
        print(f"{BLUE}║{'Monitoring Infrastructure Validation'.center(58)}║{RESET}")
        print(f"{BLUE}║{datetime.now().strftime('%Y-%m-%d %H:%M:%S').center(58)}║{RESET}")
        print(f"{BLUE}╚{'═'*58}╝{RESET}")

        # Run all tests
        self.test_prometheus_health()
        self.test_prometheus_targets()
        self.test_prometheus_rules()
        self.test_prometheus_metrics()
        self.test_grafana_health()
        self.test_grafana_datasources()
        self.test_alertmanager_health()
        self.test_alertmanager_status()

        # Print summary
        return self.print_summary()


def main():
    validator = MonitoringValidator()
    success = validator.run_all_tests()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
