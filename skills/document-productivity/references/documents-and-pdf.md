# Documents and PDF

## Word-processing documents

Use real heading levels, lists, tables, captions, footnotes, page breaks, headers, and fields. Preserve styles instead of formatting paragraphs individually. Keep tables editable and use section breaks only where page geometry or header behavior actually changes.

For edits, distinguish requested content changes from incidental reflow. Preserve comments, tracked changes, bookmarks, links, and accessibility metadata when supported and relevant.

When redlining, mark the smallest meaningful changed span and retain unchanged runs. Replacing an entire paragraph to express a one-word edit destroys useful review history.

## PDFs

Determine whether the task is extraction, review, form filling, assembly, redaction, repair, or generation. A PDF's visual page is authoritative for layout; its text layer is useful but may be incomplete or out of reading order.

For redaction, remove underlying content rather than covering it visually. For forms, use actual fields where required and verify values after saving. For generated PDFs, inspect fonts, page boxes, links, images, and selectable text.

For extraction, determine whether the PDF has a trustworthy text layer and reading order. Use layout-aware table extraction where structure matters; apply OCR to scanned pages and verify representative results against the rendered page. Preserve page references so extracted claims can be traced back.

## Visual verification

Render every page when feasible and inspect thumbnails for global consistency. Examine dense tables, page transitions, equations, forms, and the first and last page at full resolution. Check orphaned headings, clipped content, unexpected blanks, and header/footer collisions.
