import uuid
from database.connection import get_db_connection

def create_enrollment_token(organization_id: str, max_uses: int = 1) -> dict:
    """Generates a new enrollment token and saves it to the database."""
    token_str = f"tok_{uuid.uuid4().hex[:16]}"
    
    with get_db_connection() as conn:
        conn.execute(
            """
            INSERT INTO enrollment_tokens (token, organization_id, max_uses, uses)
            VALUES (?, ?, ?, 0);
            """,
            (token_str, organization_id, max_uses)
        )
        
        cursor = conn.execute("SELECT * FROM enrollment_tokens WHERE token = ?;", (token_str,))
        row = cursor.fetchone()
        return dict(row) if row else None

def get_enrollment_token(token: str) -> dict:
    """Retrieves an enrollment token's details."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT * FROM enrollment_tokens WHERE token = ?;", (token,))
        row = cursor.fetchone()
        return dict(row) if row else None

def consume_enrollment_token(token_str: str) -> bool:
    """Checks token availability and increments usage count. Returns True if consumed successfully."""
    with get_db_connection() as conn:
        cursor = conn.execute("SELECT uses, max_uses FROM enrollment_tokens WHERE token = ?;", (token_str,))
        row = cursor.fetchone()
        if not row:
            return False
            
        uses, max_uses = row["uses"], row["max_uses"]
        if uses >= max_uses:
            return False
            
        conn.execute(
            "UPDATE enrollment_tokens SET uses = uses + 1 WHERE token = ?;",
            (token_str,)
        )
        return True
