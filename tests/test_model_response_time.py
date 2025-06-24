import httpx
import json
import time

# Simple debug test
BASE_URL = "http://localhost:8000"

def test_simple_case():
    """Test with minimal text to check if optimization worked"""
    simple_text = "Python is a programming language created by Guido van Rossum in 1991. It emphasizes code readability with significant whitespace."
    
    print("Testing optimized FastAPI with async...")
    print(f"Text length: {len(simple_text)} characters")
    
    with httpx.Client(timeout=30.0) as client:
        try:
            start_time = time.time()
            print("Sending request...")
            
            response = client.post(
                f"{BASE_URL}/evaluate",
                json={
                    "article_text": simple_text,
                    "title": "Python Programming"
                }
            )
            
            end_time = time.time()
            total_time = end_time - start_time
            
            print(f"✅ Total response time: {total_time:.2f}s")
            print(f"Status code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("Full response:")
                print(json.dumps(result, indent=2))
                
                # Performance analysis
                if total_time < 1.5:
                    print("🟢 EXCELLENT: Sub-1.5s response!")
                elif total_time < 2.5:
                    print("🟡 GOOD: Sub-2.5s response")
                else:
                    print("🔴 SLOW: Still over 2.5s")
                    
            else:
                print(f"Error response: {response.text}")
                
        except httpx.ReadTimeout:
            print("❌ Request timed out")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_simple_case()