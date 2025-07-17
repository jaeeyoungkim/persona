#!/usr/bin/env python3
"""
Test script to reproduce the clipboard paste hanging issue
"""

import streamlit as st
from clipboard_paste import clipboard_paste_area

st.title("🔍 Clipboard Paste Hang Test")

st.write("Testing clipboard paste hanging issue...")
st.write("Steps to reproduce:")
st.write("1. Copy an image (Ctrl+C)")
st.write("2. Click the paste area below")
st.write("3. Press Ctrl+V")
st.write("4. Observe if it hangs at '이미지 처리 중... 잠시만 기다려주세요'")

st.write("---")

# Test clipboard paste
pasted_image = clipboard_paste_area(
    label="📋 Test clipboard paste (watch for hanging):",
    key="hang_test",
    height=200
)

st.write("---")
st.write("**Debug Information:**")
st.write(f"pasted_image type: {type(pasted_image)}")
st.write(f"pasted_image is None: {pasted_image is None}")

# Show session state
st.write("**Session State:**")
for key, value in st.session_state.items():
    if "clipboard_paste" in key:
        st.write(f"{key}: {type(value)} - {value is not None}")

if pasted_image:
    st.write("✅ Image successfully processed!")
    st.image(pasted_image, caption="Pasted image", width=300)
    
    # This button should appear after successful paste
    if st.button("Test Button (should appear after paste)"):
        st.success("Button clicked successfully!")
else:
    st.write("❌ No image detected or still processing...")

# Add some debugging info
st.write("---")
st.write("**Current Streamlit Run Count:**")
if 'run_count' not in st.session_state:
    st.session_state.run_count = 0
st.session_state.run_count += 1
st.write(f"Run #{st.session_state.run_count}")