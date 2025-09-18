import psycopg2
from psycopg2.extras import DictCursor


class UserRepository:
    def __init__(self, conn):
        self.conn = conn

    def get_content(self):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM users")
            return [dict(row) for row in cur]

    def find(self, id):
        with self.conn.cursor(cursor_factory=DictCursor) as cur:
            cur.execute("SELECT * FROM users WHERE id = %s", (id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def save(self, user_data):
        if "id" in user_data and user_data["id"]:
            self._update(user_data)
            return user_data["id"]
        else:
            return self._create(user_data)

    def _create(self, user_data):
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email) VALUES (%s, %s) RETURNING id",
                (user_data["name"], user_data["email"]),
            )
            user_id = cur.fetchone()[0]
        self.conn.commit()
        return user_id

    def _update(self, user_data):
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE users SET name = %s, email = %s WHERE id = %s",
                (user_data["name"], user_data["email"], user_data["id"]),
            )
        self.conn.commit()

    def destroy(self, id):
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM users WHERE id = %s", (id,))
        self.conn.commit()
