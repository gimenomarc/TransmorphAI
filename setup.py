from setuptools import setup, find_packages

setup(
    name="transmorphai",  
    version="0.1.0",
    author="Marc Gimeno",
    author_email="gimenocervantesmarc@gmail.com",
    description="A Python library for AI-powered API data transformation.",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/gimenomarc/TransmorphAI",
    packages=find_packages(),
    install_requires=[
        "openai",
        "python-dotenv"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
