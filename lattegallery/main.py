import uvicorn
from lattegallery.setup import create_app
app = create_app()

if __name__ == "__main__":
    uvicorn.run(app)