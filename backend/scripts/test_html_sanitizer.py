from app.services.html_sanitizer import sanitize_html


test_cases = {
    "script": "<p>Hello</p><script>alert('xss')</script>",
    "image_event": '<img src="x" onerror="alert(1)">',
    "javascript_link": '<a href="javascript:alert(1)">Click me</a>',
    "event_handler": '<p onclick="alert(1)">Hello</p>',
    "valid_html": """
        <h1>Growth Strategy</h1>
        <p>This is a <strong>valid</strong> paragraph.</p>
        <ul>
            <li>First point</li>
            <li>Second point</li>
        </ul>
        <a href="https://example.com" title="Example">Source</a>
        <pre><code>const x = 10;</code></pre>
    """,
}


for name, content in test_cases.items():
    print(f"\n--- {name} ---")
    print(sanitize_html(content))
