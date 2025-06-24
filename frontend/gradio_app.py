import gradio as gr
import httpx
import time

# API Configuration
API_BASE_URL = "http://localhost:8000"

def evaluate_article(article_text, title=""):
    """Evaluate article using the FastAPI backend"""
    
    if not article_text.strip():
        return "❌ Error", "Please enter article text to evaluate.", "", "", "", ""
    
    if len(article_text) < 50:
        return "❌ Error", "Article text is too short for meaningful evaluation (minimum 50 characters).", "", "", "", ""
    
    try:
        start_time = time.time()
        
        with httpx.Client(timeout=30.0) as client:
            response = client.post(
                f"{API_BASE_URL}/evaluate",
                json={
                    "article_text": article_text,
                    "title": title if title.strip() else None
                }
            )
        
        end_time = time.time()
        
        if response.status_code != 200:
            return "❌ Error", f"API Error: {response.text}", "", "", "", ""
        
        result = response.json()
        
        # Format the results
        overall_score = result["overall_score"]
        passes = result["passes_threshold"]
        breakdown = result["breakdown"]
        feedback = result["feedback"]
        
        # Score status
        if passes:
            status = f"✅ PASS ({overall_score}/100)"
        else:
            status = f"❌ NEEDS WORK ({overall_score}/100)"
        
        # Performance info
        performance = f"⚡ Evaluated in {end_time - start_time:.1f}s"
        
        # Breakdown scores
        npov_score = f"🔍 Neutral Point of View: {breakdown['npov_score']}/100"
        verify_score = f"📚 Verifiability: {breakdown['verifiability_score']}/100"
        research_score = f"🔬 No Original Research: {breakdown['original_research_score']}/100"
        
        # Feedback formatting
        feedback_text = "\n\n".join([f"• {item}" for item in feedback])
        
        return status, performance, npov_score, verify_score, research_score, feedback_text
        
    except httpx.ConnectError:
        return "❌ Error", "Cannot connect to evaluation API. Make sure the server is running on localhost:8000", "", "", "", ""
    except httpx.ReadTimeout:
        return "❌ Error", "Evaluation timed out. Please try again with shorter text.", "", "", "", ""
    except Exception as e:
        return "❌ Error", f"Unexpected error: {str(e)}", "", "", "", ""

def create_demo():
    """Create the Gradio interface"""
    
    with gr.Blocks(
        title="Wikipedia Article Evaluator",
        theme=gr.themes.Soft(),
        css="""
        .status-pass { color: green; font-weight: bold; }
        .status-fail { color: red; font-weight: bold; }
        .score-box { padding: 10px; margin: 5px; border-radius: 5px; background-color: #f8f9fa; }
        """
    ) as demo:
        
        gr.Markdown("""
        # 📝 Wikipedia Article Alignment Evaluator
        
        **Evaluate your Wikipedia article drafts against core content policies before submission!**
        
        This tool checks your article against Wikipedia's three core content policies:
        - **Neutral Point of View (NPOV)**: Unbiased, balanced perspective
        - **Verifiability**: Claims backed by reliable sources  
        - **No Original Research**: Content based on published sources
        
        ---
        """)
        
        with gr.Row():
            with gr.Column(scale=2):
                title_input = gr.Textbox(
                    label="📰 Article Title (Optional)",
                    placeholder="e.g., Climate Change, Python Programming Language",
                    lines=1
                )
                
                article_input = gr.Textbox(
                    label="📄 Article Text",
                    placeholder="Paste your Wikipedia article draft here...\n\nExample:\nPython is a high-level programming language created by Guido van Rossum in 1991. It emphasizes code readability with significant whitespace. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
                    lines=15,
                    max_lines=25
                )
                
                # Examples section - more prominent
                gr.Markdown("#### 📚 Try These Examples")
                with gr.Row():
                    example_good = gr.Button("📗 Load Good Example", variant="secondary")
                    example_biased = gr.Button("📕 Load Biased Example", variant="secondary")
                
                # Subtle separation
                gr.Markdown("---")
                
                # Action buttons
                with gr.Row():
                    clear_btn = gr.Button("🗑️ Clear", variant="secondary")
                    evaluate_btn = gr.Button("🔍 Evaluate Article", variant="primary", size="lg")
            
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Evaluation Results")
                
                status_output = gr.Textbox(
                    label="Overall Status",
                    interactive=False,
                    lines=1
                )
                
                performance_output = gr.Textbox(
                    label="Performance",
                    interactive=False,
                    lines=1
                )
                
                gr.Markdown("#### 📈 Score Breakdown")
                
                npov_output = gr.Textbox(
                    label="NPOV Score",
                    interactive=False,
                    lines=1
                )
                
                verify_output = gr.Textbox(
                    label="Verifiability Score", 
                    interactive=False,
                    lines=1
                )
                
                research_output = gr.Textbox(
                    label="Original Research Score",
                    interactive=False,
                    lines=1
                )
                
                feedback_output = gr.Textbox(
                    label="💡 Improvement Suggestions",
                    interactive=False,
                    lines=8,
                    max_lines=15
                )
        
        # Event handlers
        evaluate_btn.click(
            fn=evaluate_article,
            inputs=[article_input, title_input],
            outputs=[status_output, performance_output, npov_output, verify_output, research_output, feedback_output]
        )
        
        clear_btn.click(
            fn=lambda: ("", "", "", "", "", "", "", ""),
            outputs=[title_input, article_input, status_output, performance_output, npov_output, verify_output, research_output, feedback_output]
        )
        
        # Examples
        def load_good_example():
            return "Climate Change", """Climate change refers to long-term shifts in global temperatures and weather patterns. According to the Intergovernmental Panel on Climate Change (IPCC), human activities have been the main driver of climate change since the mid-20th century, primarily through the emission of greenhouse gases such as carbon dioxide.

The effects of climate change include rising sea levels, changing precipitation patterns, and more frequent extreme weather events. The IPCC's Sixth Assessment Report, published in 2021, states that global surface temperature has increased by approximately 1.1°C since 1850-1900.

Mitigation efforts include transitioning to renewable energy sources, improving energy efficiency, and implementing carbon pricing mechanisms. The Paris Agreement, adopted in 2015, aims to limit global warming to well below 2°C above pre-industrial levels."""
        
        def load_biased_example():
            return "Electric Cars", """Electric cars are absolutely amazing and everyone should buy them immediately! They are the best invention ever and will solve all our problems. Gas cars are terrible and stupid.

Tesla is the greatest company in the world and Elon Musk is a genius. I personally think that anyone who doesn't drive electric is harming the planet. My neighbor got a Tesla and now his life is perfect.

Based on my own research and personal experience, electric cars never break down and are always cheaper to maintain. I've never seen any evidence that suggests otherwise."""
        
        example_good.click(
            fn=load_good_example,
            outputs=[title_input, article_input]
        )
        
        example_biased.click(
            fn=load_biased_example,
            outputs=[title_input, article_input]
        )
        
        # Footer
        gr.Markdown("""
        ---
        
        **💡 Tips for Better Scores:**
        - Use neutral, factual language
        - Include citations and references
        - Avoid personal opinions and experiences
        - Present multiple viewpoints fairly
        - Base content on published sources
        
        **🔧 Built with FastAPI + OpenAI GPT-4.1-nano**
        """)
    
    return demo

if __name__ == "__main__":
    demo = create_demo()
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )