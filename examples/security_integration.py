"""Integration example showing complete security framework usage.

This script demonstrates how to integrate all security components
into a production application.
"""

import logging
import os
from pathlib import Path

from app.security import (
    AgentEncapsulation,
    AWSSecurityManager,
    DataPoisoningDefense,
    EnvironmentHardening,
    SecureDatabaseManager,
    SecureDataParser,
    SecurityMonitor,
)
from app.security.agent_security import NumericalProtection, PluginIsolation
from app.security.web_service import (
    InputValidator,
    RateLimiter,
    SecureWebHandler,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class SecureAIApplication:
    """Example secure AI application with full security framework."""

    def __init__(self, config: dict):
        """Initialize application with security controls.

        Args:
            config: Application configuration
        """
        self.config = config
        self.security_initialized = False

        # Initialize all security components
        self._init_environment()
        self._init_monitoring()
        self._init_database()
        self._init_aws()
        self._init_parsers()
        self._init_web_security()
        self._init_agents()

        self.security_initialized = True
        logger.info("✓ Secure AI Application initialized")

    def _init_environment(self):
        """Initialize environment hardening."""
        logger.info("Initializing environment hardening...")

        self.hardening = EnvironmentHardening(
            data_dir=self.config.get("data_dir", "data")
        )

        # Validate environment
        is_valid, issues = self.hardening.validate_environment()

        if not is_valid:
            logger.warning(f"Security issues detected: {issues}")

            # Apply fixes
            self.hardening.harden_sys_path()
            self.hardening.secure_directory_structure()

            # Re-validate
            is_valid, issues = self.hardening.validate_environment()

            if not is_valid:
                # In production, this should raise an error
                # For demo purposes, we'll log and continue
                logger.warning(f"Some security issues remain: {issues}")

        logger.info("✓ Environment hardened")

    def _init_monitoring(self):
        """Initialize security monitoring."""
        logger.info("Initializing security monitoring...")

        self.monitor = SecurityMonitor(
            region=self.config.get("aws_region", "us-east-1"),
            sns_topic_arn=self.config.get("sns_topic_arn"),
            cloudwatch_namespace=self.config.get(
                "cloudwatch_namespace", "ProjectAI/Security"
            ),
        )

        # Add common threat signatures
        self.monitor.add_threat_signature(
            "SQL Injection",
            ["' OR '1'='1", "UNION SELECT", "DROP TABLE", "--"],
        )

        self.monitor.add_threat_signature(
            "XSS", ["<script>", "javascript:", "onerror=", "onload="]
        )

        self.monitor.add_threat_signature(
            "Path Traversal", ["../../../", "..\\..\\..\\", "%2e%2e%2f"]
        )

        # Log startup
        self.monitor.log_security_event(
            event_type="application_startup",
            severity="low",
            source="init",
            description="Application started with full security framework",
            metadata={"version": "1.0.0"},
        )

        logger.info("✓ Security monitoring initialized")

    def _init_database(self):
        """Initialize secure database."""
        logger.info("Initializing secure database...")

        db_path = self.config.get("database_path", "data/secure.db")
        self.db = SecureDatabaseManager(db_path)

        logger.info(f"✓ Database initialized: {db_path}")

    def _init_aws(self):
        """Initialize AWS integration if in cloud environment."""
        if os.getenv("AWS_EXECUTION_ENV"):
            logger.info("Initializing AWS security manager...")

            try:
                self.aws = AWSSecurityManager(
                    region=self.config.get("aws_region", "us-east-1")
                )

                # Audit permissions
                audit = self.aws.audit_iam_permissions()
                logger.info(f"IAM Role: {audit.get('role_name')}")

                # Validate PoLP
                required_perms = self.config.get(
                    "required_aws_permissions",
                    [
                        "s3:GetObject",
                        "s3:PutObject",
                        "secretsmanager:GetSecretValue",
                        "cloudwatch:PutMetricData",
                    ],
                )

                if not self.aws.validate_polp(required_perms):
                    logger.warning("AWS role has excessive permissions")

                logger.info("✓ AWS security initialized")

            except Exception as e:
                logger.warning(f"AWS initialization failed: {e}")
                self.aws = None
        else:
            logger.info("Not in AWS environment - skipping AWS integration")
            self.aws = None

    def _init_parsers(self):
        """Initialize secure data parsers."""
        logger.info("Initializing secure parsers...")

        self.parser = SecureDataParser()
        self.poison_defense = DataPoisoningDefense()

        logger.info("✓ Parsers initialized")

    def _init_web_security(self):
        """Initialize web security components."""
        logger.info("Initializing web security...")

        self.web_handler = SecureWebHandler()
        self.rate_limiter = RateLimiter(
            max_requests=self.config.get("max_requests_per_minute", 100), window=60
        )
        self.input_validator = InputValidator()

        logger.info("✓ Web security initialized")

    def _init_agents(self):
        """Initialize AI agent security."""
        logger.info("Initializing agent security...")

        self.agents = {}
        self.numerical_protection = NumericalProtection()
        self.plugin_isolation = PluginIsolation(timeout=30)

        logger.info("✓ Agent security initialized")

    def create_agent(self, agent_id: str, permissions: dict) -> AgentEncapsulation:
        """Create a new secure AI agent.

        Args:
            agent_id: Unique agent identifier
            permissions: Permission configuration

        Returns:
            Configured agent
        """
        agent = AgentEncapsulation(agent_id)
        agent.set_permissions(**permissions)

        self.agents[agent_id] = agent

        self.monitor.log_security_event(
            event_type="agent_created",
            severity="low",
            source="agent_manager",
            description=f"Created agent: {agent_id}",
            metadata={"agent_id": agent_id, "permissions": permissions},
        )

        logger.info(f"✓ Created agent: {agent_id}")
        return agent

    def process_user_input(
        self, user_input: str, client_ip: str, user_id: int
    ) -> dict:
        """Process user input with full security validation.

        Args:
            user_input: User-provided input
            client_ip: Client IP address
            user_id: User identifier

        Returns:
            Processing result dictionary
        """
        # 1. Rate limiting
        if not self.rate_limiter.check_rate_limit(client_ip):
            self.monitor.log_security_event(
                event_type="rate_limit_exceeded",
                severity="medium",
                source="api",
                description=f"Rate limit exceeded for {client_ip}",
                metadata={"ip": client_ip, "user_id": user_id},
            )

            return {"error": "Rate limit exceeded", "status": 429}

        # 2. Input validation
        if not self.input_validator.validate_input(user_input, "application/json"):
            self.monitor.log_security_event(
                event_type="invalid_input",
                severity="medium",
                source="api",
                description="Invalid input format",
                metadata={"ip": client_ip, "user_id": user_id},
            )

            return {"error": "Invalid input", "status": 400}

        # 3. Poisoning check
        is_poisoned, patterns = self.poison_defense.check_for_poison(user_input)

        if is_poisoned:
            self.monitor.log_security_event(
                event_type="data_poisoning_attempt",
                severity="high",
                source="api",
                description=f"Data poisoning detected: {patterns}",
                metadata={"ip": client_ip, "user_id": user_id, "patterns": patterns},
            )

            # Blacklist the poisoned input
            self.poison_defense.add_poison_signature(user_input)

            return {"error": "Malicious input detected", "status": 403}

        # 4. Parse input
        result = self.parser.parse_json(user_input)

        if not result.validated:
            self.monitor.log_security_event(
                event_type="parsing_failed",
                severity="low",
                source="api",
                description="Input parsing failed",
                metadata={
                    "ip": client_ip,
                    "user_id": user_id,
                    "issues": result.issues,
                },
            )

            return {"error": "Parsing failed", "status": 400}

        # 5. Audit log
        self.db.log_action(
            user_id=user_id,
            action="process_input",
            resource="api_endpoint",
            details=result.data,
            ip_address=client_ip,
        )

        # 6. Process safely
        return {"success": True, "data": result.data, "status": 200}

    def execute_plugin(self, plugin_func, args, kwargs):
        """Execute untrusted plugin in isolation.

        Args:
            plugin_func: Plugin function
            args: Position arguments
            kwargs: Keyword arguments

        Returns:
            Plugin execution result
        """
        try:
            result = self.plugin_isolation.execute_isolated(
                plugin_func=plugin_func, args=args, kwargs=kwargs
            )

            self.monitor.log_security_event(
                event_type="plugin_executed",
                severity="low",
                source="plugin_manager",
                description="Plugin executed successfully",
            )

            return {"success": True, "result": result}

        except TimeoutError:
            self.monitor.log_security_event(
                event_type="plugin_timeout",
                severity="high",
                source="plugin_manager",
                description="Plugin execution timed out",
            )

            return {"error": "Plugin timeout"}

        except Exception as e:
            self.monitor.log_security_event(
                event_type="plugin_error",
                severity="medium",
                source="plugin_manager",
                description=f"Plugin execution failed: {e}",
            )

            return {"error": str(e)}

    def get_security_status(self) -> dict:
        """Get comprehensive security status.

        Returns:
            Security status dictionary
        """
        status = {
            "environment": self.hardening.get_validation_report(),
            "monitoring": self.monitor.get_event_statistics(time_window=3600),
            "agents": {
                agent_id: len(agent.get_access_log())
                for agent_id, agent in self.agents.items()
            },
        }

        # Add AWS status if available
        if self.aws:
            status["aws"] = {
                "initialized": True,
                "region": self.config.get("aws_region"),
            }

        return status

    def shutdown(self):
        """Gracefully shutdown application."""
        logger.info("Shutting down application...")

        # Log shutdown event
        self.monitor.log_security_event(
            event_type="application_shutdown",
            severity="low",
            source="shutdown",
            description="Application shutting down gracefully",
        )

        # Get final statistics
        stats = self.monitor.get_event_statistics()
        logger.info(f"Final event statistics: {stats}")

        logger.info("✓ Application shutdown complete")


def main():
    """Example application usage."""
    # Configuration
    config = {
        "data_dir": "data",
        "database_path": "data/secure.db",
        "aws_region": "us-east-1",
        "sns_topic_arn": os.getenv("SECURITY_SNS_TOPIC"),
        "cloudwatch_namespace": "ProjectAI/Security",
        "max_requests_per_minute": 100,
        "required_aws_permissions": [
            "s3:GetObject",
            "s3:PutObject",
            "secretsmanager:GetSecretValue",
            "cloudwatch:PutMetricData",
        ],
    }

    # Initialize application
    app = SecureAIApplication(config)

    # Create an AI agent
    agent = app.create_agent(
        agent_id="assistant_1", permissions={"read": True, "write": True, "execute": False}
    )

    # Store some state
    agent.set_state("model_version", "1.0.0", caller="system")

    # Simulate user requests
    print("\n=== Testing User Input Processing ===")

    # Normal request
    result = app.process_user_input(
        user_input='{"query": "Hello, world!"}', client_ip="192.168.1.100", user_id=1
    )
    print(f"Normal request: {result}")

    # Malicious request
    result = app.process_user_input(
        user_input='<script>alert("xss")</script>',
        client_ip="192.168.1.200",
        user_id=2,
    )
    print(f"Malicious request: {result}")

    # Get security status
    print("\n=== Security Status ===")
    status = app.get_security_status()
    print(f"Events (last hour): {status['monitoring']['total_events']}")
    print(f"By severity: {status['monitoring']['by_severity']}")

    # Shutdown
    app.shutdown()


if __name__ == "__main__":
    main()
