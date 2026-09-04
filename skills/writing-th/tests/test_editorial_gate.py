"""Regression tests for contract, receipt, hash, and merge enforcement."""

from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SKILL = TESTS.parent
SCRIPTS = SKILL / "scripts"
ROOT = TESTS.parents[3]
LEXICON = ROOT / "ψ" / "memory" / "style" / "LEXICON_TH.json"
sys.path.insert(0, str(SCRIPTS))

from _venv import child_python
from editorial_gate import scaffold, verify_review


def contract(profile="executive-summary", mode="synthesis"):
    return {
        "schema_version": "1.0",
        "profile": profile,
        "transformation_mode": mode,
        "audience": "ผู้บริหารกรมฯ",
        "decision_use": "ตัดสินใจเลือกทิศทางการพัฒนาระบบข้อมูล",
        "section_job": "อธิบายปัญหาและข้อสรุปที่กำกับการตัดสินใจ",
        "target_altitude": "บทสรุปสำหรับผู้บริหาร",
        "inclusions": ["ข้อค้นพบ", "ผลต่อการตัดสินใจ"],
        "exclusions": ["รายละเอียดวิธีศึกษา", "เลขสไลด์"],
        "evidence_policy": "ใช้ข้อเท็จจริงที่ตรวจสอบแล้วและแยกตัวชี้แหล่งข้อมูลออกจากเนื้อหา",
        "required_concepts": ["การค้นพบข้อมูล", "ความน่าเชื่อถือ"],
        "terminology": {"client": "กรมฯ", "actor": "คณะที่ปรึกษา"},
        "required_structures": [],
        "source_paths": ["source.md"] if mode == "rewrite" else [],
        "reference_samples": ["approved-sample.md"],
        "approval": {
            "status": "approved",
            "approved_by": "Boss",
            "approved_at": "2026-08-28T01:00:00+07:00",
        },
    }


def complete_review(review, mode="synthesis"):
    review = copy.deepcopy(review)
    review["reviewer"] = "blind-reviewer"
    for name, item in review["dimensions"].items():
        item["verdict"] = "not_applicable" if name == "source_fidelity" and mode == "new" else "pass"
        item["evidence"] = f"Verified {name} against the approved contract and exact draft."
    review["verdict"] = "pass"
    return review


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def expect(condition, message, failures):
    if not condition:
        failures.append(message)


def main():
    failures = []
    with tempfile.TemporaryDirectory(prefix="writing_th_v5_") as temp:
        base = Path(temp)
        draft = base / "draft.md"
        contract_path = base / "writing-contract.json"
        review_path = base / "editorial-review.json"
        draft.write_text(
            "กรมฯ ใช้บัญชีรายการข้อมูลเพื่อระบุชุดข้อมูลที่หน่วยงานต้องปรับปรุง "
            "ทำให้การจัดลำดับงานมีหลักฐานรองรับและกำหนดผู้รับผิดชอบได้ชัดเจน\n",
            encoding="utf-8",
        )
        write_json(contract_path, contract())
        review = complete_review(scaffold(str(draft), str(contract_path), "independent"))
        write_json(review_path, review)

        ok, _, errors, warnings = verify_review(draft, contract_path, review_path)
        expect(ok and not errors and not warnings, "independent passing receipt rejected", failures)

        self_review = complete_review(scaffold(str(draft), str(contract_path), "self"))
        write_json(review_path, self_review)
        ok, _, _, warnings = verify_review(draft, contract_path, review_path)
        expect(ok and any("DEGRADED" in item for item in warnings),
               "self-review did not pass with degraded warning", failures)

        write_json(review_path, review)
        draft.write_text(draft.read_text(encoding="utf-8") + "แก้ไขภายหลังการทบทวน\n", encoding="utf-8")
        ok, _, errors, _ = verify_review(draft, contract_path, review_path)
        expect(not ok and any("draft_sha256" in item for item in errors),
               "stale draft receipt was accepted", failures)
        draft.write_text(
            "กรมฯ ใช้บัญชีรายการข้อมูลเพื่อระบุชุดข้อมูลที่หน่วยงานต้องปรับปรุง "
            "ทำให้การจัดลำดับงานมีหลักฐานรองรับและกำหนดผู้รับผิดชอบได้ชัดเจน\n",
            encoding="utf-8",
        )

        major = copy.deepcopy(review)
        major["findings"] = [{
            "severity": "major", "location": "paragraph 1", "issue": "wrong altitude",
            "status": "unresolved", "disposition": "revise before release",
        }]
        write_json(review_path, major)
        ok, _, errors, _ = verify_review(draft, contract_path, review_path)
        expect(not ok and any("major finding must be resolved" in item for item in errors),
               "unresolved major finding was accepted", failures)

        write_json(review_path, review)
        ok, _, errors, _ = verify_review(
            draft, contract_path, review_path, mechanical_reviews=["[META] exact warning"])
        expect(not ok and any("lacks disposition" in item for item in errors),
               "missing mechanical disposition was accepted", failures)
        covered = copy.deepcopy(review)
        covered["mechanical_reviews"] = [{
            "message": "[META] exact warning", "disposition": "Removed from final prose"
        }]
        write_json(review_path, covered)
        ok, _, errors, _ = verify_review(
            draft, contract_path, review_path, mechanical_reviews=["[META] exact warning"])
        expect(ok and not errors, "covered mechanical review was rejected", failures)

        new_contract = contract(profile="report", mode="new")
        write_json(contract_path, new_contract)
        new_review = complete_review(scaffold(str(draft), str(contract_path), "independent"), mode="new")
        write_json(review_path, new_review)
        ok, _, errors, _ = verify_review(draft, contract_path, review_path)
        expect(ok and not errors, "new-mode source_fidelity not_applicable was rejected", failures)

        # Exercise the real merge path with a valid receipt, then prove a stale
        # receipt cannot touch a second destination.
        destination = base / "merged.md"
        proc = subprocess.run([
            child_python(), str(SCRIPTS / "merge_draft.py"), str(draft), str(destination),
            "--lexicon", str(LEXICON), "--contract", str(contract_path), "--review", str(review_path),
        ], capture_output=True, text=True, encoding="utf-8", errors="replace")
        expect(proc.returncode == 0 and destination.read_bytes() == draft.read_bytes(),
               "valid hash-bound merge failed", failures)

        stale_destination = base / "must-not-exist.md"
        draft.write_text(draft.read_text(encoding="utf-8") + "เปลี่ยนหลังออกใบรับรอง\n", encoding="utf-8")
        proc = subprocess.run([
            child_python(), str(SCRIPTS / "merge_draft.py"), str(draft), str(stale_destination),
            "--lexicon", str(LEXICON), "--contract", str(contract_path), "--review", str(review_path),
        ], capture_output=True, text=True, encoding="utf-8", errors="replace")
        expect(proc.returncode != 0 and not stale_destination.exists()
               and "editorial gate failed" in proc.stdout.lower(),
               "stale receipt did not block merge", failures)

    if failures:
        print(f"FAILED: {len(failures)} editorial harness case(s)")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("PASSED: 8 editorial harness scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())

