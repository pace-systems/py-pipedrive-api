#!/bin/bash

isort .
black --exclude='.*\/*(venv)\/*.*' .