from flask import Flask,request,jsonify
from langchain_community.llms import Ollama
from langchain_core.prompts import ChatPromptTemplate
from flask_basicauth import BasicAuth



#initialize the app and set the confs
app=Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key_assignment'
app.config['BASIC_AUTH_USERNAME'] = 'moizamet'
app.config['BASIC_AUTH_PASSWORD'] = '1#52Succes$'

#Basic Auth initialization
basicAuth=BasicAuth(app)

#Setting system and user prompts to get better summary result. We can add custom parameters to them.
system_prompt="""You are AI assistant with expertise in literature. Your task is to summarize the text{addition_parameter}. 
Always be consise, highlight important facts and do not provide any additional details."""

human_prompt="Text: {input_text}. \nSummary:"

prompt=ChatPromptTemplate.from_messages([
    ("system",system_prompt),
    ("human",human_prompt)
])


#Get llama3.1 model from ollama service that is part of docker container running through Docker Compose
model= Ollama(model="llama3.1", base_url="http://ollama-container:11434", verbose=True)

@app.route("/")

def home():
    return jsonify({"Message":"Success"})


#For testing ollama is up or not
@app.route("/check_ollama")
def check_ollama():
    try:
        response=model.invoke("Tell me story in 2 line")
        return jsonify({"Message":"Success",
                        "Ollam_Response":response}),200
    except:
        return jsonify({"Message":"Error"}),404

#Summary Router
@app.route("/get_summary",methods=["POST"])
@basicAuth.required
def get_summary():
    try:
        req=request.get_json()
        print(req)

        if (req.get("text") is None):
            return jsonify({"Error_Message":"Please provide text attribute for input"}),400
        
        if (len(req.get("text").strip())<1):
            return jsonify({"Error_Message":"Input Validation Error. Not a valid length"}),400

        input_text=req.get("text").strip() 
        chain=prompt | model #creating chain of llm model and prompt
        

        #User wants summary in speciic word limit    
        if (req.get("summary_word_limit")is not None):
            response=chain.invoke({
                        "input_text":input_text,
                        "addition_parameter":f' in {req.get("summary_word_limit")} words'
            })
        else:
            response=chain.invoke({
                            "input_text":input_text,
                            "addition_parameter":""
                            })
            
        print(response)
        
        return jsonify({"Message":"Success",
                        "Input_Text":input_text,
                        "Summary":response
                        }),200
    except Exception as e:
        return jsonify({"Error_Message":f"Error occured during process.Details: {e}"}),400





if __name__=="__main__":
    app.run(port=5120,debug=True,host="0.0.0.0")
