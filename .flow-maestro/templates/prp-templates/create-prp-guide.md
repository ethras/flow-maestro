# PRP Creation Guide - Flow Maestro MCP

## PRP Creation Mission

Create a comprehensive PRP that enables **one-pass implementation success** through systematic research and context curation.

**Critical Understanding**: The executing AI agent only receives:
- The PRP content you create
- Its training data knowledge
- Access to codebase files (but needs guidance on which ones)

**Therefore**: Your research and context curation directly determines implementation success. Incomplete context = implementation failure.

## Research Process

### 1. Codebase Analysis

**Deep Codebase Investigation:**
- Search the codebase for similar features/patterns
- Identify all necessary files to reference in the PRP
- Note all existing conventions to follow
- Check existing test patterns for validation approach
- Use codebase-retrieval tool extensively to understand patterns

**Key Areas to Investigate:**
- Component patterns and structures
- API route implementations
- Database schema and migration patterns
- Testing approaches and utilities
- Configuration and environment setup
- Build and deployment processes

### 2. External Research (Context7 Integration)

**Library Documentation Research:**
- Use Context7 MCP for specific library documentation
- Focus on the exact features/patterns needed for implementation
- Include specific URLs with section anchors
- Document version-specific gotchas and requirements

**Research Strategy:**
- Start with primary framework/library (e.g., Next.js, React)
- Research supporting libraries as needed
- Focus on implementation patterns, not general concepts
- Capture specific code examples and patterns

### 3. Context Gathering Integration

**Leverage Flow Maestro's context_gathering mode:**
- Use existing context_gathering patterns for research
- Integrate Context7 findings into the research process
- Document all findings in structured format
- Ensure context completeness before proceeding

## PRP Generation Process

### Step 1: Choose Template

The PRP template will be provided by the Flow Maestro MCP `create_prp` tool response. The template contains all necessary sections and formatting optimized for Flow Maestro MCP integration.

### Step 2: Context Completeness Validation

Before writing, apply the **"No Prior Knowledge" test**:
_"If someone knew nothing about this codebase, would they have everything needed to implement this successfully?"_

### Step 3: Research Integration

Transform your research findings into the template sections:

**Goal Section**: Use research to define specific, measurable Feature Goal and concrete Deliverable
**Context Section**: Populate YAML structure with your research findings - specific URLs, file patterns, gotchas
**Implementation Tasks**: Create dependency-ordered tasks using information-dense keywords from codebase analysis
**Validation Gates**: Use project-specific validation commands that you've verified work in this codebase

### Step 4: Information Density Standards

Ensure every reference is **specific and actionable**:

- URLs include section anchors, not just domain names
- File references include specific patterns to follow, not generic mentions
- Task specifications include exact naming conventions and placement
- Validation commands are project-specific and executable
- Context7 configurations specify exact library names and topics

### Step 5: Flow Maestro Integration

**Context7 Configuration:**
```yaml
context7_config:
  libraryName: "[Exact Library Name]"  # e.g., "Next.js", "React", "TypeScript"
  topic: "[Specific Topic]"            # e.g., "app-router", "hooks", "generics"
  tokens: 2000                         # Appropriate token budget
```

**Integration Points:**
- Reference existing protocol assets where applicable
- Use established comment templates and headings
- Follow Linear-first principles for task management
- Integrate with existing quality gates and validation patterns

## Output Guidelines

### File Naming and Location

**Default Location**: `work/prps/`
**Filename Pattern**: `{feature-name}-prp.md` or `{timestamp}-{feature-name}-prp.md`

**Directory Structure Creation:**
```bash
# Ensure directory exists
mkdir -p work/prps
```

### PRP Quality Gates

#### Context Completeness Check

- [ ] Passes "No Prior Knowledge" test
- [ ] All YAML references are specific and accessible
- [ ] Implementation tasks include exact naming and placement guidance
- [ ] Validation commands are project-specific and verified working
- [ ] Context7 configurations are properly specified

#### Template Structure Compliance

- [ ] All required template sections completed
- [ ] Goal section has specific Feature Goal, Deliverable, Success Definition
- [ ] Implementation Tasks follow dependency ordering
- [ ] Final Validation Checklist is comprehensive

#### Information Density Standards

- [ ] No generic references - all are specific and actionable
- [ ] File patterns point at specific examples to follow
- [ ] URLs include section anchors for exact guidance
- [ ] Task specifications use information-dense keywords from codebase
- [ ] Context7 integration properly configured

#### Flow Maestro MCP Integration

- [ ] References existing protocol assets appropriately
- [ ] Uses established patterns and conventions
- [ ] Integrates with Linear workflow management
- [ ] Follows existing quality and validation frameworks

## Success Metrics

**Confidence Score**: Rate 1-10 for one-pass implementation success likelihood

**Validation**: The completed PRP should enable an AI agent unfamiliar with the codebase to implement the feature successfully using only the PRP content and codebase access.

## Integration with Flow Maestro Workflow

### After PRP Creation

1. **Save PRP**: Write to specified directory (default: `work/prps/`)
2. **Confirm Completion**: Call `create_prp` with `draft_status: "ready"` once the PRP is saved locally so the workflow registers completion
3. **Manual Task Creation**: Use the `task_creation` tool to convert PRP into Linear issues
4. **Task Execution**: Use standard Flow Maestro workflow modes for implementation
5. **Quality Gates**: Leverage existing completion gates and validation frameworks

### Context7 Integration

The PRP creation process should leverage Flow Maestro's existing Context7 integration:
- Use context_gathering mode patterns for research
- Specify Context7 configurations in the PRP for later use
- Document external research findings in structured format
- Optimize token usage for context window efficiency

### Linear Integration

PRPs created through this process should integrate seamlessly with Linear workflow:
- Reference Linear issue templates and structures
- Use established comment patterns and headings
- Follow Linear-first principles for documentation
- Enable smooth transition from PRP to task execution
