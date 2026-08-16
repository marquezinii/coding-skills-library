---
name: markdown-to-html
description: 'Convert Markdown files to HTML similar to `marked.js`, `pandoc`, `gomarkdown/markdown`, or similar tools; or writing custom script to convert markdown to html and/or working on web template systems like `jekyll/jekyll`, `gohugoio/hugo`, or similar web templating systems that utilize markdown documents, converting them to html. Use when asked to "convert markdown to html", "transform md to html", "render markdown", "generate html from markdown", or when working with .md files and/or web a templating system that converts markdown to HTML output. Supports CLI and Node.js workflows with GFM, CommonMark, and standard Markdown flavors.'
---

# Markdown to HTML Conversion

Expert skill for converting Markdown documents to HTML using the marked.js library, or writing data conversion scripts; in this case scripts similar to [markedJS/marked](https://github.com/markedjs/marked) repository. For custom scripts knowledge is not confined to `marked.js`, but data conversion methods are utilized from tools like [pandoc](https://github.com/jgm/pandoc) and [gomarkdown/markdown](https://github.com/gomarkdown/markdown) for data conversion; [jekyll/jekyll](https://github.com/jekyll/jekyll) and [gohugoio/hugo](https://github.com/gohugoio/hugo) for templating systems.

The conversion script or tool should handle single files, batch conversions, and advanced configurations.

## When to Use This Skill

- User asks to "convert markdown to html" or "transform md files"
- User wants to "render markdown" as HTML output
- User needs to generate HTML documentation from .md files
- User is building static sites from Markdown content
- User is building template system that converts markdown to html
- User is working on a tool, widget, or custom template for an existing templating system
- User wants to preview Markdown as rendered HTML

## Converting Markdown to HTML

### Essential Basic Conversions

For more see [basic-markdown-to-html.md](references/basic-markdown-to-html.md)

```text
    ```markdown
    # Level 1
    ## Level 2

    One sentence with a [link](https://example.com), and a HTML snippet like `<p>paragraph tag</p>`.

    - `ul` list item 1
    - `ul` list item 2

    1. `ol` list item 1
    2. `ol` list item 1

    | Table Item | Description |
    | One | One is the spelling of the number `1`. |
    | Two | Two is the spelling of the number `2`. |

    ```js
    var one = 1;
    var two = 2;

    function simpleMath(x, y) {
     return x + y;
    }
    console.log(simpleMath(one, two));
    ```
    ```

    ```html
    <h1>Level 1</h1>
    <h2>Level 2</h2>

    <p>One sentence with a <a href="https://example.com">link</a>, and a HTML snippet like <code>&lt;p&gt;paragraph tag&lt;/p&gt;</code>.</p>

    <ul>
     <li>`ul` list item 1</li>
     <li>`ul` list item 2</li>
    </ul>

    <ol>
     <li>`ol` list item 1</li>
     <li>`ol` list item 2</li>
    </ol>

    <table>
     <thead>
      <tr>
       <th>Table Item</th>
       <th>Description</th>
      </tr>
     </thead>
     <tbody>
      <tr>
       <td>One</td>
       <td>One is the spelling of the number `1`.</td>
      </tr>
      <tr>
       <td>Two</td>
       <td>Two is the spelling of the number `2`.</td>
      </tr>
     </tbody>
    </table>

    <pre>
     <code>var one = 1;
     var two = 2;

     function simpleMath(x, y) {
      return x + y;
     }
     console.log(simpleMath(one, two));</code>
    </pre>
    ```
```

### Code Block Conversions

For more see [code-blocks-to-html.md](references/code-blocks-to-html.md)

```text

    ```markdown
    your code here
    ```

    ```html
    <pre><code class="language-md">
    your code here
    </code></pre>
    ```

    ```js
    console.log("Hello world");
    ```

    ```html
    <pre><code class="language-js">
    console.log("Hello world");
    </code></pre>
    ```

    ```markdown
      ```

      ```
      visible backticks
      ```

      ```
    ```

    ```html
      <pre><code>
      ```

      visible backticks

      ```
      </code></pre>
    ```
```

### Collapsed Section Conversions

For more see [collapsed-sections-to-html.md](references/collapsed-sections-to-html.md)

```text
    ```markdown
    <details>
    <summary>More info</summary>

    ### Header inside

    - Lists
    - **Formatting**
    - Code blocks

        ```js
        console.log("Hello");
        ```

    </details>
    ```

    ```html
    <details>
    <summary>More info</summary>

    <h3>Header inside</h3>

    <ul>
     <li>Lists</li>
     <li><strong>Formatting</strong></li>
     <li>Code blocks</li>
    </ul>

    <pre>
     <code class="language-js">console.log("Hello");</code>
    </pre>

    </details>
    ```
```

### Mathematical Expression Conversions

For more see [writing-mathematical-expressions-to-html.md](references/writing-mathematical-expressions-to-html.md)

```text
    ```markdown
    This sentence uses `$` delimiters to show math inline: $\sqrt{3x-1}+(1+x)^2$
    ```

    ```html
    <p>This sentence uses <code>$</code> delimiters to show math inline:
     <math-renderer><math xmlns="http://www.w3.org/1998/Math/MathML">
      <msqrt><mn>3</mn><mi>x</mi><mo>−</mo><mn>1</mn></msqrt>
      <mo>+</mo><mo>(</mo><mn>1</mn><mo>+</mo><mi>x</mi>
      <msup><mo>)</mo><mn>2</mn></msup>
     </math>
    </math-renderer>
    </p>
    ```

    ```markdown
    **The Cauchy-Schwarz Inequality**\
    $$\left( \sum_{k=1}^n a_k b_k \right)^2 \leq \left( \sum_{k=1}^n a_k^2 \right) \left( \sum_{k=1}^n b_k^2 \right)$$
    ```

    ```html
    <p><strong>The Cauchy-Schwarz Inequality</strong><br>
     <math-renderer>
      <math xmlns="http://www.w3.org/1998/Math/MathML">
       <msup>
        <mrow><mo>(</mo>
         <munderover><mo data-mjx-texclass="OP">∑</mo>
          <mrow><mi>k</mi><mo>=</mo><mn>1</mn></mrow><mi>n</mi>
         </munderover>
         <msub><mi>a</mi><mi>k</mi></msub>
         <msub><mi>b</mi><mi>k</mi></msub>
         <mo>)</mo>
        </mrow>
        <mn>2</mn>
       </msup>
       <mo>≤</mo>
       <mrow><mo>(</mo>
        <munderover><mo>∑</mo>
         <mrow><mi>k</mi><mo>=</mo><mn>1</mn></mrow>
         <mi>n</mi>
        </munderover>
        <msubsup><mi>a</mi><mi>k</mi><mn>2</mn></msubsup>
        <mo>)</mo>
       </mrow>
       <mrow><mo>(</mo>
         <munderover><mo>∑</mo>
          <mrow><mi>k</mi><mo>=</mo><mn>1</mn></mrow>
          <mi>n</mi>
         </munderover>
         <msubsup><mi>b</mi><mi>k</mi><mn>2</mn></msubsup>
         <mo>)</mo>
       </mrow>
      </math>
     </math-renderer></p>
    ```
```

### Table Conversions

For more see [tables-to-html.md](references/tables-to-html.md)

```text
    ```markdown
    | First Header  | Second Header |
    | ------------- | ------------- |
    | Content Cell  | Content Cell  |
    | Content Cell  | Content Cell  |
    ```

    ```html
    <table>
     <thead><tr><th>First Header</th><th>Second Header</th></tr></thead>
     <tbody>
      <tr><td>Content Cell</td><td>Content Cell</td></tr>
      <tr><td>Content Cell</td><td>Content Cell</td></tr>
     </tbody>
    </table>
    ```

    ```markdown
    | Left-aligned | Center-aligned | Right-aligned |
    | :---         |     :---:      |          ---: |
    | git status   | git status     | git status    |
    | git diff     | git diff       | git diff      |
    ```

    ```html
    <table>
      <thead>
       <tr>
        <th align="left">Left-aligned</th>
        <th align="center">Center-aligned</th>
        <th align="right">Right-aligned</th>
       </tr>
      </thead>
      <tbody>
       <tr>
        <td align="left">git status</td>
        <td align="center">git status</td>
        <td align="right">git status</td>
       </tr>
       <tr>
        <td align="left">git diff</td>
        <td align="center">git diff</td>
        <td align="right">git diff</td>
       </tr>
      </tbody>
    </table>
    ```
```

## Working with [`markedJS/marked`](references/marked.md)

### Prerequisites

- Node.js installed (for CLI or programmatic usage)
- Install marked globally for CLI: `npm install -g marked`
- Or install locally: `npm install marked`

### Quick Conversion Methods

See [marked.md](references/marked.md) **Quick Conversion Methods**

### Step-by-Step Workflows

See [marked.md](references/marked.md) **Step-by-Step Workflows**

### CLI Configuration

### Using Config Files

Create `~/.marked.json` for persistent options:

```json
{
  "gfm": true,
  "breaks": true
}
```

Or use a custom config:

```bash
marked -i input.md -o output.html -c config.json
```

### CLI Options Reference

| Option | Description |
|--------|-------------|
| `-i, --input <file>` | Input Markdown file |
| `-o, --output <file>` | Output HTML file |
| `-s, --string <string>` | Parse string instead of file |
| `-c, --config <file>` | Use custom config file |
| `--gfm` | Enable GitHub Flavored Markdown |
| `--breaks` | Convert newlines to `<br>` |
| `--help` | Show all options |

### Security Warning

⚠️ **Marked does NOT sanitize output HTML.** For untrusted input, use a sanitizer:

```javascript
import { marked } from 'marked';
import DOMPurify from 'dompurify';

const unsafeHtml = marked.parse(untrustedMarkdown);
const safeHtml = DOMPurify.sanitize(unsafeHtml);
```

Recommended sanitizers:

- [DOMPurify](https://github.com/cure53/DOMPurify) (recommended)
- [sanitize-html](https://github.com/apostrophecms/sanitize-html)
- [js-xss](https://github.com/leizongmin/js-xss)

### Supported Markdown Flavors

| Flavor | Support |
|--------|---------|
| Original Markdown | 100% |
| CommonMark 0.31 | 98% |
| GitHub Flavored Markdown | 97% |

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Special characters at file start | Strip zero-width chars: `content.replace(/^[\u200B\u200C\u200D\uFEFF]/,"")` |
| Code blocks not highlighting | Add a syntax highlighter like highlight.js |
| Tables not rendering | Ensure `gfm: true` option is set |
| Line breaks ignored | Set `breaks: true` in options |
| XSS vulnerability concerns | Use DOMPurify to sanitize output |


## Extended guidance

Detailed sections were moved without removing content. Load only the sections needed for the current task:

- [Working with [`pandoc`](references/pandoc.md)](references/extended-guidance.md#working-with-pandocreferencespandocmd)
- [Working with [`gomarkdown/markdown`](references/gomarkdown.md)](references/extended-guidance.md#working-with-gomarkdownmarkdownreferencesgomarkdownmd)
- [Working with [`jekyll`](references/jekyll.md)](references/extended-guidance.md#working-with-jekyllreferencesjekyllmd)
- [Working with [`hugo`](references/hugo.md)](references/extended-guidance.md#working-with-hugoreferenceshugomd)
- [References](references/extended-guidance.md#references)

