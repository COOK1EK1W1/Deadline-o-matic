#!/bin/bash
source venv/bin/activate

pip install -r requirements.txt
prisma generate

python src/main.py