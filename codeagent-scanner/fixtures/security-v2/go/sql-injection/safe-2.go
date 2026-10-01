package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
db.Exec("DELETE FROM users WHERE id=42")
}
