"""
Main entry point for the LangGraph Research Agent System
"""
import os
from dotenv import load_dotenv
from src.config.settings import settings
from src.p1_extraction import parse_module,extraction_module
from src.p2_query import researcher_node,AgentState
import argparse
import json
from datetime import datetime

if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description="Run research report agent")
    # parser.add_argument("--subject", required=True, help="The research subject (e.g. 产品功效)")
    # parser.add_argument("--industry", required=True, help="The industry (e.g. 护肤)")
    #
    # args = parser.parse_args()
    # # Extract values
    # subject = args.subject
    # industry = args.industry


    # base_dir = Path(__file__).parent.parent.parent  # Goes to Prod/
    # output_dir = base_dir / "output"
    filename = 'ASICS_Social_Listening_Report_April_2025'
    output_dir = settings.OUTPUT_DIR


    print('***' * 20)
    print('Parsing commencing ...')
    print('***' * 20)

    parse_init = parse_module(output_dir, filename)
    res1 = parse_init._parse()
    print(res1)
    for _ in res1[2]:
        print(_)
    print('***' * 20)
    print('Parsing completed ...')
    print('***' * 20)

    print('***' * 20)
    print('Extraction commencing ...')
    print('***' * 20)
    extraction_init = extraction_module(res1[2])
    res2 = extraction_init._extract()
    print(res2)
    print('***' * 20)
    print('Extraction completed ...')
    print('***' * 20)

    res3 = extraction_init._retain()
    print(res3)
    for _ in res3:
        print(_)

    print('***' * 20)
    print('Key finding retention completed ...')
    print('***' * 20)

    print('***' * 20)
    print('Query Search commencing ...')
    print('***' * 20)

    res4_support = []
    res4_oppose = []
    res3
    for _value in res3[5:15]:
        print(_value[0], _value[1])
        state1 = AgentState(subject=_value[1], support_or_oppose="支持")
        state2 = AgentState(subject=_value[1], support_or_oppose="反对")
        support_search = researcher_node(state1)
        oppose_search = researcher_node(state2)
        print(support_search)
        res4_support.append([_value[0], _value[1], support_search])
        res4_oppose.append([_value[0], _value[1], oppose_search])
    print(res4_support)
    print(res4_oppose)

    print('***' * 20)
    print('Query Search completed ...')
    print('***' * 20)

    _dict = {}
    _counter = 0
    full_str = ''
    for a, b in zip(res4_support, res4_oppose):
        _dict[_counter] = {'page': a[0], 'finding': a[1], 'supporting_evidence': a[2], 'opposing_evidence': b[2]}
        _counter += 1
        supporting_fact=''
        if isinstance(a[2], list):
            l_supporting_fact = [
                f'''# Supporting Evidence {enum + 1}:\nTitle:{i.get('Title')}\nSnippet:{i.get('Snippet')}\nLink:{i.get('Link')}'''
                for enum, i in enumerate(a[2])]
            supporting_fact = '\n\n'.join(l_supporting_fact)
        opposing_fact=''
        if isinstance(b[2], list):
            l_opposing_fact = [
                f'''# Opposing Evidence {enum + 1}:\nTitle:{i.get('Title')}\nSnippet:{i.get('Snippet')}\nLink:{i.get('Link')}'''
                for
                enum, i in enumerate(b[2])]
            opposing_fact = '\n\n'.join(l_opposing_fact)

        _str = f'''### Page Number: {a[0] + 1}\nFinding: {a[1]}\n\n{supporting_fact}\n\n{opposing_fact}'''
        _str += '\n\n#################################\n\n'
        full_str += _str

    print(full_str)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_txt = f"{filename}_research_result_{timestamp}.txt"
    output_json = f"{filename}_research_result_{timestamp}.json"
    txt_filepath = settings.OUTPUT_DIR / 'research_result' /  output_txt
    json_filepath = settings.OUTPUT_DIR / 'research_result' / output_json
    with open(txt_filepath, "w", encoding="utf-8") as f:
        f.write(full_str)

    with open(json_filepath, 'w', encoding="utf-8") as json_file:
        json.dump(_dict, json_file, indent=4)

    print(f"✅ Result saved to: {settings.OUTPUT_DIR / 'research_result'}")
    print('***' * 20)
    print('Output completed ...')
    print('***' * 20)

