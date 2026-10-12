"""
Ground Truth Annotations for Real UPI Screenshots (18 images).
Strictly verified manually against screenshot pixels.
"""

import pandas as pd
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.utils.paths import REAL_GROUND_TRUTH_CSV

DATA = [
    {
        "image_id": "real_001",
        "app_name": "GooglePay",
        "amount_str": "₹100.00",
        "amount_val": 100.00,
        "date_display": "14 Sep 2026",
        "date_iso": "2026-09-14",
        "time_str": "6:51 PM",
        "utr": "625756926385",
        "recipient": "P S JAYESHKUMAR",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_100_jayesh"
    },
    {
        "image_id": "real_002",
        "app_name": "GooglePay",
        "amount_str": "₹55.00",
        "amount_val": 55.00,
        "date_display": "21 Sep 2026",
        "date_iso": "2026-09-21",
        "time_str": "6:53 PM",
        "utr": "626451080239",
        "recipient": "ITC",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_55_itc"
    },
    {
        "image_id": "real_003",
        "app_name": "GooglePay",
        "amount_str": "₹90.00",
        "amount_val": 90.00,
        "date_display": "24 Sep 2026",
        "date_iso": "2026-09-24",
        "time_str": "4:04 PM",
        "utr": "626711871433",
        "recipient": "MSS RKINDUSTRIES",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_90_mss"
    },
    {
        "image_id": "real_004",
        "app_name": "GooglePay",
        "amount_str": "₹300.00",
        "amount_val": 300.00,
        "date_display": "04 Oct 2026",
        "date_iso": "2026-10-04",
        "time_str": "4:15 PM",
        "utr": "664394690358",
        "recipient": "ANITHA PRIYADHARSHINI",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_300_anitha"
    },
    {
        "image_id": "real_005",
        "app_name": "GooglePay",
        "amount_str": "₹220.00",
        "amount_val": 220.00,
        "date_display": "06 Oct 2026",
        "date_iso": "2026-10-06",
        "time_str": "4:16 PM",
        "utr": "627901114804",
        "recipient": "Leka Arun",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_220_leka"
    },
    {
        "image_id": "real_006",
        "app_name": "GooglePay",
        "amount_str": "₹120.00",
        "amount_val": 120.00,
        "date_display": "07 Oct 2026",
        "date_iso": "2026-10-07",
        "time_str": "9:20 PM",
        "utr": "628090243795",
        "recipient": "Leka Arun",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_120_leka"
    },
    {
        "image_id": "real_007",
        "app_name": "GooglePay",
        "amount_str": "₹1,363.00",
        "amount_val": 1363.00,
        "date_display": "08 Oct 2026",
        "date_iso": "2026-10-08",
        "time_str": "10:54 AM",
        "utr": "664749583686",
        "recipient": "FLIPKART INTERNET PRIVATE LIMITED",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_1363_flipkart"
    },
    {
        "image_id": "real_008",
        "app_name": "PhonePe",
        "amount_str": "₹1,005.20",
        "amount_val": 1005.20,
        "date_display": "11 Oct 2026",
        "date_iso": "2026-10-11",
        "time_str": "10:28 AM",
        "utr": "606426248669",
        "recipient": "Redbus India Private Limited",
        "status": "SUCCESSFUL",
        "viewport": "unscrolled_details",
        "transaction_group_id": "tx_phonepe_1005_redbus"
    },
    {
        "image_id": "real_009",
        "app_name": "PhonePe",
        "amount_str": "₹3,000.00",
        "amount_val": 3000.00,
        "date_display": "19 Jul 2026",
        "date_iso": "2026-07-19",
        "time_str": "9:27 PM",
        "utr": "620037093036",
        "recipient": "J S CONTRACTORS",
        "status": "SUCCESSFUL",
        "viewport": "unscrolled_details",
        "transaction_group_id": "tx_phonepe_3000_js"
    },
    {
        "image_id": "real_010",
        "app_name": "PhonePe",
        "amount_str": "₹998.95",
        "amount_val": 998.95,
        "date_display": "01 May 2026",
        "date_iso": "2026-05-01",
        "time_str": "8:44 AM",
        "utr": "129024183965",
        "recipient": "Redbus India Private Limited",
        "status": "SUCCESSFUL",
        "viewport": "unscrolled_details",
        "transaction_group_id": "tx_phonepe_998_redbus"
    },
    {
        "image_id": "real_011",
        "app_name": "GooglePay",
        "amount_str": "₹1,363.00",
        "amount_val": 1363.00,
        "date_display": "08 Oct 2026",
        "date_iso": "2026-10-08",
        "time_str": "10:54 AM",
        "utr": "664749583686",
        "recipient": "FLIPKART INTERNET PRIVATE LIMITED",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_1363_flipkart"
    },
    {
        "image_id": "real_012",
        "app_name": "GooglePay",
        "amount_str": "₹153.00",
        "amount_val": 153.00,
        "date_display": "30 Sep 2026",
        "date_iso": "2026-09-30",
        "time_str": "8:08 PM",
        "utr": "627370419008",
        "recipient": "Thiruvasantham",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_153_thiru"
    },
    {
        "image_id": "real_013",
        "app_name": "GooglePay",
        "amount_str": "₹90.00",
        "amount_val": 90.00,
        "date_display": "24 Sep 2026",
        "date_iso": "2026-09-24",
        "time_str": "4:04 PM",
        "utr": "626711871433",
        "recipient": "MSS RK INDUSTRIES",
        "status": "COMPLETED",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_gpay_90_mss"
    },
    {
        "image_id": "real_014",
        "app_name": "PhonePe",
        "amount_str": "₹400.00",
        "amount_val": 400.00,
        "date_display": "04 Oct 2026",
        "date_iso": "2026-10-04",
        "time_str": "12:17 PM",
        "utr": "075612108284",
        "recipient": "NEW SKIN CARE MEDICALS",
        "status": "SUCCESSFUL",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_phonepe_400_skincare"
    },
    {
        "image_id": "real_015",
        "app_name": "PhonePe",
        "amount_str": "₹1,005.20",
        "amount_val": 1005.20,
        "date_display": "11 Oct 2026",
        "date_iso": "2026-10-11",
        "time_str": "10:28 AM",
        "utr": "606426248669",
        "recipient": "Redbus India Private Limited",
        "status": "SUCCESSFUL",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_phonepe_1005_redbus"
    },
    {
        "image_id": "real_016",
        "app_name": "PhonePe",
        "amount_str": "₹100.00",
        "amount_val": 100.00,
        "date_display": "31 Aug 2026",
        "date_iso": "2026-08-31",
        "time_str": "9:51 AM",
        "utr": "927840702955",
        "recipient": "Vv Vittechnovit",
        "status": "SUCCESSFUL",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_phonepe_100_vit"
    },
    {
        "image_id": "real_017",
        "app_name": "PhonePe",
        "amount_str": "₹1,750.39",
        "amount_val": 1750.39,
        "date_display": "25 Sep 2026",
        "date_iso": "2026-09-25",
        "time_str": "12:11 PM",
        "utr": "343140498377",
        "recipient": "Rk REDBUS",
        "status": "SUCCESSFUL",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_phonepe_1750_redbus"
    },
    {
        "image_id": "real_018",
        "app_name": "PhonePe",
        "amount_str": "₹1,756.76",
        "amount_val": 1756.76,
        "date_display": "30 Sep 2026",
        "date_iso": "2026-09-30",
        "time_str": "1:01 PM",
        "utr": "830827643545",
        "recipient": "Redbus India Private Limited",
        "status": "SUCCESSFUL",
        "viewport": "full_scrolled",
        "transaction_group_id": "tx_phonepe_1756_redbus"
    }
]

def create_ground_truth():
    df = pd.DataFrame(DATA)
    df.to_csv(REAL_GROUND_TRUTH_CSV, index=False)
    print(f"Created {REAL_GROUND_TRUTH_CSV} with {len(df)} verified rows.")

if __name__ == "__main__":
    create_ground_truth()
