import gradio as gr
from theme_classifier import ThemeClassifier
from character_network import NamedEntityRecognizer, CharacterNetworkGenerator
from text_classification import JutsuClassifier
from character_chatbot import CharacterChatbot
import os
from dotenv import load_dotenv
load_dotenv()

def get_themes(theme_list_str, subtitles_path, save_path):
    theme_list = theme_list_str.split(',')
    theme_classifier = ThemeClassifier(theme_list)
    output_df = theme_classifier.get_themes(subtitles_path, save_path)

    # Remove dialogue from the theme list
    theme_list = [theme for theme in theme_list if theme != 'dialogue']
    output_df = output_df[theme_list]

    output_df = output_df[theme_list].sum().reset_index()
    output_df.columns = ['Theme', 'Score']

    output_chart = gr.BarPlot(
        output_df,
        x="Theme",
        y="Score",
        title="Series Themes",
        tooltip=["Theme", "Score"],
        # vertical=False,
        width=500,
        height=260
    )

    return output_chart


def get_character_network(subtitles_path, ner_path):
    ner = NamedEntityRecognizer()
    ner_df = ner.ger_ners(subtitles_path, ner_path)

    character_network_generator = CharacterNetworkGenerator()
    relationship_df = character_network_generator.generate_character_network(
        ner_df)
    html = character_network_generator.draw_network_graph(relationship_df)

    return html




def classify_text(text_classification_model, text_classification_data_path, text_to_classify):
    jutsu_classifier = JutsuClassifier(text_classification_model,
                                       text_classification_data_path,
                                       huggingface_token=os.getenv('HF_TOKEN'),
                                       )
    output = jutsu_classifier.classify_jutsu(text_to_classify)[0]
    return output



def chat_with_character_chatbot(message, history):
    character_chatbot = CharacterChatbot("AbdullahTarek/Naruto_Llama-3-8B",
                                         huggingface_token=os.getenv('HF_TOKEN'))
    output = character_chatbot.chat(message, history)
    output = output['content'].strip()
    
    return output
    

def main():
    with gr.Blocks() as iface:
        # Theme Classification
        with gr.Row():
            with gr.Column():
                gr.HTML("<h1>Theme Classification (Zero Shot Claasifiers)</h1>")
                with gr.Row():
                    with gr.Column():
                        plot = gr.BarPlot()
                    with gr.Column():
                        theme_list = gr.Textbox(label="Themes")
                        subtitles_path = gr.Textbox(
                            label="Subtitles or script Path")
                        save_path = gr.Textbox(label="Save Path")
                        get_themes_button = gr.Button("Get Themes")
                        get_themes_button.click(
                            get_themes, inputs=[theme_list, subtitles_path, save_path], outputs=[plot])
        # Character Network
        with gr.Row():
            with gr.Column():
                gr.HTML("<h1>Characters Network (NERs and Graphs)</h1>")
                with gr.Row():
                    with gr.Column():
                        network_html = gr.HTML()
                    with gr.Column():
                        subtitles_path = gr.Textbox(
                            label="Subtitles or script Path")
                        ner_path = gr.Textbox(label="NERs save path")
                        get_network_graph_button = gr.Button(
                            "Get Character Network Graph")
                        get_network_graph_button.click(get_character_network, inputs=[
                                                       subtitles_path, ner_path], outputs=[network_html])
        with gr.Row():
            with gr.Column():
                gr.HTML("<h1>Text Classification with LLMs</h1>")
                with gr.Row():
                    with gr.Column():
                        text_classification_ouptut = gr.Textbox(
                            label="Text Classification Output")
                    with gr.Column():
                        text_classification_model = gr.Textbox(
                            label='Model Path')
                        text_classification_data_path = gr.Textbox(
                            label='Data Path')
                        text_to_classify = gr.Textbox(label='Text input')
                        classify_text_button = gr.Button("Classify Jutsu")
                        classify_text_button.click(classify_text, inputs=[
                                                   text_classification_model, text_classification_data_path, text_to_classify], outputs=[text_classification_ouptut])
        with gr.Row():
            with gr.Column():
                gr.HTML("<h1>Character Chatbot</h1>")
                gr.ChatInterface(chat_with_character_chatbot)
                with gr.Row():
                    with gr.Column():
                        chatbot_ouptut = gr.Textbox(
                            label="Chatbot Response")
                    with gr.Column():
                        your_message = gr.Textbox(label='Your message:') 
                        text_to_classify = gr.Textbox(label='Text input')
                        classify_text_button = gr.Button("Classify Jutsu")
                        classify_text_button.click(classify_text, inputs=[
                                                   text_classification_model, text_classification_data_path, text_to_classify], outputs=[text_classification_ouptut])

    iface.launch(share=True)


if __name__ == '__main__':
    main()
