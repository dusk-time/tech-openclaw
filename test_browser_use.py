#!/usr/bin/env python3
"""Test browser-use directly without CLI"""
import asyncio
from browser_use import Browser

async def test_browser():
    print("Starting browser test...")
    
    # Create browser session
    browser = Browser(
        headless=False,  # Show browser window
    )
    
    try:
        # Start browser
        print("Starting browser...")
        await browser.start()
        
        # Navigate to example.com
        print("Navigating to https://example.com...")
        await browser.goto("https://example.com")
        
        # Get page title
        title = await browser.evaluate("document.title")
        print(f"Page title: {title}")
        
        # Take screenshot
        await browser.screenshot("test_screenshot.png")
        print("Screenshot saved to test_screenshot.png")
        
        # Wait a bit then close
        await asyncio.sleep(2)
        await browser.close()
        
        print("✅ Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        try:
            await browser.close()
        except:
            pass
        raise

if __name__ == "__main__":
    asyncio.run(test_browser())
