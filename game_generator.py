from anthropic import Anthropic
import base64
import os

class ImageToGameGenerator:
    """Handle simage analysis and game generation using Claude Vision"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        
    def encode_image(self, image_path): 
        """Convert image to base64 for Claude Vision API"""
        try:
            with open(image_path, "rb") as img_file:
                encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
                return encoded_string
        except Exception as e:
            print("Error encoding image:", str(e))
            raise
            
    def get_image_type(self, image_path):
        """Determine image media type"""
        ext = image_path.lower().split('.')[-1]
        media_types = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "bmp": "image/bmp",
            "tiff": "image/tiff"
        }
        
        return media_types.get(ext, 'image/jpeg')
    
    def analyze_image(self, image_path):  
        """
        Step 1: Analyze image with Claude Vision
        Identifies objects, spaces and potential game elements
        """
        
        image_data = self.encode_image(image_path)
        media_type = self.get_image_type(image_path)
        
        analysis_prompt = f"""
        Analyze this image for creating a 2D browser game. Identify:

        1. **OBJECTS/OBSTACLES**: What things could block the player's path?
        - Furniture, walls, large items
        - Give approximate position (left/center/right, top/middle/bottom)
        - Estimate relative size

        2. **OPEN SPACES**: Where can the player move freely?
        - Walkable areas (floors, paths, open spaces)
        - Describe boundaries

        3. **COLLECTIBLES**: What small items could be collected?
        - Items visible in the scene
        - Their locations

        4. **GOAL**: What would make a good goal/destination?
        - Most interesting endpoint
        - Should be reachable but require navigation

        5. **PLAYER START**: Best starting position
        - Should have clear path forward
        - Not blocked immediately

        Format your response as:
        ```
        SCENE TYPE: [bedroom/kitchen/outdoor/etc]
        DIMENSIONS: [estimate aspect ratio]

        OBSTACLES:
        - [object name]: [position], [size estimate]

        WALKABLE AREAS:
        - [description of safe zones]

        COLLECTIBLES:
        - [item]: [position]

        GOAL:
        - [what/where]

        START POSITION:
        - [where player should begin]
        ```

        Be specific with positions (e.g., "left side, middle height" or "center bottom").
        """
        
        try: 
            response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1500,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": media_type,
                                        "data": image_data,
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": analysis_prompt
                                }
                            ],
                        }
                    ],
                )
            model = self.model,
            max_tokens = 1500,
            messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "image",
                             "source": {
                                 "type": "base64",
                                 "media_type": media_type,
                                 "data": image_data
                                 },
                             },
                            {
                                "type": "text",
                                "text": analysis_prompt
                            }
                        ],
                    }
                ]
            
            analysis = response.content[0].text
            return analysis
        except Exception as e:
            return f"Error during image analysis: {str(e)}"
        
    def generate_game(self, image_path):
        """
        Main pipeline: Analyze image → AI generates game code
        """
        
        try:
            # Step 1: Analyze image
            print("\n" + "="*50)
            print("🔍 STEP 1: Analyzing image with Claude Vision...")
            print("="*50)
            analysis = self.analyze_image(image_path)
            
            if "Error" in analysis:
                return {
                    'analysis': analysis,
                    'reflection': '',
                    'game_html': f'<p style="color: red;">{analysis}</p>'
                }
            
            # Step 2: Get image as base64 for embedding
            print("\n" + "="*50)
            print("STEP 2: Encoding image for game background...")
            print("="*50)
            image_base64 = self.encode_image(image_path)
            
            # Step 3: AI generates the complete game code
            print("\n" + "="*50)
            print("STEP 3: Claude is WRITING the game code...")
            print("="*50)
            game_html = self.generate_game_code(analysis, image_base64)
            
            print("\n" + "="*50)
            print("GAME GENERATION COMPLETE!")
            print("="*50)
            
            return {
                'analysis': analysis,
                'reflection': 'Reflection pattern will be added in next step!',
                'game_html': game_html
            }
        
        except Exception as e:
            error_msg = f"Error in pipeline: {str(e)}"
            print(f"{error_msg}")
            return {
                'analysis': error_msg,
                'reflection': '',
                'game_html': f'<p style="color: red;">{error_msg}</p>'
            }
        
    def generate_game_code(self, analysis, image_base64):
        """
        Step 2: AI GENERATES the complete game code
        This is where the magic happens - Claude writes the JavaScript!
        """
        print("🎮 Asking Claude to GENERATE game code...")
        
        code_generation_prompt = f"""You are a creative game developer. Based on this image analysis, write a COMPLETE, WORKING HTML5 Canvas game.

        IMAGE ANALYSIS:
        {analysis}

        YOUR TASK:
        Write the ENTIRE game as a single HTML file with embedded JavaScript. Be creative and match the game mechanics to the scene!

        REQUIREMENTS:
        1. **Canvas**: 800x600 pixels
        2. **Background**: Use this embedded image: data:image/jpeg;base64,{image_base64}
        3. **Player**: Controlled with arrow keys (←↑↓→)
        4. **Obstacles**: Based on objects identified in analysis
        5. **Collectibles**: Based on small items identified
        6. **Goal**: Clear win condition
        7. **UI**: Show score and timer
        8. **Styling**: Dark theme with green accents (#00ff88)

        CREATIVE ELEMENTS:
        - Match game mechanics to scene type (kitchen = cooking, beach = surfing, etc.)
        - Add personality to the game (fun messages, creative obstacle behaviors)
        - Make it engaging and playable
        - Add win message when player succeeds

        IMPORTANT:
        - Write COMPLETE, EXECUTABLE code (not pseudocode or templates)
        - Include ALL JavaScript logic (movement, collision, scoring, etc.)
        - Make the game actually fun and creative!
        - Use the scene context to inspire mechanics

        OUTPUT FORMAT:
        Return ONLY the complete HTML code. Start with <!DOCTYPE html> and include everything needed to run the game.
        No explanations, just the code.
        """

        try:
            print("Claude is writing the game code...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,  # Need more tokens for full game code
                messages=[
                    {
                        "role": "user",
                        "content": code_generation_prompt
                    }
                ],
            )
            
            print("Game code generated!")
            
            game_code = response.content[0].text
            
            # Clean up markdown code blocks if Claude wrapped it
            if "```html" in game_code:
                game_code = game_code.split("```html")[1].split("```")[0].strip()
            elif "```" in game_code:
                game_code = game_code.split("```")[1].split("```")[0].strip()
            
            return game_code
            
        except Exception as e:
            return f"<p style='color: red;'>Error generating game: {str(e)}</p>"
  