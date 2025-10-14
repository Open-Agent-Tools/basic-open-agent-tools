# Markdown Module TODO

## Planned Enhancements

### High Priority

#### Enhanced HTML Conversion
- [ ] Support for blockquotes
- [ ] Support for horizontal rules
- [ ] Support for task lists
- [ ] Support for tables in HTML output
- [ ] Proper escaping of HTML entities

#### Advanced Parsing
- [ ] Parse reference-style links
- [ ] Parse footnotes
- [ ] Parse definition lists
- [ ] Parse task lists with checkboxes
- [ ] Extract image references

### Medium Priority

#### GFM (GitHub Flavored Markdown) Support
- [ ] Strikethrough (~~text~~)
- [ ] Task lists ([x] and [ ])
- [ ] Automatic URL linking
- [ ] Emoji support
- [ ] Table alignment parsing

#### Generation Enhancements
- [ ] Generate reference-style links
- [ ] Generate footnotes
- [ ] Generate definition lists
- [ ] Generate blockquotes
- [ ] Generate horizontal rules

### Low Priority

#### Conversion Features
- [ ] Markdown to JSON structure
- [ ] JSON to Markdown
- [ ] Markdown to reStructuredText
- [ ] HTML to Markdown

#### Validation
- [ ] Lint Markdown for common issues
- [ ] Check broken links
- [ ] Validate frontmatter schema
- [ ] Check heading hierarchy

#### Advanced Features
- [ ] Table of contents generation
- [ ] Anchor link generation
- [ ] Cross-reference checking
- [ ] Template rendering

## Testing Requirements

### Unit Tests Needed
- [ ] Test all parsing functions with various formats
- [ ] Test generation functions with edge cases
- [ ] Test HTML conversion accuracy
- [ ] Test error handling for malformed Markdown
- [ ] Test file size limits
- [ ] Test permission handling

### Integration Tests
- [ ] Test complete workflows (parse -> modify -> generate)
- [ ] Test with real-world Markdown files
- [ ] Test with agent frameworks
- [ ] Performance benchmarks with large files

## Documentation Improvements
- [ ] Add more usage examples
- [ ] Create tutorial for common workflows
- [ ] Document Markdown flavor support
- [ ] Add troubleshooting guide

## Version History
- v0.13.0: Initial Markdown module implementation (12 functions)
  - Parsing: 6 functions
  - Generation: 6 functions
  - No external dependencies
