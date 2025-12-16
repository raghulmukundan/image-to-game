import gradio as gr
import os
from dotenv import load_dotenv
from game_generator import ImageToGameGenerator

# Load environment variables
load_dotenv()

# Initialize game generator
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY not found in .env file!")

generator = ImageToGameGenerator(api_key=api_key)

def generate_game(image):
    """
    Main function that generates the game from an image.
    """
    if image is None:
        return (
            "<p style='color: red;'>Please upload an image first!</p>",
            "No image uploaded",
            ""
        )
    
    try:
            for result in generator.generate_game(image):
                yield (
                    result['game_html'],
                    result['analysis'],
                    result['reflection']
                )
        
    except Exception as e:
        error_html = f"""
        <div style='padding: 20px; background: #1a1a1a; color: #ff4444; border-radius: 10px;'>
            <h3>Error During Generation</h3>
            <p>{str(e)}</p>
            <p style='font-size: 12px; margin-top: 10px; color: #666;'>
                Check the terminal for detailed error messages
            </p>
        </div>
        """
        yield (error_html, f"Error: {str(e)}", "")


# Create Gradio Interface
with gr.Blocks(title="Image to Game Generator") as app:
    
    gr.Markdown("# 🎮 Turn Your Photo Into a Playable Game!")
    gr.Markdown("""
    Upload any image and **Claude AI will write a complete browser game** based on what it sees!
    
    Different scenes = different game mechanics (kitchen → cooking game, beach → surfing, etc.)
    """)
    
    with gr.Row():
        with gr.Column():
            # Image upload
            image_input = gr.Image(
                type="filepath",
                label="Upload Your Image",
                height=400
            )
            
            # Generate button
            generate_btn = gr.Button(
                "🎮 Generate Game!",
                variant="primary",
                size="lg"
            )
            
            gr.Markdown("""
            **⏱️ Generation takes 30-45 seconds**
            - Step 1: Analyze image (15s)
            - Step 2: Generate game code (30s)
            """)
    
    # Game output area
    gr.Markdown("---")
    gr.Markdown("## 🎮 Your Playable Game")
    gr.Markdown("*Claude will write the entire game code based on your image!*")
    
    game_output = gr.HTML(
        label="Game will appear here",
        value="<p style='text-align: center; color: #666; padding: 40px;'>Upload an image and click 'Generate Game!' to start</p>"
    )
    
    # Show AI's process (collapsible)
    gr.Markdown("---")
    with gr.Accordion("🔍 AI's Design Process", open=True):
        gr.Markdown("""
        **What happens:**
        1. 🖼️ **Vision Analysis**: Claude examines your image
        2. 🎨 **Game Design**: Claude decides mechanics based on scene type
        3. 💻 **Code Generation**: Claude WRITES the complete JavaScript game
        4. 🎮 **Play**: Your unique game is ready!
        
        *Every image creates a different game with different mechanics!*
        """)
        
        analysis_output = gr.Textbox(
            label="Step 1: Image Analysis (What Claude Sees)",
            lines=15,
            placeholder="Claude's vision analysis will appear here..."
        )
        
        reflection_output = gr.Textbox(
            label="Step 2: Game Specification, Code Generation, Feedback and Repair",
            lines=5,
            placeholder="Claude's code generation repair will appear here..."
        )
    
    # Footer
    gr.Markdown("---")
    gr.Markdown("""
    **🎮 How to Play:** Use Arrow Keys (← ↑ ↓ →) to move • Collect items • Reach the goal!
    
    **Built with:** Claude Vision + Code Generation (Agentic AI Pattern)
    
    *Note: Claude writes the game code - bugs are part of the learning process! Reflection pattern will fix them.*
    """)
    
    # Connect button to function
    generate_btn.click(
        fn=generate_game,
        inputs=[image_input],
        outputs=[game_output, analysis_output, reflection_output]
    )

# Launch the app
if __name__ == "__main__":
    app.launch(
        server_name="127.0.0.1",
        server_port=7860,
        share=False
    )