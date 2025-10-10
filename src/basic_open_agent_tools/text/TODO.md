# Text Processing Module TODO

This document outlines planned enhancements for the text processing module to better support LLM-based agents with natural language tasks.

## Current Implementation Status (v0.15.0) ✅

### ✅ Core Text Processing (Complete - 10+ functions)
- [x] **Basic text cleaning**: `clean_whitespace()`, `normalize_line_endings()`
- [x] **Case conversions**: `to_snake_case()`, `to_camel_case()`, `to_title_case()`
- [x] **HTML processing**: `strip_html_tags()`
- [x] **Unicode normalization**: `normalize_unicode()`
- [x] **Text splitting**: `smart_split_lines()`, `extract_sentences()`
- [x] **List formatting**: `join_with_oxford_comma()`

### ✅ Google ADK Compliance (v0.15.0)
- [x] **Google ADK Function Tool Compliance**: Full compatibility with Google ADK standards
- [x] **Enhanced Test Coverage**: Achieved 96%+ test coverage with comprehensive testing
- [x] **Quality Assurance**: 100% ruff + mypy compliance across all functions
- [x] **Agent Framework Integration**: Verified compatibility with Google ADK, LangChain, and custom agents
- [x] **Comprehensive Testing Infrastructure**: Dual testing strategy (traditional + agent evaluation)
- [x] **Type Safety**: JSON-serializable types only, no defaults, consistent exception patterns
- [x] **Module Complete**: Complete testing and documentation

## Status: ✅ MODULE COMPLETE

The text processing module is **complete** with 10+ essential functions covering comprehensive text processing needs for AI agents. All functions are fully compliant with Google ADK standards and extensively tested.

## Planned Enhancements 📋 (Future Versions)

### High Priority - Advanced LLM Agent Features (Future)

#### 1. Template/Placeholder Processing
- [ ] **Variable substitution**: Support `${variable}`, `{{variable}}`, `{variable}` formats
- [ ] **Safe template rendering**: Validate variables and prevent injection
- [ ] **Conditional text blocks**: Handle if/else logic in templates
- [ ] **Nested variable support**: Complex object property access
- [ ] **Default value handling**: Fallback values for missing variables

#### 2. Text Similarity and Comparison
- [ ] **Fuzzy string matching**: Find approximate matches with configurable threshold
- [ ] **Text diff generation**: Character and word-level differences
- [ ] **Similarity scoring**: Multiple algorithms (Levenshtein, Jaccard, cosine)
- [ ] **Duplicate detection**: Identify similar or identical text blocks
- [ ] **Best match finding**: Select closest match from list of options

#### 3. Content Summarization and Analysis
- [ ] **Intelligent truncation**: Preserve meaning while reducing length
- [ ] **Key phrase extraction**: Identify important terms and concepts
- [ ] **Word frequency analysis**: Count and rank word usage
- [ ] **Text metrics**: Character/word/sentence counts, readability scores
- [ ] **Content classification**: Detect text type and structure

#### 4. Format Detection and Validation
- [ ] **Auto-format detection**: Identify markdown, JSON, XML, CSV, etc.
- [ ] **Structure validation**: Verify format compliance
- [ ] **Format conversion hints**: Suggest appropriate processing functions
- [ ] **Content type detection**: Distinguish between prose, lists, data, etc.

#### 5. Natural Language Helpers
- [ ] **Pluralization/singularization**: English language rules with exceptions
- [ ] **Number to word conversion**: "1" → "one", "21" → "twenty-one"
- [ ] **Word to number conversion**: "twenty-one" → "21"
- [ ] **Ordinal number handling**: "1st", "2nd", "3rd" conversions
- [ ] **Text normalization**: Standardize contractions, abbreviations

#### 6. Safe Text Processing
- [ ] **Context-aware escaping**: HTML, XML, JSON, CSV, regex escaping
- [ ] **Input sanitization**: Remove or escape potentially harmful content
- [ ] **Encoding handling**: Safe UTF-8, ASCII, Unicode conversions
- [ ] **Special character normalization**: Handle quotes, dashes, spaces
- [ ] **Content validation**: Check for malicious patterns

### Medium Priority - Extended Features

#### 7. Advanced Text Manipulation
- [ ] **Smart capitalization**: Handle proper nouns, acronyms, titles
- [ ] **Text expansion**: Expand abbreviations and contractions
- [ ] **Whitespace normalization**: Intelligent paragraph and spacing handling
- [ ] **Quote normalization**: Standardize quote marks and styles
- [ ] **List processing**: Extract and format various list types

#### 8. Language-Aware Processing
- [ ] **Language detection**: Identify text language automatically
- [ ] **Locale-aware formatting**: Numbers, dates, names by region
- [ ] **Character set validation**: Ensure appropriate encoding
- [ ] **Script detection**: Latin, Cyrillic, CJK, Arabic, etc.

#### 9. Content Structure Analysis
- [ ] **Paragraph detection**: Intelligent paragraph boundary identification
- [ ] **Heading extraction**: Identify and rank heading levels
- [ ] **List structure parsing**: Detect numbered, bulleted, nested lists
- [ ] **Table detection**: Identify tabular data in plain text
- [ ] **Citation parsing**: Extract and format references

### Low Priority - Nice-to-Have Features

#### 10. Advanced Analytics
- [ ] **Reading time estimation**: Calculate approximate reading duration
- [ ] **Complexity scoring**: Assess text difficulty level
- [ ] **Sentiment indicators**: Basic positive/negative/neutral detection
- [ ] **Keyword density**: Calculate term frequency and distribution

#### 11. Specialized Formatting
- [ ] **Bibliography formatting**: Various citation styles
- [ ] **Address parsing**: Extract and validate postal addresses
- [ ] **Phone number formatting**: International number standardization
- [ ] **URL processing**: Extract, validate, and normalize web addresses

## Implementation Guidelines

### Design Principles
1. **Agent-First Design**: Functions optimized for LLM agent workflows
2. **Safety-Focused**: Prevent injection attacks and handle malformed input
3. **Performance-Aware**: Efficient processing for large text volumes
4. **Configurable**: Allow customization of behavior and parameters
5. **Composable**: Functions work well together in processing pipelines

### Technical Requirements
- **Type Safety**: Full type annotations for all functions
- **Error Handling**: Comprehensive validation and clear error messages
- **Documentation**: Agent-focused docstrings with practical examples
- **Testing**: 70%+ test coverage with edge case handling
- **Dependencies**: Prefer Python stdlib, minimize external requirements

### Function Naming Conventions
- Use clear, descriptive names that indicate purpose
- Follow existing patterns: `action_target()` format
- Group related functions logically
- Maintain consistency with current module style

## Integration Notes

### Helper Function Updates
New functions will be automatically included in:
- `load_all_text_tools()` helper function
- Module `__all__` exports
- Agent framework integrations

### Backward Compatibility
- All additions maintain 100% backward compatibility
- No breaking changes to existing function signatures
- Deprecated functions marked clearly with migration paths

## Priority Implementation Order

1. **Template processing** - Critical for dynamic content generation
2. **Text similarity** - Essential for matching and comparison tasks
3. **Smart truncation** - Important for handling context length limits
4. **Safe text processing** - Security and reliability improvements
5. **Natural language helpers** - Enhanced language understanding
6. **Format detection** - Better content type handling

---

*This TODO reflects the needs of LLM-based agents working with natural language processing tasks.*