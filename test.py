import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def test_server():
    """Test if the server is running"""
    print("🧪 Testing RAG Chatbot API\n")
    print("="*50)
    
    # Test 1: Root endpoint
    print("\n1️⃣ Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print("✅ Server is running!")
            print(f"   Status: {data.get('status')}")
            print(f"   Gemini configured: {data.get('gemini_configured')}")
            print(f"   Embedding model loaded: {data.get('embedding_model_loaded')}")
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server!")
        print("   Make sure the server is running with: python main.py")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test 2: Health check
    print("\n2️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed!")
            print(f"   Documents loaded: {data.get('documents_loaded')}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Test chat without documents
    print("\n3️⃣ Testing chat endpoint (no documents)...")
    try:
        response = requests.post(
            f"{BASE_URL}/chat",
            json={"message": "Hello, can you hear me?", "top_k": 3}
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Chat endpoint working!")
            print(f"   Response preview: {data.get('response')[:100]}...")
        else:
            print(f"❌ Chat failed: {response.status_code}")
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 4: List documents
    print("\n4️⃣ Testing documents endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/documents")
        if response.status_code == 200:
            data = response.json()
            print("✅ Documents endpoint working!")
            print(f"   Total chunks: {data.get('total_chunks')}")
            print(f"   Unique documents: {data.get('unique_documents')}")
        else:
            print(f"❌ Documents endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "="*50)
    print("✨ Testing complete!")
    print("\n💡 Next steps:")
    print("   1. Visit http://localhost:8000/docs for interactive API docs")
    print("   2. Upload a document using the /upload endpoint")
    print("   3. Chat with your documents using the /chat endpoint")
    print("="*50)
    
    return True

if __name__ == "__main__":
    print("Waiting for server to start...")
    time.sleep(2)  # Give server time to start if just launched
    test_server()