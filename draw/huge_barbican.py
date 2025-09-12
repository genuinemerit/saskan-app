import argparse
import base64
import os
import sys
from datetime import datetime
from pathlib import Path


def default_prompt() -> str:
    return (
        "Widescreen establishing shot of an impregnable barbican: two triangular stone "
        "curtain walls forming a spearpoint, 12 m tall and 20 m long, with corner guard "
        "towers 16 m high. No entry anywhere: no gate, portal, or doorway; only "
        "machicolations and arrow slits. Set on a windswept cliff before a walled city. "
        "Composition: low-angle 3/4 view, leading lines converging on the spearpoint, "
        "foreground rocks in silhouette for depth, tiny human sentries for scale. "
        "Mood and atmosphere: epic dark fantasy at storm-tossed dusk; roiling "
        "thunderclouds, rain curtains, drifting mist, circling ravens, torchlit braziers. "
        "Lighting: cinematic and high-contrast; backlit lightning, volumetric god rays, "
        "wet stone glistening, strong rim light. Style and finish: detailed matte "
        "painting, painterly realism, intricate stonework, dramatic chiaroscuro. "
        "Palette: deep teals and cold blues with warm copper firelight accents. "
        "Exclude: modern elements, signage, sci-fi tech, text, logos."
    )


def resolve_size(aspect: str) -> str:
    if aspect == "wide":
        return "1792x1024"
    if aspect == "tall":
        return "1024x1792"
    return "1024x1024"  # square default


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def save_b64_png(b64_data: str, out_path: Path) -> None:
    raw = base64.b64decode(b64_data)
    out_path.write_bytes(raw)


def main():
    parser = argparse.ArgumentParser(description="Generate a dramatic fantasy barbican image.")
    parser.add_argument(
        "--model",
        default="dall-e-3",
        choices=["dall-e-3", "gpt-image-1"],
        help="Image model to use",
    )
    parser.add_argument(
        "--aspect",
        default="wide",
        choices=["wide", "tall", "square"],
        help="Convenience aspect preset (maps to size)",
    )
    parser.add_argument(
        "--size",
        default=None,
        help="Explicit size like 1792x1024; overrides --aspect",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=1,
        help="Number of images to generate (note: dall-e-3 supports n=1)",
    )
    parser.add_argument(
        "--quality",
        default="hd",
        choices=["standard", "hd"],
        help="Rendering quality (hd recommended for drama)",
    )
    parser.add_argument(
        "--style",
        default="vivid",
        choices=["vivid", "natural"],
        help="Stylistic bias (DALL·E 3)",
    )
    parser.add_argument(
        "--prompt",
        default=None,
        help="Override the default cinematic prompt",
    )
    # Default output directory next to this script
    script_dir = Path(__file__).resolve().parent
    parser.add_argument(
        "--out-dir",
        default=str(script_dir / "out"),
        help="Directory to save images when --save is enabled (default)",
    )
    parser.add_argument(
        "--no-save",
        dest="save",
        action="store_false",
        help="Do not save images; print URLs instead",
    )
    parser.set_defaults(save=True)

    args = parser.parse_args()

    # Lazy import to allow --help without SDK installed
    from openai import OpenAI

    # Load OpenAI API key
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        raise ValueError("Missing OpenAI API Key. Set OPENAI_API_KEY as an environment variable.")

    client = OpenAI(api_key=OPENAI_API_KEY)

    prompt = args.prompt if args.prompt else default_prompt()
    size = args.size if args.size else resolve_size(args.aspect)
    n = max(1, args.n)
    if args.model == "dall-e-3" and n != 1:
        print("Note: dall-e-3 supports n=1 only; clamping.", file=sys.stderr)
        n = 1

    params = {
        "model": args.model,
        "prompt": prompt,
        "size": size,
        "n": n,
    }

    # Optional quality/style controls (style mainly for DALL·E 3)
    if args.model == "dall-e-3":
        if args.quality:
            params["quality"] = args.quality
        if args.style:
            params["style"] = args.style

    # If saving locally, request base64 images
    if args.save:
        params["response_format"] = "b64_json"

    response = client.images.generate(**params)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

    outputs = []
    if args.save:
        out_dir = Path(args.out_dir)
        ensure_dir(out_dir)
        for i, item in enumerate(response.data, start=1):
            b64_png = getattr(item, "b64_json", None)
            if not b64_png:
                # Fallback if API returned URL despite request
                url = getattr(item, "url", None)
                outputs.append(url)
                print(url)
                continue
            fname = f"barbican_{args.model}_{size}_{timestamp}_{i}.png"
            out_path = out_dir / fname
            save_b64_png(b64_png, out_path)
            outputs.append(str(out_path))
            print(str(out_path))
    else:
        for item in response.data:
            url = getattr(item, "url", None)
            outputs.append(url)
            print(url)


if __name__ == "__main__":
    main()
