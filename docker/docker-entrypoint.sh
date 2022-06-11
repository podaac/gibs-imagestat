#!/bin/bash
set -e

uvicorn dag.main:app --proxy-headers --host 0.0.0.0 --port 80
