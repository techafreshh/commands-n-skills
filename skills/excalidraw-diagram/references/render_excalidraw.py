"""Render Excalidraw JSON to PNG using agent-browser (headless Chromium via CDP).

Usage:
    python3 render_excalidraw.py <path-to-file.excalidraw> [--output path.png] [--scale 2] [--width 1920]

First-time setup (only if the agent-browser CLI isn't installed yet):
    npm i -g agent-browser && agent-browser install

The script drives agent-browser in a dedicated session ("excalidraw-render").
That session stays warm across invocations, so repeated renders in a
render-view-fix loop skip the cold browser start and the CDN module fetch.
Pass --close to shut the session down when you're done rendering.

No Python dependencies — stdlib only.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SESSION = "excalidraw-render"
INSTALL_HINT = "If the CLI is missing: npm i -g agent-browser && agent-browser install"

# Set after a sandbox-restricted launch failure; retried with --no-sandbox
# (standard in containers/VMs, where Chrome's namespace sandbox can't start).
_sandbox_fallback = False


def validate_excalidraw(data: dict) -> list[str]:
    """Validate Excalidraw JSON structure. Returns list of errors (empty = valid)."""
    errors: list[str] = []

    if data.get("type") != "excalidraw":
        errors.append(f"Expected type 'excalidraw', got '{data.get('type')}'")

    if "elements" not in data:
        errors.append("Missing 'elements' array")
    elif not isinstance(data["elements"], list):
        errors.append("'elements' must be an array")
    elif len(data["elements"]) == 0:
        errors.append("'elements' array is empty — nothing to render")

    return errors


def compute_bounding_box(elements: list[dict]) -> tuple[float, float, float, float]:
    """Compute bounding box (min_x, min_y, max_x, max_y) across all elements."""
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    for el in elements:
        if el.get("isDeleted"):
            continue
        x = el.get("x", 0)
        y = el.get("y", 0)
        w = el.get("width", 0)
        h = el.get("height", 0)

        # For arrows/lines, points array defines the shape relative to x,y
        if el.get("type") in ("arrow", "line") and "points" in el:
            for px, py in el["points"]:
                min_x = min(min_x, x + px)
                min_y = min(min_y, y + py)
                max_x = max(max_x, x + px)
                max_y = max(max_y, y + py)
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + abs(w))
            max_y = max(max_y, y + abs(h))

    if min_x == float("inf"):
        return (0, 0, 800, 600)

    return (min_x, min_y, max_x, max_y)


def run_ab(
    args: list[str],
    input_text: str | None = None,
    timeout: int = 120,
    hint: str | None = None,
) -> str:
    """Run an agent-browser command in the dedicated session. Returns trimmed stdout."""
    global _sandbox_fallback

    def launch(extra: list[str]) -> subprocess.CompletedProcess:
        cmd = ["agent-browser", "--session", SESSION, *extra, *args]
        return subprocess.run(cmd, input=input_text, capture_output=True, text=True, timeout=timeout)

    proc = launch([])
    if proc.returncode != 0 and not _sandbox_fallback:
        detail = (proc.stderr or proc.stdout)
        # Chrome can't start its namespace sandbox (containers, VMs, hardened
        # distros) — retry once with the sandbox disabled.
        if "No usable sandbox" in detail or "DevToolsActivePort" in detail:
            _sandbox_fallback = True
            print("Note: Chrome sandbox unavailable in this environment — retrying with --no-sandbox.", file=sys.stderr)
            proc = launch(["--args", "--no-sandbox"])

    if proc.returncode != 0:
        print(f"ERROR: agent-browser command failed: {' '.join(args)}", file=sys.stderr)
        detail = (proc.stderr or proc.stdout).strip()
        if detail:
            print(f"  {detail}", file=sys.stderr)
        if hint:
            print(f"  hint: {hint}", file=sys.stderr)
        sys.exit(1)
    return proc.stdout.strip()


def render(
    excalidraw_path: Path,
    output_path: Path | None = None,
    scale: int = 2,
    max_width: int = 1920,
    close: bool = False,
) -> Path:
    """Render an .excalidraw file to PNG. Returns the output PNG path."""
    if shutil.which("agent-browser") is None:
        print("ERROR: agent-browser CLI not found.", file=sys.stderr)
        print(f"  {INSTALL_HINT}", file=sys.stderr)
        sys.exit(1)

    # Read and validate
    raw = excalidraw_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {excalidraw_path}: {e}", file=sys.stderr)
        sys.exit(1)

    errors = validate_excalidraw(data)
    if errors:
        print(f"ERROR: Invalid Excalidraw file:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        sys.exit(1)

    # Compute viewport size from element bounding box
    elements = [e for e in data["elements"] if not e.get("isDeleted")]
    min_x, min_y, max_x, max_y = compute_bounding_box(elements)
    padding = 80
    diagram_w = max_x - min_x + padding * 2
    diagram_h = max_y - min_y + padding * 2

    # Cap viewport width, let height be natural
    vp_width = min(int(diagram_w), max_width)
    vp_height = max(int(diagram_h), 600)

    # Output path — must be absolute: the agent-browser daemon resolves
    # relative paths against its own working directory, not the caller's.
    if output_path is None:
        output_path = excalidraw_path.with_suffix(".png")
    output_path = output_path.resolve()

    # Template path (same directory as this script)
    template_path = Path(__file__).parent / "render_template.html"
    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    template_url = template_path.as_uri()

    # Size the viewport to the diagram (scale = device scale factor for crisp PNGs)
    run_ab(["set", "viewport", str(vp_width), str(vp_height), str(scale)])

    # Load the render template. It imports @excalidraw/excalidraw from esm.sh;
    # the first-ever load needs network, afterwards the browser cache serves it.
    run_ab(
        ["open", template_url],
        timeout=180,
        hint=f"{INSTALL_HINT}; also check network access to esm.sh",
    )
    run_ab(
        ["wait", "--fn", "window.__moduleReady === true"],
        timeout=60,
        hint="Template module never became ready — check network access to esm.sh",
    )

    # Kick off the render (async in the page), then wait for the completion
    # signal the template sets. Resetting the flags first keeps this correct
    # across warm-session re-renders of the same page.
    json_str = json.dumps(data)
    kick = (
        "window.__renderComplete = false;\n"
        "window.__renderError = null;\n"
        f"window.renderDiagram({json_str});\n"
        "true"
    )
    run_ab(["eval", "--stdin"], input_text=kick)
    run_ab(["wait", "--fn", "window.__renderComplete === true"])

    err = run_ab(["eval", "String(window.__renderError)"]).strip().strip('"')
    if err and err != "null":
        print(f"ERROR: Render failed: {err}", file=sys.stderr)
        sys.exit(1)

    # Size the viewport to the rendered SVG before capturing — element
    # screenshots don't capture content beyond the viewport, so an SVG
    # larger than the viewport (exportToSvg renders at 2x) would clip.
    dims = run_ab(
        ["eval", "(() => { const r = document.querySelector('#root svg').getBoundingClientRect(); return `${Math.ceil(r.width)}x${Math.ceil(r.height)}`; })()"]
    ).strip().strip('"')
    try:
        svg_w, svg_h = (int(v) for v in dims.split("x", 1))
    except ValueError:
        print(f"ERROR: Could not determine rendered SVG size (got: {dims!r})", file=sys.stderr)
        sys.exit(1)
    run_ab(["set", "viewport", str(svg_w), str(svg_h), str(scale)])

    # Screenshot the rendered SVG element
    run_ab(["screenshot", "#root svg", str(output_path)], hint=INSTALL_HINT)
    if not output_path.exists() or output_path.stat().st_size == 0:
        print(f"ERROR: Screenshot was not written to {output_path}", file=sys.stderr)
        sys.exit(1)

    if close:
        run_ab(["close"])

    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Render Excalidraw JSON to PNG")
    parser.add_argument("input", type=Path, help="Path to .excalidraw JSON file")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output PNG path (default: same name with .png)")
    parser.add_argument("--scale", "-s", type=int, default=2, help="Device scale factor (default: 2)")
    parser.add_argument("--width", "-w", type=int, default=1920, help="Max viewport width (default: 1920)")
    parser.add_argument("--close", action="store_true", help="Shut down the agent-browser session after rendering")
    args = parser.parse_args()

    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    png_path = render(args.input, args.output, args.scale, args.width, args.close)
    print(str(png_path))


if __name__ == "__main__":
    main()
