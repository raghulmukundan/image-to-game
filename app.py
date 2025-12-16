import gradio as gr
import os
from dotenv import load_dotenv
from game_generator import ImageToGameGenerator

# Load environment variables (for local development)
load_dotenv()

# Global generator (will be set when API key provided)
generator = None

def generate_game(image, api_key):
    """Main function that generates the game from an image."""
    
    global generator
    
    # Validate inputs
    if image is None:
        yield {
            'analysis': 'Please upload an image first!',
            'reflection': '',
            'game_html': '<p style="color: red;">No image uploaded</p>'
        }
        return
    
    if not api_key or api_key.strip() == "":
        yield {
            'analysis': 'Please enter your Anthropic API key!',
            'reflection': '',
            'game_html': '<p style="color: red;">No API key provided</p>'
        }
        return
    
    try:
        # Initialize generator with provided API key
        generator = ImageToGameGenerator(api_key.strip())
        
        # Generate game - iterate over all yields
        for result in generator.generate_game(image):
            yield (
                result['game_html'],
                result['analysis'],
                result['reflection']
            )
        
    except Exception as e:
        error_html = f"""
        <div style='padding: 20px; background: #1a1a1a; color: #ff4444; border-radius: 10px;'>
            <h3>❌ Error During Generation</h3>
            <p>{str(e)}</p>
            <p style='font-size: 12px; margin-top: 10px; color: #666;'>
                Check that your API key is valid. Get one at: console.anthropic.com
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
            # API Key input
            api_key_input = gr.Textbox(
                label="🔑 Anthropic API Key",
                placeholder="sk-ant-api03-...",
                type="password",
                value=os.getenv("ANTHROPIC_API_KEY", ""),
                info="Get your API key at console.anthropic.com"
            )
            
            gr.Markdown("---")
            
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
            - Step 2: Generate & verify game (30s)
            """)
    
    # Game output area
    gr.Markdown("---")
    gr.Markdown("## 🎮 Your Playable Game")
    gr.Markdown("*Claude will write the entire game code based on your image!*")
    
    game_output = gr.HTML(
        label="Game will appear here",
        value="<p style='text-align: center; color: #666; padding: 40px;'>Enter API key, upload image, and click 'Generate Game!'</p>"
    )
    
    # Show AI's process (collapsible)
    gr.Markdown("---")
    with gr.Accordion("🔍 AI's Design Process", open=False):
        gr.Markdown("""
        **What happens:**
        1. 🖼️ **Vision Analysis**: Claude examines your image
        2. 🎨 **Game Design**: Claude decides mechanics based on scene type
        3. 💻 **Code Generation**: Claude WRITES the complete JavaScript game
        4. ✅ **Verification**: System checks for errors and repairs automatically
        5. 🎮 **Play**: Your unique game is ready!
        
        *Every image creates a different game with different mechanics!*
        """)
        
        analysis_output = gr.Textbox(
            label="Step 1: Image Analysis (What Claude Sees)",
            lines=10,
            placeholder="Claude's vision analysis will appear here..."
        )
        
        reflection_output = gr.Textbox(
            label="Step 2: Verification & Repair (Agentic Loop)",
            lines=8,
            placeholder="System verification and repair logs will appear here..."
        )
    
    # Footer
    gr.Markdown("---")
    gr.Markdown("""
    **🎮 How to Play:** Use Arrow Keys (← ↑ ↓ →) to move • Collect items • Reach the goal!
    
    **Built with:** Claude Vision + Agentic Reflection Pattern
    
    **Note:** Your API key is not stored. Each generation uses ~$0.10-0.20 in API credits.
    """)
    
    # Connect button to function
    generate_btn.click(
        fn=generate_game,
        inputs=[image_input, api_key_input],
        outputs=[game_output, analysis_output, reflection_output]
    )

# Launch the app
if __name__ == "__main__":
    app.launch(
        server_name="0.0.0.0",  # Important for HF Spaces
        server_port=7860,
        share=False
    )