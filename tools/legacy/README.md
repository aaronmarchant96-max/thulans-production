# Historical Varek scripts

The former root-level V19–V35 builders, refiners, renderers, material passes, and walk experiments are in `blender/`. Their V35 preflight JSON is kept alongside them. These historical filenames do not establish current engineering approval.

The four DeepSeek generation helpers are in `llm/`. Generated builder files are written into the sibling `blender/` directory. Existing model settings and Blender asset paths are preserved; many asset paths refer to the original local workstation.

Run Blender scripts from the repository root using their new path, for example:

```bash
blender --background --python tools/legacy/blender/render_v35_standalone.py
```

Blender MCP installation and enablement helpers are in [`../blender_setup/`](../blender_setup/). The other tools directly under `tools/` keep their existing paths.
