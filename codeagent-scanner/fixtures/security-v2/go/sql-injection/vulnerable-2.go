package fixture
import (
"net/http"
"database/sql"
"crypto/tls"
)
func handler(r *http.Request, db *sql.DB) {
id := r.FormValue("id")
db.Exec("DELETE FROM users WHERE id=" + id)
}
