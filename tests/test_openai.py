import os
from dotenv import load_dotenv
from openai import OpenAI
import time

# Load environment
load_dotenv()

def speed_test_comprehensive():
    """Comprehensive speed test across models and prompt sizes"""
    
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    models_to_test = [
        "gpt-3.5-turbo",
        "gpt-4o-mini", 
        "gpt-4.1-nano",
        "gpt-4.1-mini",
    ]
    
    # Different test sizes
    tests = {
        "ULTRA_MINIMAL": {
            "prompt": "Rate 0-100: Python is good. Number only.",
            "max_tokens": 5
        },
        "SMALL": {
            "prompt": "Rate this Wikipedia text 0-100 for quality: 'Python is a programming language created by Guido van Rossum.' Return JSON: {score: X, reason: 'brief reason'}",
            "max_tokens": 50
        },
        "MEDIUM": {
            "prompt": """Evaluate this Wikipedia text against these criteria:
1. Neutral Point of View (0-100)
2. Verifiability (0-100) 
3. No Original Research (0-100)

Text: "Python is a high-level programming language created by Guido van Rossum in 1991. It emphasizes code readability with significant whitespace. Python supports multiple programming paradigms including procedural, object-oriented, and functional programming."

Return JSON: {"npov": X, "verify": Y, "research": Z, "overall": avg}""",
            "max_tokens": 100
        },
        "LARGE": {
            "prompt": """Evaluate this Wikipedia article draft against Wikipedia's core guidelines:

**Text:** "Climate change refers to long-term shifts in global temperatures and weather patterns. According to the Intergovernmental Panel on Climate Change (IPCC), human activities have been the main driver of climate change since the mid-20th century, primarily through the emission of greenhouse gases such as carbon dioxide. The effects include rising sea levels, changing precipitation patterns, and more frequent extreme weather events."

**Criteria:**
1. Neutral Point of View (NPOV): Is content neutral and unbiased?
2. Verifiability: Are claims backed by reliable sources?
3. No Original Research: Is content based on published sources?

Return JSON format:
{
  "overall_score": 85,
  "breakdown": {
    "npov_score": 90,
    "verifiability_score": 80,
    "original_research_score": 85
  },
  "feedback": ["suggestion 1", "suggestion 2"]
}""",
            "max_tokens": 200
        }
    }
    
    results = {}
    
    print("🚀 COMPREHENSIVE SPEED TEST")
    print("=" * 60)
    
    for test_name, test_config in tests.items():
        print(f"\n📝 {test_name} TEST")
        print(f"Prompt length: {len(test_config['prompt'])} chars")
        print(f"Max tokens: {test_config['max_tokens']}")
        print("-" * 40)
        
        results[test_name] = {}
        
        for model in models_to_test:
            try:
                start_time = time.time()
                
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": test_config["prompt"]}],
                    temperature=0,
                    max_tokens=test_config["max_tokens"],
                )
                
                end_time = time.time()
                latency = end_time - start_time
                
                results[test_name][model] = latency
                
                status = "🟢" if latency < 1.0 else "🟡" if latency < 2.0 else "🔴"
                print(f"{status} {model:15} | {latency:5.2f}s | {response.choices[0].message.content[:50]}...")
                
            except Exception as e:
                results[test_name][model] = float('inf')
                print(f"❌ {model:15} | ERROR | {str(e)[:50]}...")
        
        # Show best for this test
        best_model = min(results[test_name], key=results[test_name].get)
        best_time = results[test_name][best_model]
        print(f"🏆 Fastest: {best_model} ({best_time:.2f}s)")
    
    # Summary table
    print("\n" + "=" * 60)
    print("📊 SUMMARY TABLE (seconds)")
    print("=" * 60)
    print(f"{'Model':<15} | {'Ultra':<6} | {'Small':<6} | {'Medium':<6} | {'Large':<6} | {'Avg':<6}")
    print("-" * 60)
    
    for model in models_to_test:
        times = []
        row = f"{model:<15} |"
        
        for test_name in tests.keys():
            time_val = results[test_name].get(model, float('inf'))
            if time_val == float('inf'):
                row += f" {'ERROR':<6} |"
            else:
                row += f" {time_val:5.2f} |"
                times.append(time_val)
        
        avg_time = sum(times) / len(times) if times else float('inf')
        if avg_time == float('inf'):
            row += f" {'ERROR':<6}"
        else:
            row += f" {avg_time:5.2f}"
        
        print(row)
    
    # Recommendations
    print("\n🎯 RECOMMENDATIONS:")
    print("-" * 30)
    
    # Find best overall
    avg_times = {}
    for model in models_to_test:
        times = []
        for test_name in tests.keys():
            time_val = results[test_name].get(model, float('inf'))
            if time_val != float('inf'):
                times.append(time_val)
        if times:
            avg_times[model] = sum(times) / len(times)
    
    if avg_times:
        best_overall = min(avg_times, key=avg_times.get)
        print(f"🏆 Best Overall: {best_overall} (avg: {avg_times[best_overall]:.2f}s)")
    
    # Find sub-1s options
    sub_1s_options = []
    for test_name in tests.keys():
        for model, time_val in results[test_name].items():
            if time_val < 1.0:
                sub_1s_options.append(f"{model} on {test_name}")
    
    if sub_1s_options:
        print(f"⚡ Sub-1s options: {', '.join(sub_1s_options[:3])}...")
    
    # Find sub-2s options  
    sub_2s_count = 0
    for test_name in tests.keys():
        for model, time_val in results[test_name].items():
            if time_val < 2.0:
                sub_2s_count += 1
    
    print(f"🟡 Sub-2s results: {sub_2s_count}/{len(models_to_test) * len(tests)} total")

if __name__ == "__main__":
    speed_test_comprehensive()