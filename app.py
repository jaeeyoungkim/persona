#!/usr/bin/env python3
"""
AI 페르소나 프로토타입 평가 에이전트 - MVP 구현
PRD 기반 핵심 기능 구현
"""

import streamlit as st
import openai
import base64
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import os
from PIL import Image
import io

# 페이지 설정
st.set_page_config(
    page_title="AI 페르소나 프로토타입 평가 에이전트",
    page_icon="🤖",
    layout="wide"
)

# 기본 페르소나 라이브러리 (P0 요구사항)
DEFAULT_PERSONAS = {
    "개발자": {
        "description": "5년 경력의 백엔드 개발자. 기술적 세부사항을 중시하고, 효율성과 논리적 구조를 선호한다.",
        "characteristics": "기술 친화적, 논리적 사고, 효율성 중시, 복잡한 UI보다 기능성 선호"
    },
    "기획자": {
        "description": "3년 경력의 제품 기획자. 사용자 경험과 비즈니스 가치를 균형있게 고려한다.",
        "characteristics": "사용자 중심적 사고, 비즈니스 임팩트 고려, 데이터 기반 의사결정 선호"
    },
    "비숙련 사용자": {
        "description": "IT 기술에 익숙하지 않은 40대 일반 사용자. 직관적이고 간단한 인터페이스를 선호한다.",
        "characteristics": "기술 비친화적, 직관성 중시, 복잡한 기능 회피, 명확한 안내 필요"
    },
    "디자이너": {
        "description": "UI/UX 디자이너로 시각적 일관성과 사용자 경험을 중시한다.",
        "characteristics": "시각적 일관성 중시, 사용자 경험 전문가, 접근성 고려, 트렌드 민감"
    },
    "마케터": {
        "description": "디지털 마케팅 담당자로 전환율과 사용자 참여도를 중시한다.",
        "characteristics": "전환율 중시, 사용자 참여도 관심, 명확한 CTA 선호, 브랜딩 고려"
    }
}

class PersonaEvaluator:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
    
    def encode_image(self, image_input) -> str:
        """이미지를 base64로 인코딩 (파일 업로드 또는 PIL Image 지원)"""
        # Check for None or invalid input types
        if image_input is None:
            raise ValueError("이미지 입력이 None입니다.")
        
        # Check if input is a DeltaGenerator or other Streamlit object
        if hasattr(image_input, '__class__') and 'DeltaGenerator' in str(type(image_input)):
            raise TypeError("DeltaGenerator 객체는 이미지로 처리할 수 없습니다. 올바른 이미지를 업로드해주세요.")
        
        # Check if input is a PIL Image
        if hasattr(image_input, 'save') and hasattr(image_input, 'format'):
            try:
                # PIL Image의 경우
                img_bytes = io.BytesIO()
                image_input.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                return base64.b64encode(img_bytes.getvalue()).decode('utf-8')
            except Exception as e:
                raise ValueError(f"PIL 이미지 처리 중 오류가 발생했습니다: {str(e)}")
        
        # Check if input has getvalue method (file upload)
        elif hasattr(image_input, 'getvalue'):
            try:
                # 파일 업로드의 경우 (BytesIO)
                return base64.b64encode(image_input.getvalue()).decode('utf-8')
            except Exception as e:
                raise ValueError(f"파일 업로드 처리 중 오류가 발생했습니다: {str(e)}")
        
        else:
            # Unsupported input type
            raise TypeError(f"지원되지 않는 이미지 형식입니다: {type(image_input)}. PIL Image 또는 파일 업로드만 지원됩니다.")
    
    def evaluate_single_screen(self, image_base64: str, persona_name: str, persona_info: Dict) -> Dict:
        """단일 화면 평가 (P0 요구사항)"""
        prompt = f"""
        당신은 '{persona_name}' 페르소나입니다.
        
        페르소나 정보:
        - 설명: {persona_info['description']}
        - 특성: {persona_info['characteristics']}
        
        첨부된 프로토타입 화면을 이 페르소나의 관점에서 평가해주세요.
        
        다음 형식으로 응답해주세요:
        1. 전체적인 인상 (1-10점)
        2. 장점 (3가지)
        3. 단점 (3가지)
        4. 개선 제안 (3가지)
        5. 이 페르소나가 가장 중요하게 생각할 요소
        
        구체적이고 실용적인 피드백을 제공해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            return {
                "persona": persona_name,
                "evaluation": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "persona": persona_name,
                "evaluation": f"평가 중 오류가 발생했습니다: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def compare_ab_test(self, image_a_base64: str, image_b_base64: str, 
                       persona_name: str, persona_info: Dict) -> Dict:
        """A/B 테스트 평가 (P0 요구사항)"""
        prompt = f"""
        당신은 '{persona_name}' 페르소나입니다.
        
        페르소나 정보:
        - 설명: {persona_info['description']}
        - 특성: {persona_info['characteristics']}
        
        첨부된 두 개의 프로토타입 화면(A안, B안)을 비교하여 평가해주세요.
        
        다음 형식으로 응답해주세요:
        1. 선호하는 안: A안 또는 B안
        2. 선호도: A안 vs B안 (예: 70% vs 30%)
        3. 선택 이유 (구체적으로 3가지)
        4. A안의 장단점
        5. B안의 장단점
        6. 이 페르소나 관점에서의 최종 추천
        
        객관적이고 구체적인 근거를 제시해주세요.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_a_base64}"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{image_b_base64}"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1200
            )
            
            return {
                "persona": persona_name,
                "comparison": response.choices[0].message.content,
                "timestamp": datetime.now().isoformat()
            }
        except Exception as e:
            return {
                "persona": persona_name,
                "comparison": f"비교 평가 중 오류가 발생했습니다: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }

def main():
    st.title("🤖 AI 페르소나 프로토타입 평가 에이전트")
    st.markdown("### SaaS 프로토타입을 AI 페르소나가 빠르게 평가해드립니다")
    
    # API 키 입력 (기본값 설정)
    default_api_key = ""
    api_key = st.sidebar.text_input("OpenAI API Key", value=default_api_key, type="password")
    if not api_key:
        st.warning("OpenAI API 키를 입력해주세요.")
        return
    
    evaluator = PersonaEvaluator(api_key)
    
    # 평가 모드 선택
    evaluation_mode = st.radio(
        "평가 모드를 선택하세요:",
        ["단일 화면 평가", "A/B 테스트 비교"]
    )
    
    # 페르소나 선택
    st.subheader("📋 평가할 페르소나 선택")
    selected_personas = st.multiselect(
        "페르소나를 선택하세요 (복수 선택 가능):",
        list(DEFAULT_PERSONAS.keys()),
        default=["개발자", "비숙련 사용자"]
    )
    
    if not selected_personas:
        st.warning("최소 하나의 페르소나를 선택해주세요.")
        return
    
    # 선택된 페르소나 정보 표시
    with st.expander("선택된 페르소나 정보"):
        for persona in selected_personas:
            st.write(f"**{persona}**: {DEFAULT_PERSONAS[persona]['description']}")
    
    if evaluation_mode == "단일 화면 평가":
        st.subheader("📱 프로토타입 업로드")
        
        uploaded_file = st.file_uploader(
            "프로토타입 이미지를 업로드하세요",
            type=['png', 'jpg', 'jpeg']
        )
        
        if uploaded_file and st.button("평가 시작"):
            with st.spinner("AI 페르소나들이 평가 중입니다..."):
                # 업로드된 파일이나 붙여넣은 이미지 처리 (encode_image가 둘 다 처리)
                image_base64 = evaluator.encode_image(uploaded_file)
                
                # 이미지 표시
                st.image(uploaded_file, caption="평가 대상 프로토타입", width=400)
                
                # 각 페르소나별 평가 실행
                results = []
                for persona in selected_personas:
                    result = evaluator.evaluate_single_screen(
                        image_base64, persona, DEFAULT_PERSONAS[persona]
                    )
                    results.append(result)
                
                # 결과 표시
                st.subheader("📊 평가 결과")
                for result in results:
                    with st.expander(f"🎭 {result['persona']} 페르소나 평가"):
                        st.write(result['evaluation'])
                        st.caption(f"평가 시간: {result['timestamp']}")
    
    else:  # A/B 테스트 모드
        st.subheader("📱 A/B 테스트 프로토타입 업로드")
        
        
        col1, col2 = st.columns(2)
        
        uploaded_file_a = None
        uploaded_file_b = None
        pasted_image_a = None
        pasted_image_b = None
        
        with col1:
            st.write("**A안**")
            uploaded_file_a = st.file_uploader(
                "A안 이미지 업로드",
                type=['png', 'jpg', 'jpeg'],
                key="file_a"
            )
        
        with col2:
            st.write("**B안**")
            uploaded_file_b = st.file_uploader(
                "B안 이미지 업로드",
                type=['png', 'jpg', 'jpeg'],
                key="file_b"
            )
        
        # 현재 이미지들 설정
        current_image_a = uploaded_file_a
        current_image_b = uploaded_file_b
        
        # 이미지 미리보기 표시
        col1_preview, col2_preview = st.columns(2)
        with col1_preview:
            if current_image_a:
                st.image(current_image_a, caption="A안 미리보기", width=300)
        with col2_preview:
            if current_image_b:
                st.image(current_image_b, caption="B안 미리보기", width=300)
        
        # A/B 테스트 버튼 표시 조건 개선 - 세션 상태도 확인
        show_ab_button = False
        if ab_upload_method == "파일 업로드":
            if uploaded_file_a and uploaded_file_b:
                show_ab_button = True
        elif ab_upload_method == "클립보드에서 붙여넣기":
            # 컴포넌트 반환값 또는 세션 상태 확인
            session_key_a = "clipboard_paste_paste_a"
            session_key_b = "clipboard_paste_paste_b"
            has_image_a = pasted_image_a or (session_key_a in st.session_state and st.session_state[session_key_a] is not None)
            has_image_b = pasted_image_b or (session_key_b in st.session_state and st.session_state[session_key_b] is not None)
            if has_image_a and has_image_b:
                show_ab_button = True
        
        if show_ab_button and st.button("A/B 테스트 시작"):
            with st.spinner("AI 페르소나들이 A/B 테스트를 진행 중입니다..."):
                # A안, B안 이미지 처리 (encode_image가 파일과 PIL Image 둘 다 처리)
                image_a_base64 = evaluator.encode_image(current_image_a)
                image_b_base64 = evaluator.encode_image(current_image_b)
                
                # 이미지들 표시
                col1, col2 = st.columns(2)
                with col1:
                    st.image(current_image_a, caption="A안", width=300)
                with col2:
                    st.image(current_image_b, caption="B안", width=300)
                
                # 각 페르소나별 A/B 테스트 실행
                results = []
                for persona in selected_personas:
                    result = evaluator.compare_ab_test(
                        image_a_base64, image_b_base64, persona, DEFAULT_PERSONAS[persona]
                    )
                    results.append(result)
                
                # 결과 표시
                st.subheader("📊 A/B 테스트 결과")
                for result in results:
                    with st.expander(f"🎭 {result['persona']} 페르소나 비교 평가"):
                        st.write(result['comparison'])
                        st.caption(f"평가 시간: {result['timestamp']}")
    
    # 사이드바에 추가 정보
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📋 사용 가이드")
    st.sidebar.markdown("""
    1. **단일 화면 평가**: 하나의 프로토타입에 대한 페르소나별 피드백
    2. **A/B 테스트**: 두 개의 프로토타입을 비교하여 선호도 분석
    3. **페르소나**: 다양한 사용자 관점에서 평가 제공
    """)
    
    st.sidebar.markdown("### ⚡ 주요 기능")
    st.sidebar.markdown("""
    - 5분 이내 빠른 피드백
    - 다중 페르소나 동시 평가
    - 정성적/정량적 분석
    - 구체적인 개선 제안
    """)

if __name__ == "__main__":
    main()