#!/usr/bin/env python3
"""
Debug script to test clipboard paste behavior
"""

import streamlit as st
from clipboard_paste import clipboard_paste_area

st.title("🔍 Clipboard Paste Debug")

st.write("Testing clipboard paste functionality...")

# Test clipboard paste
pasted_image = clipboard_paste_area(
    label="📋 Test clipboard paste:",
    key="debug_paste",
    height=200
)

st.write("---")
st.write("**Debug Information:**")
st.write(f"pasted_image type: {type(pasted_image)}")
st.write(f"pasted_image is None: {pasted_image is None}")
st.write(f"pasted_image is truthy: {bool(pasted_image)}")

if pasted_image:
    st.write("✅ Image detected!")
    st.image(pasted_image, caption="Pasted image", width=300)
    
    # Show button
    if st.button("Test Button"):
        st.success("Button clicked successfully!")
else:
    st.write("❌ No image detected")

# Show session state
st.write("---")
st.write("**Session State:**")
for key, value in st.session_state.items():
    if "clipboard_paste" in key:
        st.write(f"{key}: {type(value)} - {value is not None}")