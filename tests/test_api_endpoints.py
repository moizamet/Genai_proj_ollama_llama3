from app import app

def test_home_endpoint():
    response=app.test_client().get("/")
    print(response)
    assert response.status_code==200

def test_llama_integration():
    response=app.test_client().get("/check_ollama")
    assert response.status_code==200
    


test_home_endpoint()

    