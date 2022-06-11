from github import Github, Repository, PaginatedList, Tag, Commit, ContentFile
from typing import List


def download_headers(download_dir: str, tag: str, headers: List[str]):
    g = Github()
    repo: Repository = g.get_repo('TokTok/c-toxcore')
    tags: PaginatedList = repo.get_tags()
    found_tags: List[Tag] = [possible_tag for possible_tag in tags if possible_tag.name == tag]
    if not found_tags:
        raise RuntimeError('Can\'t find a git tag with the specified Tox version')
    found_commit: Commit = found_tags[0].commit
    for header in headers:
        tox_header: ContentFile = repo.get_contents(header, ref=found_commit.sha)
        with open(f'{download_dir}/{tox_header.name}', 'wb') as f:
            f.write(tox_header.decoded_content)
