from setuptools import setup, find_packages

setup(
    name="voice-pos-server",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi',
        'uvicorn',
        'vosk',
        'websockets',
        'sounddevice',
        'numpy',
        'python-dotenv',
        'pydantic',
        'python-multipart',
        'soundfile',
    ],
) 