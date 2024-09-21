from flask import Flask,request,jsonify
import psycopg2
from pydantic import BaseModel, ValidationError
from typing import Optional
# from GenerateEmbeddings import GenerateEmbeddings
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from flask_basicauth import BasicAuth
from langchain_core.documents import Document
from langchain_postgres import PGVector
from langchain_postgres.vectorstores import PGVector
from langchain_huggingface import HuggingFaceEmbeddings

collection_name="Books_Summary"
server="localhost"
username="postgres"
password="security"
port="5432"
database="genai_books_project"
ollama_base_url="localhost"
ollama_base_url="http://ollama-container:11434"
server="pgvector-container"

db_connection=f"postgresql+psycopg://{username}:{password}@{server}:{port}/{database}"
model_name = "sentence-transformers/all-MiniLM-L6-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

vector_store = PGVector(
    embeddings=embeddings,
    collection_name=collection_name,
    connection=db_connection,
    use_jsonb=True,
)
print("Vector store Connection established..")


#Get llama3.1 model from ollama service that is part of docker container running through Docker Compose
model= Ollama(model="llama3.1", 
              base_url=ollama_base_url, 
              verbose=True)

#db connection
con=psycopg2.connect(
        host=server,
        port=port,
        database=database,
        user=username,
        password=password
)


#Setting system and user prompts to get better summary result. We can add custom parameters to them.
system_prompt="""You are AI assistant with expertise in literature. Your task is to summarize the book content. 
Always be consise, highlight important facts and only summarize the provided information without adding any additional details."""

human_prompt="Text: {input_text}. \nSummary:"

prompt=ChatPromptTemplate.from_messages([
    ("system",system_prompt),
    ("human",human_prompt)
])

#pydantic book model for validations
class Book(BaseModel):
    id: Optional[int]=None
    title:str
    author:str
    genre:str
    year_published: int
    content:str
    summary:Optional[str]=None

#pydantic review model for validation
class Review(BaseModel):
    id:Optional[int]=None
    book_id:Optional[int]=None
    user_id:int
    review_text:str
    rating:float

#object used to generate embedding
# obj=GenerateEmbeddings()

def getSummaryFromLLM(input_text):
    print("Generating Summary")
    chain=prompt | model
    summary=chain.invoke({"input_text":input_text})
    return summary


#initilization of app
app=Flask("__name__")
app.config['SECRET_KEY'] = 'secret_key_assignment'
app.config['BASIC_AUTH_USERNAME'] = 'moizamet'
app.config['BASIC_AUTH_PASSWORD'] = '1#52Succes$'

#Basic Auth initialization
basicAuth=BasicAuth(app)





#helper method to execute query
def execute_query(query,args):
    """Execute a database query and return the result.

    Args:
        query (str): The SQL query to be executed.
        args (tuple): The parameters to be used in the SQL query.

    Returns:
        list or None: The results of the query, or None if no results were fetched.
    """
    obj=None
    try:
        cur=con.cursor()
        print(f"Executing Query: {query}")
        cur.execute(query,args)
        try:
            obj=cur.fetchall()
        except:
            obj=None
        con.commit()
        cur.close()
        return obj
    except Exception as e:
        con.commit()
        cur.close()
        raise Exception("Error occured during db execution",str(e))
    
#recommendation helper function
def getRecommendation(user_input):
    """Fetch book recommendations based on user input.

    This function generates embeddings from the user's input and queries the database 
    to find relevant book IDs. It then retrieves the corresponding book details 
    and formats them into a recommendation list.

    Args:
        user_input (str): The user's preferences or keywords for book recommendations.

    Returns:
        list: A list of formatted book recommendations or a message if no matches are found.
    """
    print("getting recommendations", user_input)
    # em=obj.getEmbeddings(user_input)
    # query="select book_id from books_summary_embeddings order by embeddingzz <=> %s ::vector"
    # response=execute_query(query,(em,))

    response=vector_store.similarity_search_with_relevance_scores(user_input,k=5)
    for doc in response:
        print(doc)
        print("====================================")

    

    if len(response)>0:
        book_ids=()
        
        for doc in response:
            book_ids=book_ids+(str(doc[0].metadata["book_id"]),)
        print(book_ids)
        # ids="','".join(book_ids)
        # print(ids)
        query=f"select distinct * from books where id IN %s;"
        books=execute_query(query,(book_ids,))
        recommendation_list=[]
        for book in books:
            value=f"{book[1]} By {book[2]} in {book[3]} genre, published in {book[4]}"
            recommendation_list.append(value)
        return recommendation_list
    else:
        return ["Sorry No book Matching preference. Try with new keywords"]


        


@app.route("/")
def home():
    return jsonify({
        "Message":"Success"
    })

def addToVectoDb(summary,id):
    docs=[
    Document(
        page_content=summary,
        metadata={"book_id":id}
    )
    ]
    vector_store.add_documents(docs,ids=[id])

@app.route("/books",methods=["POST"])
@basicAuth.required
def add_book():
    print("Adding Records")

    data=request.get_json()
    try:
        new_book=Book(**data)
        new_book.summary=getSummaryFromLLM(new_book.content)
        query="""insert into books (title,author,genre,year_published,summary)
                values (%s,%s,%s,%s,%s)
                returning id;
                """
        id=execute_query(query,(new_book.title,new_book.author,new_book.genre,new_book.year_published,new_book.summary))
        print(id)
        new_book.id=id[0][0]
        
        #Adding book in vector store for similarity
        addToVectoDb(new_book.summary,id[0][0])
        # em=obj.getEmbeddings(new_book.summary)
        # query="insert into books_summary_embeddings (book_id,embeddingzz) values (%s, %s);"
        # execute_query(query,(id[0],em ))
        
        return jsonify({
            "Message":"Record Inserted Successfully",
            "New_Book":new_book.model_dump()
        }),201
    except ValidationError as e:
         return jsonify({'error': str(e)}), 400 
    

@app.route("/books/<int:bookId>",methods=["PUT"])
@basicAuth.required
def update_book(bookId):
    print(f"Updating for {bookId} book id")
    query="select * from books where id=%s"
    current_book=execute_query(query,(bookId,))
    if (len(current_book)<1):
        return jsonify({
                "error":f"No book found with this id. Id:{bookId} "
        })
    data=request.get_json()
    try:      
        print(update_book)
        update_obj=dict(data)
        valid_fiedl=0   
        fields=["title","author","genre","year_published","content"]
        query="update books set "
        args=()
        for column in update_obj.keys():
            if column in fields:
                if column=="content": #If content itself is updated then the summary needs to be created from llm and then new updating needs to be udpated
                    summary=getSummaryFromLLM(update_obj[column])
                    query=query+"summary=%s, "
                    args=args+(summary,)

                    #updating embedding
                    # em=obj.getEmbeddings(summary)
                    # execute_query("update books_summary_embeddings set embeddingzz=%s where book_id=%s",(em,bookId))
                    vector_store.delete(ids=[str(bookId)])
                    addToVectoDb(summary,bookId)

                else:
                    query=query+f"{column}=%s, "
                    args=args+(update_obj[column],)
                valid_fiedl+=1

        if valid_fiedl > 0: # only for valid fields run the update query
            query=query[:-2]
            query=query+" where id=%s"
            args=args+(bookId,)
            print(query)
            execute_query(query,args)
            return jsonify({
                "Message":"Updated Successfully"
            })
        else:
            return jsonify({'error': "Invalid Field Identified"}), 400 
        

    except Exception as e:
           return jsonify({'error': str(e)}), 400 
    

    
    
@app.route("/books/<int:bookId>",methods=["DELETE"])
@basicAuth.required
def deleteBook(bookId):
    try:
        print(f"deleting book: {bookId}")
        query="select * from books where id=%s"
        current_book=execute_query(query,(bookId,))
        if (len(current_book)<1):
            return jsonify({
                    "error":f"No book found with this id. Id:{bookId} "
            })
        query="delete from reviews where book_id=%s"
        execute_query(query,(bookId,))
        # query="delete from books_summary_embeddings where book_id=%s"
        # execute_query(query,(bookId,))
        vector_store.delete(ids=[str(bookId)])

        query="delete from books where id=%s"
        execute_query(query,(bookId,))
        return jsonify({
                    "Message":"Deleted Successfully"
                }),200
    except Exception as e:
         return jsonify({
                    "Error":str(e)
                }),400

 
@app.route("/books",methods=["GET"])
@basicAuth.required
def get_books():
    try:
        print("Fetching all books")
        query=f"Select id as id,title,author,genre,year_published,summary from books;"
        results=execute_query(query,())
        print(results)
        return jsonify(results)
    except Exception as e:
        return jsonify({
                "error":str(e)
            }),400
    
@app.route("/books/<int:bookId>",methods=["GET"])
@basicAuth.required
def get_book(bookId):
    try:
        print(f"Fetching book with id {bookId}")
        query="Select id as id,title,author,genre,year_published,summary from books where id=%s"
        book=execute_query(query,(bookId,))

        return jsonify(
        book
        )
    except Exception as e:
        return jsonify({
                "error":str(e)
            }),400

@app.route("/books/<int:bookId>/reviews",methods=["GET"])
@basicAuth.required
def getReviews(bookId):
    try:
        print(f"getting reviews for : {bookId}")
        query="select * from reviews where book_id=%s"
        reviews=execute_query(query,(bookId,))
        return jsonify(reviews)
    except Exception as e:
        return jsonify({
            "error":str(e)
        }),400

@app.route("/books/<int:bookId>/reviews",methods=["POST"])
@basicAuth.required
def addReviews(bookId):
    print(f"adding reviews for : {bookId}")
    data=request.get_json()
    try:
        review_obj=Review(**data)
        review_obj.book_id=bookId
        query="""insert into reviews (book_id, user_id,review_text,rating) 
                    values (%s,%s,%s,%s)"""
        execute_query(query,(review_obj.book_id,review_obj.user_id,review_obj.review_text,review_obj.rating))
        return jsonify({"Message":"Success"}),201
    except ValidationError as e:
        return jsonify({
            "error":str(e)
        }),400
    
@app.route("/books/<int:bookId>/summary",methods=["GET"])
@basicAuth.required
def getAggregateSummary(bookId):
    try:
        print(f"getting aggregated Summary for : {bookId}")
        query="select b.summary,avg(r.rating) from books b join reviews r on b.id=r.book_id where b.id=%s group by b.summary, b.id "
        print(query)
        response=execute_query(query,(bookId,))
        return jsonify({
            "Summary":response[0][0],
            "Aggregated_Rating":response[0][1],
        })
    except Exception as e:
        return jsonify({"error":str(e)}),400


@app.route("/recommendations",methods=["GET"])
@basicAuth.required
def getUserRecommenedBooks():
    user_input=request.args.get("preferences")
    books=getRecommendation(user_input)
    return jsonify({
        "Message":"Success",
        "Books":books
    })

@app.route("/generate-summary",methods=["POST"])
@basicAuth.required
def generateSummary():
    print("Generating summary")
    input_text=request.json["text"]
    summary=getSummaryFromLLM(input_text)

    
    return jsonify({
        "Input_Text":input_text,
        "Summary":summary,
    })


if __name__=="__main__":
    app.run(debug=True,
            port=5120,
            host="0.0.0.0")