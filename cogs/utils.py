import os
import textwrap


def encode(s):
    """Encode URL Parameters"""
    return s.replace("/", "%2F").replace(".", "%2E")


async def fetch_http(session, url, response_format="text", **kwargs):
    """Uses aiohttp to make http GET requests"""

    async with session.get(url, **kwargs) as response:
        if response_format == "text":
            return await response.text()
        elif response_format == "json":
            return await response.json()


async def fetch_github_snippet(session, repo, path, start_line, end_line):
    """Fetches a snippet from a github repo"""

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

    file_contents = await fetch_http(
        session,
        f"https://api.github.com/repos/{repo}/contents/{file_path}?ref={ref}",
        "text",
        headers=headers,
    )

    return await snippet_to_embed(file_contents, file_path, start_line, end_line)


async def fetch_github_gist_snippet(session, gist_id, revision, file_path, start_line, end_line):
    """Fetches a snippet from a gist"""

    headers = {"Accept": "application/vnd.github.v3.raw"}
    if "GITHUB_TOKEN" in os.environ:
        headers["Authorization"] = f'token {os.environ["GITHUB_TOKEN"]}'

    gist_json = await fetch_http(
        session,
        f'https://api.github.com/gists/{gist_id}{f"/{revision}" if len(revision) > 0 else ""}',
        "json",
        headers=headers,
    )

    for gist_file in gist_json["files"]:
        if file_path == gist_file.lower().replace(".", "-"):
            file_contents = await fetch_http(
                session,
                gist_json["files"][gist_file]["raw_url"],
                "text",
            )

            return await snippet_to_embed(file_contents, gist_file, start_line, end_line)

    return ''


async def fetch_gitlab_snippet(session, repo, path, start_line, end_line):
    """Fetches a snippet from a gitlab repo"""

    headers = {}
    if "GITLAB_TOKEN" in os.environ:
        headers["PRIVATE-TOKEN"] = os.environ["GITLAB_TOKEN"]

    enc_repo = encode(repo)

    refs = (await fetch_http(session, f"https://gitlab.com/api/v4/projects/{enc_repo}/repository/branches", "json", headers=headers) +
            await fetch_http(session, f"https://gitlab.com/api/v4/projects/{enc_repo}/repository/tags", "json", headers=headers))

    ref = path.split("/")[0]
    file_path = "/".join(path.split("/")[1:])
    for possible_ref in refs:
        if path.startswith(possible_ref["name"] + "/"):
            ref = possible_ref["name"]
            file_path = path[len(ref) + 1:]
            break

    enc_ref = encode(ref)
    enc_file_path = encode(file_path)

    file_contents = await fetch_http(
        session,
        f"https://gitlab.com/api/v4/projects/{enc_repo}/repository/files/{enc_file_path}/raw?ref={enc_ref}",
        "text",
        headers=headers,
    )

    return await snippet_to_embed(file_contents, file_path, start_line, end_line)


async def fetch_bitbucket_snippet(session, repo, ref, file_path, start_line, end_line):
    """Fetches a snippet from a bitbucket repo"""

    file_contents = await fetch_http(
        session,
        f"https://bitbucket.org/{encode(repo)}/raw/{encode(ref)}/{encode(file_path)}",
        "text",
    )

    return await snippet_to_embed(file_contents, file_path, start_line, end_line)


async def snippet_to_embed(file_contents, file_path, start_line, end_line):
    """Given file contents, file path, start line and end line creates a code block"""

    if end_line is None:
        start_line = end_line = int(start_line)
    else:
        start_line = int(start_line)
        end_line = int(end_line)

    split_file_contents = file_contents.splitlines()

    if start_line > end_line:
        start_line, end_line = end_line, start_line
    if start_line > len(split_file_contents) or end_line < 1:
        return ""

    start_line = max(1, start_line)
    end_line = min(len(split_file_contents), end_line)

    required = "\n".join(split_file_contents[start_line - 1:end_line])
    required = textwrap.dedent(required).rstrip().replace("`", "`\u200b")

    language = file_path.split("/")[-1].split(".")[-1]
    if not language.replace("-", "").replace("+", "").replace("_", "").isalnum():
        language = ""

    if len(required) != 0:
        return f"```{language}\n{required}```\n"
    return "``` ```\n"
