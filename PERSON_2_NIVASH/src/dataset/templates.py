"""
Template Synthesis Engine — Person 2.
UPI Transaction Fraud Forensics Platform (IDP).

Generates original (unmanipulated) synthetic payment receipt images across
three structurally distinct layout families (PayLite, QuickPe, UniPay).
Produces reproducible ground-truth field records for OCR accuracy benchmarking.
"""

import argparse
import csv
import math
import random
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image, ImageDraw, ImageFont

from src.dataset import config
from src.utils.paths import DATA_DIR, DOCS_DIR, RAW_DIR, ensure_dir


# ---------------------------------------------------------------------------
# Fictional Name Pools (Strictly non-branded, no real PII)
# ---------------------------------------------------------------------------

FICTIONAL_PAYEES = [
    "Apex Mart",
    "Metro Book Store",
    "City Electronics",
    "Green Grocers",
    "Sunrise Cafe",
    "Blue Star Retail",
    "Urban Coffee Roasters",
    "Apex Stationery",
    "Modern Bakery Store",
    "Global Tech Supplies",
    "Express Fuel Station",
    "Horizon Supermarket",
    "Central Pharmacy",
    "Nova Clothing Store",
    "Daily Fresh Dairy",
]

FICTIONAL_PAYERS = [
    "Synthetic Student Account",
    "Demo Academic User",
    "Fictional Payer Account",
    "Research Test Account",
    "Sample Consumer Wallet",
]


# ---------------------------------------------------------------------------
# Font Resolution Helper (Multi-platform fallback)
# ---------------------------------------------------------------------------

def get_font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    """
    Load a true-type sans-serif font across macOS, Linux, and Windows.
    Falls back gracefully to default PIL font if no system font is located.
    """
    candidate_paths = [
        # macOS
        "/System/Library/Fonts/Helvetica.ttc",
        "/Library/Fonts/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Helvetica.ttc",
        # Linux / Ubuntu
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        # Windows
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
    ]
    for p in candidate_paths:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size)
            except Exception:
                continue
    return ImageFont.load_default()


# ---------------------------------------------------------------------------
# Fictional Field Value Generation
# ---------------------------------------------------------------------------

def format_inr_amount(amount: float) -> str:
    """Format float into standard Indian Rupee string with comma grouping."""
    int_part = int(amount)
    dec_part = int(round((amount - int_part) * 100))
    s = str(int_part)
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        groups = []
        while len(rest) > 2:
            groups.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            groups.insert(0, rest)
        formatted_int = ",".join(groups) + "," + last3
    else:
        formatted_int = s
    return f"₹{formatted_int}.{dec_part:02d}"


def generate_fictional_record(
    src_id: int,
    template_family: int,
    rng: random.Random,
    reference_date_str: str = "2026-03-15",
) -> Dict[str, Any]:
    """
    Generate a single record of randomized fictional transaction fields.
    All dates are strictly in the past relative to reference_date_str.
    """
    # 1. Amount
    min_amt, max_amt = config.AMOUNT_RANGE
    # Generate realistic distribution: 70% small/medium, 30% large
    if rng.random() < 0.7:
        amt_val = round(rng.uniform(min_amt, 3500.0), 2)
    else:
        amt_val = round(rng.uniform(3500.0, max_amt), 2)
    amount_str = format_inr_amount(amt_val)

    # 2. Date & Time (in the past relative to reference date)
    ref_date = datetime.strptime(reference_date_str, "%Y-%m-%d")
    days_back = rng.randint(1, 180)
    txn_datetime = ref_date - timedelta(days=days_back, minutes=rng.randint(10, 1400))
    
    # Format per template family
    if template_family == 1:
        # PayLite: "12 Mar 2026"
        date_str = txn_datetime.strftime("%d %b %Y")
        time_str = txn_datetime.strftime("%I:%M %p")
    elif template_family == 2:
        # QuickPe: "12-03-2026"
        date_str = txn_datetime.strftime("%d-%m-%Y")
        time_str = txn_datetime.strftime("%I:%M %p")
    else:
        # UniPay: "2026-03-12"
        date_str = txn_datetime.strftime("%Y-%m-%d")
        time_str = txn_datetime.strftime("%H:%M")

    # 3. 12-Digit Transaction ID / UTR
    utr_digits = "".join(str(rng.randint(0, 9)) for _ in range(config.TXN_ID_LENGTH))
    # Ensure leading non-zero for realistic bank reference
    if utr_digits[0] == "0":
        utr_digits = "4" + utr_digits[1:]

    # 4. Names & Status
    payee = rng.choice(FICTIONAL_PAYEES)
    payer = rng.choice(FICTIONAL_PAYERS)
    
    app_names = {1: "PayLite", 2: "QuickPe", 3: "UniPay"}
    status_map = {
        1: "Paid Successfully",
        2: "Payment Completed",
        3: "SUCCESS",
    }

    app_name = app_names[template_family]
    status_str = status_map[template_family]
    image_id = config.ID_PATTERN.format(
        tpl_id=template_family,
        src_id=src_id,
        edit_type="none",
        var_id=1,
    )

    return {
        "image_id": image_id,
        "template_family": template_family,
        "app_name": app_name,
        "amount": amount_str,
        "amount_val": amt_val,
        "date": date_str,
        "time": time_str,
        "transaction_id": utr_digits,
        "payer": payer,
        "payee": payee,
        "status": status_str,
        "filename": f"{image_id}.png",
    }


# ---------------------------------------------------------------------------
# Layout Family Renderers
# ---------------------------------------------------------------------------

def draw_watermark(draw: ImageDraw.ImageDraw, w: int, h: int, color: Tuple[int, int, int]) -> None:
    """Draw the mandatory academic watermark at the bottom of the receipt."""
    font = get_font(11, bold=False)
    text = config.DEMO_WATERMARK_TEXT
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw) // 2, h - 30), text, fill=color, font=font)


def render_family_1_paylite(record: Dict[str, Any]) -> Image.Image:
    """
    Family 1: PayLite — Top Header Banner + Centered Hero Amount.
    """
    w, h = config.IMAGE_SIZE
    img = Image.new("RGB", (w, h), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # 1. Top Primary Header Banner
    banner_color = "#1A73E8"
    draw.rectangle([(0, 0), (w, 80)], fill=banner_color)
    
    f_title = get_font(20, bold=True)
    f_sub = get_font(12, bold=False)
    draw.text((25, 20), record["app_name"] + " UPI", fill="#FFFFFF", font=f_title)
    draw.text((25, 48), "Fast & Secure Digital Payments", fill="#D2E3FC", font=f_sub)

    # 2. Centered Status Icon & Text
    cx = w // 2
    draw.ellipse([(cx - 24, 115), (cx + 24, 163)], fill="#E6F4EA", outline="#34A853", width=2)
    # Checkmark inside circle
    draw.line([(cx - 10, 138), (cx - 3, 147), (cx + 10, 130)], fill="#34A853", width=3)
    
    f_status = get_font(17, bold=True)
    bbox = draw.textbbox((0, 0), record["status"], font=f_status)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 175), record["status"], fill="#202124", font=f_status)

    # 3. Large Centered Hero Amount
    f_hero = get_font(34, bold=True)
    amt_text = record["amount"]
    bbox = draw.textbbox((0, 0), amt_text, font=f_hero)
    tw = bbox[2] - bbox[0]
    draw.text((cx - tw // 2, 215), amt_text, fill="#1A73E8", font=f_hero)

    # Divider
    draw.line([(30, 275), (w - 30, 275)], fill="#E8EAED", width=1)

    # 4. Details Table
    f_label = get_font(13, bold=False)
    f_val = get_font(13, bold=True)

    rows = [
        ("Paid to", record["payee"]),
        ("Paid from", record["payer"]),
        ("Payment Date", record["date"]),
        ("Payment Time", record["time"]),
        ("UPI Ref (UTR)", record["transaction_id"]),
        ("Transaction Status", "COMPLETED"),
    ]

    y = 295
    for lbl, val in rows:
        draw.text((35, y), lbl, fill="#5F6368", font=f_label)
        draw.text((165, y), val, fill="#202124", font=f_val)
        y += 40

    # Card border container
    draw.rectangle([(20, 95), (w - 20, 560)], outline="#DADCE0", width=1)

    # Mandatory Watermark
    draw_watermark(draw, w, h, color=(128, 134, 139))
    return img


def render_family_2_quickpe(record: Dict[str, Any]) -> Image.Image:
    """
    Family 2: QuickPe — Dark Theme with Elevated Floating Card Containers.
    """
    w, h = config.IMAGE_SIZE
    bg_color = "#121824"
    img = Image.new("RGB", (w, h), color=bg_color)
    draw = ImageDraw.Draw(img)

    # 1. Header
    f_logo = get_font(20, bold=True)
    draw.text((25, 25), record["app_name"], fill="#00D2C6", font=f_logo)
    
    # Pill Status Badge
    draw.rounded_rectangle([(w - 170, 25), (w - 25, 52)], radius=12, fill="#0F3836", outline="#00D2C6", width=1)
    f_pill = get_font(11, bold=True)
    draw.text((w - 155, 31), "✓ COMPLETED", fill="#00D2C6", font=f_pill)

    # 2. Elevated Top Card (Amount & Recipient)
    draw.rounded_rectangle([(20, 75), (w - 20, 220)], radius=12, fill="#1E2738", outline="#2C384F", width=1)
    
    f_small = get_font(12, bold=False)
    f_payee = get_font(17, bold=True)
    f_hero = get_font(32, bold=True)

    draw.text((38, 95), "Paid to:", fill="#94A3B8", font=f_small)
    draw.text((38, 118), record["payee"], fill="#FFFFFF", font=f_payee)
    
    draw.text((38, 150), "Amount Transferred:", fill="#94A3B8", font=f_small)
    draw.text((38, 170), record["amount"], fill="#00D2C6", font=f_hero)

    # 3. Lower Details Card
    draw.rounded_rectangle([(20, 235), (w - 20, 560)], radius=12, fill="#1E2738", outline="#2C384F", width=1)
    
    draw.text((38, 255), "TRANSACTION DETAILS", fill="#64748B", font=get_font(11, bold=True))
    draw.line([(38, 275), (w - 38, 275)], fill="#2C384F", width=1)

    rows = [
        ("Reference ID (UTR)", record["transaction_id"]),
        ("Date", record["date"]),
        ("Time", record["time"]),
        ("Debited From", record["payer"]),
        ("Mode", "UPI Instant Transfer"),
    ]

    y = 295
    for lbl, val in rows:
        draw.text((38, y), lbl, fill="#94A3B8", font=f_small)
        draw.text((38, y + 18), val, fill="#F1F5F9", font=get_font(13, bold=True))
        y += 48

    # Watermark
    draw_watermark(draw, w, h, color=(100, 116, 139))
    return img


def render_family_3_unipay(record: Dict[str, Any]) -> Image.Image:
    """
    Family 3: UniPay — Minimalist Clean Grid Layout with ISO Date Format.
    """
    w, h = config.IMAGE_SIZE
    img = Image.new("RGB", (w, h), color="#FAFAFA")
    draw = ImageDraw.Draw(img)

    # 1. Minimal Header
    draw.text((30, 30), record["app_name"], fill="#5E35B1", font=get_font(22, bold=True))
    
    draw.rectangle([(w - 125, 30), (w - 30, 55)], fill="#E8F5E9", outline="#4CAF50", width=1)
    draw.text((w - 110, 36), "SUCCESS", fill="#2E7D32", font=get_font(11, bold=True))

    # 2. Hero Section
    draw.text((30, 85), "Total Amount Paid", fill="#757575", font=get_font(12, bold=False))
    draw.text((30, 105), record["amount"], fill="#212121", font=get_font(34, bold=True))

    draw.line([(30, 165), (w - 30, 165)], fill="#E0E0E0", width=1)

    # 3. Grid Table
    draw.rectangle([(25, 185), (w - 25, 570)], fill="#FFFFFF", outline="#E0E0E0", width=1)

    grid_rows = [
        ("Recipient Name", record["payee"]),
        ("Sender Account", record["payer"]),
        ("Transaction Date", record["date"]),
        ("Timestamp", record["time"]),
        ("Bank Ref (UTR)", record["transaction_id"]),
        ("Payment Channel", "Unified Payments Interface (UPI)"),
    ]

    y = 205
    for lbl, val in grid_rows:
        draw.text((40, y), lbl.upper(), fill="#9E9E9E", font=get_font(10, bold=True))
        draw.text((40, y + 16), val, fill="#212121", font=get_font(13, bold=False))
        draw.line([(40, y + 42), (w - 40, y + 42)], fill="#F5F5F5", width=1)
        y += 56

    # Watermark
    draw_watermark(draw, w, h, color=(158, 158, 158))
    return img


# Renderer Dispatcher
RENDERERS = {
    1: render_family_1_paylite,
    2: render_family_2_quickpe,
    3: render_family_3_unipay,
}


# ---------------------------------------------------------------------------
# Master Dataset Generation Orchestrator
# ---------------------------------------------------------------------------

def generate_originals(
    count: int = 60,
    output_dir: Optional[Path] = None,
    ground_truth_path: Optional[Path] = None,
    seed: int = config.RANDOM_SEED,
) -> Dict[str, Any]:
    """
    Generate N original synthetic receipts across the 3 layout families.
    Saves images and writes the ground-truth CSV answer key.
    """
    if output_dir is None:
        output_dir = RAW_DIR
    if ground_truth_path is None:
        ground_truth_path = DATA_DIR / "ground_truth.csv"

    output_dir = Path(output_dir)
    ensure_dir(output_dir)
    ensure_dir(ground_truth_path.parent)

    rng = random.Random(seed)
    
    # Calculate per-family distribution
    num_families = len(RENDERERS)
    base_per_family = count // num_families
    remainder = count % num_families

    counts_per_family = {i: base_per_family + (1 if i <= remainder else 0) for i in range(1, num_families + 1)}

    records = []
    src_id = 1

    for fam_id, fam_count in counts_per_family.items():
        renderer_func = RENDERERS[fam_id]
        for _ in range(fam_count):
            rec = generate_fictional_record(src_id=src_id, template_family=fam_id, rng=rng)
            img = renderer_func(rec)
            
            # Save Image (PNG for lossless synthesis baseline)
            out_file = output_dir / rec["filename"]
            img.save(out_file, format="PNG")
            
            records.append(rec)
            src_id += 1

    # Write ground_truth.csv
    fieldnames = [
        "image_id",
        "template_family",
        "app_name",
        "amount",
        "amount_val",
        "date",
        "time",
        "transaction_id",
        "payer",
        "payee",
        "status",
        "filename",
    ]

    with open(ground_truth_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in records:
            writer.writerow(r)

    return {
        "total_generated": len(records),
        "per_family": counts_per_family,
        "output_dir": str(output_dir),
        "ground_truth_csv": str(ground_truth_path),
        "seed": seed,
    }


# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic original UPI receipts across 3 layout families.")
    parser.add_argument("--count", type=int, default=60, help="Number of original images to generate (default: 60)")
    parser.add_argument("--out", type=str, default=str(RAW_DIR), help="Output directory for generated images")
    parser.add_argument("--seed", type=int, default=config.RANDOM_SEED, help="Random seed for reproducibility")
    parser.add_argument("--samples", action="store_true", help="Also export sample images to docs/samples/")
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("UPI Fraud Forensics — Person 2: Template Synthesis Engine")
    print("=" * 60)
    print(f"Generating {args.count} original receipts (Seed: {args.seed})...")

    summary = generate_originals(
        count=args.count,
        output_dir=Path(args.out),
        seed=args.seed,
    )

    print("\nGeneration Complete:")
    print(f"  • Total Images Generated : {summary['total_generated']}")
    print(f"  • PayLite (Family 1)      : {summary['per_family'][1]}")
    print(f"  • QuickPe (Family 2)      : {summary['per_family'][2]}")
    print(f"  • UniPay  (Family 3)      : {summary['per_family'][3]}")
    print(f"  • Output Directory       : {summary['output_dir']}")
    print(f"  • Ground Truth CSV       : {summary['ground_truth_csv']}")
    print("=" * 60 + "\n")

    # Export 3 sample images for documentation
    samples_dir = DOCS_DIR / "samples"
    ensure_dir(samples_dir)
    
    # Pick first generated image of each family
    raw_dir = Path(summary["output_dir"])
    f1_sample = list(raw_dir.glob("tpl1_*.png"))[0]
    f2_sample = list(raw_dir.glob("tpl2_*.png"))[0]
    f3_sample = list(raw_dir.glob("tpl3_*.png"))[0]

    shutil.copy(f1_sample, samples_dir / "sample_family1_paylite.png")
    shutil.copy(f2_sample, samples_dir / "sample_family2_quickpe.png")
    shutil.copy(f3_sample, samples_dir / "sample_family3_unipay.png")
    print(f"Exported 3 sample images to {samples_dir}")


if __name__ == "__main__":
    main()
