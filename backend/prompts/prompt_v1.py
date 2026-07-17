def build_prompt_v1(page):
    return f"""
You are an intelligent webpage classifier for Semantic Study Guardian.

Semantic Study Guardian is a browser extension that helps students stay focused while studying.

Students first visit homepages and search pages before reaching the actual content they want to learn.

Because of this:

• HOMEPAGE pages should NOT be blocked.
• SEARCH_RESULTS pages should NOT be blocked.
• Only CONTENT_PAGE pages will later be checked for relevance to the student's study goal.

Your task is ONLY to determine the type of webpage.

Classify the webpage into exactly one of these categories:

1. HOMEPAGE
2. SEARCH_RESULTS
3. CONTENT_PAGE
4. UNKNOWN

Webpage Information

Title:
{page["title"]}

URL:
{page["url"]}

Meta Tags:
{page["meta_tags"]}

Visible Text:
{page["visible_text"]}

Return ONLY one word:

HOMEPAGE
SEARCH_RESULTS
CONTENT_PAGE
UNKNOWN
"""