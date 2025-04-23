#!/usr/bin/env python3
import typer
import os
import requests
from openai import OpenAI, APIError, RateLimitError, AuthenticationError
from datetime import datetime
from pathlib import Path
from typing_extensions import Annotated
from typing import Optional, List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt, Confirm, IntPrompt
from dotenv import load_dotenv
import shlex
import json
import openai

# --- Configuration ---
load_dotenv()
APP_NAME = "ImageGen CLI (DALL-E 3)"
DEFAULT_MODEL = "dall-e-3"
DEFAULT_OUTPUT_DIR = Path(".")

ASPECT_RATIOS = {
    "1": ("1:1", "1024x1024"),
    "2": ("16:9", "1792x1024"),
    "3": ("9:16", "1024x1792"),
}
QUALITY_OPTIONS = ["hd", "standard"]
STYLE_OPTIONS = ["vivid", "natural"]

app = typer.Typer(help=f"{APP_NAME}: Generate images using OpenAI's DALL-E 3. Run without a prompt for interactive mode.")
console = Console()


def generate_filename(prompt_prefix: str, index: int, output_dir: Path, ext: str = "png") -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_prefix = "".join(c if c.isalnum() else "_" for c in prompt_prefix[:15]).strip("_") or "image"
    filename = f"{safe_prefix}_{timestamp}_{index+1:02d}.{ext}"
    return output_dir / filename


def download_image(url: str, save_path: Path):
    try:
        response = requests.get(url, stream=True, timeout=90)
        response.raise_for_status()
        with open(save_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        console.print(f"   [green]\u2713[/green] Saved locally as: [cyan]{save_path.name}[/cyan]")
        return True
    except Exception as e:
        console.print(f"   [bold red]Error:[/bold red] {e}")
        return False


def validate_api_key(api_key: Optional[str]) -> str:
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        console.print("[bold red]Error:[/bold red] OpenAI API key not found.")
        raise typer.Exit(code=1)
    return key


def ask_choice(question: str, options: Dict[str, Any], default: str) -> Any:
    console.print(f"\n[bold cyan]{question}[/bold cyan]")
    choices = list(options.keys())
    for key in choices:
        label = options[key][0] if isinstance(options[key], tuple) else options[key]
        default_marker = " (default)" if key == default else ""
        console.print(f"  [yellow]{key}[/yellow]: {label}{default_marker}")
    while True:
        choice_key = Prompt.ask("Enter choice number", choices=choices, default=default)
        if choice_key in options:
            return options[choice_key]


def ask_str_choice(question: str, options: List[str], default: str) -> str:
    console.print(f"\n[bold cyan]{question}[/bold cyan]")
    option_map = {str(i+1): opt for i, opt in enumerate(options)}
    valid_choices = list(option_map.keys())
    for i, opt in enumerate(options):
        default_marker = " (default)" if opt == default else ""
        console.print(f"  [yellow]{i+1}[/yellow]: {opt}{default_marker}")
    default_choice_num = str(options.index(default) + 1)
    while True:
        choice_key = Prompt.ask("Enter choice number", choices=valid_choices, default=default_choice_num)
        if choice_key in option_map:
            return option_map[choice_key]


@app.command()
def generate(
    prompt_arg: Annotated[Optional[str], typer.Argument()] = None,
    n_arg: Annotated[Optional[int], typer.Option("--num-images", "-n")] = None,
    aspect_ratio_arg: Annotated[Optional[str], typer.Option("--aspect-ratio", "-ar")] = None,
    output_dir_arg: Annotated[Optional[Path], typer.Option("--output-dir", "-o")] = None,
    quality_arg: Annotated[Optional[str], typer.Option("--quality", "-q")] = None,
    style_arg: Annotated[Optional[str], typer.Option("--style", "-s")] = None,
    model: Annotated[str, typer.Option("--model", "-m")] = DEFAULT_MODEL,
    api_key: Annotated[Optional[str], typer.Option("--api-key", "-k")] = None,
    no_download_arg: Annotated[Optional[bool], typer.Option("--no-download")] = None,
):
    console.print(Panel(f"🖼️  {APP_NAME} ", title="Welcome", border_style="blue"))
    api_key_validated = validate_api_key(api_key)

    if prompt_arg is None:
        console.print("\n[bold green]Entering Interactive Mode...[/bold green]")
        while True:
            prompt = Prompt.ask("[bold cyan]Enter the image prompt[/]")
            if prompt.strip():
                break
        chosen_aspect_ratio = ask_choice("Choose aspect ratio:", ASPECT_RATIOS, default="1")
        aspect_ratio_key = chosen_aspect_ratio[0]
        size = chosen_aspect_ratio[1]
        quality = ask_str_choice("Choose generation quality:", QUALITY_OPTIONS, default="hd")
        style = ask_str_choice("Choose generation style:", STYLE_OPTIONS, default="vivid")
        n = IntPrompt.ask("[bold cyan]Number of images to generate?[/bold cyan]", default=1)
        output_dir_str = Prompt.ask("[bold cyan]Output directory[/bold cyan]", default=str(DEFAULT_OUTPUT_DIR.resolve()))
        output_dir = Path(output_dir_str)
        no_download = not Confirm.ask("[bold cyan]Download images automatically?[/bold cyan]", default=True)
    else:
        console.print("\n[bold green]Running in Command-Line Mode...[/bold green]")
        prompt = prompt_arg
        n = n_arg or 1
        aspect_ratio_key_input = aspect_ratio_arg or "1:1"
        quality = quality_arg or "hd"
        style = style_arg or "vivid"
        output_dir = output_dir_arg or DEFAULT_OUTPUT_DIR
        no_download = no_download_arg or False

        valid_ar_keys = [v[0] for v in ASPECT_RATIOS.values()]
        if aspect_ratio_key_input not in valid_ar_keys:
            console.print(f"[bold red]Error:[/bold red] Invalid aspect ratio '{aspect_ratio_key_input}'")
            raise typer.Exit(code=1)
        aspect_ratio_key = aspect_ratio_key_input
        size = next((v[1] for v in ASPECT_RATIOS.values() if v[0] == aspect_ratio_key), "1024x1024")

    if n > 1 and (size != "1024x1024" or quality == "hd"):
        console.print(f"[yellow]Warning:[/yellow] Forcing n=1 due to API limitations.")
        n = 1
    elif n > 10:
        console.print(f"[yellow]Warning:[/yellow] Max images per request is 10. Setting n=10.")
        n = 10

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        console.print(f"[bold red]Could not create output directory:[/bold red] {e}")
        raise typer.Exit(code=1)

    console.print(f"\n[bold]Prompt:[/bold] {prompt}\n[bold]Model:[/bold] {model}\n[bold]Size:[/bold] {size}\n[bold]Quality:[/bold] {quality}\n[bold]Style:[/bold] {style}\n[bold]Images:[/bold] {n}")

    try:
        console.print(f"\n[bold]OpenAI SDK version:[/bold] {openai.__version__}")
        client = OpenAI(api_key=api_key_validated)
        generation_params = {
            "model": model,
            "prompt": prompt,
            "n": n,
            "size": size,
            "quality": quality,
            "style": style,
        }
        console.print(Panel(json.dumps(generation_params, indent=2), title="DEBUG: Generation Parameters", border_style="magenta"))
        with console.status("[yellow]Generating image(s)...", spinner="dots"):
            response = client.images.generate(**generation_params)
    except AuthenticationError:
        console.print("[bold red]Authentication failed. Check your API key.[/bold red]")
        raise typer.Exit(code=1)
    except RateLimitError as e:
        console.print(f"[bold red]Rate limit exceeded ({e.status_code}).[/bold red]")
        raise typer.Exit(code=1)
    except APIError as e:
        error_details = e.body.get('error', {}) if e.body else {}
        console.print(f"[bold red]API Error:[/bold red] {error_details.get('message', 'No message')} (Code: {error_details.get('code', 'N/A')})")
        raise typer.Exit(code=1)
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise typer.Exit(code=1)

    if not response.data:
        console.print("[yellow]No images returned.[/yellow]")
        raise typer.Exit()

    image_urls = [img.url for img in response.data if img.url]
    revised_prompts = [img.revised_prompt for img in response.data if hasattr(img, 'revised_prompt') and img.revised_prompt]

    for i, url in enumerate(image_urls):
        console.print(f"\n[+] Image {i+1} URL: [link={url}]{url}[/link]")
        if revised_prompts and i < len(revised_prompts):
            console.print(f"   Revised Prompt: [italic]{revised_prompts[i]}[/italic]")
        if not no_download:
            filename = generate_filename(prompt.split(" ")[0], i, output_dir)
            with console.status(f"[yellow]Downloading image {i+1}...", spinner="dots"):
                download_image(url, filename)

    console.print(Panel(f"\u2705 Process finished. {len(image_urls)} image(s) handled.", title="Done", border_style="green", expand=False))


if __name__ == "__main__":
    app()
