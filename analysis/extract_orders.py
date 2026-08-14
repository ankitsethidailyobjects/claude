#!/usr/bin/env python3
"""
Extract unique ORDERS (not SKU lines) from a DMR file.

DMR is order-LINE level: one Order No. can span many rows (one per SKU).
We aggregate each Order No. to a single record.

Output CSV columns: order_no, email, order_date(YYYY-MM-DD), year, paid, delivered
  paid      = 1 if any line has a status other than paymentPending/paymentFailed
  delivered = 1 if any line is delivered/shipped/reversePickup*/rto/invoiced (fulfilled)

Also prints per-file data-quality metrics as JSON to <out>.qc.json
"""
import sys, os, csv, json, datetime as dt
from collections import Counter, defaultdict

NEVER_PAID = {"paymentpending", "paymentfailed"}
FULFILLED  = {"delivered", "shipped", "reversepickupdone", "reversepickupinitiated",
              "rto", "invoiced", "cod", "codverified", "paymentreceived"}

def norm_email(v):
    if v is None: return ""
    return str(v).strip().lower()

def parse_date(v):
    """Return datetime.date or None."""
    if v is None: return None
    if isinstance(v, dt.datetime): return v.date()
    if isinstance(v, dt.date): return v
    s = str(v).strip()
    if not s: return None
    # take date part if datetime string
    s = s.split(" ")[0]
    for fmt in ("%m/%d/%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%y", "%d-%m-%Y"):
        try:
            return dt.datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None

import re
def _norm(h):
    """Normalize a header cell: lowercase, drop all non-alphanumerics.
    'Order No.' / 'Order_No_' / 'OrderNo' -> 'orderno'."""
    if h is None: return ""
    return re.sub(r"[^a-z0-9]", "", str(h).strip().lower())

def _normset(header):
    return {_norm(h) for h in header}

def _has_cols(header, strict=True):
    s = _normset(header)
    has_ord = "orderno" in s
    has_em  = "useremail" in s or "email" in s
    has_dt  = "onlydate" in s or "orderdate" in s
    has_st  = "itemstatus" in s or "laststatus" in s
    if strict:
        return has_ord and has_em and has_dt and has_st
    return has_ord and has_em

def iter_rows(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        with open(path, newline="", encoding="utf-8-sig", errors="replace") as f:
            r = csv.reader(f)
            for row in r:
                yield row
    else:
        import openpyxl
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        firsts = {}
        for sn in wb.sheetnames:
            try:
                firsts[sn] = next(wb[sn].iter_rows(values_only=True))
            except StopIteration:
                firsts[sn] = []
        # prefer a sheet that has ALL key cols; else any with order+email
        chosen = next((sn for sn in wb.sheetnames if _has_cols(firsts[sn], True)), None)
        if chosen is None:
            chosen = next((sn for sn in wb.sheetnames if _has_cols(firsts[sn], False)), None)
        if chosen is None:
            chosen = wb.sheetnames[0]
        sys.stderr.write(f"[sheet] using {chosen!r} of {wb.sheetnames}\n")
        for row in wb[chosen].iter_rows(values_only=True):
            yield list(row)

def find_idx(header, *names):
    hl = [_norm(h) for h in header]
    for n in names:
        nl = _norm(n)
        if nl in hl:
            return hl.index(nl)
    return None

def main():
    path, out = sys.argv[1], sys.argv[2]
    rows = iter_rows(path)
    header = next(rows)
    i_ord = find_idx(header, "Order No.", "Order No", "OrderNo")
    i_em  = find_idx(header, "User Email", "Email", "user_email")
    i_od  = find_idx(header, "Only Date", "Order Date")
    i_od2 = find_idx(header, "Order Date")
    i_st  = find_idx(header, "Item Status", "Last Status")
    assert None not in (i_ord, i_em, i_od, i_st), f"missing cols: {(i_ord,i_em,i_od,i_st)} in {header}"

    orders = {}  # order_no -> [email, date, paid, delivered]
    qc = {"file": os.path.basename(path), "lines": 0, "blank_order": 0,
          "blank_email": 0, "bad_date": 0, "email_conflict_lines": 0,
          "status_counts": Counter(), "year_counts_lines": Counter()}

    maxcol = max(i_ord, i_em, i_od, (i_od2 or 0), i_st)
    for row in rows:
        if not row or len(row) <= maxcol:
            continue
        qc["lines"] += 1
        ono = row[i_ord]
        if ono is None or str(ono).strip() == "":
            qc["blank_order"] += 1
            continue
        ono = str(ono).strip()
        email = norm_email(row[i_em])
        if email == "":
            qc["blank_email"] += 1
        d = parse_date(row[i_od])
        if d is None and i_od2 is not None:
            d = parse_date(row[i_od2])
        if d is None:
            qc["bad_date"] += 1
        st = str(row[i_st]).strip().lower() if row[i_st] is not None else ""
        qc["status_counts"][st] += 1
        if d: qc["year_counts_lines"][d.year] += 1
        paid = 0 if st in NEVER_PAID else 1
        deliv = 1 if st in FULFILLED else 0

        rec = orders.get(ono)
        if rec is None:
            orders[ono] = [email, d, paid, deliv]
        else:
            if rec[0] == "" and email:
                rec[0] = email
            elif email and rec[0] and email != rec[0]:
                qc["email_conflict_lines"] += 1
            if d and (rec[1] is None or d < rec[1]):
                rec[1] = d
            rec[2] = rec[2] or paid
            rec[3] = rec[3] or deliv

    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["order_no", "email", "order_date", "year", "paid", "delivered"])
        for ono, (email, d, paid, deliv) in orders.items():
            w.writerow([ono, email, d.isoformat() if d else "",
                        d.year if d else "", paid, deliv])

    qc["unique_orders"] = len(orders)
    qc["status_counts"] = dict(qc["status_counts"].most_common())
    qc["year_counts_lines"] = dict(sorted(qc["year_counts_lines"].items()))
    with open(out + ".qc.json", "w") as f:
        json.dump(qc, f, indent=2, default=str)
    print(json.dumps({k: qc[k] for k in
          ["file","lines","unique_orders","blank_order","blank_email","bad_date",
           "email_conflict_lines","year_counts_lines"]}, indent=2, default=str))

if __name__ == "__main__":
    main()
