from flask import Flask, render_template, request, redirect 
from openai import OpenAI
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)

# load environment variables
load_dotenv()

# initialize OpenAI API
client = OpenAI(api_key=os.getenv('api_key'))



  
# homescreen  
@app.route('/')
def index():
    
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    if request.method == 'POST':
        assistant_env = os.getenv('paragraph_writer_id')
        
        # Create a conversation thread 
        thread = client.beta.threads.create()

        company_name = request.form['company_name']
        subject_summary = request.form['subject_summary']
        target_audience = request.form['target_audience']
        tone = request.form['tone']
        print(company_name, subject_summary, target_audience, tone)
        
        # Add a message to the thread (as needed)
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Company Name = {company_name} Subject Summary = {subject_summary} Target Audience = {target_audience} Tone = {tone}"
        )

        # Run the Assistant 
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_env
        )
        
        # Check run status
        run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
        )
    
        
        while True:
            run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
            )
            if run.status == "completed":
                break
            else:
                continue
        
        # List the messages in the thread
        messages = client.beta.threads.messages.list(
        thread_id=thread.id
    )
        
        generated_paragraph = messages.data[0].content[0].text.value
        print(messages.data[0].content[0].text.value)
        
        
        
        return render_template('index.html', generated_paragraph=generated_paragraph)
    
    if request.method == 'GET':
        
        return render_template('index.html', generated_paragraph=generated_paragraph)

if __name__ == '__main__':
    app.run()
    app.run(debug=True)