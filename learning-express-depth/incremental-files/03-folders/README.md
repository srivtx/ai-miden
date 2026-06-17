# 03 — Folders (File Storage)

Hierarchical folders. Folders can contain files and other folders.

**What's new:**
- `folders` table with `parent_id` (self-reference)
- `files` table with `folder_id`
- Create folder (optionally nested in another)
- List folder contents (subfolders + files)
- Move folder
- Build the path by walking up the tree

**Why hierarchical folders?** Same as on your computer: organize files. Without folders, a thousand files in one list is unusable.

**Why `parent_id` IS NULL for root?** Every folder has a parent except the root. We use `NULL` for the root.

**Path resolution:** `getFolderPath` walks up the tree by following `parent_id`. Each level prepends the folder name. `/Documents/Work/Reports`.

## Run
```bash
npm install && node server.js
```

```bash
# Create root folder's children
curl -X POST http://localhost:3000/folders -H "Content-Type: application/json" -d '{"name": "Documents"}'
curl -X POST http://localhost:3000/folders -H "Content-Type: application/json" -d '{"name": "Work", "parent_id": "<docs-id>"}'
curl -X POST http://localhost:3000/folders -H "Content-Type: application/json" -d '{"name": "Reports", "parent_id": "<work-id>"}'

# List
curl http://localhost:3000/folders/<reports-id>
# { folder: { name: "Reports", path: "/Documents/Work/Reports" }, subfolders: [], files: [] }

# List Work (contains Reports)
curl http://localhost:3000/folders/<work-id>

# Move Reports to root
curl -X PATCH http://localhost:3000/folders/<reports-id>/move -H "Content-Type: application/json" -d '{"new_parent_id": null}'
```

## What this stage teaches
- Self-referencing tables (parent_id)
- Tree traversal
- Path building
- Recursive structures in SQL

## Next
**04-sharing** — share files with other users. Permissions.
