import gradio as gr
import pandas as pd
from theme_classifier import ThemeClassifier

def get_themes(theme_list_str, subtitles_path, save_path):
    # Process input themes
    theme_list = theme_list_str.split(',')
    theme_classifier = ThemeClassifier(theme_list)
    output_df = theme_classifier.get_themes(subtitles_path, save_path)

    # Remove 'dialogue' from themes and sum scores
    theme_list = [theme for theme in theme_list if theme != 'dialogue']
    output_df = output_df[theme_list]
    output_df = output_df.sum().reset_index()
    output_df.columns = ['Theme', 'Score']

    # Return the data for updating BarPlot
    return output_df

def main():
    with gr.Blocks() as iface:
        with gr.Row():
            with gr.Column():
                gr.HTML("<h1>Theme Classification (Zero Shot Classifiers)</h1>")
                with gr.Row():
                    with gr.Column():
                        # Define BarPlot component
                        plot = gr.BarPlot(
                            label="Theme Scores",
                            x="Theme",
                            y="Score",
                            title="Series Themes",
                            tooltip=["Theme", "Score"],
                            vertical=False,
                            width=500,
                            height=260,
                        )
                    with gr.Column():
                        # Define input components
                        theme_list = gr.Textbox(label="Themes")
                        subtitles_path = gr.Textbox(label="Subtitles or Script Path")
                        save_path = gr.Textbox(label="Save Path")
                        get_themes_button = gr.Button("Get Themes")

                        # Link button click to the function
                        get_themes_button.click(
                            get_themes, 
                            inputs=[theme_list, subtitles_path, save_path], 
                            outputs=[plot]
                        )
        
    iface.launch(share=True)

if __name__ == "__main__":
    main()
