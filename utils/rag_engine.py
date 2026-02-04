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
        당신은 시멘트 제조 공정 및 품질 관리 전문가입니다. 
        제공된 엑셀 데이터(사용자가 올린 실시간 공정 데이터)와 기술 문서(RAG 지식 베이스)를 모두 참고하여 답변하세요.
        
        답변 가이드라인:
        1. 엑셀 데이터가 있다면 수치 중심의 구체적인 분석을 제공하세요.
        2. 공정 이론이나 품질 기준은 기술 문서 내용을 바탕으로 설명하세요.
        3. 엑셀 데이터에서 이상 징후가 보인다면 기술 지식을 기반으로 원인과 해결책을 제안하세요.
        4. 답변은 한국어로 하며, 전문적이면서도 친절한 톤을 유지하세요.
        5. 수식이나 표를 사용하면 더 좋습니다.
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
