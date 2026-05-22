import json
from sqlalchemy.orm import Session
from src.database.models import AuditLedger
from src.governance.crypto import (
    calculate_record_hash,
    sign_data,
    verify_signature
)

GENESIS_HASH = "0" * 64

def append_audit_entry(db: Session, action: str, system_name: str, payload_data: dict) -> AuditLedger:
    """
    Appends a new audit record to the ledger, establishing a cryptographic hash link
    to the preceding record. Signs the new record block with the platform private key.
    """
    # 1. Standardise and serialise payload to deterministic JSON string
    payload_json = json.dumps(payload_data, sort_keys=True)

    # 2. Retrieve the absolute latest record in the chain to get its hash
    latest_record = db.query(AuditLedger).order_by(AuditLedger.id.desc()).first()
    
    if latest_record is None:
        # If no records exist, this is our genesis record
        previous_hash = GENESIS_HASH
    else:
        # Otherwise, the previous hash is the fingerprint of the latest block
        previous_hash = latest_record.record_hash

    # 3. Calculate the deterministic hash of the new record block
    record_hash = calculate_record_hash(action, system_name, payload_json, previous_hash)

    # 4. Create the RSA private-key signature on the record hash
    signature = sign_data(record_hash.encode("utf-8"))

    # 5. Insert block into PostgreSQL
    audit_entry = AuditLedger(
        action=action,
        system_name=system_name,
        payload=payload_json,
        previous_hash=previous_hash,
        record_hash=record_hash,
        signature=signature
    )
    db.add(audit_entry)
    db.commit()
    db.refresh(audit_entry)
    
    return audit_entry

def verify_audit_ledger(db: Session) -> dict:
    """
    Scans the entire audit_ledger table chronologically, verifying that every block's
    data matches its hash, its cryptographic signature is valid, and its link to the
    preceding block is completely unbroken.
    
    Returns a status dictionary detailing audit outcome.
    """
    # Fetch all records in ascending chronological order
    records = db.query(AuditLedger).order_by(AuditLedger.id.asc()).all()
    
    expected_previous_hash = GENESIS_HASH
    
    for idx, row in enumerate(records):
        # Check 1: Verify data integrity (Hash Check)
        calculated_hash = calculate_record_hash(
            row.action,
            row.system_name,
            row.payload,
            row.previous_hash
        )
        if calculated_hash != row.record_hash:
            return {
                "is_valid": False,
                "corrupted_id": row.id,
                "action_taken": row.action,
                "system_name": row.system_name,
                "reason": "Hash mismatch: Data inside the record has been modified after insertion."
            }
            
        # Check 2: Verify non-repudiation (Signature Check)
        is_signature_valid = verify_signature(
            row.record_hash.encode("utf-8"),
            row.signature
        )
        if not is_signature_valid:
            return {
                "is_valid": False,
                "corrupted_id": row.id,
                "action_taken": row.action,
                "system_name": row.system_name,
                "reason": "Cryptographic signature validation failed. The entry was signed by an unauthorised key or signature was altered."
            }
            
        # Check 3: Verify chain continuity (Previous Hash Link Check)
        if row.previous_hash != expected_previous_hash:
            return {
                "is_valid": False,
                "corrupted_id": row.id,
                "action_taken": row.action,
                "system_name": row.system_name,
                "reason": f"Previous hash link broken! Expected previous hash '{expected_previous_hash[:10]}...' but found '{row.previous_hash[:10]}...'. A record has likely been deleted."
            }
            
        # Move chain forward
        expected_previous_hash = row.record_hash
        
    return {
        "is_valid": True,
        "total_records_verified": len(records),
        "status": "Ledger is mathematically intact. No deletions, insertions, or updates detected."
    }
