import os
import gradio
import utils.model_llm_utils as model_llm


def main():
    # Configure gradio QA app 
    print("Configuring gradio app")
    demo = gradio.Interface(
        fn=get_responses,
        inputs=gradio.Textbox(label="Question", placeholder="Enter your question here"),
        outputs=gradio.Textbox(label="LLM Response"),
        examples=[
            "What are ML Runtimes?",
            "What kinds of users use CML?",
            "How do data scientists use CML?",
            "What are iceberg tables?"
        ],
        allow_flagging="never"
    )

    # Launch gradio app
    print("Launching gradio app")
    demo.launch(
        share=True,
        enable_queue=True,
        show_error=True,
        server_name='127.0.0.1',
        server_port=int(os.getenv('CDSW_APP_PORT'))
    )
    print("Gradio app ready")

# Helper function for generating responses for the QA app
def get_responses(question):
    # Create a prompt directly based on the user input
    prompt = create_prompt(question)
    
    # Generate response using the LLM model
    response = get_llm_response(prompt)
    
    return response

def create_prompt(question):
    prompt_template = """<human>: %s
<bot>:"""
    return prompt_template % question

# Pass through user input to LLM model with enhanced prompt and stop tokens
def get_llm_response(prompt):
    stop_words = ['<human>:', '\n<bot>:']

    generated_text = model_llm.get_llm_generation(
        prompt,
        stop_words,
        max_new_tokens=256,
        do_sample=False,
        temperature=0.7,
        top_p=0.85,
        top_k=70,
        repetition_penalty=1.07
    )
    return generated_text

if __name__ == "__main__":
    main()
