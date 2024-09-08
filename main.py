from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"message": " Hello World"}


@app.get('/greet/{name}/')
def greet_name(name: str) -> dict:
    """
    If we remove {name} from @app.get('/greet/{name}') then append url {name} with query params.
    :param name:
    :return: message
    """
    return {"message": f"Hello {name}"}
