#!/usr/bin/env python3
"""Qualify Codex's npm resolver and native setup using a local registry fixture, without inference."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

from smoke_codex_agents import Rpc, onboarding_context, status, tool


def qualify(codex: str, archive: Path, work: Path, scope: str) -> dict:
    with tarfile.open(archive, "r:gz") as package:
        metadata = json.load(package.extractfile("package/package.json"))
        manifest = json.load(package.extractfile("package/.codex-plugin/plugin.json"))
        catalog = json.load(package.extractfile("package/com.openai/agents/catalog.json"))
        hook_path = "package/" + manifest["hooks"].removeprefix("./")
        hooks = json.load(package.extractfile(hook_path))["hooks"]
        role_bytes = {entry["file"]: package.extractfile("package/com.openai/agents/" + entry["file"]).read()
                      for entry in catalog["roles"]}
    plugin = manifest["name"]
    home, repo, marketplace = work / "user", work / "repo", work / "marketplace"
    home.mkdir(parents=True)
    repo.mkdir()
    subprocess.run(["git", "init", "--quiet", str(repo)], capture_output=True, check=True)
    (home / ".codex").mkdir()
    config = (f'model = "gpt-6.1-sol"\n[projects.{json.dumps(str(repo))}]\ntrust_level = "trusted"\n').encode()
    (home / ".codex/config.toml").write_bytes(config)
    source = {"source": "npm", "package": metadata["name"], "version": metadata["version"],
              "registry": metadata["publishConfig"]["registry"]}
    manifest_path = marketplace / ".agents/plugins/marketplace.json"
    manifest_path.parent.mkdir(parents=True)
    manifest_path.write_text(json.dumps({"name": "npm-role-qualification", "plugins": [
        {"name": plugin, "source": source, "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
         "category": "Developer Tools"}]}))
    # Only the package-registry boundary is replaced. Codex still executes its
    # own npm materialization, archive extraction, plugin cache and native MCP.
    binary = work / "bin"
    binary.mkdir()
    npm = binary / "npm"
    arguments = work / "npm-arguments.json"
    npm.write_text(f'''#!{sys.executable}
import json, shutil, sys
from pathlib import Path
args = sys.argv[1:]
assert args[0] == "pack" and "--ignore-scripts" in args
assert args[-1] == {metadata["name"] + "@" + metadata["version"]!r}
assert args[args.index("--registry") + 1] == {source["registry"]!r}
destination = Path(args[args.index("--pack-destination") + 1])
shutil.copyfile({str(archive.resolve())!r}, destination / "fixture.tgz")
Path({str(arguments)!r}).write_text(json.dumps(args))
''')
    npm.chmod(0o755)
    environment = {"PATH": str(binary) + os.pathsep + os.environ["PATH"]}
    cli_env = dict(os.environ, HOME=str(home), CODEX_HOME=str(home / ".codex"), **environment)
    subprocess.run([codex, "plugin", "marketplace", "add", str(marketplace)], cwd=repo, env=cli_env,
                   capture_output=True, check=True, timeout=30)
    params = {"marketplacePath": str(manifest_path), "pluginName": plugin}
    rpc = Rpc(codex, home, repo, plugin, environment)
    try:
        rpc.initialize()
        rpc.call("plugin/install", params)
        detail = rpc.call("plugin/read", params)["plugin"]
        expected_hooks = sum(len(row["hooks"]) for rows in hooks.values() for row in rows)
        assert len(detail["hooks"]) == expected_hooks, "Native hook inventory differs from the package."
        assert detail["onboardingSkill"]["name"].endswith(":manage-codex-agents")
    finally:
        rpc.close()
    # Native plugin installation intentionally enables the package in config.
    # The separate role installer must preserve that resulting configuration.
    config = (home / ".codex/config.toml").read_bytes()
    target = (home / ".codex" if scope == "user" else repo / ".codex") / "agents" / plugin
    rpc = Rpc(codex, home, repo, plugin, environment)
    try:
        rpc.initialize()
        thread_id = rpc.call("thread/start", {"cwd": str(repo), "ephemeral": True, "model": "gpt-6.1-sol"})["thread"]["id"]
        statuses = rpc.call("mcpServerStatus/list", {"threadId": thread_id})["data"]
        assert any(server["name"] == plugin + "-agents" for server in statuses)
        declined = tool(rpc, thread_id, repo, "npm-declined")
        assert "Onboarding result: deferred" in onboarding_context(declined), f"Declined setup returned {declined}."
        assert not target.exists()
        answer = {"action": "accept", "content": {"scope": scope, "confirm": True}}
        accepted = tool(rpc, thread_id, repo, "npm-installed", answer)
        assert "Onboarding result: installed" in onboarding_context(accepted), f"Accepted setup returned {accepted}."
        assert status(rpc, thread_id, repo)["installations"][scope]["state"] == "ready"
        assert {path.name for path in target.glob("*.toml")} == set(role_bytes), "Installed role inventory differs."
        assert all((target / name).read_bytes() == data for name, data in role_bytes.items()), "Installed role bytes differ."
        assert (home / ".codex/config.toml").read_bytes() == config, "Role setup changed native plugin configuration."
        assert len(rpc.forms) == 2, "Expected exactly one decline and one acceptance form."
    finally:
        rpc.close()
    assert "--ignore-scripts" in json.loads(arguments.read_text())
    return {"plugin": plugin, "package": source, "scope": scope, "hooksDiscovered": expected_hooks,
            "installedRoles": sorted(role_bytes), "formDeclinePreservedState": True,
            "configPreserved": True, "registryAccess": "local fixture; no live registry or credentials"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--codex", default=shutil.which("codex"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    receipt = {"verified": False, "inferenceRequests": 0, "actualUserConfigurationChanged": False,
               "desktopActivation": False, "liveRegistryAccess": "unverified", "cases": []}
    try:
        if not args.codex:
            raise RuntimeError("Codex CLI is required.")
        receipt["archiveSha256"] = hashlib.sha256(args.archive.read_bytes()).hexdigest()
        receipt["codexVersion"] = subprocess.check_output([args.codex, "--version"], text=True).strip()
        with tempfile.TemporaryDirectory(prefix="codex-npm-qualification-") as temporary:
            for scope in ("user", "project"):
                receipt["cases"].append(qualify(args.codex, args.archive, Path(temporary).resolve() / scope, scope))
        receipt["verified"] = True
    except Exception as error:
        receipt["failure"] = {"type": type(error).__name__, "message": str(error)}
    if args.output:
        args.output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))
    return int(not receipt["verified"])


if __name__ == "__main__":
    raise SystemExit(main())
