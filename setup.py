from setuptools import setup, find_packages

setup(
    name="baixar",
    version="1.0.0",
    description="Script para copiar e mover arquivos do Google Drive usando a API do Google Drive.",
    author="Caio Hamamura",
    author_email="caiohamamura@gmail.com",
    packages=find_packages(),
    install_requires=[
        "google-api-python-client",
        "google-auth-httplib2",
        "google-auth-oauthlib",
    ],
    entry_points={
        "console_scripts": [
            "baixar=baixar:run",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)