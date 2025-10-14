# Excel Module TODO

## Planned Enhancements

### High Priority

#### Charts and Graphs
- [ ] Create bar charts
- [ ] Create line charts
- [ ] Create pie charts
- [ ] Create scatter plots
- [ ] Extract chart data
- [ ] Modify existing charts

#### Conditional Formatting
- [ ] Apply color scales
- [ ] Apply data bars
- [ ] Apply icon sets
- [ ] Custom conditional formatting rules
- [ ] Extract conditional formatting

#### Data Validation
- [ ] Add dropdown lists
- [ ] Set number range validation
- [ ] Set date validation
- [ ] Set text length validation
- [ ] Custom validation formulas

### Medium Priority

#### Pivot Tables
- [ ] Create pivot tables
- [ ] Modify pivot table structure
- [ ] Extract pivot table data
- [ ] Refresh pivot tables

#### Images and Shapes
- [ ] Insert images
- [ ] Extract images
- [ ] Resize/position images
- [ ] Add shapes and text boxes
- [ ] Extract shape properties

#### Advanced Formulas
- [ ] Array formulas support
- [ ] Named ranges
- [ ] Formula auditing (precedents/dependents)
- [ ] Evaluate formulas programmatically

#### Filtering and Sorting
- [ ] Apply autofilter
- [ ] Set filter criteria
- [ ] Sort columns
- [ ] Extract filtered data

### Low Priority

#### Protection and Security
- [ ] Password protect workbooks
- [ ] Password protect sheets
- [ ] Restrict cell editing
- [ ] Remove protection

#### Workbook Operations
- [ ] Copy sheets between workbooks
- [ ] Merge multiple workbooks
- [ ] Split workbook into multiple files
- [ ] Compare two workbooks

#### Advanced Styling
- [ ] Cell borders and styles
- [ ] Number formatting (currency, percentage, etc.)
- [ ] Date/time formatting
- [ ] Custom cell styles
- [ ] Theme colors

#### Comments and Notes
- [ ] Add cell comments
- [ ] Extract comments
- [ ] Threaded comments support
- [ ] Add cell notes

#### Hyperlinks
- [ ] Add hyperlinks to cells
- [ ] Extract hyperlinks
- [ ] Link to other sheets/workbooks
- [ ] Link to external URLs

#### Print Settings
- [ ] Set print area
- [ ] Set page breaks
- [ ] Configure page setup
- [ ] Set headers/footers

## Testing Requirements

### Unit Tests Needed
- [ ] Test all reading functions with various file formats
- [ ] Test creation functions with edge cases
- [ ] Test formatting functions with different styles
- [ ] Test error handling for all functions
- [ ] Test with corrupted files
- [ ] Test file size limits
- [ ] Test permission handling
- [ ] Test formula evaluation

### Integration Tests
- [ ] Test complete workflows (read -> modify -> write)
- [ ] Test with real-world spreadsheets
- [ ] Test with agent frameworks (Google ADK, LangChain)
- [ ] Performance benchmarks with large files
- [ ] Test multi-sheet operations
- [ ] Test formula dependencies

## Documentation Improvements
- [ ] Add more usage examples
- [ ] Create tutorial for common workflows
- [ ] Document performance characteristics
- [ ] Add troubleshooting guide
- [ ] Document Excel version compatibility

## Version History
- v0.13.0: Initial Excel module implementation (24 functions)
  - Reading: 8 functions
  - Writing: 8 functions
  - Formatting: 8 functions
