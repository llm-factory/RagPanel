from setuptools import setup, find_packages


def get_requires():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        file_content = f.read()
        lines = [line.strip() for line in file_content.strip().split("\n") if not line.startswith("#")]
        return lines


extras_require={
    "redis": "redis",
    "es": "elasticsearch[async]",
    "elasticsearch": "elasticsearch[async]",
    "chroma": "chromadb",
    "milvus": "pymilvus>=2.3.0"
}

def main():
    setup(
        name="ragpanel",
        version="0.1",
        author="the-seeds", 
        description="a unified rag platform",
        long_description=open("README.md").read(),
        long_description_content_type="text/markdown",
        keywords=["LLM", "RAG"],
        license="Apache 2.0 License",
        url="https://github.com/the-seeds/RagPanel",
        package_dir={"": "src"},
        packages=find_packages("src"),
        python_requires=">=3.9.0",
        install_requires=get_requires(),
        extras_require=extras_require,
        entry_points={"console_scripts": ["ragpanel-cli = RagPanel.api.launch:interactive_cli"]},
        classifiers=[
            "Development Status :: 3 - Alpha",
            "Intended Audience :: Developers",
            "Intended Audience :: Education",
            "Intended Audience :: Science/Research",
            "License :: OSI Approved :: Apache Software License",
            "Operating System :: OS Independent",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: 3.9",
            "Programming Language :: Python :: 3.10",
            "Programming Language :: Python :: 3.11",
            "Topic :: Scientific/Engineering :: Artificial Intelligence",
        ] 
    )
    

if __name__ == "__main__":
    main()