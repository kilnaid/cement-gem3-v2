import os
from google import genai
from google.genai import types
from pinecone import Pinecone
import pandas as pd
from typing import List, Dict

class RAGEngine:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.pc_api_key = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "cement-qna")
        self.login_id = os.getenv("LOGIN_ID", "sampyo")
        self.login_pw = os.getenv("LOGIN_PASSWORD", "1q2w3e4r")
        
        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)
        
        # Initialize Pinecone
        if self.pc_api_key:
            self.pc = Pinecone(api_key=self.pc_api_key)
            self.index = self.pc.Index(self.index_name)
        else:
            self.index = None

    def get_embedding(self, text: str) -> List[float]:
        """텍스트의 임베딩을 생성합니다."""
        result = self.client.models.embed_content(
            model="text-embedding-004",
            contents=text
        )
        return result.embeddings[0].values

    def query_pinecone(self, query: str, top_k: int = 3) -> str:
        """Pinecone에서 관련 문서를 검색합니다."""
        if not self.index:
            return ""
        
        query_embedding = self.get_embedding(query)
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            include_metadata=True
        )
        
        contexts = [item['metadata']['text'] for item in results['matches'] if 'text' in item['metadata']]
        return "\n\n".join(contexts)

    def generate_response(self, user_query: str, excel_context: str = "", chat_history: List[Dict] = []) -> str:
        """엑셀 데이터와 RAG 문맥을 기반으로 답변을 생성합니다."""
        
        # Search for technical documentation context
        rag_context = self.query_pinecone(user_query)
        
        # Construct Prompt
        system_instruction = """
        당신은 시멘트 제조 공정 및 품질 관리 전문가인 'Cement Expert AI'입니다. 
        사용자가 제공한 엑셀 데이터(실시간 공정 데이터)와 기술 문서(RAG 지식 베이스)를 기반으로 고도의 전문적인 답변을 한국어로 제공하는 것이 당신의 역할입니다.
        
        [답변 원칙]
        1. 모든 답변은 한국어로 하며, 전문적이면서도 신뢰감 있는 전문가의 톤을 유지하십시오.
        2. 엑셀 데이터가 제공된 경우, 공정 수치(온도, 압력, 성분비 등)를 정밀하게 분석하여 구체적인 현황을 설명하십시오.
        3. RAG 컨텍스트(기술 문서)를 참고하여 표준 공정 가이드라인, 품질 기준, 이론적 배경을 함께 설명하십시오.
        4. 현장에서 발생할 수 있는 이상 징후나 개선 포인트가 보인다면, 전문가 관점에서 원인과 해결책을 논리적으로 제안하십시오.
        5. 수식, 표, 글머리 기호를 적절히 활용하여 가독성이 높은 구조적 답변을 만드십시오.
        
        [데이터 우선순위]
        - 실시간 현황 질문: 엑셀 데이터 > RAG 문서
        - 공정 원리 및 기준 질문: RAG 문서 > 엑셀 데이터
        - 복합 질문: 두 데이터를 연계하여 종합 분석
        """
        
        prompt = f"사용자 질문: {user_query}\n\n"
        
        if excel_context:
            prompt += f"--- 엑셀 데이터 분석 컨텍스트 ---\n{excel_context}\n\n"
            
        if rag_context:
            prompt += f"--- 관리 기준/기술 문서 컨텍스트 ---\n{rag_context}\n\n"

        # Generate using Gemini 2.0 Flash
        response = self.client.models.generate_content(
            model="gemini-2.0-flash",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.2
            ),
            contents=prompt
        )
        
        return response.text
