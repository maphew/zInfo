# Search Form Redesign Plan

## Current State Analysis
The current search form has 7 separate input fields:
- Title
- Shortname
- Client
- Team
- Author
- Type
- Dir ID

This creates a cluttered interface that takes up significant vertical space.

## Proposed Design
**Single Input + Field Selection Approach:**
1. **Single search input** - One text field where users enter their search term
2. **Field selection checkboxes** - Checkboxes to enable/disable which fields to search in
3. **Clean, compact layout** - Better use of space and improved UX

## Implementation Details

### Frontend Changes (UI)
- Replace 7 input fields with 1 search input field
- Add 7 checkboxes for field selection (title, shortname, client, team, author, type, dir_id)
- Style checkboxes in a horizontal flex layout for better space utilization
- Default all checkboxes to checked (search all fields by default)
- Add clear labels for each checkbox

### Backend Changes (Search Logic)
- Update `/search` route to accept new parameters:
  - `query` - the search term
  - `search_title`, `search_shortname`, `search_client`, etc. - boolean flags for enabled fields
- Modify search logic to only search in enabled fields
- Update parameter validation for new structure
- Maintain backward compatibility considerations

### User Experience Considerations
- **Progressive disclosure** - Simple by default, advanced options visible
- **Visual feedback** - Clear indication of which fields are being searched
- **Accessibility** - Proper labels and keyboard navigation
- **Mobile responsive** - Checkboxes should work well on mobile devices

## Technical Implementation Steps

1. **Update search form HTML structure** in the index route
2. **Modify search route parameters** to handle new structure
3. **Update search logic** to conditionally search only enabled fields
4. **Update parameter validation** for new parameters
5. **Test the implementation** with various search scenarios

## Benefits of This Approach
- **Cleaner interface** - Less visual clutter
- **Better space utilization** - More compact form
- **Flexible searching** - Users can choose exactly which fields to search
- **Progressive enhancement** - Simple search by default, advanced options available
- **Mobile friendly** - Better responsive design

## Potential Edge Cases to Consider
- What happens when no fields are selected?
- How to handle empty search queries
- Performance implications of searching multiple fields
- User expectations when switching between field selections


When plan implementation is complete AND approved,
- move to @history/Plan_ui-one-search-box.md
- Commit changes
