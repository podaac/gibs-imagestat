#!/bin/bash
set -e

uvicorn imagestat.api:app --proxy-headers --host 0.0.0.0 --port 80
