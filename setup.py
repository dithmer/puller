import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="puller",  # Replace with your own username
    version="0.3.0.dev4",
    author="Tim Dithmer",
    author_email="dith.tim@gmail.com",
    description="An automatic repo puller",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/dithmer/puller",
    project_urls={
        "Bug Tracker": "https://github.com/dithmer/puller/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=["fastapi", "pyyaml", "uvicorn", "shellescape"],
    packages=setuptools.find_packages(),
    python_requires=">=3.6",
    entry_points={  
        "console_scripts": [
            "puller=puller:start_server",
        ],
    },
)