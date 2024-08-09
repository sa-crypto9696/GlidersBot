
from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
import spacy

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('localhost', 27017)
db = client.chatbot
collection = db.qa

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

@app.route('/')
def index():
    return render_template("try.html")

@app.route('/chatbot', methods=['POST'])
def chatbot():
    user_input = request.json.get('message')
    
    result = collection.find_one({"Question": user_input})
    
    if result:
        return jsonify({'response': result['Answer']})
    
    # If no exact match, perform NLP-based matching
    user_doc = nlp(user_input)
    suggestions = []
    threshold = 0.5 # Similarity threshold for suggestions

    for qa in collection.find():
        question = qa["Question"]
        question_doc = nlp(question)
        
        # Calculate similarity between user input and database question
        similarity = user_doc.similarity(question_doc)
        
        if similarity > threshold:
            suggestions.append(question)
    
    if suggestions:
        return jsonify({
            'response': 'No exact match found. Here are some similar questions:',
            'suggestions': suggestions
        })
    
    # If no suitable suggestions, add the question to the database
    collection.insert_one({"Question": user_input, "Answer": None})
    return jsonify({'response': 'Question added to the database for manual response.'})

if __name__ == '__main__':
    app.run(debug=True)
