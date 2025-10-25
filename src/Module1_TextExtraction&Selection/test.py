
import os
import json
from pathlib import Path


class parse_module():
    def __init__(self ,doc_path ,_filename):
        self._filename = _filename

        _path = doc_path / _filename / 'auto'
        _file = _path / f'{_filename}_content_list.json'
        with open(_file, 'r', encoding='utf-8') as f:
            self.l_data = json.load(f)

    def _parse(self):
        l_res = []
        l_page = []
        for enum, _i in enumerate(self.l_data):
            page_idx = _i.get('page_idx')
            if enum == 0:
                prev_page_idx = page_idx
                _counter = 1
            if prev_page_idx != page_idx:
                l_res.append([prev_page_idx, l_page])
                l_page = []
                prev_page_idx = page_idx
                _counter = 1

            if _i.get('type') == 'text':
                text = _i.get('text')
                text_level = _i.get('text_level')
                if text == '':
                    pass
                text = f'''<{_counter}>{text}</{_counter}>'''
                if text_level == 1:
                    text = '# ' + text
                l_page.append(text)
                _counter += 1

        if len(l_page) >= 1:
            l_res.append([page_idx, l_page])

        l_res2 = [[i[0], '\n\n'.join(i[1])] if len(i[1]) >= 1 else '' for i in l_res]
        l_conso = [self._filename, l_res, l_res2]
        return l_conso


if __name__ == "__main__":
    base_dir = Path(__file__).parent.parent.parent  # Goes to Prod/
    output_dir = base_dir / "output"

    _filename = 'ASICS_Social_Listening_Report_April_2025'
    parse_init = parse_module(output_dir,_filename)
    res = parse_init._parse()
    print(res)
    for _ in res[2]:
        print(_)


