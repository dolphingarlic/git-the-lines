import textwrap

async def fetch_http(session, url, response_format='text', **kwargs):
    """Uses aiohttp to make http GET requests"""

    async with session.get(url, **kwargs) as response:
        if response_format == 'text':
            return await response.text()
        elif response_format == 'json':
            return await response.json()


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


async def create_message(d, file_contents):
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