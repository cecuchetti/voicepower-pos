import asyncio
import aiohttp
from server.audio_processor import AudioProcessor
import os
from datetime import datetime
import time

async def countdown(seconds: int):
    """Shows a countdown in the console."""
    print("\nPreparing recording...")
    for i in range(seconds, 0, -1):
        print(f"Starting in {i}...", end='\r')
        await asyncio.sleep(1)
    print("\nRecording!")

async def test_audio_api():
    # Create processor instance
    processor = AudioProcessor()
    
    try:
        print("Starting audio test...")
        await countdown(3)
        
        print("Recording 10 seconds of audio...")
        audio_file = await processor.record_audio(duration=10)
        
        # Create a permanent copy of the file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        permanent_file = f"recordings/recording_{timestamp}.wav"
        
        # Ensure directory exists
        os.makedirs("recordings", exist_ok=True)
        
        # Copy the file
        with open(audio_file, 'rb') as src, open(permanent_file, 'wb') as dst:
            dst.write(src.read())
            
        print(f"\nAudio saved at: {os.path.abspath(permanent_file)}")
        
        print("\nSending audio to API...")
        async with aiohttp.ClientSession() as session:
            # Send file to the cart creation API
            with open(audio_file, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('audio_file', f, filename='recording.wav', content_type='audio/wav')
                
                async with session.post('http://localhost:8000/audio/process/cart', data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        text = result['text']
                        cart_id = result['cart_id']
                        items = result['items']
                        
                        print("\nAPI Response:")
                        print(f"Recognized text: {text}")
                        print(f"Cart created with ID: {cart_id}")
                        print("\nItems in cart:")
                        for item in items:
                            print(f"- {item['quantity']} x {item['name']} "
                                  f"(${item['unit_price']} each)")
                        
                        # Get details of the created cart
                        async with session.get(f'http://localhost:8000/carts/{cart_id}') as cart_response:
                            if cart_response.status == 200:
                                cart = await cart_response.json()
                                print("\nSaved cart details:")
                                for item in cart['items']:
                                    print(f"- {item['quantity']} x {item['product_name']} "
                                          f"at ${item['unit_price']}")
                    else:
                        print(f"\nError: {response.status}")
                        print(await response.text())
            
    finally:
        # Clean up only the temporary file
        if 'audio_file' in locals():
            os.unlink(audio_file)
            print(f"\nTemporary file deleted, but you can find the recording at: {permanent_file}")

if __name__ == "__main__":
    asyncio.run(test_audio_api()) 