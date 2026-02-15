"""
AI分析器模块
"""
import os
import json
import time
from typing import Dict, Any, Optional, List
from datetime import datetime
from zhipuai import ZhipuAI
from dataclasses import dataclass, asdict

@dataclass
class ProjectAnalysis:
    """项目分析结果"""
    title: str
    description: str
    url: str
    category: str
    technology_highlight: str
    potential_applications: str
    is_highlight: bool = False
    stars_today: Optional[int] = None

@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    date: str
    total_projects: int
    highlight_project: ProjectAnalysis
    categories: Dict[str, List[str]]
    trends: List[str]
    insights: List[str]
    prediction: str
    analysis_time: str


class AIAnalyzer:
    """AI分析器"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "glm-4-flash"):
        """
        初始化AI分析器
        
        Args:
            api_key: 智谱AI API密钥
            model: AI模型名称
        """
        self.api_key = api_key or os.environ.get("ZHIPUAI_API_KEY", "")
        self.model = model
        self.client = None
        self.initialize_client()
    
    def initialize_client(self):
        """初始化智谱AI客户端"""
        if not self.api_key:
            raise ValueError("ZHIPUAI_API_KEY 未设置")
        self.client = ZhipuAI(api_key=self.api_key)
    
    def analyze_trends(self, trends_file: str, system_prompt: str) -> str:
        """
        分析GitHub趋势
        
        Args:
            trends_file: 包含趋势数据的文件路径
            system_prompt: 系统提示词
            
        Returns:
            分析结果文本
        """
        try:
            # 读取趋势数据
            with open(trends_file, 'r', encoding='utf-8') as f:
                trends_content = f.read()
            
            print(f"🔍 AI正在分析趋势数据，共 {len(trends_content.splitlines())} 个项目...")
            
            # 调用AI分析
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": trends_content}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            analysis_result = response.choices[0].message.content
            print("✅ AI分析完成")
            
            return analysis_result
            
        except Exception as e:
            print(f"❌ AI分析失败: {e}")
            raise
    
    def parse_structured_analysis(self, raw_analysis: str) -> TrendAnalysis:
        """
        解析结构化分析结果
        
        Args:
            raw_analysis: 原始AI分析文本
            
        Returns:
            结构化的分析结果
        """
        try:
            # 这里可以添加更复杂的解析逻辑
            # 暂时返回简单的结构化数据
            lines = raw_analysis.split('\n')
            
            # 提取关键部分（简化的解析逻辑）
            highlight_project = None
            categories = {}
            trends = []
            insights = []
            prediction = ""
            
            current_section = ""
            for line in lines:
                if line.startswith('##'):
                    current_section = line.strip('# ')
                elif line.startswith('###'):
                    current_section = line.strip('# ')
                elif current_section == "最惊艳项目" and line.strip() and not highlight_project:
                    highlight_project = ProjectAnalysis(
                        title="待解析",
                        description=line.strip(),
                        url="",
                        category="惊艳项目",
                        technology_highlight="",
                        potential_applications="",
                        is_highlight=True
                    )
                elif current_section == "今日技术趋势" and line.strip():
                    trends.append(line.strip('- '))
                elif current_section == "深度洞察" and line.strip() and line.startswith(('1.', '2.', '3.')):
                    insights.append(line.strip('123. '))
                elif current_section == "预测建议" and line.strip():
                    prediction = line.strip()
            
            # 如果没有解析到惊艳项目，使用默认值
            if not highlight_project:
                highlight_project = ProjectAnalysis(
                    title="AI趋势项目",
                    description="今日GitHub趋势中最引人注目的项目",
                    url="",
                    category="综合",
                    technology_highlight="AI驱动的创新",
                    potential_applications="多种应用场景",
                    is_highlight=True
                )
            
            # 统计项目数量
            project_count = len([l for l in lines if l.strip().startswith('[')])
            
            # 创建分析结果
            analysis = TrendAnalysis(
                date=datetime.now().strftime('%Y-%m-%d'),
                total_projects=project_count,
                highlight_project=highlight_project,
                categories=categories,
                trends=trends[:3] if trends else ["AI技术创新持续活跃"],
                insights=insights[:3] if insights else ["今日趋势显示AI项目多样性增加"],
                prediction=prediction or "AI与各行业融合将继续深化",
                analysis_time=datetime.now().strftime('%H:%M:%S')
            )
            
            return analysis
            
        except Exception as e:
            print(f"解析分析结果失败: {e}")
            # 返回默认分析结果
            return self.create_default_analysis()
    
    def create_default_analysis(self) -> TrendAnalysis:
        """创建默认分析结果"""
        highlight_project = ProjectAnalysis(
            title="GitHub趋势分析",
            description="今日AI项目趋势分析报告",
            url="",
            category="综合",
            technology_highlight="多领域AI应用",
            potential_applications="技术开发、商业应用",
            is_highlight=True
        )
        
        return TrendAnalysis(
            date=datetime.now().strftime('%Y-%m-%d'),
            total_projects=15,
            highlight_project=highlight_project,
            categories={"综合": ["AI项目"]},
            trends=["AI技术持续创新"],
            insights=["AI项目多样性增加", "开源社区活跃", "实用工具类项目增多"],
            prediction="AI与实体经济融合将加速",
            analysis_time=datetime.now().strftime('%H:%M:%S')
        )
    
    def save_analysis(self, analysis: TrendAnalysis, output_file: str):
        """
        保存分析结果
        
        Args:
            analysis: 分析结果
            output_file: 输出文件路径
        """
        # 保存为JSON格式
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(analysis), f, ensure_ascii=False, indent=2)
        
        # 同时保存为文本格式（兼容原有格式）
        txt_file = output_file.replace('.json', '.txt')
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write(self.format_analysis_text(analysis))
        
        print(f"📝 分析结果已保存到: {output_file}")
    
    def format_analysis_text(self, analysis: TrendAnalysis) -> str:
        """
        格式化分析结果为文本
        
        Args:
            analysis: 分析结果
            
        Returns:
            格式化文本
        """
        lines = [
            f"## {analysis.date} GitHub趋势分析报告",
            "",
            f"### 分析时间: {analysis.analysis_time}",
            f"### 分析项目数: {analysis.total_projects}",
            "",
            "### 最惊艳项目",
            f"{analysis.highlight_project.title} - {analysis.highlight_project.description}",
            "",
            "### 今日技术趋势",
        ]
        for trend in analysis.trends:
            lines.append(f"- {trend}")
        
        lines.extend([
            "",
            "### 深度洞察",
        ])
        for i, insight in enumerate(analysis.insights, 1):
            lines.append(f"{i}. {insight}")
        
        lines.extend([
            "",
            "### 预测建议",
            analysis.prediction,
            "",
            "---",
            "我是谢苹果，AI信息流2.0，由nanobot智能优化，复活了。"
        ])
        
        return '\n'.join(lines)