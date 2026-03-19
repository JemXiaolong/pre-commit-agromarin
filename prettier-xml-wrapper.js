#!/usr/bin/env node
/**
 * Wrapper for prettier that resolves @prettier/plugin-xml from the
 * pre-commit node_modules instead of the project directory.
 *
 * This is needed because pre-commit installs additional_dependencies
 * in its own cache, but prettier resolves plugins declared in the
 * project's .prettierrc relative to the project root.
 */
const { execFileSync } = require("child_process");
const path = require("path");

// Resolve the plugin from this script's node_modules (pre-commit cache)
const pluginPath = require.resolve("@prettier/plugin-xml");

// Build prettier args: --write --plugin <resolved_path> <files...>
const files = process.argv.slice(2);
const args = ["--write", "--plugin", pluginPath, ...files];

try {
    execFileSync("prettier", args, { stdio: "inherit" });
} catch (err) {
    process.exit(err.status || 1);
}
