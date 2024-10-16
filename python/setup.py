import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cs2cpp",
    version="0.2.0",
    author="Ethosa",
    author_email="social.ethosa@gmail.com",
    description="Csharp to Cpp code translator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/linksplatform/RegularExpressions.Transformer.CSharpToCpp/tree/master/python",
    packages=setuptools.find_packages(),
    license="LGPLv3",
    keywords="csharp cpp cs2cpp links platform ethosa konard",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: OS Independent",
    ],
    project_urls={
        "Github": "https://github.com/linksplatform/RegularExpressions.Transformer.CSharpToCpp/tree/master/python",
        "Documentation": "https://github.com/linksplatform/RegularExpressions.Transformer.CSharpToCpp/tree/master/python",
    },
    python_requires=">=3",
    install_requires=["retranslator >= 0.2.0"]
)
