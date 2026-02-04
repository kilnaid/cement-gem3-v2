import pandas as pd
import streamlit as st
import os
from typing import Optional

class ExcelAnalyzer:
    def __init__(self):
        self.df: Optional[pd.DataFrame] = None
    
    def load_file(self, file):
        """엑셀 또는 CSV 파일을 로드합니다."""
        try:
            if file.name.endswith('.xlsx') or file.name.endswith('.xls'):
                self.df = pd.read_excel(file)
            elif file.name.endswith('.csv'):
                self.df = pd.read_csv(file)
            return True, "파일 로드 성공"
        except Exception as e:
            return False, f"파일 로드 실패: {str(e)}"

    def get_summary(self):
        """데이터프레임의 요약을 생성합니다."""
        if self.df is None:
            return "분석할 데이터가 없습니다."
        
        summary = {
            "columns": list(self.df.columns),
            "total_rows": len(self.df),
            "missing_values": self.df.isnull().sum().to_dict(),
            "numerical_stats": self.df.describe().to_dict() if not self.df.select_dtypes(include=['number']).empty else "No numerical data"
        }
        return summary

    def get_data_context(self):
        """LLM에 전달할 데이터의 문맥(샘플 행 등)을 생성합니다."""
        if self.df is None:
            return ""
        
        context = f"데이터 컬럼: {', '.join(self.df.columns)}\n"
        context += f"전체 행 수: {len(self.df)}\n"
        context += "데이터 샘플 (상위 3개):\n"
        context += self.df.head(3).to_markdown()
        return context
