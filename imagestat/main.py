"""
Can be used to run the service locally.
"""
import uvicorn

if __name__ == "__main__":
    uvicorn.run("api:app", host="127.0.0.1", port=9000, reload=True, log_config='conf/logging.ini')
