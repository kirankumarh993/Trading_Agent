"""
Cryptographic Licensing & Client Access Guard (HMAC-SHA256)
"""
import os
import json
import hmac
import hashlib
import base64
import datetime
from typing import Dict, Tuple
from config.settings import MASTER_SECRET_KEY, REGISTRY_FILE, CLIENT_LICENSE_FILE

class LicenseAuthority:
    def __init__(self, registry_file: str = REGISTRY_FILE):
        self.registry_file = registry_file
        self.registry = self._load()

    def _load(self) -> Dict[str, dict]:
        if not os.path.exists(self.registry_file):
            return {}
        try:
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}

    def _save(self):
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2)

    def generate_license(self, user_name: str, days_valid: int) -> str:
        issue_date = datetime.date.today()
        expiry_date = issue_date + datetime.timedelta(days=days_valid)
        payload = {
            "user_name": user_name,
            "issued_on": str(issue_date),
            "expires_on": str(expiry_date),
            "days_allowed": days_valid,
            "status": "ACTIVE"
        }
        raw_bytes = json.dumps(payload, sort_keys=True).encode('utf-8')
        sig = hmac.new(MASTER_SECRET_KEY.encode('utf-8'), raw_bytes, hashlib.sha256).hexdigest()
        container = {"payload": payload, "signature": sig}
        encoded = base64.b64encode(json.dumps(container).encode('utf-8')).decode('utf-8')
        lic_id = f"LIC_{user_name.upper()}_{issue_date.strftime('%Y%m%d')}"
        self.registry[lic_id] = {
            "user_name": user_name,
            "license_id": lic_id,
            "license_key": encoded,
            "issued_on": str(issue_date),
            "expires_on": str(expiry_date),
            "days_allowed": days_valid,
            "status": "ACTIVE"
        }
        self._save()
        return encoded

    def revoke_license(self, user_name: str) -> bool:
        revoked = False
        for lic_id, info in self.registry.items():
            if info["user_name"].lower() == user_name.lower():
                info["status"] = "REVOKED"
                revoked = True
        if revoked:
            self._save()
        return revoked

    def get_dashboard_summary(self) -> Dict:
        today = str(datetime.date.today())
        total = len(self.registry)
        active, expired, revoked = 0, 0, 0
        user_list = []
        for lic_id, info in self.registry.items():
            is_expired = info["expires_on"] < today
            st = info["status"]
            if st == "REVOKED":
                revoked += 1
                curr = "REVOKED"
            elif is_expired:
                expired += 1
                curr = "EXPIRED"
            else:
                active += 1
                curr = "ACTIVE"
            user_list.append({"User": info["user_name"], "Issued": info["issued_on"], "Expires": info["expires_on"], "Status": curr})
        return {"total": total, "active": active, "expired": expired, "revoked": revoked, "users": user_list}

class LicenseGuard:
    def __init__(self, license_file: str = CLIENT_LICENSE_FILE):
        self.license_file = license_file

    def verify_access(self) -> Tuple[bool, str]:
        if not os.path.exists(self.license_file):
            return False, "NO_LICENSE_FOUND: Please obtain a valid license.key from the owner."
        try:
            with open(self.license_file, 'r', encoding='utf-8') as f:
                encoded = f.read().strip()
            container = json.loads(base64.b64decode(encoded.encode('utf-8')).decode('utf-8'))
            payload = container["payload"]
            sig = container["signature"]
            raw = json.dumps(payload, sort_keys=True).encode('utf-8')
            expected = hmac.new(MASTER_SECRET_KEY.encode('utf-8'), raw, hashlib.sha256).hexdigest()
            if not hmac.compare_digest(sig, expected):
                return False, "INVALID_SIGNATURE: License corrupted or modified."
            today = datetime.date.today()
            exp = datetime.datetime.strptime(payload["expires_on"], '%Y-%m-%d').date()
            if (exp - today).days < 0:
                return False, f"LICENSE_EXPIRED: Access expired on {exp}."
            if os.path.exists(REGISTRY_FILE):
                try:
                    with open(REGISTRY_FILE, 'r', encoding='utf-8') as reg_f:
                        reg = json.load(reg_f)
                    for _, inf in reg.items():
                        if inf["user_name"].lower() == payload["user_name"].lower() and inf["status"] == "REVOKED":
                            return False, "LICENSE_REVOKED: Access has been revoked by the owner."
                except Exception:
                    pass
            return True, f"ACCESS_GRANTED: Valid for '{payload['user_name']}' until {exp} ({(exp - today).days} days left)."
        except Exception as e:
            return False, f"VERIFICATION_ERROR: {str(e)}"
