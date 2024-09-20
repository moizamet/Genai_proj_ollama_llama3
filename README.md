
# GenAI Summarization API 

Developed API using flask framework for summarization that laverages llama3.1 model & PGVector Store.
llama3.1 is deployed locally using ollama container.


### Below is the high level architecture
![GenAI Book Summarization App](https://github.com/user-attachments/assets/9e406721-924c-41d4-8772-1bf49d0c764f)



### Deployment Steps
1. Create Docker Image of the application using below command 
```bash
docker build . -t llm_summary_app
```

(if required create image for ollama as well using this command. )
```bash
docker run ollama/ollama 
```


2. Run docker-compose to bring up ollama, pgvector and application container. It will also mount the directory so we don't need to download model everytime.
It will also setup the ports required.

```bash
docker-compose up
```




3. For first time you would need to download llama3.1 latest model. (to get the container name you can use the docker-compose ps command)
```bash
docker-compose ps
```
![image](https://github.com/user-attachments/assets/c5344012-9b60-4601-9010-16814d212301)


It will show you running container. Now once you get the ollama container then download model

```bash
docker exec -it flask-ollama-container-1 ollama run llama3.1
```

4. Finaly I have provided sql queries. Connect directly to the container or use dbeaver to connect with pgvector db container and execute the queries.

That's it. You can now try the endpoints.

## Refer the Swagger Documentation to get the Endpoint relevant details.

### Result
![image](https://github.com/user-attachments/assets/5b0e6d9b-13c2-476c-a3f6-92c3578cfb19)


