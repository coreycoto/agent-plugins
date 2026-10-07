"""Release guards use actual Git state and archives without provider operations."""
from __future__ import annotations

import base64
import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest
import yaml
from build_codex_package import distribution_projection
from qualify_plugin_release import (
    PLUGINS,
    qualify,
    qualify_registry_metadata,
    qualify_registry_version,
    require_first_publication,
)

ROOT = Path(__file__).resolve().parents[1]


def commit(root: Path) -> str:
    subprocess.run(['git', 'add', '.'], cwd=root, check=True)
    subprocess.run(['git', '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid',
                    'commit', '-qm', 'Release fixture'], cwd=root, check=True)
    return subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=root, text=True).strip()


@pytest.fixture
def candidate(tmp_path):
    root = tmp_path / 'source'
    root.mkdir()
    for name in ['plugins', 'adapters', '.agents/plugins']:
        shutil.copytree(ROOT / name, root / name, ignore=shutil.ignore_patterns('__pycache__'))
    shutil.copyfile(ROOT / 'LICENSE', root / 'LICENSE')
    subprocess.run(['git', 'init', '-q', str(root)], check=True)
    revision = commit(root)
    version = json.loads((root / 'plugins/communication/plugin.json').read_text())['version']
    distributions = distribution_projection(root)
    archives = {}
    for plugin in PLUGINS:
        archives[plugin] = tmp_path / f'{plugin}.tgz'
        archives[plugin].write_bytes(distributions[f'npm/coreycoto-agent-plugin-{plugin}-{version}.tgz'])
    return root, revision, version, archives


@pytest.mark.parametrize('plugin', PLUGINS)
def test_exact_clean_candidate_has_github_only_publication_identity(candidate, plugin):
    root, revision, version, archives = candidate
    receipt = qualify(root, revision, version, archives[plugin], plugin)
    assert receipt['source_revision'] == revision
    assert receipt['package'] == f'@coreycoto/agent-plugin-{plugin}'
    assert receipt['registry'] == 'https://npm.pkg.github.com'
    assert receipt['intended_visibility'] == 'public'
    assert receipt['archive_bytes'] == archives[plugin].stat().st_size


@pytest.mark.parametrize('change', ['revision', 'version', 'dirty', 'tamper', 'symlink'])
def test_mismatched_source_or_artifact_cannot_qualify(candidate, change):
    root, revision, version, archives = candidate
    archive = archives['communication']
    if change == 'revision':
        revision = '0' * 40
    elif change == 'version':
        version = '99.0.0'
    elif change == 'dirty':
        (root / 'LICENSE').write_text('Changed after review')
    elif change == 'tamper':
        archive.write_bytes(archive.read_bytes() + b'changed')
    else:
        real = archive.with_suffix('.original')
        archive.rename(real)
        archive.symlink_to(real)
    with pytest.raises(ValueError):
        qualify(root, revision, version, archive, 'communication')


def test_another_plugins_archive_cannot_qualify(candidate):
    root, revision, version, archives = candidate
    with pytest.raises(ValueError, match='differs'):
        qualify(root, revision, version, archives['product-management'], 'communication')


@pytest.mark.parametrize('revision,version', [('main', '0.9.1'), ('a' * 40, '../0.9.1'),
                                             ('a' * 40, '0.9.1; echo injected')])
def test_release_selectors_are_bounded_before_git_or_path_use(tmp_path, revision, version):
    with pytest.raises(ValueError, match='full source SHA'):
        qualify(tmp_path, revision, version, tmp_path / 'unused', 'communication')


def test_plugin_selector_is_bounded_before_git_or_path_use(tmp_path):
    with pytest.raises(ValueError, match='public plugin'):
        qualify(tmp_path, 'a' * 40, '0.9.1', tmp_path / 'unused', '../private')


@pytest.mark.parametrize('ignored', [False, True])
def test_uncommitted_packaged_file_cannot_claim_exact_source(candidate, ignored):
    root, revision, version, archives = candidate
    # Even a different package in this coordinated release must have committed inputs.
    extra = root / 'plugins/product-development/skills/extra.md'
    if ignored:
        (root / '.git/info/exclude').write_text('extra.md\n')
    extra.write_text('Unreviewed instructions')
    with pytest.raises(ValueError, match='not the committed source'):
        qualify(root, revision, version, archives['communication'], 'communication')


def test_committed_mixed_versions_cannot_qualify(candidate):
    root, _, version, archives = candidate
    manifest = root / 'plugins/product-management/plugin.json'
    data = json.loads(manifest.read_text())
    data['version'] = '99.0.0'
    manifest.write_text(json.dumps(data))
    catalog = root / '.agents/plugins/marketplace.json'
    data = json.loads(catalog.read_text())
    for entry in data['plugins']:
        if entry['name'] == 'product-management':
            entry['source']['version'] = '99.0.0'
    catalog.write_text(json.dumps(data))
    revision = commit(root)
    with pytest.raises(ValueError, match='Coordinated public package'):
        qualify(root, revision, version, archives['communication'], 'communication')


def test_first_new_version_dispatch_is_allowed():
    require_first_publication([{'id': 1, 'display_title': 'Agent Plugins 0.9.0'},
                               {'id': 2, 'display_title': 'Agent Plugins 0.9.1'}], 2, 1, '0.9.1')


@pytest.mark.parametrize('status', ['completed', 'in_progress', 'queued'])
def test_prior_attempt_holds_all_packages_even_when_absent(status):
    with pytest.raises(ValueError, match='already attempted'):
        require_first_publication([{'id': 1, 'display_title': 'Agent Plugins 0.9.1',
                                    'status': status}], 2, 1, '0.9.1')


def test_rerun_requires_reviewed_recovery():
    with pytest.raises(ValueError, match='already attempted'):
        require_first_publication([], 2, 2, '0.9.1')


def package_metadata(visibility='private'):
    return {'visibility': visibility, 'name': 'agent-plugin-communication',
            'package_type': 'npm', 'repository': {'full_name': 'coreycoto/agent-plugins'}}


def test_initial_private_visibility_is_recorded_without_claiming_public_delivery():
    receipt = qualify_registry_metadata(package_metadata(), 'communication')
    assert receipt['package_identity_verified']
    assert receipt['observed_visibility'] == 'private'
    assert not receipt['public_visibility_verified']


def test_public_visibility_needs_a_fresh_registry_observation():
    receipt = qualify_registry_metadata(package_metadata('public'), 'communication')
    assert receipt['public_visibility_verified']


@pytest.mark.parametrize('field,value', [('visibility', 'internal'), ('visibility', None),
                                       ('name', 'another-package'), ('repository', {}),
                                       ('repository', None), ('package_type', 'container')])
def test_registry_metadata_must_prove_identity_and_association(field, value):
    metadata = package_metadata()
    metadata[field] = value
    with pytest.raises(ValueError, match='unverified'):
        qualify_registry_metadata(metadata, 'communication')


@pytest.fixture
def registry_version(tmp_path):
    archive = tmp_path / 'acquired.tgz'
    payload = b'Independent acquired package bytes'
    archive.write_bytes(payload)
    metadata = {'name': '@coreycoto/agent-plugin-communication', 'version': '0.9.1',
                'dist': {'tarball': 'https://npm.pkg.github.com/download/communication/0.9.1/archive',
                         'shasum': hashlib.sha1(payload).hexdigest(),
                         'integrity': 'sha512-' + base64.b64encode(hashlib.sha512(payload).digest()).decode()}}
    return archive, metadata


def test_fresh_registry_version_checksums_bind_to_acquired_bytes(registry_version):
    archive, metadata = registry_version
    receipt = qualify_registry_version(metadata, 'communication', '0.9.1', archive)
    assert receipt['registry_checksum_verified']
    assert receipt['archive_sha256'] == hashlib.sha256(archive.read_bytes()).hexdigest()


@pytest.mark.parametrize('missing', [['integrity'], ['shasum'], ['integrity', 'shasum']])
def test_optional_registry_checksum_fields_are_reported_explicitly(registry_version, missing):
    archive, metadata = registry_version
    for name in missing:
        del metadata['dist'][name]
    receipt = qualify_registry_version(metadata, 'communication', '0.9.1', archive)
    assert set(receipt['registry_checksums_observed']) == {'shasum', 'integrity'} - set(missing)
    assert receipt['registry_checksum_verified'] == (len(missing) != 2)


@pytest.mark.parametrize('change', ['package', 'version', 'registry', 'credentials',
                                  'sha1', 'sha512', 'bytes'])
def test_registry_checksum_or_destination_mismatch_cannot_qualify(registry_version, change):
    archive, metadata = registry_version
    if change == 'package':
        metadata['name'] = '@coreycoto/agent-plugin-other'
    elif change == 'version':
        metadata['version'] = '0.9.0'
    elif change == 'registry':
        metadata['dist']['tarball'] = 'https://registry.npmjs.org/package'
    elif change == 'credentials':
        metadata['dist']['tarball'] = 'https://user:password@npm.pkg.github.com/package'
    elif change == 'sha1':
        metadata['dist']['shasum'] = '0' * 40
    elif change == 'sha512':
        metadata['dist']['integrity'] = 'sha512-unverified'
    else:
        archive.write_bytes(b'Different acquired artifact')
    with pytest.raises(ValueError, match='checksum mismatch'):
        qualify_registry_version(metadata, 'communication', '0.9.1', archive)


def test_workflow_contains_publication_and_independent_receipt_gates():
    workflow = yaml.safe_load((ROOT / '.github/workflows/publish-plugins.yml').read_text())
    jobs = workflow['jobs']
    assert workflow['concurrency']['cancel-in-progress'] is False
    assert jobs['qualify']['permissions'] == {'contents': 'read', 'actions': 'read'}
    assert jobs['publish']['needs'] == 'qualify'
    assert jobs['publish']['strategy']['fail-fast'] is False
    assert set(jobs['publish']['strategy']['matrix']['plugin']) == set(PLUGINS)
    assert jobs['publish']['permissions']['packages'] == 'write'
    steps = jobs['publish']['steps']
    publish = next(step for step in steps if step.get('id') == 'publication')
    assert publish['run'].count('npm publish ') == 1
    assert '--registry=https://npm.pkg.github.com' in publish['run']
    assert "['error']['code'] == 'E404'" in publish['run']
    assert 'unknown-requires-review' in publish['run']
    acquire = next(step for step in steps if step.get('name') == 'Verify fresh authenticated acquisition')
    assert acquire['if'] == "always() && steps.publication.outcome == 'success'"
    assert '--cache "$RUNNER_TEMP/fresh-npm-cache"' in acquire['run']
    assert 'qualify_registry_version' in acquire['run']
    assert steps[-1]['if'] == 'always()'


def test_workflow_embedded_shell_is_syntactically_valid():
    workflow = yaml.safe_load((ROOT / '.github/workflows/publish-plugins.yml').read_text())
    for job in workflow['jobs'].values():
        for step in job['steps']:
            if 'run' in step:
                result = subprocess.run(['bash', '-n'], input=step['run'], text=True,
                                        capture_output=True, check=False)
                assert result.returncode == 0, f"{step['name']}: {result.stderr}"
