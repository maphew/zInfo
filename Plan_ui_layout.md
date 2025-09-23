### **📋 Plan Summary**

Guidelines for this plan:

- use @/reference/llms-ctx.txt for FastHTML docs. 

- After implementing functionality or resolving problems, run the tests for that unit of code that was improved. If functionality is missing then it's your job to add it as per the application specifications. Think hard.

- When you discover an issue, immediately update @/tickets with your findings using a subagent. When the issue is resolved, update @/tickets and mark closed.

- When the tests pass, update @/tickets, then add changed code and ticket with "git add -A" via bash, then do a "git commit" with a message that describes the changes you made to the code. After the commit, do a "git push" to push the changes to the remote repository.

- FIND THE SIMPLEST SOLUTION - Look for the cleanest, most elegant fix that leverages existing infrastructure.

- NO OVER-ENGINEERING - Avoid complex new systems, multiple file changes, or unnecessary abstractions unless absolutely necessary.

- LEVERAGE WHAT EXISTS - Use existing patterns, functions, and infrastructure rather than building new things.

- Commit after completing each subtask and task.

Ensure the plan is iterative, starting with core UI components, integrating FastHTML seamlessly, and prioritizing user experience while adhering to zinfo's existing architecture. Document all steps, assumptions, and potential risks in the plan.


**🎯 New Layout Design:**
- **Search form**: Centered at the top of the page
- **Scan form**: Compact version positioned in the upper right corner
- **Results**: Displayed directly below the search form
- **Layout method**: CSS Grid for main structure with Flexbox for component alignment

### **🔧 Key Implementation Components**

1. **Compact Scan Form** - Reduced from large fieldset to streamlined version:
   - Condensed input fields with minimal help text
   - Horizontal layout for space efficiency
   - Maintained all functionality (profiles, validation, status)

2. **Grid-Based Layout Structure**:
   - Header area: Search form (center) + Scan form (right)
   - Main content area: Results below search form
   - Responsive breakpoints for mobile/tablet/desktop

3. **Enhanced Styling**:
   - Improved visual hierarchy with better spacing
   - Professional color scheme and typography
   - Card-based design for better organization
   - Subtle shadows and borders for depth

4. **Responsive Design**:
   - Mobile: Stacked vertical layout
   - Tablet: Adjusted spacing and sizing
   - Desktop: Full planned layout with optimal positioning

### **⚡ Technical Considerations**

- **HTMX Compatibility**: All existing interactions preserved
- **JavaScript**: Updated for new layout structure
- **Performance**: Maintained efficient DOM updates
- **Accessibility**: Preserved form labels and ARIA attributes

### **🧪 Testing Requirements**

**Layout Testing:**
- Verify positioning on different screen sizes
- Test responsive breakpoints
- Check form usability in compact mode

**Functionality Testing:**
- Search with various parameters
- Scan with different profiles and directories
- Results display and pagination
- Detail view interactions
- Error handling scenarios

### **🚀 Next Steps**

To implement this plan:

1. **Switch to Code Mode** to make the actual changes to `src/zinfo/ui/fh_ui.py`
2. **Apply the layout restructuring** as outlined in the plan
3. **Test thoroughly** across different devices and browsers
4. **Iterate based on user feedback** for any refinements needed

The plan maintains all existing functionality while improving the visual layout to match your mockup design. The compact scan form in the upper right, centered search form, and results positioned directly below the search form will create a more intuitive user interface.
