import mkdocs.plugins
import mkdocs.structure.nav
import re
from typing import List
from bs4 import BeautifulSoup, Tag
from bs4.element import ResultSet


class ReferenceLinkFixer(mkdocs.plugins.BasePlugin):
    def on_page_content(self, html: str, page: mkdocs.structure.nav.Page, config, files) -> str:
        new_html = html
        soup = BeautifulSoup(new_html, 'html.parser')
        code_blocks: ResultSet = soup.find_all('code')

        for code_block in code_blocks:
            spans: ResultSet = code_block.find_all('span')
            for span in spans:
                new_span_text = span.text
                matches: List[str] = re.findall(r'\[\w+\]\((?:\.\.\/)?\w*\)', new_span_text)
                if matches:
                    new_span = soup.new_tag('span')
                    for match in matches:
                        grouped_match: re.Match = re.match(r'\[(.+)\]\((.+)\)', match)
                        if grouped_match:
                            display_text: str = grouped_match[1]
                            href: str = grouped_match[2]
                            link_tag = soup.new_tag('a', href=href)
                            link_tag.string = display_text
                            new_span_text = new_span_text.replace(match, str(link_tag))
                    new_span.append(BeautifulSoup(new_span_text[1:-1], 'html.parser'))
                    try:
                        span.replace_with(new_span)
                    except ValueError:
                        pass
                    span.decompose()

        return str(soup)

