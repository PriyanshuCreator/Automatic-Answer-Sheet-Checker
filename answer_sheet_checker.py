from flask import Flask, render_template, request
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import KNeighborsRegressor
from sklearn.pipeline import Pipeline
from fuzzywuzzy import process
import spacy

app = Flask(__name__)

# Functions from your script

def mark_predict(question, answer):
    df = pd.read_csv('question_answer_mark.csv')
    df['question'].fillna('', inplace=True)
    df['answer'].fillna('', inplace=True)

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer()), 
        ('knn', KNeighborsRegressor()) 
    ])

    pipeline.fit(df['question'] + ' ' + df['answer'], df['marks'])
    value = pipeline.predict([question + ' ' + answer])

    return value[0]  # Returning the predicted mark value

def question_answer_processing(user_question, user_answer):
    df = pd.read_csv('question_answer_mark.csv')
    questions = df['question'].tolist()
    match, score = process.extractOne(user_question, questions)
    if score >= 80:
        result = df[df['question'] == match]
        nlp = spacy.load('en_core_web_lg')
        demo_answer = nlp(result['answer'].iloc[0])
        answer_match_score = nlp(user_answer).similarity(demo_answer)
        if answer_match_score > 0.80:
            return user_answer
        else:
            return "Wrong Answer"

def predict_answer_topic(answer):
    df = pd.read_csv('question_answer_mark.csv')
    df['topics_num'] = df['topics'].map({
        'biology': 1,
        'physics': 2
    })

    x = df['answer']
    df['answer'].fillna('', inplace=True)

    from sklearn.feature_extraction.text import CountVectorizer
    v = CountVectorizer()
    x_num = v.fit_transform(x.values)
    y_num = df['topics_num']

    from sklearn.naive_bayes import MultinomialNB
    model = MultinomialNB()
    model.fit(x_num, y_num)
    predicted_topic = model.predict(v.transform([answer]))
    return predicted_topic[0]  # Returning the predicted topic value

def checking_answer(question, answer):
    mark_topic = []
    final_answer = question_answer_processing(question, answer)
    if final_answer == "Wrong Answer":
        mark_topic.append(0)
    else:
        mark_otaion = mark_predict(question, final_answer)
        mark_topic.append(mark_otaion)
    topic = predict_answer_topic(answer)
    if topic == 1:
        mark_topic.append("Biology")
    elif topic == 2:
        mark_topic.append("Physics")
    return mark_topic

def import_questions(file_path):
    questions_list = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            line = line.strip()
            if line: 
                parts = line.split('.', 2)  
                if len(parts) == 3:
                    question = parts[1].strip()
                    answer = parts[2].strip()
                    questions_list.append((question, answer))
                else:
                    print(f"Invalid line format: {line}")
    return questions_list

def import_answers(file_path):
    answers_list = []
    with open(file_path, 'r') as file:
        lines = file.readlines() 
        for line in lines:
            line = line.strip()
            if line:  
                parts = line.split('.', 2) 
                if len(parts) == 3:
                    question = parts[1].strip()
                    answer = parts[2].strip()
                    answers_list.append((question, answer))
                else:
                    print(f"Invalid line format: {line}")
    return answers_list

# Routes to render the form for file selection
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle form submission and display results
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        question_file_path = request.form['question_file']
        answer_file_path = request.form['answer_file']

        questions = import_questions(question_file_path)
        answers = import_answers(answer_file_path)
        
        results = []
        total_marks_obtained = 0  # Initialize total marks obtained
        for i, (question, answer) in enumerate(zip(questions, answers), start=1):
            result = checking_answer(question[0], answer[0])
            total_marks_obtained += result[0]  # Add marks obtained in the current question
            results.append({
                'question': question[0],
                'answer': answer[0],
                'mark': result[0],
                'topic': result[1]
            })
        
        total_questions = len(results)
        overall_percentage = (total_marks_obtained / (total_questions * 5)) * 100
        
        return render_template('results.html', results=results, total_marks=total_marks_obtained, total_questions=total_questions, overall_percentage=overall_percentage)
if __name__ == '__main__':
    app.run(debug=True)
