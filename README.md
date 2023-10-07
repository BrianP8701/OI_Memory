# OI_Memory
Making a way to have LLMs autonomously construct, query and update an external database from raw data.

## Day 1
- Measure performance of system:
  - Create library (Pdfs, textbooks, documentation, code etc)
  - Create queries corresponding to a chunk of text (To test performance of external database)
- Implement system:
  - Create binary tree with LLMs using sumarization(Constructing tree) and comparison(Traversing tree) first
  - Add features:
    - Try optimizing for tokens, aka, not strictly a binary tree
    - Allow for clone nodes, implement cleanup operation
  - Put on GCP
