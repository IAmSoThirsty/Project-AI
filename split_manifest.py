# (Manifest Fragment Engine)              [2026-04-09 04:26]
#                                          Status: Active
import os

root = r'C:\Users\Quencher\.gemini\antigravity\scratch\Sovereign-Governance-Substrate'
brain = r'C:\Users\Quencher\.gemini\antigravity\brain\0156c356-3dfd-4a74-954c-fd87d14d630a'
exclude_dirs = {'.git', '.gradle', '.venv', '.venv_prod', '.antigravity', '__pycache__', '.pytest_cache', '.mypy_cache'}
exclude_files = {'.DS_Store', 'Thumbs.db', 'desktop.ini'}

groups = {
    'core': ['src/', 'engines/', 'kernel/', 'tarl/', 'project_ai/', 'orchestrator/', 'cognition/'],
    'docs_tests': ['docs/', 'tests/', 'adversarial_tests/', 'e2e/', 'benchmarks/'],
    'app_ext': ['projects/', 'external/', 'integrations/', 'api/', 'web/', 'desktop/', 'android/'],
    'infra_other': [] # Catch-all
}

files = []
for dirpath, dirnames, filenames in os.walk(root):
    # Filter directories in place
    dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
    rel_dir = os.path.relpath(dirpath, root).replace('\\', '/')
    if rel_dir == '.':
        rel_dir = ''
    for filename in filenames:
        if filename in exclude_files:
            continue
        path = (rel_dir + '/' + filename if rel_dir else filename)
        files.append(path)

files.sort()

manifests = {k: [] for k in groups}

for f in files:
    matched = False
    for k, prefixes in groups.items():
        if k == 'infra_other': continue
        for p in prefixes:
            if f.startswith(p):
                manifests[k].append(f)
                matched = True
                break
        if matched: break
    if not matched:
        manifests['infra_other'].append(f)

for k, flist in manifests.items():
    part_path = os.path.join(brain, f'repo_manifest_{k}.md')
    with open(part_path, 'w', encoding='utf-8') as mf:
        mf.write(f'# REPO MANIFEST PART: {k.upper()}\n\n')
        mf.write(f'**File Count**: {len(flist)}\n\n')
        mf.write('## FILE LISTING\n\n')
        for f in flist:
            mf.write(f'- {f}\n')

# Overwrite the original large manifest with a redirection page
with open(os.path.join(brain, 'repo_wide_manifest.md'), 'w', encoding='utf-8') as f:
    f.write('# REPO WIDE MANIFEST (REDIRECTION)\n\n')
    f.write('The original manifest was too large for UI rendering. It has been split into parts below:\n\n')
    f.write(f'- Core & Engines: {len(manifests["core"])} files\n')
    f.write(f'- Docs & Tests: {len(manifests["docs_tests"])} files\n')
    f.write(f'- App & Submodules: {len(manifests["app_ext"])} files\n')
    f.write(f'- Infra & Other: {len(manifests["infra_other"])} files\n')
    f.write('\n**Note**: Use the links provided in the notification to access each part.')

print('Manifest splitting complete.')
