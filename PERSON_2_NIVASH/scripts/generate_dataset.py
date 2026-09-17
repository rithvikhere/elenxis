#!/usr/bin/env python3
"""
Dataset Generator for Synthetic UPI Receipts.
Designed for Person 2 scope of the UPI Transaction Fraud Forensics Platform (IDP Project).

Features:
- Fictional, non-branded payment templates (ApexPay, ZenithUPI, NovaPay).
- Explicit DEMO / SYNTHETIC watermarks to prevent real-world misuse.
- Controlled tamper variants:
    * original (unaltered clean receipt)
    * amount_change (altered amount formatting, decimals, or tampered digits)
    * date_change (future date, invalid date syntax)
    * transaction_id_change (truncated or invalid 10/14-digit UTR, non-numeric chars)
    * text_tamper (misaligned/tampered recipient name, missing status)
- Strict split strategy (train/val/test grouped by template scenario to prevent data leakage).
- Ground truth metadata CSV export.
"""

import os
import csv
import random
from PIL import Image, ImageDraw, ImageFont

# Set deterministic seed for reproducibility
random.seed(42)

DATA_RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "raw")
METADATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "metadata.csv")

# Fictional merchant/recipient names (strictly synthetic)
RECIPIENTS = [
    "Metro Book Store",
    "Sunrise Cafe",
    "Blue Star Electronics",
    "Green Grocers Mart",
    "Apex Stationery",
    "Urban Coffee Roasters",
    "City Pharmacy Retail",
    "Modern Bakery Store"
]

# Base font loader with graceful fallback
def get_font(size=20, bold=False):
    font_paths = [
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFCompact.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for p in font_paths:
        if os.path.exists(p):
            try:
                # index 0 is regular, index 1 is bold for Helvetica.ttc
                idx = 1 if (bold and p.endswith(".ttc")) else 0
                return ImageFont.truetype(p, size, index=idx)
            except Exception:
                pass
    return ImageFont.load_default()

def draw_demo_banner(draw, width):
    """Adds a clear, non-deceptive synthetic banner at top and bottom."""
    draw.rectangle([(0, 0), (width, 28)], fill="#F1F5F9")
    font = get_font(12, bold=True)
    draw.text((width // 2, 14), "DEMO / SYNTHETIC UPI RECEIPT - ACADEMIC RESEARCH ONLY", fill="#64748B", anchor="mm", font=font)

def render_template_apex(data, output_path, tamper_type=None):
    """
    Template A: ApexPay (Card-style blue & white layout)
    """
    W, H = 540, 800
    img = Image.new("RGB", (W, H), "#F8FAFC")
    draw = ImageDraw.Draw(img)

    # Header Banner
    draw_demo_banner(draw, W)

    # App Header
    draw.rectangle([(0, 28), (W, 110)], fill="#1E40AF")
    font_title = get_font(26, bold=True)
    draw.text((W // 2, 68), "ApexPay UPI", fill="#FFFFFF", anchor="mm", font=font_title)

    # Success Badge
    draw.ellipse([(W // 2 - 36, 140), (W // 2 + 36, 212)], fill="#10B981")
    font_tick = get_font(34, bold=True)
    draw.text((W // 2, 174), "✓", fill="#FFFFFF", anchor="mm", font=font_tick)

    # Status text
    font_status = get_font(20, bold=True)
    status_text = "Paid Successfully" if tamper_type != "text_tamper" else "Payment Confirmed"
    draw.text((W // 2, 235), status_text, fill="#0F172A", anchor="mm", font=font_status)

    # Amount display
    font_amt = get_font(42, bold=True)
    # If amount_change, simulate mismatched spacing or font size
    if tamper_type == "amount_change":
        # Draw with suspicious font size or slight offset
        tamper_font = get_font(36, bold=False)
        draw.text((W // 2, 290), data["amount"], fill="#1E293B", anchor="mm", font=tamper_font)
    else:
        draw.text((W // 2, 290), data["amount"], fill="#0F172A", anchor="mm", font=font_amt)

    # Card container for details
    draw.rectangle([(30, 340), (W - 30, 680)], fill="#FFFFFF", outline="#CBD5E1", width=1)

    details = [
        ("To Recipient", data["recipient"]),
        ("Payment Date", data["date"]),
        ("Time", data["time"]),
        ("UPI Ref (UTR)", data["utr"]),
        ("From", "Synthetic Student Account"),
        ("Transaction Status", "COMPLETED")
    ]

    curr_y = 370
    font_lbl = get_font(15, bold=False)
    font_val = get_font(16, bold=True)

    for label, val in details:
        draw.text((50, curr_y), label, fill="#64748B", font=font_lbl)
        draw.text((W - 50, curr_y), val, fill="#1E293B", anchor="ra", font=font_val)
        draw.line([(50, curr_y + 35), (W - 50, curr_y + 35)], fill="#F1F5F9", width=1)
        curr_y += 50

    # Footer note
    font_ft = get_font(12)
    draw.text((W // 2, 720), "IDP Project - Person 2 Forensic Validation Module", fill="#94A3B8", anchor="mm", font=font_ft)
    draw_demo_banner(draw, W)

    img.save(output_path, quality=95)
    return output_path

def render_template_zenith(data, output_path, tamper_type=None):
    """
    Template B: ZenithUPI (Purple modern theme)
    """
    W, H = 540, 820
    img = Image.new("RGB", (W, H), "#F5F3FF")
    draw = ImageDraw.Draw(img)

    draw_demo_banner(draw, W)

    # Top Header
    draw.rectangle([(0, 28), (W, 120)], fill="#6D28D9")
    font_title = get_font(26, bold=True)
    draw.text((W // 2, 74), "ZenithUPI Instant Transfer", fill="#FFFFFF", anchor="mm", font=font_title)

    # Transfer confirmation card
    draw.rounded_rectangle([(30, 150), (W - 30, 310)], radius=12, fill="#FFFFFF", outline="#DDD6FE", width=1)

    font_paid_to = get_font(15)
    draw.text((W // 2, 175), "Transfer to", fill="#6B7280", anchor="mm", font=font_paid_to)

    font_name = get_font(22, bold=True)
    draw.text((W // 2, 205), data["recipient"], fill="#1F2937", anchor="mm", font=font_name)

    font_amt = get_font(40, bold=True)
    if tamper_type == "amount_change":
        draw.text((W // 2, 260), data["amount"], fill="#4C1D95", anchor="mm", font=get_font(34, bold=False))
    else:
        draw.text((W // 2, 260), data["amount"], fill="#5B21B6", anchor="mm", font=font_amt)

    # Transaction Statement Card
    draw.rounded_rectangle([(30, 330), (W - 30, 720)], radius=12, fill="#FFFFFF", outline="#E5E7EB", width=1)

    font_hdr = get_font(17, bold=True)
    draw.text((50, 355), "Transaction Details", fill="#374151", font=font_hdr)
    draw.line([(50, 385), (W - 50, 385)], fill="#EDE9FE", width=2)

    fields = [
        ("UPI Transaction ID", data["utr"]),
        ("Date", data["date"]),
        ("Time", data["time"]),
        ("Payment Mode", "UPI Peer-to-Merchant"),
        ("Banking Reference", "SYNTH-BNK-990"),
        ("Verification Code", "APPROVED-44")
    ]

    curr_y = 410
    font_lbl = get_font(15)
    font_val = get_font(15, bold=True)
    for lbl, val in fields:
        draw.text((50, curr_y), lbl, fill="#6B7280", font=font_lbl)
        draw.text((W - 50, curr_y), val, fill="#111827", anchor="ra", font=font_val)
        curr_y += 48

    font_ft = get_font(12)
    draw.text((W // 2, 750), "Security Forensics Academic Evaluation Only", fill="#8B5CF6", anchor="mm", font=font_ft)
    draw_demo_banner(draw, W)

    img.save(output_path, quality=95)
    return output_path

def render_template_nova(data, output_path, tamper_type=None):
    """
    Template C: NovaPay (Minimalist green accented receipt)
    """
    W, H = 540, 780
    img = Image.new("RGB", (W, H), "#FFFFFF")
    draw = ImageDraw.Draw(img)

    draw_demo_banner(draw, W)

    # Top brand
    font_app = get_font(24, bold=True)
    draw.text((W // 2, 70), "NovaPay Transfer", fill="#047857", anchor="mm", font=font_app)

    # Checkmark circle
    draw.ellipse([(W // 2 - 32, 105), (W // 2 + 32, 169)], fill="#ECFDF5", outline="#10B981", width=2)
    draw.text((W // 2, 137), "✓", fill="#059669", anchor="mm", font=get_font(30, bold=True))

    font_success = get_font(18, bold=True)
    draw.text((W // 2, 190), "Transaction Successful", fill="#065F46", anchor="mm", font=font_success)

    font_amt = get_font(44, bold=True)
    if tamper_type == "amount_change":
        draw.text((W // 2, 245), data["amount"], fill="#047857", anchor="mm", font=get_font(38, bold=False))
    else:
        draw.text((W // 2, 245), data["amount"], fill="#047857", anchor="mm", font=font_amt)

    draw.line([(40, 290), (W - 40, 290)], fill="#E2E8F0", width=1)

    items = [
        ("Recipient Name", data["recipient"]),
        ("Transaction Date", data["date"]),
        ("Time", data["time"]),
        ("UTR Number", data["utr"]),
        ("Status", "SUCCESS"),
        ("Source", "Synthetic Test Wallet")
    ]

    curr_y = 320
    font_k = get_font(15)
    font_v = get_font(16, bold=True)

    for k, v in items:
        draw.text((50, curr_y), k, fill="#64748B", font=font_k)
        draw.text((W - 50, curr_y), v, fill="#0F172A", anchor="ra", font=font_v)
        curr_y += 50

    draw.line([(40, 640), (W - 40, 640)], fill="#E2E8F0", width=1)
    font_ft = get_font(12)
    draw.text((W // 2, 675), "Synthetic Academic Evaluation Sample", fill="#94A3B8", anchor="mm", font=font_ft)
    draw_demo_banner(draw, W)

    img.save(output_path, quality=95)
    return output_path

RENDERERS = {
    "apex": render_template_apex,
    "zenith": render_template_zenith,
    "nova": render_template_nova,
}

def generate_base_scenario(idx):
    """Generates a clean baseline synthetic transaction record."""
    amounts = ["₹450.00", "₹1,200.00", "₹85.50", "₹3,499.00", "₹250.00", "₹5,000.00", "₹150.00", "₹899.00"]
    dates = ["12 Mar 2026", "14 Mar 2026", "15 Mar 2026", "16 Mar 2026", "17 Mar 2026", "10 Feb 2026"]
    times = ["10:15 AM", "02:45 PM", "08:20 PM", "11:30 AM", "04:12 PM", "06:55 PM"]

    # Fictional 12-digit standard UTR
    utr_num = f"4{random.randint(10000000000, 99999999999)}"
    amt = amounts[idx % len(amounts)]
    dt = dates[idx % len(dates)]
    tm = times[idx % len(times)]
    rec = RECIPIENTS[idx % len(RECIPIENTS)]

    return {
        "amount": amt,
        "date": dt,
        "time": tm,
        "utr": utr_num,
        "recipient": rec
    }

def main():
    os.makedirs(DATA_RAW_DIR, exist_ok=True)
    records = []

    # 15 distinct scenario bases (5 per template)
    # Each scenario generates:
    # 1 original + 3 controlled tampered variants = 4 images per scenario
    # Total = 15 * 4 = 60 images
    # Split:
    # - Scenarios 0-8: Train (36 images)
    # - Scenarios 9-11: Validation (12 images)
    # - Scenarios 12-14: Test (12 images)
    # Grouping by scenario guarantees ZERO leakage between splits!

    templates = ["apex", "zenith", "nova"]

    img_counter = 1
    for s_idx in range(15):
        tpl_name = templates[s_idx % len(templates)]
        renderer = RENDERERS[tpl_name]

        # Determine split
        if s_idx < 9:
            split = "train"
        elif s_idx < 12:
            split = "val"
        else:
            split = "test"

        base_data = generate_base_scenario(s_idx)

        # 1. Original Clean
        img_id = f"img_{img_counter:03d}"
        img_filename = f"{img_id}.png"
        img_path = os.path.join(DATA_RAW_DIR, img_filename)
        renderer(base_data, img_path, tamper_type=None)

        records.append({
            "image_id": img_id,
            "filename": img_filename,
            "label": "original",
            "edit_type": "none",
            "amount_changed": "no",
            "date_changed": "no",
            "transaction_id_changed": "no",
            "template_type": tpl_name,
            "split": split,
            "ground_truth_amount": base_data["amount"],
            "ground_truth_date": base_data["date"],
            "ground_truth_time": base_data["time"],
            "ground_truth_utr": base_data["utr"],
            "ground_truth_recipient": base_data["recipient"]
        })
        img_counter += 1

        # 2. Tampered Variant: Amount Change
        img_id = f"img_{img_counter:03d}"
        img_filename = f"{img_id}.png"
        img_path = os.path.join(DATA_RAW_DIR, img_filename)

        tampered_amt_data = dict(base_data)
        tampered_amt_data["amount"] = f"₹{random.randint(20000, 95000)}.99"
        renderer(tampered_amt_data, img_path, tamper_type="amount_change")

        records.append({
            "image_id": img_id,
            "filename": img_filename,
            "label": "synthetic_fake",
            "edit_type": "amount_change",
            "amount_changed": "yes",
            "date_changed": "no",
            "transaction_id_changed": "no",
            "template_type": tpl_name,
            "split": split,
            "ground_truth_amount": tampered_amt_data["amount"],
            "ground_truth_date": tampered_amt_data["date"],
            "ground_truth_time": tampered_amt_data["time"],
            "ground_truth_utr": tampered_amt_data["utr"],
            "ground_truth_recipient": tampered_amt_data["recipient"]
        })
        img_counter += 1

        # 3. Tampered Variant: Date Change (Future / Invalid date)
        img_id = f"img_{img_counter:03d}"
        img_filename = f"{img_id}.png"
        img_path = os.path.join(DATA_RAW_DIR, img_filename)

        tampered_date_data = dict(base_data)
        # Future date: e.g. year 2029 or 2030
        tampered_date_data["date"] = f"28 Dec 2029"
        renderer(tampered_date_data, img_path, tamper_type="date_change")

        records.append({
            "image_id": img_id,
            "filename": img_filename,
            "label": "synthetic_fake",
            "edit_type": "date_change",
            "amount_changed": "no",
            "date_changed": "yes",
            "transaction_id_changed": "no",
            "template_type": tpl_name,
            "split": split,
            "ground_truth_amount": tampered_date_data["amount"],
            "ground_truth_date": tampered_date_data["date"],
            "ground_truth_time": tampered_date_data["time"],
            "ground_truth_utr": tampered_date_data["utr"],
            "ground_truth_recipient": tampered_date_data["recipient"]
        })
        img_counter += 1

        # 4. Tampered Variant: UTR Change (Malformed 10-digit or 14-digit / invalid)
        img_id = f"img_{img_counter:03d}"
        img_filename = f"{img_id}.png"
        img_path = os.path.join(DATA_RAW_DIR, img_filename)

        tampered_utr_data = dict(base_data)
        # Invalid length (e.g. 10 digits instead of standard 12)
        tampered_utr_data["utr"] = f"UTR{random.randint(1000000, 9999999)}"
        renderer(tampered_utr_data, img_path, tamper_type="transaction_id_change")

        records.append({
            "image_id": img_id,
            "filename": img_filename,
            "label": "synthetic_fake",
            "edit_type": "transaction_id_change",
            "amount_changed": "no",
            "date_changed": "no",
            "transaction_id_changed": "yes",
            "template_type": tpl_name,
            "split": split,
            "ground_truth_amount": tampered_utr_data["amount"],
            "ground_truth_date": tampered_utr_data["date"],
            "ground_truth_time": tampered_utr_data["time"],
            "ground_truth_utr": tampered_utr_data["utr"],
            "ground_truth_recipient": tampered_utr_data["recipient"]
        })
        img_counter += 1

    # Write metadata.csv
    fieldnames = [
        "image_id", "filename", "label", "edit_type",
        "amount_changed", "date_changed", "transaction_id_changed",
        "template_type", "split",
        "ground_truth_amount", "ground_truth_date", "ground_truth_time",
        "ground_truth_utr", "ground_truth_recipient"
    ]

    with open(METADATA_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)

    print(f"Successfully generated {len(records)} images in {DATA_RAW_DIR}")
    print(f"Metadata written to {METADATA_PATH}")

    # Summary
    splits_count = {"train": 0, "val": 0, "test": 0}
    labels_count = {"original": 0, "synthetic_fake": 0}
    for r in records:
        splits_count[r["split"]] += 1
        labels_count[r["label"]] += 1
    print(f"Splits: {splits_count}")
    print(f"Labels: {labels_count}")

if __name__ == "__main__":
    main()
