from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass


@dataclass(frozen=True)
class Language:
    key: str
    label: str
    names: tuple[str, ...]  # first entry is the canonical extension; all are accepted
    files: Callable[[str], dict[str, str]]
    gitignore: str = ""
    post: tuple[tuple[str, ...], ...] = ()  # commands run inside the new project

    @property
    def extension(self) -> str:
        return self.names[0]


def _single(filename: str, template: str) -> Callable[[str], dict[str, str]]:
    return lambda name: {filename: template.replace("@NAME@", name)}


_PY = '''# @NAME@


def main() -> None:
    # Write your code here
    pass


if __name__ == "__main__":
    main()
'''

_JAVA = """// @NAME@

import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner scanner = new Scanner(System.in);

        // Write your code here

        scanner.close();
    }
}
"""

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>@NAME@</title>
    <link rel="stylesheet" href="style.css">
    <script src="index.js" defer></script>
</head>
<body>
    <!-- Write your code here -->
</body>
</html>
"""

_CPP = """// @NAME@

#include <iostream>

int main() {
    // Write your code here
    return 0;
}
"""

_GO = """// @NAME@

package main

func main() {
	// Write your code here
}
"""

_CS = """// @NAME@

using System;

class Program
{
    static void Main(string[] args)
    {
        // Write your code here
    }
}
"""


def _web(name: str) -> dict[str, str]:
    return {"index.html": _HTML.replace("@NAME@", name), "index.js": "", "style.css": ""}


LANGUAGES: tuple[Language, ...] = (
    Language("python", "Python", ("py", "python"), _single("main.py", _PY),
             gitignore="__pycache__/\n*.pyc\n.venv/\ndist/\n"),
    Language("javascript", "JavaScript", ("js", "javascript", "nodejs", "node"),
             _single("index.js", "// @NAME@\n"),
             gitignore="node_modules/\n", post=(("npm", "init", "-y"),)),
    Language("typescript", "TypeScript", ("ts", "typescript"),
             _single("main.ts", "// @NAME@\n"), gitignore="node_modules/\n"),
    Language("java", "Java", ("java",), _single("Main.java", _JAVA), gitignore="*.class\n"),
    Language("web", "Web (HTML/CSS/JS)", ("html", "css", "web"), _web),
    Language("rust", "Rust", ("rs", "rust"), lambda _name: {},
             gitignore="/target\n",
             post=(("cargo", "init", "--vcs", "none", "--name", "{name}"),)),
    Language("cpp", "C++", ("cpp", "c++"), _single("main.cpp", _CPP),
             gitignore="a.out\n*.o\n*.exe\n"),
    Language("go", "Go", ("go",), _single("main.go", _GO),
             post=(("go", "mod", "init", "{name}"),)),
    Language("csharp", "C#", ("cs", "c#", "csharp"), _single("Program.cs", _CS),
             gitignore="bin/\nobj/\n"),
)

_LOOKUP: dict[str, Language] = {n: lang for lang in LANGUAGES for n in lang.names}


def find_language(token: str) -> Language | None:
    return _LOOKUP.get(token.lower())