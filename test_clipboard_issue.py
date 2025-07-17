#!/usr/bin/env python3
"""
Test script to reproduce the clipboard paste button issue
"""

import streamlit as st
from clipboard_paste import clipboard_paste_area

st.title("🔍 Clipboard Paste Button Issue Test")

st.write("Testing the reported issue:")
st.write("1. Copy an image (Ctrl+C)")
st.write("2. Click the paste area below")
st.write("3. Press Ctrl+V")
st.write("4. Check if evaluation button appears")

st.write("---")

# Test single screen evaluation like in main app
upload_method = st.radio(
    "업로드 방법을 선택하세요:",
    ["파일 업로드", "클립보드에서 붙여넣기"],
    horizontal=True
)

uploaded_file = None
pasted_image = None

if upload_method == "파일 업로드":
    uploaded_file = st.file_uploader(
        "프로토타입 이미지를 업로드하세요",
        type=['png', 'jpg', 'jpeg']
    )
else:
    pasted_image = clipboard_paste_area(
        label="📋 이미지를 복사한 후 아래 영역을 클릭하고 Ctrl+V를 눌러주세요:",
        key="paste_single",
        height=200
    )

# Same logic as in main app
if uploaded_file:
    current_image = uploaded_file
elif pasted_image:
    current_image = pasted_image
else:
    # 세션 상태에서 붙여넣은 이미지 확인
    session_key = "clipboard_paste_paste_single"
    current_image = st.session_state.get(session_key, None)

# Debug information
st.write("---")
st.write("**Debug Information:**")
st.write(f"upload_method: {upload_method}")
st.write(f"uploaded_file: {uploaded_file is not None}")
st.write(f"pasted_image: {pasted_image is not None}")
st.write(f"current_image: {current_image is not None}")

# Show session state
st.write("**Session State:**")
for key, value in st.session_state.items():
    if "clipboard_paste" in key:
        st.write(f"{key}: {type(value)} - {value is not None}")

# Image preview
if current_image:
    st.image(current_image, caption="업로드된 프로토타입", width=400)

# Button visibility logic (same as main app)
show_button = False
if upload_method == "파일 업로드" and uploaded_file:
    show_button = True
elif upload_method == "클립보드에서 붙여넣기":
    # 컴포넌트 반환값 또는 세션 상태 확인
    session_key = "clipboard_paste_paste_single"
    if pasted_image or (session_key in st.session_state and st.session_state[session_key] is not None):
        show_button = True

st.write(f"**show_button: {show_button}**")

if show_button:
    if st.button("평가 시작"):
        st.success("✅ Button clicked successfully!")
        st.write("This proves the button logic is working correctly.")
else:
    st.warning("❌ 평가 버튼이 표시되지 않습니다.")