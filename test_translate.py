#!/usr/bin/env python3
"""
测试翻译功能
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from arxiv_app import translate_and_summarize

# 测试文本
test_text = """This paper introduces InvisPose, a novel WiFi-based system for dense human pose estimation. 
The system uses commercial mesh routers to enable real-time whole-body tracking through walls. 
Our method achieves state-of-the-art performance on multiple benchmarks while being more practical 
and cost-effective than existing solutions."""

print("测试翻译功能...")
print("英文原文:")
print(test_text)
print("\n" + "="*60 + "\n")

# 测试翻译
try:
    result = translate_and_summarize(test_text, max_length=150)
    print("翻译结果:")
    print(result)
    print(f"长度: {len(result)} 字符")
except Exception as e:
    print(f"❌ 翻译失败: {e}")

# 测试更长的文本
print("\n" + "="*60 + "\n")
long_text = """Large language models have shown remarkable capabilities in natural language understanding and generation. 
However, their performance on complex reasoning tasks remains limited. 
This paper proposes a novel framework that combines chain-of-thought prompting with external knowledge retrieval 
to improve reasoning accuracy. Our method achieves 15% improvement on challenging reasoning benchmarks 
while maintaining computational efficiency. The key innovation is a dynamic retrieval mechanism that selectively 
incorporates relevant information during the reasoning process."""
print("测试更长文本翻译...")
try:
    result2 = translate_and_summarize(long_text, max_length=120)
    print("翻译结果:")
    print(result2)
    print(f"长度: {len(result2)} 字符")
except Exception as e:
    print(f"❌ 翻译失败: {e}")