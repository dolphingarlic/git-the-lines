import os
import textwrap


async def fetch_http(session, url, response_format='text', **kwargs):
    """Uses aiohttp to make http GET requests"""

    async with session.get(url, **kwargs) as response:
        if response_format == 'text':
            return await response.text()
        elif response_format == 'json':
            return await response.json()


async def fetch_github_snippet(session, repo, path, start_line, end_line):
    headers = {"Accept": "application/vnd.github.v3.raw"}
    if "GITHUB_TOKEN" in os.environ:
        headers["Authorization"] = f'token {os.environ["GITHUB_TOKEN"]}'

    refs = (await fetch_http(session, f"https://api.github.com/repos/{repo}/branches", "json", headers=headers) +
            await fetch_http(session, f"https://api.github.com/repos/{repo}/tags", "json", headers=headers))

    ref = path.split("/")[0]
    file_path = "/".join(path.split("/")[1:])
    for possible_ref in refs:
        if path.startswith(possible_ref["name"] + "/"):
            ref = possible_ref["name"]
            file_path = path[len(ref) + 1:]
            break

    url = f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={ref}"
    file_contents = await fetch_http(session, url, "text", headers=headers)

    return await snippet_to_embed({
        "file_path": file_path,
        "start_line": start_line,
        "end_line": end_line,
    }, file_contents)


async def revert_to_orig(d):
    """Replace URL Encoded values back to their original"""

    for obj in d:
        if d[obj] is not None:
            d[obj] = d[obj].replace('%2F', '/').replace('%2E', '.')


async def orig_to_encode(d):
    """Encode URL Parameters"""

    for obj in d:
        if d[obj] is not None:
            d[obj] = d[obj].replace('/', '%2F').replace('.', '%2E')


async def snippet_to_embed(d, file_contents):
    """
    Given a regex groupdict and file contents, creates a code block
    """

    if d['end_line']:
        start_line = int(d['start_line'])
        end_line = int(d['end_line'])
    else:
        start_line = end_line = int(d['start_line'])

    split_file_contents = file_contents.split('\n')

    if start_line > end_line:
        start_line, end_line = end_line, start_line
    if start_line > len(split_file_contents) or end_line < 1:
        return ''
    start_line = max(1, start_line)
    end_line = min(len(split_file_contents), end_line)

    required = '\n'.join(split_file_contents[start_line - 1:end_line])
    required = textwrap.dedent(required).rstrip().replace('`', '`\u200b')

    language = d['file_path'].split('/')[-1].split('.')[-1]
    if not language.replace('-', '').replace('+', '').replace('_', '').isalnum():
        language = ''

    if len(required) != 0:
        return f'```{language}\n{required}```\n'
    return '``` ```\n'
