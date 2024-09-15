
# GenAI Summarization API 

Developed API using flask framework for summarization that laverages llama3.1 model. 
llama3.1 is deployed locally using ollama container.


### Below is the high level architecture
![image](https://github.com/user-attachments/assets/cefcb9f3-999d-45a6-a460-64d2c3e0113b)


### Deployment Steps
1. Create Docker Image of the application using below command 
```bash
docker build . -t llm_summary_app
```

(if required create image for ollama as well using this command. )
```bash
docker run ollama/ollama 
```


2. Run docker-compose to bring up ollama and application container. It will also mount the directory so we don't need to download model everytime.
It will also setup the ports required.

```bash
docker-compose up
```




3. For first time you would need to download llama3.1 latest model. (to get the container name you can use the docker-compose ps command)
```bash
docker-compose ps
```
![image](https://github.com/user-attachments/assets/7fc9374a-b2da-407f-adbe-1cf7714e1a0e)

It will show you running container. Now once you get the ollama container then download model

```bash
docker exec -it flask-ollama-container-1 ollama run llama3.1
```

That's it. You can now try the endpoints.

- For validating if app is running try this:
 ```GET localhost:5120/ ``` 

- For checking interation of ollama with app try this:
```GET localhost:5120/check_ollama```

- For getting summary, try this:
``` POST localhost:5120/get_summary ```

### Example:
#### Set basic authentication
Username: moizamet\
password: 1#52Succes$ \
(good practice to protect the sensitive information but for quick demo purpose i have in plane text)

#### JSON Request
```bash
{
"text":"text to be summarize",
"summary_word_limit":"Numeric Optional parameter. Example if 50 is sent then the summary will be of 50 words."
}
```
