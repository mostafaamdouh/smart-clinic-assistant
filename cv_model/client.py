"""
API Client - Test the skin classifier with your own images
استخدم هذا الملف للاختبار مع صورك الخاصة
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import requests
    from PIL import Image
except ImportError:
    print("Error: Please install requests and Pillow")
    print("  pip install requests pillow")
    sys.exit(1)


def test_health(api_url: str) -> bool:
    """Check if API is running."""
    try:
        response = requests.get(f"{api_url}/health", timeout=5)
        if response.status_code == 200:
            health = response.json()
            print("\n API Health Check:")
            print(f"  Status: {health['status']}")
            print(f"  Model loaded: {health['model_loaded']}")
            print(f"  Device: {health['device']}")
            print(f"  Best accuracy: {health['best_val_accuracy']:.4f}")
            return True
        else:
            print(f" API returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f" Could not connect to API at {api_url}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def list_classes(api_url: str):
    """List all supported disease classes."""
    try:
        response = requests.get(f"{api_url}/classes", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("\n Supported Classes:")
            print("-" * 60)
            for cls in data["classes"]:
                color = "🔴" if cls["risk"] == "High" else "🟡" if cls["risk"] == "Medium" else "🟢"
                print(f"{color} {cls['code']:8s} → {cls['name']:35s} ({cls['risk']})")
            return True
        return False
    except Exception as e:
        print(f" Error: {e}")
        return False


def predict(api_url: str, image_path: str) -> dict:
    """
    Send image to API and get prediction.
    
    """
    image_path = Path(image_path)
    
    # Check file exists
    if not image_path.exists():
        print(f"✗ File not found: {image_path}")
        return None
    
    # Check file format
    if image_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
        print(f"✗ File must be JPG or PNG, got: {image_path.suffix}")
        return None
    
    # Check file size
    file_size_mb = image_path.stat().st_size / (1024 * 1024)
    if file_size_mb > 10:
        print(f"⚠ File is large ({file_size_mb:.1f}MB). Image will be compressed.")
    
    try:
        # Validate image
        with Image.open(image_path) as img:
            print(f"✓ Image info: {img.size} {img.mode}")
        
        # Send to API
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, f'image/{image_path.suffix[1:]}')}
            response = requests.post(
                f"{api_url}/predict",
                files=files,
                timeout=30
            )
        
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            print(f"✗ API error {response.status_code}: {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error: {e}")
        return None


def format_result(result: dict):
    """Pretty print prediction result."""
    if not result:
        return
    
    risk_color = {
        "High": "🔴",
        "Medium": "🟡",
        "Low": "🟢"
    }
    
    risk = result.get("risk_level", "Unknown")
    color = risk_color.get(risk, "⚪")
    
    print("\n" + "="*60)
    print("🔬 PREDICTION RESULT")
    print("="*60)
    print(f"\nPredicted Disease: {result['predicted_label']}")
    print(f"Code: {result['predicted_class']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"\nRisk Level: {color} {risk}")
    
    print("\n📊 All Confidence Scores:")
    print("-" * 40)
    scores = sorted(
        result['all_scores'].items(),
        key=lambda x: x[1],
        reverse=True
    )
    for label, score in scores:
        bar = "█" * int(score * 20)
        print(f"{label:8s} │{bar:<20s} {score:.4f}")
    
    print("\n⚠️  DISCLAIMER:")
    print(result['disclaimer'])
    print("="*60 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Skin Classifier API Client",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Check API status
  python client.py --health
  
  # List all disease classes
  python client.py --classes
  
  # Predict from image
  python client.py --image path/to/skin_lesion.jpg
  
  # Use different API host
  python client.py --image photo.jpg --url http://192.168.1.100:8000
        """
    )
    
    parser.add_argument(
        '--url',
        default='http://localhost:8000',
        help='API base URL (default: http://localhost:8000)'
    )
    parser.add_argument(
        '--image',
        type=str,
        help='Path to skin lesion image for prediction'
    )
    parser.add_argument(
        '--health',
        action='store_true',
        help='Check API health status'
    )
    parser.add_argument(
        '--classes',
        action='store_true',
        help='List all supported disease classes'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🔬 SKIN DISEASE CLASSIFIER - API CLIENT")
    print("="*60)
    print(f"API URL: {args.url}\n")
    
    # Check health first
    if not test_health(args.url):
        print("\n⚠️ API is not running!")
        print("Start it with: python api.py")
        sys.exit(1)
    
    # List classes if requested
    if args.classes:
        list_classes(args.url)
    
    # Predict if image provided
    if args.image:
        print(f"\n📷 Processing image: {args.image}")
        result = predict(args.url, args.image)
        format_result(result)
    elif not args.classes and not args.health:
        # No action specified
        parser.print_help()


if __name__ == "__main__":
    main()
