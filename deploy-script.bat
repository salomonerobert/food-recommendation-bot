#!/bin/bash

@echo on
echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing project dependencies...
python -m pip install -r requirements.txt

echo Deployment completed.