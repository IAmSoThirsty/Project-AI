from setuptools import setup, find_packages

setup(
    name="ai-desktop-assistant",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        'PyQt6',
        'openai',
        'requests',
        'python-dotenv',
        'cryptography',
        'geopy',
        'PyPDF2',
        'numpy',
        'pandas',
        'matplotlib',
        'scikit-learn',
        'passlib'
    ],
    entry_points={
        'console_scripts': [
            'ai-assistant=app.main:main',
        ],
    },
    author="Your Name",
    description="AI Desktop Assistant with various features",
    python_requires=">=3.8",
)
