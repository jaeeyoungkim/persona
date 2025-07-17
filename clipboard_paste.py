#!/usr/bin/env python3
"""
Native clipboard paste functionality for Streamlit
Uses JavaScript and HTML5 clipboard API for Ctrl+V support
"""

import streamlit as st
import streamlit.components.v1 as components
import base64
from PIL import Image
import io
import uuid

def clipboard_paste_component(key: str, height: int = 200):
    """
    Create a native clipboard paste component that responds to Ctrl+V
    
    Args:
        key: Unique key for the component
        height: Height of the paste area in pixels
    
    Returns:
        PIL Image or None if no image was pasted
    """
    
    # Initialize session state for this component
    session_key = f"clipboard_paste_{key}"
    if session_key not in st.session_state:
        st.session_state[session_key] = None
    
    # Generate unique IDs for this component instance
    component_id = f"clipboard_paste_{key}_{uuid.uuid4().hex[:8]}"
    
    # HTML and JavaScript for clipboard paste functionality
    html_code = f"""
    <div id="{component_id}" style="
        border: 2px dashed #ccc;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        background-color: #f9f9f9;
        height: {height}px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
        cursor: pointer;
        transition: all 0.3s ease;
    ">
        <div id="paste_instruction_{component_id}" style="
            font-size: 16px;
            color: #666;
            margin-bottom: 10px;
        ">
            📋 이미지를 복사한 후 여기를 클릭하고 Ctrl+V를 눌러주세요
        </div>
        <div id="paste_status_{component_id}" style="
            font-size: 14px;
            color: #999;
        ">
            또는 이미지 파일을 드래그 앤 드롭하세요
        </div>
        <canvas id="preview_canvas_{component_id}" style="
            max-width: 100%;
            max-height: 150px;
            display: none;
            margin-top: 10px;
            border: 1px solid #ddd;
        "></canvas>
    </div>

    <script>
    (function() {{
        const pasteArea = document.getElementById('{component_id}');
        const instruction = document.getElementById('paste_instruction_{component_id}');
        const status = document.getElementById('paste_status_{component_id}');
        const canvas = document.getElementById('preview_canvas_{component_id}');
        const ctx = canvas.getContext('2d');
        
        let pastedImageData = null;
        
        // Make the area focusable
        pasteArea.setAttribute('tabindex', '0');
        
        // Focus on click
        pasteArea.addEventListener('click', function() {{
            pasteArea.focus();
            status.textContent = '이제 Ctrl+V를 눌러 이미지를 붙여넣으세요';
            pasteArea.style.borderColor = '#007bff';
            pasteArea.style.backgroundColor = '#f0f8ff';
        }});
        
        // Handle focus/blur visual feedback
        pasteArea.addEventListener('focus', function() {{
            pasteArea.style.borderColor = '#007bff';
            pasteArea.style.backgroundColor = '#f0f8ff';
        }});
        
        pasteArea.addEventListener('blur', function() {{
            pasteArea.style.borderColor = '#ccc';
            pasteArea.style.backgroundColor = '#f9f9f9';
        }});
        
        // Handle paste event
        pasteArea.addEventListener('paste', function(e) {{
            e.preventDefault();
            
            const items = e.clipboardData.items;
            let imageFound = false;
            
            for (let i = 0; i < items.length; i++) {{
                const item = items[i];
                
                if (item.type.indexOf('image') !== -1) {{
                    imageFound = true;
                    const blob = item.getAsFile();
                    
                    const reader = new FileReader();
                    reader.onload = function(event) {{
                        const img = new Image();
                        img.onload = function() {{
                            // Resize canvas to fit image
                            const maxWidth = 300;
                            const maxHeight = 150;
                            let width = img.width;
                            let height = img.height;
                            
                            if (width > maxWidth) {{
                                height = (height * maxWidth) / width;
                                width = maxWidth;
                            }}
                            if (height > maxHeight) {{
                                width = (width * maxHeight) / height;
                                height = maxHeight;
                            }}
                            
                            canvas.width = width;
                            canvas.height = height;
                            canvas.style.display = 'block';
                            
                            // Draw image on canvas
                            ctx.drawImage(img, 0, 0, width, height);
                            
                            // Convert to base64
                            const base64Data = canvas.toDataURL('image/png').split(',')[1];
                            pastedImageData = base64Data;
                            
                            // Update UI
                            instruction.textContent = '✅ 이미지가 성공적으로 붙여넣어졌습니다!';
                            instruction.style.color = '#28a745';
                            status.textContent = '이미지 처리 중... 잠시만 기다려주세요';
                            
                            // Send data to Streamlit
                            window.parent.postMessage({{
                                type: 'streamlit:setComponentValue',
                                value: base64Data
                            }}, '*');
                        }};
                        img.src = event.target.result;
                    }};
                    reader.readAsDataURL(blob);
                    break;
                }}
            }}
            
            if (!imageFound) {{
                status.textContent = '❌ 이미지를 찾을 수 없습니다. 이미지를 복사한 후 다시 시도해주세요.';
                status.style.color = '#dc3545';
            }}
        }});
        
        // Handle drag and drop
        pasteArea.addEventListener('dragover', function(e) {{
            e.preventDefault();
            pasteArea.style.borderColor = '#007bff';
            pasteArea.style.backgroundColor = '#f0f8ff';
            status.textContent = '이미지를 여기에 드롭하세요';
        }});
        
        pasteArea.addEventListener('dragleave', function(e) {{
            e.preventDefault();
            pasteArea.style.borderColor = '#ccc';
            pasteArea.style.backgroundColor = '#f9f9f9';
            status.textContent = '또는 이미지 파일을 드래그 앤 드롭하세요';
        }});
        
        pasteArea.addEventListener('drop', function(e) {{
            e.preventDefault();
            pasteArea.style.borderColor = '#ccc';
            pasteArea.style.backgroundColor = '#f9f9f9';
            
            const files = e.dataTransfer.files;
            if (files.length > 0 && files[0].type.startsWith('image/')) {{
                const file = files[0];
                const reader = new FileReader();
                
                reader.onload = function(event) {{
                    const img = new Image();
                    img.onload = function() {{
                        // Same image processing as paste
                        const maxWidth = 300;
                        const maxHeight = 150;
                        let width = img.width;
                        let height = img.height;
                        
                        if (width > maxWidth) {{
                            height = (height * maxWidth) / width;
                            width = maxWidth;
                        }}
                        if (height > maxHeight) {{
                            width = (width * maxHeight) / height;
                            height = maxHeight;
                        }}
                        
                        canvas.width = width;
                        canvas.height = height;
                        canvas.style.display = 'block';
                        
                        ctx.drawImage(img, 0, 0, width, height);
                        
                        const base64Data = canvas.toDataURL('image/png').split(',')[1];
                        pastedImageData = base64Data;
                        
                        instruction.textContent = '✅ 이미지가 성공적으로 업로드되었습니다!';
                        instruction.style.color = '#28a745';
                        status.textContent = '이미지 처리 중... 잠시만 기다려주세요';
                        
                        window.parent.postMessage({{
                            type: 'streamlit:setComponentValue',
                            value: base64Data
                        }}, '*');
                    }};
                    img.src = event.target.result;
                }};
                reader.readAsDataURL(file);
            }} else {{
                status.textContent = '❌ 이미지 파일만 업로드할 수 있습니다.';
                status.style.color = '#dc3545';
            }}
        }});
        
        // Keyboard shortcut hint
        document.addEventListener('keydown', function(e) {{
            if (e.ctrlKey && e.key === 'v' && document.activeElement === pasteArea) {{
                // The paste event will be handled by the paste event listener
                status.textContent = '붙여넣기 중...';
            }}
        }});
    }})();
    </script>
    """
    
    # Create the component
    result = components.html(html_code, height=height + 50)
    
    # Handle component result and session state
    if result:
        try:
            # Check if result is a valid base64 string (not DeltaGenerator or other objects)
            if not isinstance(result, str):
                # If result is not a string (e.g., DeltaGenerator), return stored image
                return st.session_state[session_key]
            
            # Additional validation: check if it looks like base64
            if not result or len(result) < 10:
                return st.session_state[session_key]
            
            # Decode base64 to image
            image_data = base64.b64decode(result)
            image = Image.open(io.BytesIO(image_data))
            
            # Store in session state
            st.session_state[session_key] = image
            
            # Trigger rerun to update the UI and button visibility
            st.rerun()
            
            return image
        except (TypeError, ValueError, base64.binascii.Error) as e:
            # Handle base64 decode errors specifically
            st.error(f"이미지 처리 중 오류가 발생했습니다: 올바른 이미지 데이터가 아닙니다.")
            return st.session_state[session_key]
        except Exception as e:
            st.error(f"이미지 처리 중 오류가 발생했습니다: {str(e)}")
            return st.session_state[session_key]
    
    # Return stored image if available
    return st.session_state[session_key]

def clipboard_paste_area(label: str, key: str, height: int = 200):
    """
    Streamlit wrapper for clipboard paste functionality
    
    Args:
        label: Label to display above the paste area
        key: Unique key for the component
        height: Height of the paste area
    
    Returns:
        PIL Image or None
    """
    st.write(label)
    return clipboard_paste_component(key, height)