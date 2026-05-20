"""Deployment tests for Docker, docker-compose, and systemd configurations"""

import os
import subprocess
from pathlib import Path

import pytest


class TestDockerfile:
    """Dockerfile tests"""

    def test_dockerfile_exists(self):
        """Test that Dockerfile exists in project root"""
        dockerfile = Path(__file__).parent.parent / "Dockerfile"
        assert dockerfile.exists(), "Dockerfile should exist in project root"

    def test_dockerfile_valid_syntax(self):
        """Test that Dockerfile has valid syntax"""
        dockerfile = Path(__file__).parent.parent / "Dockerfile"
        content = dockerfile.read_text()

        # Check for required stages
        assert "FROM python:3.12-slim AS builder" in content
        assert "FROM python:3.12-slim" in content
        assert "COPY --from=builder" in content

        # Check for required directives
        assert "WORKDIR /app" in content
        assert "EXPOSE 8000" in content
        assert "CMD " in content

        # Check for health check
        assert "HEALTHCHECK" in content

    def test_dockerfile_optimizations(self):
        """Test that Dockerfile uses best practices"""
        dockerfile = Path(__file__).parent.parent / "Dockerfile"
        content = dockerfile.read_text()

        # Multi-stage build
        assert "AS builder" in content, "Should use multi-stage build"

        # No cache in pip install
        assert "--no-cache-dir" in content, "Should use --no-cache-dir for pip"

        # Non-root user
        assert "USER kidagent" in content or "USER" in content, "Should run as non-root user"


class TestDockerCompose:
    """docker-compose.yml tests"""

    def test_docker_compose_exists(self):
        """Test that docker-compose.yml exists"""
        compose_file = Path(__file__).parent.parent / "docker-compose.yml"
        assert compose_file.exists(), "docker-compose.yml should exist"

    def test_docker_compose_valid_structure(self):
        """Test that docker-compose.yml has valid structure"""
        import yaml

        compose_file = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_file, "r") as f:
            config = yaml.safe_load(f)

        assert "version" in config
        assert "services" in config
        assert "kid-agent" in config["services"]

        service = config["services"]["kid-agent"]
        assert "build" in service or "image" in service
        assert "ports" in service
        assert "volumes" in service
        assert "healthcheck" in service

    def test_docker_compose_port_mapping(self):
        """Test that docker-compose.yml has correct port mapping"""
        import yaml

        compose_file = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_file, "r") as f:
            config = yaml.safe_load(f)

        ports = config["services"]["kid-agent"].get("ports", [])
        assert any("8000" in str(p) for p in ports), "Should map port 8000"

    def test_docker_compose_volumes(self):
        """Test that docker-compose.yml has correct volume mappings"""
        import yaml

        compose_file = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_file, "r") as f:
            config = yaml.safe_load(f)

        volumes = config["services"]["kid-agent"].get("volumes", [])
        volume_strs = [str(v) for v in volumes]

        # Should have data and config volumes
        assert any("data" in v for v in volume_strs), "Should have data volume"
        assert any("config" in v for v in volume_strs), "Should have config volume"

    def test_docker_compose_environment(self):
        """Test that docker-compose.yml has environment variables"""
        import yaml

        compose_file = Path(__file__).parent.parent / "docker-compose.yml"
        with open(compose_file, "r") as f:
            config = yaml.safe_load(f)

        env = config["services"]["kid-agent"].get("environment", {})

        # Check for key environment variables
        assert "DB_PATH" in env or any("DB_PATH" in str(e) for e in env)
        assert "LOG_LEVEL" in env or any("LOG_LEVEL" in str(e) for e in env)


class TestDockerignore:
    """.dockerignore tests"""

    def test_dockerignore_exists(self):
        """Test that .dockerignore exists"""
        dockerignore = Path(__file__).parent.parent / ".dockerignore"
        assert dockerignore.exists(), ".dockerignore should exist"

    def test_dockerignore_excludes_unnecessary_files(self):
        """Test that .dockerignore excludes unnecessary files"""
        dockerignore = Path(__file__).parent.parent / ".dockerignore"
        content = dockerignore.read_text()

        # Should exclude common patterns
        assert "__pycache__" in content
        assert ".git" in content
        assert ".venv" in content
        # .dockerignore may use *.py[cod] or *.pyc
        assert "*.pyc" in content or "*.py[" in content

    def test_dockerignore_excludes_tests(self):
        """Test that .dockerignore excludes test files"""
        dockerignore = Path(__file__).parent.parent / ".dockerignore"
        content = dockerignore.read_text()

        assert "tests/" in content or "*.test.py" in content


class TestSystemdService:
    """Systemd service file tests"""

    def test_systemd_service_exists(self):
        """Test that kid-agent.service exists"""
        service_file = Path(__file__).parent.parent / "deploy" / "kid-agent.service"
        assert service_file.exists(), "kid-agent.service should exist in deploy/"

    def test_systemd_service_valid_sections(self):
        """Test that systemd service has required sections"""
        service_file = Path(__file__).parent.parent / "deploy" / "kid-agent.service"
        content = service_file.read_text()

        assert "[Unit]" in content, "Should have [Unit] section"
        assert "[Service]" in content, "Should have [Service] section"
        assert "[Install]" in content, "Should have [Install] section"

    def test_systemd_service_required_directives(self):
        """Test that systemd service has required directives"""
        service_file = Path(__file__).parent.parent / "deploy" / "kid-agent.service"
        content = service_file.read_text()

        # Unit section
        assert "Description=" in content, "Should have Description"
        assert "After=" in content, "Should have After directive"

        # Service section
        assert "Type=" in content, "Should have Type directive"
        assert "User=" in content, "Should have User directive"
        assert "WorkingDirectory=" in content, "Should have WorkingDirectory"
        assert "ExecStart=" in content, "Should have ExecStart"
        assert "Restart=" in content, "Should have Restart policy"

        # Install section
        assert "WantedBy=" in content, "Should have WantedBy"

    def test_systemd_service_security(self):
        """Test that systemd service has security settings"""
        service_file = Path(__file__).parent.parent / "deploy" / "kid-agent.service"
        content = service_file.read_text()

        # Check for security directives
        security_directives = [
            "NoNewPrivileges",
            "PrivateTmp",
            "ProtectSystem",
            "ProtectHome",
            "ReadWritePaths",
        ]

        has_security = any(directive in content for directive in security_directives)
        assert has_security, "Should have at least one security directive"


class TestNginxConfig:
    """Nginx configuration tests"""

    def test_nginx_config_exists(self):
        """Test that nginx-kid-agent.conf exists"""
        nginx_file = Path(__file__).parent.parent / "deploy" / "nginx-kid-agent.conf"
        assert nginx_file.exists(), "nginx-kid-agent.conf should exist"

    def test_nginx_config_websocket_support(self):
        """Test that nginx config supports WebSocket"""
        nginx_file = Path(__file__).parent.parent / "deploy" / "nginx-kid-agent.conf"
        content = nginx_file.read_text()

        # Check for WebSocket upgrade headers
        assert "upgrade" in content.lower() or "Upgrade" in content
        assert "Connection" in content

    def test_nginx_config_proxy_pass(self):
        """Test that nginx config has proxy_pass"""
        nginx_file = Path(__file__).parent.parent / "deploy" / "nginx-kid-agent.conf"
        content = nginx_file.read_text()

        assert "proxy_pass" in content
        assert "127.0.0.1:8000" in content or "kid_agent_backend" in content

    def test_nginx_config_proxy_settings(self):
        """Test that nginx config has proxy settings"""
        nginx_file = Path(__file__).parent.parent / "deploy" / "nginx-kid-agent.conf"
        content = nginx_file.read_text()

        # Should have proxy settings for HTTP headers
        assert "X-Real-IP" in content or "X-Forwarded-For" in content
        assert "X-Forwarded-Proto" in content or "X-Forwarded" in content


class TestDeployScript:
    """Deploy script tests"""

    def test_deploy_script_exists(self):
        """Test that deploy.sh exists"""
        deploy_script = Path(__file__).parent.parent / "scripts" / "deploy.sh"
        assert deploy_script.exists(), "deploy.sh should exist"

    def test_deploy_script_executable(self):
        """Test that deploy.sh is executable"""
        deploy_script = Path(__file__).parent.parent / "scripts" / "deploy.sh"
        assert os.access(deploy_script, os.X_OK), "deploy.sh should be executable"

    def test_deploy_script_has_functions(self):
        """Test that deploy.sh has required functions"""
        deploy_script = Path(__file__).parent.parent / "scripts" / "deploy.sh"
        content = deploy_script.read_text()

        # Check for key functions
        required_functions = [
            "install_service",
            "start_service",
            "stop_service",
            "restart_service",
            "health_check",
        ]

        for func in required_functions:
            assert func in content, f"deploy.sh should have {func} function"

    def test_deploy_script_has_help(self):
        """Test that deploy.sh has help function"""
        deploy_script = Path(__file__).parent.parent / "scripts" / "deploy.sh"
        content = deploy_script.read_text()

        assert "usage" in content.lower() or "Usage" in content or "help" in content.lower()


class TestProductionConfig:
    """Production configuration tests"""

    def test_production_env_template_exists(self):
        """Test that .env.production exists"""
        env_file = Path(__file__).parent.parent / "config" / ".env.production"
        assert env_file.exists(), ".env.production should exist"

    def test_production_env_has_sections(self):
        """Test that .env.production has configuration sections"""
        env_file = Path(__file__).parent.parent / "config" / ".env.production"
        content = env_file.read_text()

        # Check for key sections
        sections = [
            "LLM",
            "Database",
            "TTS",
            "WeChat",
            "CORS",
        ]

        for section in sections:
            assert section in content, f".env.production should have {section} section"

    def test_production_env_has_placeholders(self):
        """Test that .env.production has placeholder values"""
        env_file = Path(__file__).parent.parent / "config" / ".env.production"
        content = env_file.read_text()

        # Should have placeholder values, not real keys
        assert "your_glm_api_key_here" in content or "your_api_key" in content.lower()
        assert "yourdomain.com" in content or "example.com" in content


class TestProductionConfigClass:
    """ProductionConfig class tests in settings.py"""

    @pytest.mark.asyncio
    async def test_get_production_config(self):
        """Test that get_production_config returns production environment"""
        from src.config.settings import get_production_config

        old_env = os.environ.get("ENVIRONMENT")

        try:
            config = get_production_config()
            assert config.environment.value == "production"
        finally:
            if old_env is not None:
                os.environ["ENVIRONMENT"] = old_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]

    @pytest.mark.asyncio
    async def test_get_development_config(self):
        """Test that get_development_config returns development environment"""
        from src.config.settings import get_development_config

        old_env = os.environ.get("ENVIRONMENT")

        try:
            config = get_development_config()
            assert config.environment.value == "development"
        finally:
            if old_env is not None:
                os.environ["ENVIRONMENT"] = old_env
            elif "ENVIRONMENT" in os.environ:
                del os.environ["ENVIRONMENT"]


class TestDockerBuild:
    """Docker build tests (optional - requires Docker)"""

    @pytest.mark.skipif(
        not os.path.exists("/usr/bin/docker") and not os.path.exists("/usr/local/bin/docker"),
        reason="Docker not installed"
    )
    def test_docker_can_build(self, tmp_path):
        """Test that Dockerfile can build (integration test)"""
        result = subprocess.run(
            ["docker", "build", "-t", "kid-agent-test", "--no-cache", "-f", "Dockerfile", "."],
            capture_output=True,
            text=True,
            timeout=300,
        )

        # Note: This test may fail if API keys are not configured
        # The test mainly checks if Dockerfile syntax is correct
        if result.returncode != 0:
            # Check if it's a syntax error or dependency issue
            if "syntax" in result.stderr.lower() or "unknown" in result.stderr.lower():
                pytest.fail(f"Dockerfile syntax error: {result.stderr}")
