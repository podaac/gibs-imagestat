import uvicorn

if __name__ == "__main__":
    # uvicorn.run("api:app", host="ec2-3-65-18-201.eu-central-1.compute.amazonaws.com", port=8080, reload=True)
    uvicorn.run("api:app", host="localhost", port=9000, reload=True)
