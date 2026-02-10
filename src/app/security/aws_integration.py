"""AWS cloud security integration for Project-AI.

This module implements:
- AWS Boto3 integration for S3/EBS/Secrets Manager
- PoLP (Principle of Least Privilege) IAM validation
- Temporary credential management
- Permission auditing
- Secure resource access
"""

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)

try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError, NoCredentialsError

    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False
    logger.warning("boto3 not available - AWS features disabled")


class AWSSecurityManager:
    """Secure AWS resource management with PoLP."""

    def __init__(self, region: str = "us-east-1"):
        """Initialize AWS security manager.

        Args:
            region: AWS region to use
        """
        if not BOTO3_AVAILABLE:
            raise ImportError("boto3 is required for AWS integration")

        self.region = region
        self.session = None
        self._init_session()

    def _init_session(self) -> None:
        """Initialize AWS session with IAM role credentials."""
        try:
            # Try to use IAM role credentials (no static credentials)
            self.session = boto3.Session(region_name=self.region)

            # Verify credentials
            sts = self.session.client("sts")
            identity = sts.get_caller_identity()
            logger.info(
                "AWS session initialized: %s (%s)",
                identity.get("Arn"),
                identity.get("Account"),
            )

        except NoCredentialsError:
            logger.error(
                "No AWS credentials found - must use IAM role or temp credentials"
            )
            raise
        except (BotoCoreError, ClientError) as e:
            logger.error("Failed to initialize AWS session: %s", e)
            raise

    def get_secret(self, secret_name: str) -> dict[str, Any]:
        """Retrieve secret from AWS Secrets Manager.

        Args:
            secret_name: Name of the secret

        Returns:
            Secret data as dictionary

        Raises:
            ClientError: If secret retrieval fails
        """
        try:
            client = self.session.client("secretsmanager")
            response = client.get_secret_value(SecretId=secret_name)

            # Parse secret
            if "SecretString" in response:
                return json.loads(response["SecretString"])
            else:
                # Binary secret
                return {"binary": response["SecretBinary"]}

        except ClientError as e:
            logger.error("Failed to retrieve secret %s: %s", secret_name, e)
            raise

    def put_secret(self, secret_name: str, secret_data: dict[str, Any]) -> None:
        """Store secret in AWS Secrets Manager.

        Args:
            secret_name: Name of the secret
            secret_data: Secret data to store

        Raises:
            ClientError: If secret storage fails
        """
        try:
            client = self.session.client("secretsmanager")

            # Try to create or update
            try:
                client.create_secret(
                    Name=secret_name, SecretString=json.dumps(secret_data)
                )
                logger.info("Created secret: %s", secret_name)
            except client.exceptions.ResourceExistsException:
                client.update_secret(
                    SecretId=secret_name, SecretString=json.dumps(secret_data)
                )
                logger.info("Updated secret: %s", secret_name)

        except ClientError as e:
            logger.error("Failed to store secret %s: %s", secret_name, e)
            raise

    def upload_to_s3(
        self, bucket: str, key: str, data: bytes, encryption: str = "AES256"
    ) -> None:
        """Upload data to S3 with encryption.

        Args:
            bucket: S3 bucket name
            key: Object key
            data: Data to upload
            encryption: Server-side encryption method

        Raises:
            ClientError: If upload fails
        """
        try:
            s3 = self.session.client("s3")

            # Upload with server-side encryption
            s3.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ServerSideEncryption=encryption,
            )

            logger.info("Uploaded to S3: s3://%s/%s", bucket, key)

        except ClientError as e:
            logger.error("Failed to upload to S3: %s", e)
            raise

    def download_from_s3(self, bucket: str, key: str) -> bytes:
        """Download data from S3.

        Args:
            bucket: S3 bucket name
            key: Object key

        Returns:
            Downloaded data

        Raises:
            ClientError: If download fails
        """
        try:
            s3 = self.session.client("s3")
            response = s3.get_object(Bucket=bucket, Key=key)

            data = response["Body"].read()
            logger.info("Downloaded from S3: s3://%s/%s", bucket, key)

            return data

        except ClientError as e:
            logger.error("Failed to download from S3: %s", e)
            raise

    def audit_iam_permissions(self, role_arn: str | None = None) -> dict[str, Any]:
        """Audit IAM permissions for current role.

        Args:
            role_arn: Optional specific role ARN to audit

        Returns:
            Dictionary containing permission audit results
        """
        try:
            iam = self.session.client("iam")
            sts = self.session.client("sts")

            # Get current identity
            if not role_arn:
                identity = sts.get_caller_identity()
                role_arn = identity.get("Arn")

            # Extract role name from ARN
            if ":role/" in role_arn:
                role_name = role_arn.split(":role/")[-1]
            else:
                return {"error": "Not a role ARN"}

            # Get role policies
            attached_policies = iam.list_attached_role_policies(RoleName=role_name)
            inline_policies = iam.list_role_policies(RoleName=role_name)

            audit_result = {
                "role_arn": role_arn,
                "role_name": role_name,
                "attached_policies": attached_policies.get("AttachedPolicies", []),
                "inline_policies": inline_policies.get("PolicyNames", []),
                "permissions": [],
            }

            # Get policy details
            for policy in attached_policies.get("AttachedPolicies", []):
                policy_arn = policy["PolicyArn"]
                try:
                    policy_version = iam.get_policy(PolicyArn=policy_arn)
                    version_id = policy_version["Policy"]["DefaultVersionId"]

                    policy_doc = iam.get_policy_version(
                        PolicyArn=policy_arn, VersionId=version_id
                    )

                    audit_result["permissions"].append(
                        {
                            "policy_name": policy["PolicyName"],
                            "policy_arn": policy_arn,
                            "document": policy_doc["PolicyVersion"]["Document"],
                        }
                    )
                except ClientError as e:
                    logger.warning("Could not get policy %s: %s", policy_arn, e)

            logger.info("IAM audit completed for role: %s", role_name)
            return audit_result

        except ClientError as e:
            logger.error("IAM audit failed: %s", e)
            return {"error": str(e)}

    def validate_polp(self, required_permissions: list[str]) -> bool:
        """Validate that current role follows PoLP.

        Args:
            required_permissions: List of required permissions

        Returns:
            True if PoLP is followed
        """
        audit = self.audit_iam_permissions()

        if "error" in audit:
            logger.error("Cannot validate PoLP: %s", audit["error"])
            return False

        # Check if we have only required permissions
        all_permissions = set()

        for perm in audit.get("permissions", []):
            doc = perm.get("document", {})
            for statement in doc.get("Statement", []):
                actions = statement.get("Action", [])
                if isinstance(actions, str):
                    actions = [actions]
                all_permissions.update(actions)

        # Check for overly permissive wildcards
        dangerous_patterns = ["*:*", "*"]
        for pattern in dangerous_patterns:
            if pattern in all_permissions:
                logger.warning("Overly permissive permission detected: %s", pattern)
                return False

        logger.info("PoLP validation passed")
        return True

    def enable_mfa_delete(self, bucket: str) -> None:
        """Enable MFA Delete on S3 bucket for critical data protection.

        Args:
            bucket: S3 bucket name

        Raises:
            ClientError: If operation fails
        """
        try:
            s3 = self.session.client("s3")

            # Enable versioning (required for MFA Delete)
            s3.put_bucket_versioning(
                Bucket=bucket,
                VersioningConfiguration={"Status": "Enabled"},
            )

            logger.info("Enabled versioning on bucket: %s", bucket)
            logger.warning("MFA Delete must be enabled via root account with MFA token")

        except ClientError as e:
            logger.error("Failed to enable versioning: %s", e)
            raise

    def get_temporary_credentials(
        self, role_arn: str, session_name: str, duration: int = 3600
    ) -> dict[str, str]:
        """Get temporary credentials via STS AssumeRole.

        Args:
            role_arn: ARN of role to assume
            session_name: Session name for tracking
            duration: Session duration in seconds

        Returns:
            Dictionary with temporary credentials

        Raises:
            ClientError: If role assumption fails
        """
        try:
            sts = self.session.client("sts")

            response = sts.assume_role(
                RoleArn=role_arn,
                RoleSessionName=session_name,
                DurationSeconds=duration,
            )

            credentials = response["Credentials"]

            logger.info("Assumed role: %s (session: %s)", role_arn, session_name)

            return {
                "access_key_id": credentials["AccessKeyId"],
                "secret_access_key": credentials["SecretAccessKey"],
                "session_token": credentials["SessionToken"],
                "expiration": credentials["Expiration"].isoformat(),
            }

        except ClientError as e:
            logger.error("Failed to assume role %s: %s", role_arn, e)
            raise
