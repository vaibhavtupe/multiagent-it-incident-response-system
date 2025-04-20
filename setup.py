from setuptools import setup, find_packages

setup(
    name="it_incident_response",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.2",
        "colorlog>=6.7.0",
        "numpy>=1.24.0",
    ],
    author="Your Name",
    author_email="your.email@example.com",
    description="Automated IT Incident Response System using Google A2A and Anthropic MCP",
    keywords="incident, response, a2a, mcp, agent",
    python_requires=">=3.8",
)