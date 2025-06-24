import httpx
import json

# Test the API with sample articles
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health")
        print("Health Check:", response.json())

def test_good_article():
    """Test with a well-written article"""
    good_article = """
    Climate change refers to long-term shifts in global temperatures and weather patterns. According to the Intergovernmental Panel on Climate Change (IPCC), human activities have been the main driver of climate change since the mid-20th century, primarily through the emission of greenhouse gases such as carbon dioxide.

    The effects of climate change include rising sea levels, changing precipitation patterns, and more frequent extreme weather events. The IPCC's Sixth Assessment Report, published in 2021, states that global surface temperature has increased by approximately 1.1°C since 1850-1900.

    Mitigation efforts include transitioning to renewable energy sources, improving energy efficiency, and implementing carbon pricing mechanisms. The Paris Agreement, adopted in 2015, aims to limit global warming to well below 2°C above pre-industrial levels.
    """
    
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/evaluate",
            json={
                "article_text": good_article,
                "title": "Climate Change"
            }
        )
        print("Good Article Result:")
        print(json.dumps(response.json(), indent=2))

def test_biased_article():
    """Test with a biased article"""
    biased_article = """
    Electric cars are absolutely amazing and everyone should buy them immediately! They are the best invention ever and will solve all our problems. Gas cars are terrible and stupid.

    Tesla is the greatest company in the world and Elon Musk is a genius. I personally think that anyone who doesn't drive electric is harming the planet. My neighbor got a Tesla and now his life is perfect.

    Based on my own research and personal experience, electric cars never break down and are always cheaper to maintain. I've never seen any evidence that suggests otherwise.
    """
    
    with httpx.Client() as client:
        response = client.post(
            f"{BASE_URL}/evaluate",
            json={
                "article_text": biased_article,
                "title": "Electric Cars"
            }
        )
        print("\nBiased Article Result:")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    print("Testing Wikipedia Evaluator API...")
    test_health()
    test_good_article()
    test_biased_article()