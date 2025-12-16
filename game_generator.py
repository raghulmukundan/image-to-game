from anthropic import Anthropic
import base64
from urllib.parse import quote
from PIL import Image
import io
import json


class ImageToGameGenerator:
    """Handle simage analysis and game generation using Claude Vision"""
    
    def __init__(self, api_key: str):
        self.client = Anthropic(api_key=api_key)
        self.model = "claude-sonnet-4-20250514"
        self.max_repair_attempts = 2 
        
    def encode_image(self, image_path): 
        """Convert image to base64 and compress for Claude Vision API"""
        try:
            print(f"Reading: {image_path}")
            
            img = Image.open(image_path)
            
            if img.mode != 'RGB':
                img = img.convert('RGB')
                
            # Resize image if too large
            max_size = (1200, 900)
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                print(f"Resizing from {img.size} to fit within {max_size}")
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Save as JPEG with compression
            buffer = io.BytesIO()
            img.save(buffer, format="JPEG", quality=75)
            buffer.seek(0)
            
            encoded = base64.b64encode(buffer.read()).decode('utf-8')
            print(f"Encoded: {len(encoded)} chars")
            return encoded
        except Exception as e:
            print(f"Error encoding image: {str(e)}")
            raise
    
    def generate_game(self, image_path):
        """
        Main entry point to generate game from image
        """
        try: 
            print("\n" + "="*50)
            print("STARTING GAME GENERATION PIPELINE")
            print("="*50)
            
            yield {
                'analysis': 'Starting image analysis...',
                'reflection': '',
                'game_html': '<p style="text-align: center; padding: 40px;">Processing...</p>'
           }
             # Step 1: Analyze image 
            
            analysis = self.analyze_image(image_path)
            
            if "Error" in analysis:
                yield {
                    'analysis': analysis,
                    'reflection': '',
                    'game_html': '<p style="color: red;">Analysis failed</p>'
                }
                return
            
            yield {
                'analysis': analysis,
                'reflection': 'Step 1 complete!\nGenerating game specification...',
                'game_html': '<p style="text-align: center; padding: 40px;">Designing game mechanics...</p>'
            }
           
            spec = self.generate_game_spec(analysis)
            # Safety check - if spec is None, use default
            if spec is None:
                print("Spec was None, using default")
                spec = self._get_default_spec()
            
            # Repair loop for collectible positions
            for attempt in range(self.max_repair_attempts):
                print(f"\nPosition Check - Attempt {attempt + 1}/{self.max_repair_attempts}")
                
                position_issues = self.verify_collectible_positions(spec)
                
                if not position_issues:
                    print("All positions valid!")
                    break
                
                if attempt < self.max_repair_attempts - 1:
                    print(f"Attempting repair...")
                    spec = self.repair_collectible_positions(spec, position_issues)
                else:
                    print(f"Max repair attempts reached, continuing anyway...")
            
            # Yield after spec completes
            spec_preview = json.dumps(spec, indent=2)
            position_status = "Verified" if not position_issues else f"⚠️ {len(position_issues)} issues remaining"
            yield {
                'analysis': analysis,
                'reflection': f'Step 2 complete!\n\nGame Spec:\n{spec_preview}\n\nPosition Check: {len(position_status)} issues\n\nNext: Component generation...',
                'game_html': f'<p style="text-align: center; padding: 40px;">Building {spec.get("title", "game")}...</p>'
            }
            
            # Step 3: Generate HTML
            html = self.generate_html_component(spec)
            html_issues = self.verify_html_component(html, spec['contracts'])
            
            # Yield after HTML
            html_status = "Passed" if not html_issues else f"{len(html_issues)} issues"
            yield {
                'analysis': analysis,
                'reflection': f'{spec_preview}\n\nHTML Component: {html_status}\n{"Issues: " + ", ".join(html_issues) if html_issues else ""}\n\nNext: CSS and JS components...',
                'game_html': f'<p style="text-align: center; padding: 40px; color: #00ff88;">HTML ready! ({len(html) if html else 0} chars)</p>'
            }
            
                    # Step 3b: CSS
            css = self.generate_css_component(spec, html)
            css_issues = self.verify_css_component(css, spec['contracts'])
            
            yield {
                'analysis': analysis,
                'reflection': f'HTML: {"✓" if not html_issues else "⚠"}\nCSS: {"Passed" if not css_issues else f"{len(css_issues)} issues"}\nGenerating JavaScript...',
                'game_html': '<p style="text-align: center; padding: 40px;">Adding game logic...</p>'
            }
            
                    # Get image for JS
            image_base64 = self.encode_image(image_path)
            
            # Step 3c: JavaScript
            js = self.generate_js_component(spec, html, image_base64)
            js_issues = self.verify_js_component(js, spec['contracts'])
            
            yield {
                'analysis': analysis,
                'reflection': f'HTML: {"✓" if not html_issues else "⚠"}\nCSS: {"✓" if not css_issues else "⚠"}\nJS: {"Passed" if not js_issues else f"{len(js_issues)} issues"}\n\nAssembling game...',
                'game_html': '<p style="text-align: center; padding: 40px;">🔨 Assembling components...</p>'
            }
            
            yield {
                'analysis': analysis,
                'reflection': f'All components generated!\n\nHTML: {len(html) if html else 0} chars\nCSS: {len(css) if css else 0} chars\nJS: {len(js) if js else 0} chars\n\nNext: Assembly',
                'game_html': '<p style="text-align: center; padding: 40px; color: #00ff88;">Ready to assemble!</p>'
            }
            
            game_html = self.assemble_game(html, css, js, spec)
            total_issues = len(html_issues) + len(css_issues) + len(js_issues)

            summary = f'''GENERATION COMPLETE! 🎉

            Components:
            - HTML: {len(html)} chars ({"✓" if not html_issues else f"⚠ {len(html_issues)} issues"})
            - CSS: {len(css)} chars ({"✓" if not css_issues else f"⚠ {len(css_issues)} issues"})
            - JS: {len(js)} chars ({"✓" if not js_issues else f"⚠ {len(js_issues)} issues"})

            Total: {len(game_html)} chars
            Issues: {total_issues}

            Game Spec:
            {json.dumps(spec, indent=2)}

            Use arrow keys (←↑↓→) to play!
            '''
        
            yield {
                'analysis': analysis,
                'reflection': summary,
                'game_html': game_html
            }
            
            print("\n" + "="*50)
            print("PIPELINE COMPLETE!")
            print("="*50)
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
            yield {
                'analysis': f'Error: {e}',
                'reflection': '',
                'game_html': f'<p style="color: red;">Error: {e}</p>'
            }
                 
    def analyze_image(self, image_path):  
        """
        Step 1: Analyze image with Claude Vision
        Identifies objects, spaces and potential game elements
        """
        print("\nSTEP 1: Analyzing Image")
        print("-" * 50)
        image_data = self.encode_image(image_path)
        
        prompt = """Analyze this image for creating a 2D browser game.

        Provide:

        1. **SCENE TYPE**: What kind of scene is this? (living room, kitchen, office, outdoor, etc.)

        2. **MAIN OBJECTS** (3-5 obstacles):
        - Name, position (left/center/right, top/middle/bottom), size (small/medium/large)

        3. **COLLECTIBLES** (3-5 small items):
        - Name, position

        4. **GOAL**: What would be a natural winning destination?

        5. **GAME THEME**: What kind of game fits this scene?
        - Kitchen → cooking/ingredient collection
        - Beach → surfing/shell collecting
        - Living room → treasure hunt
        - Be creative!

        6. **PLAYER START**: Best starting position

        Be specific with positions and creative with theme!"""
        
        try:
            print("\nCalling Claude Vision for image analysis...")
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image",
                        "source": {"type": "base64", "media_type": "image/jpeg", "data": image_data}},
                        {"type": "text", "text": prompt},
                    ],
                }],
            )
            analysis = response.content[0].text
            print(f"Analysis complete ({len(analysis)} chars)")
            return analysis
        except Exception as e:
            error_msg = f"Error analyzing image: {str(e)}"
            print(f"{error_msg}")
            return error_msg
        
    def generate_game_spec(self, analysis):
      """
      Step 2: Generate game specification with contracts
      """
      print("\nSTEP 2: Generating Game Spec")
      print("-" * 50)  
      
      prompt = f"""Based on this image analysis, create a game specification in JSON format.
      ANALYSIS:
        {analysis}
    
      CRITICAL POSITIONING RULES:
        1. Collectibles must NOT be placed inside obstacle rectangles
        2. Collectibles should be at least 20 pixels away from obstacle edges
        3. Collectibles must be reachable by the player
        4. Check each collectible position against all obstacles before assigning
      
      Generate a JSON spec with this exact structure:
      
      {{
        "title": "Creative game title",
        "theme": "Brief theme description",
        "contracts": {{
            "canvas_id": "gameCanvas",
            "score_id": "score",
            "timer_id": "timer",
            "container_id": "gameContainer"
        }},
        "player": {{
            "startX": 50,
            "startY": 500,
            "size": 25,
            "speed": 4
        }},
        "obstacles": [
            {{"name": "Object name", "x": 200, "y": 300, "width": 150, "height": 100, "color": "#8B4513"}}
        ],
        "collectibles": [
            {{"name": "Item name", "x": 400, "y": 200, "size": 15, "color": "#FFD700"}}
        ],
        "goal": {{
            "name": "Goal description",
            "x": 700,
            "y": 50,
            "width": 80,
            "height": 60
        }}
     }}

        COORDINATE SYSTEM:
        - Canvas is 800x600 pixels
        - Origin (0,0) is top-left
        - Positions: left(50-200), center(300-500), right(600-750)
        - Vertical: top(50-200), middle(250-400), bottom(450-550)

        COLORS:
        - Use realistic colors: brown for furniture, green for plants, gold for collectibles
        - Make goal stand out with bright color

        Return ONLY valid JSON, no explanations."""
      
      try:
          print("\nCalling Claude to design game...")
          response = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
           )
        
          json_text = response.content[0].text
        
          print(f"📄 Response length: {len(json_text)} chars")
          print(f"📄 First 100 chars: {json_text[:100]}")
          # Clean markdown if present
          if "```json" in json_text:
            print("🧹 Cleaning JSON markdown")
            json_text = json_text.split("```json")[1].split("```")[0].strip()
          elif "```" in json_text:
            print("🧹 Cleaning generic markdown")
            json_text = json_text.split("```")[1].split("```")[0].strip()
    
          print(f"🔍 Parsing JSON ({len(json_text)} chars)...")
          spec = json.loads(json_text)
          print(f"Spec generated: {spec.get('title', 'Untitled')}")
          return spec
      except json.JSONDecodeError as e:
            print(f"JSON parsing failed: {e}")
            print(f"Raw response: {json_text[:200]}...")
            return self._get_default_spec()    
      
      except Exception as e:
            error_msg = f"Error generating game spec: {str(e)}"
            print(f"{error_msg}")
            return {"error": error_msg}
        
    def _get_default_spec(self):
        """Fallback spec if generation fails"""
        return {
            "title": "Photo Adventure",
            "theme": "Navigate the scene",
            "contracts": {
                "canvas_id": "gameCanvas",
                "score_id": "score",
                "timer_id": "timer",
                "container_id": "gameContainer"
            },
            "player": {"startX": 50, "startY": 500, "size": 25, "speed": 4},
            "obstacles": [
                {"name": "Obstacle", "x": 300, "y": 300, "width": 150, "height": 100, "color": "#8B4513"}
            ],
            "collectibles": [
                {"name": "Item", "x": 400, "y": 200, "size": 15, "color": "#FFD700"}
            ],
            "goal": {"name": "Goal", "x": 700, "y": 50, "width": 60, "height": 60}
        }
        
    def generate_html_component(self, spec):
        """Step 3a: Generate HTML component"""
        
        print("\nSTEP 3A: Generating HTML Component")
        print("-" * 50)
        
        contracts = spec['contracts']
        
        prompt = f"""Generate the HTML body structure for this game.

        GAME SPEC:
        Title: {spec['title']}
        Theme: {spec['theme']}

        REQUIRED ELEMENTS WITH THESE EXACT IDs:
        - Container: id="{contracts['container_id']}"
        - Canvas: id="{contracts['canvas_id']}" (must be 800x600)
        - Score display: id="{contracts['score_id']}"
        - Timer display: id="{contracts['timer_id']}"

        REQUIREMENTS:
        - Clean, semantic HTML
        - Title should be: {spec['title']}
        - Add brief instructions
        - Show score as "Score: X/{len(spec['collectibles'])}"

        Return ONLY the HTML body content (no <!DOCTYPE>, <html>, <head>, or <style>).
        Start with <div id="{contracts['container_id']}"> and end with </div>."""

        try:
            print("Calling Claude to generate HTML...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            html = response.content[0].text
            
            # Clean markdown
            if "```html" in html:
                html = html.split("```html")[1].split("```")[0].strip()
            elif "```" in html:
                html = html.split("```")[1].split("```")[0].strip()
            
            print(f"HTML generated ({len(html)} chars)")
            return html
            
        except Exception as e:
            print(f"HTML generation failed: {e}")
            return None

    def verify_html_component(self, html, contracts):
        """Verify HTML has required elements"""
        
        print("\nVerifying HTML Component")
        print("-" * 50)
        
        issues = []
        
        if html is None:
            issues.append("HTML is None")
            return issues
        
        # Check required IDs
        required_ids = [
            (contracts['canvas_id'], 'Canvas'),
            (contracts['score_id'], 'Score'),
            (contracts['timer_id'], 'Timer'),
            (contracts['container_id'], 'Container')
        ]
        
        for id_name, description in required_ids:
            if f'id="{id_name}"' not in html and f"id='{id_name}'" not in html:
                issues.append(f"Missing required id: {id_name} ({description})")
                print(f"Missing: {id_name}")
            else:
                print(f"Found: {id_name}")
        
        # Check canvas dimensions
        if '<canvas' in html:
            if 'width="800"' not in html or 'height="600"' not in html:
                issues.append("Canvas missing correct dimensions (800x600)")
                print("Canvas dimensions incorrect")
            else:
                print("Canvas dimensions correct")
        else:
            issues.append("No canvas element found")
            print("No canvas element")
        
        if not issues:
            print("HTML verification passed!")
        
        return issues
  
    def generate_css_component(self, spec, html):
        """Step 3b: Generate CSS component"""
    
        print("\nSTEP 3B: Generating CSS Component")
        print("-" * 50)
        
        contracts = spec['contracts']
        
        prompt = f"""Generate CSS for this game.

        GAME TITLE: {spec['title']}

        HTML IDs TO STYLE:
        - #{contracts['container_id']}
        - #{contracts['canvas_id']}
        - #{contracts['score_id']}
        - #{contracts['timer_id']}

        REQUIREMENTS:
        - Dark theme: background #1a1a1a
        - Green accents: #00ff88
        - Canvas: 3px solid #00ff88 border, rounded corners
        - Centered layout
        - Good typography
        - Responsive spacing

        Return ONLY the CSS (no <style> tags, just the CSS rules)."""

        try:
            print("Calling Claude to generate CSS...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            css = response.content[0].text
            
            # Clean markdown
            if "```css" in css:
                css = css.split("```css")[1].split("```")[0].strip()
            elif "```" in css:
                css = css.split("```")[1].split("```")[0].strip()
            
            print(f"CSS generated ({len(css)} chars)")
            return css
            
        except Exception as e:
            print(f"CSS generation failed: {e}")
            return None

    def verify_css_component(self, css, contracts):
        """Verify CSS component"""
        
        print("\nVerifying CSS Component")
        print("-" * 50)
        
        issues = []
        
        if css is None:
            issues.append("CSS is None")
            return issues
        
        # Check required selectors
        required_selectors = [
            (f"#{contracts['canvas_id']}", "Canvas"),
            (f"#{contracts['container_id']}", "Container")
        ]
        
        for selector, description in required_selectors:
            if selector not in css:
                issues.append(f"Missing CSS for: {selector} ({description})")
                print(f"Missing: {selector}")
            else:
                print(f"Found: {selector}")
        
        # Check braces balanced
        if css.count('{') != css.count('}'):
            issues.append("Unbalanced braces in CSS")
            print("Unbalanced braces")
        else:
            print("Braces balanced")
        
        if not issues:
            print("CSS verification passed!")
        
        return issues

    def generate_js_component(self, spec, html, image_base64):
        """Step 3c: Generate JavaScript component"""
        
        print("\nSTEP 3C: Generating JavaScript Component")
        print("-" * 50)
        
        contracts = spec['contracts']
        
        prompt = f"""Generate JavaScript game logic for this browser game.

        GAME SPEC:
        {json.dumps(spec, indent=2)}

        REQUIRED DOM ELEMENTS (from HTML):
        - Canvas: document.getElementById('{contracts['canvas_id']}')
        - Score: document.getElementById('{contracts['score_id']}')
        - Timer: document.getElementById('{contracts['timer_id']}')

        REQUIREMENTS:
        1. Get canvas context: const ctx = canvas.getContext('2d')
        2. Load background image: - USE THIS EXACT PLACEHOLDER:
           const bgImage = new Image();
           bgImage.onload = () => {{ console.log('Image loaded'); startGame(); }};
           bgImage.onerror = () => {{ console.warn('Image failed'); startGame(); }};
           bgImage.src = 'PLACEHOLDER_IMAGE_DATA';
        3. Arrow key controls (←↑↓→)
        4. Player moves at speed from spec
        5. Collision detection with obstacles from spec
        6. Collect items from spec
        7. Win when all items collected + reach goal
        8. Update score and timer displays
        9. Game loop with requestAnimationFrame
        10. Required functions: startGame(), gameLoop(), draw()
        11. Game should finish in 2 minute
        12. When an item is collected, the item collected name should briefly appear at the top of the canvas for 3 seconds.
        13. The obstacles should be drawn as filled rectangles using their specified colors from the spec. but keep the rectangle as translucent as possible and name of the obstacle written in a smaller font inside the obstacle.
        14. CRITICAL - START GAME IMMEDIATELY:
            At the very end of the script, call startGame() immediately:
            
            // Start game when DOM is ready
            if (document.readyState === 'loading') {{
                document.addEventListener('DOMContentLoaded', startGame);
            }} else {{
                startGame();
            }}
        15. CRITICAL: Use EXACTLY the text 'PLACEHOLDER_IMAGE_DATA' for the image src.
            Do NOT generate any base64 data yourself.
            
            Return ONLY JavaScript code (no <script> tags).
            Use the exact obstacle and collectible positions from the spec."""

        try:
                print("Calling Claude to generate JavaScript...")
                
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=3500,  # JS is bigger
                    messages=[{"role": "user", "content": prompt}]
                )
                
                js = response.content[0].text
                
                # Clean markdown
                if "```javascript" in js:
                    js = js.split("```javascript")[1].split("```")[0].strip()
                elif "```js" in js:
                    js = js.split("```js")[1].split("```")[0].strip()
                elif "```" in js:
                    js = js.split("```")[1].split("```")[0].strip()
                
                      # CRITICAL: Replace placeholder with actual base64
                print(f"Checking for placeholder...")
                if 'PLACEHOLDER_IMAGE_DATA' in js:
                    print("Found placeholder, injecting image...")
                    js = js.replace('PLACEHOLDER_IMAGE_DATA', f'data:image/jpeg;base64,{image_base64}')
                else:
                    print("Placeholder not found! Trying fallback replacement...")
                    # Fallback: look for any data:image/jpeg;base64, pattern and replace
                    import re
                    pattern = r"bgImage\.src\s*=\s*['\"]data:image/jpeg;base64,[^'\"]*['\"]"
                    replacement = f"bgImage.src = 'data:image/jpeg;base64,{image_base64}'"
                    js = re.sub(pattern, replacement, js)
                
                # FORCE START - add this at the end if not present
                if 'startGame()' not in js.split('\n')[-10:]:  # Check last 10 lines
                    print("Adding forced game start...")
                    js += "\n\n// Force start\nif (document.readyState === 'loading') {\n    document.addEventListener('DOMContentLoaded', startGame);\n} else {\n    startGame();\n}"
                js += "\n\n// Debug logging\nconsole.log('✅ Script loaded');\nconsole.log('Canvas:', document.getElementById('" + contracts['canvas_id'] + "'));\nconsole.log('Starting in 100ms...');\nsetTimeout(() => { console.log('Calling startGame...'); startGame(); }, 100);"
                print(f"JavaScript generated ({len(js)} chars)")
                        
                  # Verify image is actually in there
                if image_base64[:50] in js:
                    print("Image data verified in JS")
                else:
                    print("WARNING: Image data might not be properly injected!")
                return js
                        
        except Exception as e:
                print(f"JavaScript generation failed: {e}")
                return None     

    def verify_js_component(self, js, contracts):
        """Verify JavaScript component"""
        
        print("\nVerifying JavaScript Component")
        print("-" * 50)
        
        issues = []
        
        if js is None:
            issues.append("JavaScript is None")
            return issues
        
        # Check required functions
        required_functions = ['startGame', 'gameLoop', 'draw']
        
        for func in required_functions:
            if f'function {func}' not in js and f'{func} =' not in js and f'const {func}' not in js:
                issues.append(f"Missing function: {func}")
                print(f"Missing: {func}()")
            else:
                print(f"Found: {func}()")
        
        # Check uses correct IDs
        required_ids = [contracts['canvas_id'], contracts['score_id'], contracts['timer_id']]
        
        for id_name in required_ids:
            if f"'{id_name}'" not in js and f'"{id_name}"' not in js:
                issues.append(f"Doesn't use required ID: {id_name}")
                print(f"Doesn't use: {id_name}")
            else:
                print(f"Uses: {id_name}")
        
        # Check for game loop
        if 'requestAnimationFrame' not in js:
            issues.append("Missing requestAnimationFrame")
            print("No requestAnimationFrame")
        else:
            print("Has requestAnimationFrame")
        
        if not issues:
            print("JavaScript verification passed!")
        
        return issues
    
    def assemble_game(self, html_code, css, js, spec):
        """Step 4: Assemble all components into final HTML"""
        
        print("\nSTEP 4: Assembling Game")
        print("-" * 50)
        
        title = spec.get('title', 'Photo Game')
        
        full_html = f'''<!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
        {css}
            </style>
        </head>
        <body>
        {html_code}
            <script>
        {js}
            </script>
        </body>
        </html>'''
        
        print(f"Assembly complete!")
        print(f"   Total size: {len(full_html)} chars")
        print(f"   - HTML: {len(html_code)} chars")
        print(f"   - CSS: {len(css)} chars")
        print(f"   - JS: {len(js)} chars")
        import html
        # Escape so it can live safely inside srcdoc=""
        escaped = html.escape(full_html, quote=True)

        # IMPORTANT: allow-scripts so the JS runs
        iframe = f"""
            <iframe
            srcdoc="{escaped}"
            style="width: 100%; max-width: 920px; height: 760px; border: 0; border-radius: 12px;"
            sandbox="allow-scripts allow-same-origin"
            ></iframe>
            """
        return iframe
    
    def verify_collectible_positions(self, spec):
        """Verify collectibles aren't inside obstacles"""
        
        print("\nVERIFICATION: Collectible Positions")
        print("-" * 50)
        
        issues = []
        
        for collectible in spec['collectibles']:
            cx = collectible['x']
            cy = collectible['y']
            c_size = collectible['size']
            c_name = collectible['name']
            
            for obstacle in spec['obstacles']:
                ox = obstacle['x']
                oy = obstacle['y']
                ow = obstacle['width']
                oh = obstacle['height']
                o_name = obstacle['name']
                
                # Check if collectible center is inside obstacle
                if (cx > ox and cx < ox + ow and 
                    cy > oy and cy < oy + oh):
                    
                    issue = f"{c_name} at ({cx},{cy}) is inside {o_name} [{ox},{oy},{ox+ow},{oy+oh}]"
                    issues.append(issue)
                    print(f"{issue}")
        
        if not issues:
            print("All collectibles are reachable!")
        else:
            print(f"Found {len(issues)} position issues")
        
        return issues
    
    def repair_collectible_positions(self, spec, issues):
        """Repair collectibles that overlap obstacles"""
        
        print("\nREPAIR: Fixing Collectible Positions")
        print("-" * 50)
        
        # Extract which collectibles have issues
        broken_collectibles = []
        for issue in issues:
            # Parse collectible name from issue string
            c_name = issue.split(" at ")[0]
            broken_collectibles.append(c_name)
        
        print(f"Broken collectibles: {', '.join(broken_collectibles)}")
        
        prompt = f"""Fix the collectible positions in this game spec.

    CURRENT SPEC:
    {json.dumps(spec, indent=2)}

    PROBLEMS FOUND:
    {chr(10).join([f"- {issue}" for issue in issues])}

    TASK:
    Generate NEW positions for these collectibles: {', '.join(broken_collectibles)}

    RULES:
    - Keep same collectibles (names, sizes, colors)
    - Change ONLY their x,y positions
    - Must NOT overlap any obstacle rectangles
    - Must be at least 20 pixels from obstacle edges
    - Must be reachable by player

    Return ONLY a JSON array of the fixed collectibles with this structure:
    [
    {{"name": "Item", "x": 123, "y": 456, "size": 15, "color": "#FFD700", "collected": false}}
    ]

    Return ONLY the JSON array, no explanations."""

        try:
            print("Asking Claude to fix positions...")
            
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            json_text = response.content[0].text
            
            # Clean markdown
            if "```json" in json_text:
                json_text = json_text.split("```json")[1].split("```")[0].strip()
            elif "```" in json_text:
                json_text = json_text.split("```")[1].split("```")[0].strip()
            
            fixed_collectibles = json.loads(json_text)
            
            # Replace broken collectibles in spec
            for fixed in fixed_collectibles:
                for i, original in enumerate(spec['collectibles']):
                    if original['name'] == fixed['name']:
                        spec['collectibles'][i] = fixed
                        print(f"✅ Fixed {fixed['name']}: ({fixed['x']}, {fixed['y']})")
            
            return spec
            
        except Exception as e:
            print(f"Repair failed: {e}")
            return spec  # Return original if repair fails