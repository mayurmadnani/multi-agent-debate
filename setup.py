from setuptools import setup, find_packages

setup(
    name="debate-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "pyyaml>=6.0",
        "requests>=2.31.0",
        "streamlit>=1.28.0",
        "colorama>=0.4.6",
        "transformers>=4.35.0",
        "torch>=2.0.0",
        "accelerate>=0.24.0",
        "bitsandbytes>=0.41.0",
        "python-dotenv>=1.0.0",
    ],
    extras_require={
        "dev": ["pytest>=7.4.0", "pytest-cov>=4.1.0", "pytest-mock>=3.12.0"],
    },
    python_requires=">=3.9",
    description="Modular multi-agent philosophical debate system",
    author="",
)
