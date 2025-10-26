

from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.utilities import GoogleSerperAPIWrapper
import operator
import os
from langchain.chat_models import init_chat_model
from datetime import datetime
from pydantic import BaseModel, Field
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import PromptTemplate
from langchain.prompts import ChatPromptTemplate
from typing import Dict, List
from langchain_tavily import TavilySearch
from src.config.settings import settings


class SerperSearchResult(BaseModel):
    """Represents a single raw search result."""
    summary: str  = Field(description="网络搜索信息的内容摘要")
    title: str  = Field(description="网络搜索信息的标题")
    snippet: str = Field(description="网络搜索信息的片段")
    link: str  = Field(description="网络搜索信息的链接")

class TavilySearchResult(BaseModel):
    """Represents a single raw search result."""
    summary: str  = Field(description="网络搜索信息的内容摘要")
    title: str  = Field(description="网络搜索信息的标题")
    content: str = Field(description="网络搜索信息的内容")
    url: str  = Field(description="网络搜索信息的链接")

class SearchResultsProcessor(BaseModel):
    """Processes search results and outputs only summary, title, snippet and link."""
    results: List[TavilySearchResult] = Field(default={}, description="网络搜索信息的内容摘要、标题、片段和链接")
    # def top_five(self) -> List[dict]:
    #     """Return a list of up to 3 items (summary, title, url) from first 5 results."""
    #     top_five = self.results[:5]
    #     output = [
    #         {"summary": r.summary, "title": r.title, "url": str(r.url)}
    #         for r in top_five[:5]
    #     ]
    #     return output

parser = PydanticOutputParser(pydantic_object=SearchResultsProcessor)
format_inst=parser.get_format_instructions()

llm = init_chat_model(model=settings.MODEL_NAME, model_provider=settings.MODEL_PROVIDER, temperature=settings.TEMPERATURE)

# Define the shared state
class AgentState(TypedDict):
    industry: str
    subject: str
    support_or_oppose: str
    query: Annotated[list, operator.add]
    messages: Annotated[list, operator.add]
    research_data: Annotated[list, operator.add]
    final_result: str
    next_agent: str
    iteration_count: int

serper_search = GoogleSerperAPIWrapper(k=5)
tavily_search = TavilySearch(
    max_results=5,
    topic="general",
    # include_answer=False,
    # include_raw_content=False,
    # include_images=False,
    # include_image_descriptions=False,
    # include_favicon=False,
    # search_depth="basic",
    # time_range="day",
    # include_domains=None,
    # exclude_domains=None,
    # country=None
)


# # Initialize the LLM and Serper search tool
# llm = init_chat_model(model=settings.MODEL_NAME, model_provider=settings.MODEL_PROVIDER,
#                       temperature=settings.TEMPERATURE)
# search = GoogleSerperAPIWrapper(k=10)

def serper_perform_search(query: str) -> str:
    """
    Perform a web search using Serper API
    """
    try:
        results = serper_search.results(query)

        # Extract relevant information
        search_results = []

        # Add organic results
        if "organic" in results:
            for i, result in enumerate(results["organic"][:5], 1):
                _dict={f'Title':result.get('title', 'N/A'), 'Snippet': result.get('snippet', 'N/A'),'Link': result.get('link', 'N/A')}
                search_results.append(_dict)

        # Add knowledge graph if available
        if "knowledgeGraph" in results:
            kg = results["knowledgeGraph"]
            search_results.append({'KG Title':kg.get('title', 'N/A'),'KG Description':kg.get('description', 'N/A')})

        # Add answer box if available
        if "answerBox" in results:
            ab = results["answerBox"]
            search_results.append({'Answer Box':ab.get('answer', ab.get('snippet', 'N/A'))})

        return search_results if search_results else "No results found"

    except Exception as e:
        return f"Search error: {str(e)}"


def tavily_perform_search(query: str) -> str:
    """
    Perform a web search using Serper API
    """
    try:
        results = tavily_search.invoke({"query": query})
        search_results = tool_res.get('results')
        # Extract relevant information
        search_results = []
        return search_results if search_results else "No results found"

    except Exception as e:
        return f"Search error: {str(e)}"


def researcher_node(state: AgentState) -> AgentState:
    """
    Researcher agent that performs searches using Serper API
    """
    print("\n🔍 RESEARCHER AGENT ACTIVE")

    # Get the last message to understand what to research
    messages = state.get("messages", [])
    subject = state.get("subject", "")
    support_or_oppose = state.get("support_or_oppose", "")

    system_prompt1 = f'''
    ## 角色：
    你是一位擅长使用搜索工具的分析研究员，核心能力是基于用户提供的结论进行信息调整与网络查询，以验证结论有效性。

    ## 任务：
    1、分析师会先提供结论，结论如下：\n{subject}
    2、根据这个分析师提供的结论，通过网络查询收集【{support_or_oppose}】该结论的论据，完成【{support_or_oppose}】结论的验证。
    3、仅需编写 1 个 用于搜索的查询句子，无需额外内容。
    4、查询句子可采用以下两种形式：
        - 改写式：直接改写原结论，确保改写后句子的核心逻辑、大方向与原结论一致。
        示例：原结论 “今年越来越多人不想消费了”，可改写为 “最近人们都不消费”、“最近大家都在省钱”。
        - 疑问式：将原结论转化为疑问句，保持核心语义不变。
        示例：原结论 “今年越来越多人不想消费了”，可改写为 “最近人们是不是都不太想消费了？”

    ## 原则：
    1、你编写搜索查询句子需要依据的结论是：{subject}
    2、请不要编写和上述结论无关的查询句子
    3、严格仅输出你的搜索查询句子，禁止添加其他任何文字!!!!'''

    response = llm.invoke([SystemMessage(content=system_prompt1)])
    search_query = response.content

    # Perform actual web search using Serper
    print(f"Searching web for: {search_query}")
    search_results = serper_perform_search(search_query)
    print(f"Searched result:\n\n {search_results}")
    return search_results



