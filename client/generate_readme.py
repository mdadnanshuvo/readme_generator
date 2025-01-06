import re

def text_to_markdown(text):
    """
    Converts plain text into Markdown syntax by intelligently identifying and formatting:
    - Headings
    - Lists
    - Code blocks
    - Inline code
    - Paragraphs
    - Hyperlinks and images (if any)
    """
    markdown = []
    lines = text.split("\n")
    in_code_block = False

    for line in lines:
        line = line.strip()

        # Handle Headings
        if line.lower().startswith("introduction"):
            markdown.append("# Introduction")
        elif line.lower().startswith("installation"):
            markdown.append("## Installation")
        elif line.lower().startswith("usage"):
            markdown.append("## Usage")
        elif line.lower().startswith("license"):
            markdown.append("## License")
        elif line.lower().startswith("authors") or line.lower().startswith("credits"):
            markdown.append("## Authors")
        elif line.lower().startswith("acknowledgments"):
            markdown.append("## Acknowledgments")
        elif line.lower().startswith("features"):
            markdown.append("## Features")
        elif line.lower().startswith("how to contribute"):
            markdown.append("## How to Contribute")
        elif line.lower().startswith("tests"):
            markdown.append("## Tests")

        # Handle Bullet Points
        elif re.match(r"^\s*[-*•]\s", line):
            markdown.append(f"- {line.lstrip('-*• ')}")

        # Handle Inline Code
        elif re.match(r"^\s*`.*`$", line):
            markdown.append(f"`{line.strip('`')}`")

        # Handle Code Blocks
        elif line.startswith("    ") or line.startswith("```"):
            if not in_code_block:
                markdown.append("```")
                in_code_block = True
            markdown.append(line.strip())
        elif in_code_block:
            markdown.append("```")
            in_code_block = False

        # Handle URLs and Images
        elif re.match(r"(http|https)://[^\s]+", line):
            markdown.append(f"[{line}]({line})")

        # Handle Paragraphs
        elif line:
            markdown.append(line)

        # Add Blank Line for Spacing
        else:
            markdown.append("")

    # Close any unclosed code block
    if in_code_block:
        markdown.append("```")

    return "\n".join(markdown)


def generate_readme_from_plain_text(plain_text):
    """
    Process plain text content into a properly formatted Markdown README file.
    """
    markdown_content = text_to_markdown(plain_text)

    # Save the formatted Markdown content to README.md
    with open("README.md", "w") as file:
        file.write(markdown_content)

    print("README.md generated successfully with Markdown syntax!")


if __name__ == "__main__":
    # Example plain text input (this would come from AI-generated content)
    plain_text_input = """
    Introduction
    This is a Python project that integrates Flask and Transformers.

    Installation
    - Clone the repository
    - Install dependencies
    - Run the setup script

    Usage
    - Start the Flask server
    - Access the API at http://127.0.0.1:5000

    License
    This project is licensed under the MIT License.

    Authors
    - John Doe (GitHub: johndoe)
    - Jane Smith (GitHub: janesmith)

    Acknowledgments
    Special thanks to the open-source community.
    """

    # Generate README from the plain text input
    generate_readme_from_plain_text(plain_text_input)
