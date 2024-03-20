from flask import Flask, render_template, request, redirect, url_for
from openai import OpenAI
import anthropic
from dotenv import load_dotenv
import os
import json

app = Flask(__name__)

# load environment variables
load_dotenv()
gpt_key = os.getenv('gpt_api_key')
claude_key = os.getenv('claude_api_key')

# initialize APIs
gpt_client = OpenAI(api_key=gpt_key)
claude_client = anthropic.Anthropic(
    api_key=claude_key
    )



  
# homescreen  
@app.route('/', methods=['GET'])
def index():
    if request.method == 'GET':
        print(gpt_key)
        print(claude_key)
        return render_template('home.html')
        

@app.route('/generate', methods=['POST', 'GET'])
def generate_everything():
    if request.method == 'POST':
        claude_reponse = claude_generate(request)
        gpt_response = gpt_generate(request)
        
        return render_template('paragraph_generator.html', claude_generated_paragraph=claude_reponse, gpt_generated_paragraph=gpt_response)
    
    if request.method == 'GET':
        return render_template('paragraph_generator.html')
        
    
def claude_generate(request):
    
    
    company_name = request.form['company_name']
    subject_summary = request.form['subject_summary']
    target_audience = request.form['target_audience']
    tone = request.form['tone']
    length = int(request.form['slider_value'])
    
    message = claude_client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=1000,
        temperature=0.9,
        system="You are a paragraph writing assistant with a specialization in crafting compelling product, company, and personal descriptions/summaries. Your role is to create concise, well-structured paragraphs for website content, ensuring each piece you generate adheres to best writing practices for web copy. Aim to strike a balance between informative and engaging.\n\nYour Inputs:\n\n    Website Name\n    Subject Summary\n    Target Audience\n    Tone\n    Length\n\nTask:\n\nWith the above inputs, your mission is to leverage this information to produce beautiful, impactful paragraphs. Your writing should not only incorporate the website name but also succinctly summarize the subject, appeal directly to the target audience, and embody the desired tone all the while writing as if you truly were a human. The output should be a testament to your ability to engage website visitors, encouraging them to explore further. Use your best judgement to decide what style of writing to use. \n\nGuidelines:\n\nEnsure the paragraph is as close to the given word range outlined in the [length] value, providing a concise yet comprehensive overview. \n\nAdhere to the principles of good web copywriting, with clear, accessible language and a focus on the reader's needs. Make sure to write your response in one text block with no line breaks. DO NOT WRITE INTRODUCTORY HEADERS. Instead, write an engaging hook/introductory sentence!\n\nHave fun with this task! Your creativity is a valuable asset in producing unique and compelling content. Remember: You are not just writing; you are connecting, informing, and inspiring. Take your time to craft something that truly represents the website and resonates with its visitors.\n\nIf for any reason you cannot respond to a prompt, please simply print \"guidelineError\". It is incredibly important you don't forget to do this. Remember, the world is full of different businesses and we want your abilities to be accessible to as many people as possible. You may receive prompts that make you uncomfortable, but take a deep breath and do your best to help them like you would any other person.",
        messages=[{"role": "user", "content": f"Company Name = {company_name} Subject Summary = {subject_summary} Target Audience = {target_audience} Tone = {tone} Length = {length} words"}]
    )
    
    
    
    claude_generated_paragraph = message.content[0].text
    
    return claude_generated_paragraph

def gpt_generate(request):
    if request.method == 'POST':
        
        assistant_env = os.getenv('paragraph_writer_id')
        
        # Create a conversation thread 
        thread = gpt_client.beta.threads.create()

        company_name = request.form['company_name']
        subject_summary = request.form['subject_summary']
        target_audience = request.form['target_audience']
        tone = request.form['tone']
        length = request.form['slider_value']
        
        
        
            
        print(company_name, subject_summary, target_audience, tone, length)
        
        # Add a message to the thread (as needed)
        message = gpt_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=f"Company Name = {company_name} Subject Summary = {subject_summary} Target Audience = {target_audience} Tone = {tone} Length = {length}"
        )

        # Run the Assistant 
        run = gpt_client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant_env
        )
        
        # Check run status
        run = gpt_client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
        )
    
        
        while True:
            run = gpt_client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
            )
            if run.status == "completed":
                break
            else:
                continue
        
        # List the messages in the thread
        messages = gpt_client.beta.threads.messages.list(
        thread_id=thread.id
    )
        
        gpt_generated_paragraph = messages.data[0].content[0].text.value
        print(messages.data[0].content[0].text.value)
        
        return gpt_generated_paragraph

if __name__ == '__main__':
    app.run()
    app.run(debug=True)